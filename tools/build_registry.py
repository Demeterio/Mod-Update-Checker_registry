#!/usr/bin/env python3
"""Build a fresh unsigned MUC registry from reviewed GitHub Release sources."""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from functools import total_ordering
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ENTRY_SCHEMA = 1
REGISTRY_SCHEMA = 1
MAX_ENTRY_FILES = 10000
MAX_GENERATED_ENTRIES = 10000
MAX_RELEASE_PAGES = 10
RELEASES_PER_PAGE = 100
REQUEST_TIMEOUT_SECONDS = 20
GITHUB_API_VERSION = "2026-03-10"

MOD_ID_PATTERN = re.compile(r"^[a-z0-9_-]+\.[a-z0-9_-]+\.[0-9A-F]{16}$")
REPOSITORY_PATTERN = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9_.-]{0,98}[A-Za-z0-9])?/"
    r"[A-Za-z0-9](?:[A-Za-z0-9_.-]{0,98}[A-Za-z0-9])?$"
)
GITHUB_LOGIN_PATTERN = re.compile(
    r"^[a-z0-9](?:[a-z0-9-]{0,37}[a-z0-9])?$"
)
TAG_PREFIX_PATTERN = re.compile(
    r"^(?:[A-Za-z0-9][A-Za-z0-9._/+\-]{0,95})?$"
)
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
ENTRY_FIELDS = frozenset(
    ("$schema", "schema", "mod_id", "display_name", "creator_name", "mod_page", "maintainers", "source")
)
SOURCE_FIELDS = frozenset(("type", "repository", "tag_prefix", "channels"))
CHANNELS = frozenset(("stable", "prerelease"))


class RegistrySourceError(Exception):
    """Raised when reviewed source data cannot produce a safe registry."""


@total_ordering
class SemVer:
    __slots__ = ("major", "minor", "patch", "prerelease", "text")

    def __init__(self, major, minor, patch, prerelease, text):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.text = text

    @classmethod
    def parse(cls, text: str) -> "SemVer":
        if not isinstance(text, str) or text != text.strip():
            raise RegistrySourceError("Version must be an exact string")
        match = SEMVER_PATTERN.fullmatch(text)
        if match is None:
            raise RegistrySourceError("Version is not valid SemVer: {}".format(text))
        prerelease = []
        if match.group(4):
            for identifier in match.group(4).split("."):
                if identifier.isdigit():
                    if len(identifier) > 1 and identifier.startswith("0"):
                        raise RegistrySourceError(
                            "Numeric prerelease identifiers must not contain leading zeroes: {}".format(text)
                        )
                    prerelease.append(int(identifier))
                else:
                    prerelease.append(identifier)
        return cls(int(match.group(1)), int(match.group(2)), int(match.group(3)), tuple(prerelease), text)

    def __eq__(self, other):
        if not isinstance(other, SemVer):
            return NotImplemented
        return (self.major, self.minor, self.patch, self.prerelease) == (
            other.major, other.minor, other.patch, other.prerelease
        )

    def __lt__(self, other):
        if not isinstance(other, SemVer):
            return NotImplemented
        left_core = (self.major, self.minor, self.patch)
        right_core = (other.major, other.minor, other.patch)
        if left_core != right_core:
            return left_core < right_core
        if not self.prerelease:
            return False
        if not other.prerelease:
            return True
        for left, right in zip(self.prerelease, other.prerelease):
            if left == right:
                continue
            left_numeric = isinstance(left, int)
            right_numeric = isinstance(right, int)
            if left_numeric and right_numeric:
                return left < right
            if left_numeric != right_numeric:
                return left_numeric
            return str(left) < str(right)
        return len(self.prerelease) < len(other.prerelease)


def utc_now_text() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise RegistrySourceError("JSON contains duplicate key: {}".format(key))
        result[key] = value
    return result


def require_string(value, field_name, maximum, allow_empty=False):
    if not isinstance(value, str):
        raise RegistrySourceError("{} must be a string".format(field_name))
    if value != value.strip():
        raise RegistrySourceError(
            "{} must not contain leading or trailing whitespace".format(field_name)
        )
    if not value and not allow_empty:
        raise RegistrySourceError("{} must not be empty".format(field_name))
    if len(value) > maximum:
        raise RegistrySourceError("{} is too long".format(field_name))
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise RegistrySourceError("{} must not contain control characters".format(field_name))
    return value


def validate_mod_page(value):
    mod_page = require_string(value, "mod_page", 2048)
    if any(character.isspace() for character in mod_page):
        raise RegistrySourceError("mod_page must not contain whitespace")
    try:
        parsed = urllib.parse.urlsplit(mod_page)
        parsed.port
    except ValueError as exc:
        raise RegistrySourceError("mod_page is not a valid HTTPS URL") from exc
    if parsed.scheme != "https" or not parsed.netloc or parsed.hostname is None:
        raise RegistrySourceError("mod_page must use HTTPS and include a public hostname")
    if parsed.username is not None or parsed.password is not None:
        raise RegistrySourceError("mod_page must not contain embedded credentials")
    hostname = parsed.hostname.lower().rstrip(".")
    if hostname == "localhost" or hostname.endswith(".local"):
        raise RegistrySourceError("mod_page must use a public hostname")
    return mod_page


def load_json(path: Path):
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise RegistrySourceError("Unable to read {}".format(path)) from exc
    if not raw:
        raise RegistrySourceError("{} must not be empty".format(path))
    if raw.startswith(b"\xef\xbb\xbf"):
        raise RegistrySourceError("{} must not contain a UTF-8 BOM".format(path))
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicate_keys)
    except RegistrySourceError:
        raise
    except (UnicodeDecodeError, TypeError, ValueError) as exc:
        raise RegistrySourceError("{} is not valid UTF-8 JSON".format(path)) from exc
    if not isinstance(data, dict):
        raise RegistrySourceError("{} root must be an object".format(path))
    return data


def validate_entry(path: Path, data):
    if frozenset(data.keys()) != ENTRY_FIELDS:
        raise RegistrySourceError("{} contains invalid root fields".format(path))
    if data["$schema"] != "../schemas/mod-entry.schema.json":
        raise RegistrySourceError("{} has an invalid $schema path".format(path))
    if isinstance(data["schema"], bool) or data["schema"] != ENTRY_SCHEMA:
        raise RegistrySourceError("{} schema must be integer 1".format(path))

    mod_id = require_string(data["mod_id"], "mod_id", 128)
    if MOD_ID_PATTERN.fullmatch(mod_id) is None:
        raise RegistrySourceError("{} contains an invalid mod_id".format(path))
    expected_filename = "{}.json".format(mod_id)
    if path.name != expected_filename:
        raise RegistrySourceError("{} must be named {}".format(path, expected_filename))

    display_name = require_string(data["display_name"], "display_name", 128)
    creator_name = require_string(data["creator_name"], "creator_name", 128)
    mod_page = validate_mod_page(data["mod_page"])

    maintainers = data["maintainers"]
    if not isinstance(maintainers, list) or not 1 <= len(maintainers) <= 20:
        raise RegistrySourceError("{} maintainers must contain 1 to 20 GitHub usernames".format(path))
    seen_maintainers = set()
    validated_maintainers = []
    for maintainer in maintainers:
        login = require_string(maintainer, "maintainer", 39)
        if GITHUB_LOGIN_PATTERN.fullmatch(login) is None:
            raise RegistrySourceError(
                "{} contains an invalid or non-lowercase GitHub maintainer".format(path)
            )
        if login in seen_maintainers:
            raise RegistrySourceError("{} contains a duplicate maintainer".format(path))
        seen_maintainers.add(login)
        validated_maintainers.append(login)

    source = data["source"]
    if not isinstance(source, dict) or frozenset(source.keys()) != SOURCE_FIELDS:
        raise RegistrySourceError("{} source fields are invalid".format(path))
    if source["type"] != "github_releases":
        raise RegistrySourceError("{} source.type must be github_releases".format(path))

    repository = require_string(source["repository"], "source.repository", 201)
    if REPOSITORY_PATTERN.fullmatch(repository) is None or ".." in repository:
        raise RegistrySourceError("{} source.repository must use valid Owner/Repository format".format(path))

    tag_prefix = require_string(source["tag_prefix"], "source.tag_prefix", 96, allow_empty=True)
    if TAG_PREFIX_PATTERN.fullmatch(tag_prefix) is None:
        raise RegistrySourceError(
            "{} source.tag_prefix must be empty or start with an alphanumeric character".format(path)
        )

    channels = source["channels"]
    if not isinstance(channels, list) or not 1 <= len(channels) <= 2:
        raise RegistrySourceError("{} source.channels must contain one or two channels".format(path))
    seen_channels = set()
    for channel in channels:
        if not isinstance(channel, str) or channel not in CHANNELS:
            raise RegistrySourceError("{} contains an invalid release channel".format(path))
        if channel in seen_channels:
            raise RegistrySourceError("{} contains a duplicate release channel".format(path))
        seen_channels.add(channel)

    return {
        "mod_id": mod_id,
        "display_name": display_name,
        "creator_name": creator_name,
        "mod_page": mod_page,
        "maintainers": validated_maintainers,
        "repository": repository,
        "tag_prefix": tag_prefix,
        "channels": list(channels),
        "path": str(path),
    }


def load_entries(entries_directory: Path):
    if not entries_directory.is_dir():
        raise RegistrySourceError("Entries directory was not found: {}".format(entries_directory))
    paths = sorted(entries_directory.glob("*.json"))
    if len(paths) > MAX_ENTRY_FILES:
        raise RegistrySourceError("Too many registry entry files")
    entries = []
    seen_mod_ids = set()
    for path in paths:
        if not path.is_file():
            continue
        entry = validate_entry(path, load_json(path))
        if entry["mod_id"] in seen_mod_ids:
            raise RegistrySourceError("Duplicate mod_id: {}".format(entry["mod_id"]))
        seen_mod_ids.add(entry["mod_id"])
        entries.append(entry)
    return entries


def github_headers(token=""):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Demeterio-MUC-Registry-Builder",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }
    if token:
        headers["Authorization"] = "Bearer {}".format(token)
    return headers


def request_github_json(url, token):
    attempts = [token, ""] if token else [""]
    last_error = None
    for attempt_token in attempts:
        request = urllib.request.Request(url, headers=github_headers(attempt_token), method="GET")
        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            last_error = exc
            if attempt_token and exc.code in (401, 403, 404):
                continue
            detail = ""
            try:
                detail = exc.read().decode("utf-8", errors="replace").strip()
            except Exception:
                pass
            raise RegistrySourceError(
                "GitHub API returned HTTP {} for {}{}".format(
                    exc.code, url, ": {}".format(detail[:300]) if detail else ""
                )
            ) from exc
        except (OSError, urllib.error.URLError) as exc:
            raise RegistrySourceError("Unable to contact GitHub: {}".format(exc)) from exc
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, TypeError, ValueError) as exc:
            raise RegistrySourceError("GitHub returned invalid JSON") from exc
    raise RegistrySourceError(
        "GitHub API returned HTTP {}".format(last_error.code if last_error else "unknown")
    )


def fetch_releases(repository, token):
    owner, name = repository.split("/", 1)
    releases = []
    for page in range(1, MAX_RELEASE_PAGES + 1):
        url = (
            "https://api.github.com/repos/{}/{}/releases?per_page={}&page={}"
        ).format(
            urllib.parse.quote(owner, safe=""),
            urllib.parse.quote(name, safe=""),
            RELEASES_PER_PAGE,
            page,
        )
        data = request_github_json(url, token)
        if not isinstance(data, list):
            raise RegistrySourceError("GitHub Releases response for {} is not an array".format(repository))
        releases.extend(item for item in data if isinstance(item, dict))
        if len(data) < RELEASES_PER_PAGE:
            return releases
    raise RegistrySourceError("{} has too many retrievable releases".format(repository))


def release_candidate(release, tag_prefix, channel):
    if release.get("draft") is True:
        return None
    prerelease_flag = release.get("prerelease")
    if channel == "stable" and prerelease_flag is not False:
        return None
    if channel == "prerelease" and prerelease_flag is not True:
        return None
    tag_name = release.get("tag_name")
    if not isinstance(tag_name, str) or tag_name != tag_name.strip():
        return None
    if not tag_name.startswith(tag_prefix):
        return None
    if len(tag_name) > 128:
        raise RegistrySourceError("Matching release tag is longer than 128 characters")
    version_text = tag_name[len(tag_prefix):]
    try:
        version = SemVer.parse(version_text)
    except RegistrySourceError:
        return None
    if channel == "stable" and version.prerelease:
        return None
    published_at = release.get("published_at")
    return version, tag_name, published_at if isinstance(published_at, str) else ""


def choose_release(releases, tag_prefix, channel):
    best = None
    for release in releases:
        candidate = release_candidate(release, tag_prefix, channel)
        if candidate is None:
            continue
        if best is None or candidate[0] > best[0] or (
            candidate[0] == best[0] and candidate[2] > best[2]
        ):
            best = candidate
    return best


def resolve_registry_entries(sources, token):
    repository_cache = {}
    generated = []
    warnings = []
    checked_at = utc_now_text()
    for source in sources:
        repository = source["repository"]
        if repository not in repository_cache:
            repository_cache[repository] = fetch_releases(repository, token)
        found_any = False
        for channel in source["channels"]:
            candidate = choose_release(
                repository_cache[repository], source["tag_prefix"], channel
            )
            if candidate is None:
                if channel == "prerelease" and "stable" in source["channels"]:
                    warnings.append(
                        "{} has no matching prerelease; stable remains available".format(source["mod_id"])
                    )
                    continue
                raise RegistrySourceError(
                    "{} has no matching published {} GitHub Release in {} using tag prefix {!r}".format(
                        source["mod_id"], channel, repository, source["tag_prefix"]
                    )
                )
            version, release_tag, _published_at = candidate
            generated.append(
                {
                    "mod_id": source["mod_id"],
                    "release_channel": channel,
                    "version": version.text,
                    "release_tag": release_tag,
                    "checked_at": checked_at,
                }
            )
            found_any = True
            if len(generated) > MAX_GENERATED_ENTRIES:
                raise RegistrySourceError("Generated registry contains too many channel entries")
        if not found_any:
            raise RegistrySourceError("{} did not produce any registry entry".format(source["mod_id"]))
    generated.sort(key=lambda item: (item["mod_id"], item["release_channel"]))
    return generated, warnings


def github_repository_url(repository):
    owner, name = repository.split("/", 1)
    return "https://github.com/{}/{}".format(
        urllib.parse.quote(owner, safe=""), urllib.parse.quote(name, safe="")
    )


def github_release_url(repository, release_tag):
    return "{}/releases/tag/{}".format(
        github_repository_url(repository), urllib.parse.quote(release_tag, safe="")
    )


def build_readable_registry(sources, entries):
    resolved = {}
    generated_at = ""
    for entry in entries:
        generated_at = max(generated_at, entry["checked_at"])
        resolved.setdefault(entry["mod_id"], {})[entry["release_channel"]] = entry
    if not generated_at:
        generated_at = utc_now_text()
    mods = []
    for source in sources:
        channel_entries = resolved.get(source["mod_id"], {})
        def channel_data(name):
            item = channel_entries.get(name)
            if item is None:
                return None
            return {
                "version": item["version"],
                "release_tag": item["release_tag"],
                "release_url": github_release_url(source["repository"], item["release_tag"]),
                "checked_at": item["checked_at"],
            }
        checked_values = [item["checked_at"] for item in channel_entries.values()]
        mods.append(
            {
                "mod_id": source["mod_id"],
                "display_name": source["display_name"],
                "creator_name": source["creator_name"],
                "mod_page": source["mod_page"],
                "repository": source["repository"],
                "repository_url": github_repository_url(source["repository"]),
                "configured_channels": list(source["channels"]),
                "stable": channel_data("stable"),
                "prerelease": channel_data("prerelease"),
                "checked_at": max(checked_values) if checked_values else "",
            }
        )
    mods.sort(key=lambda item: (item["display_name"].casefold(), item["creator_name"].casefold(), item["mod_id"]))
    return {"schema": 1, "generated_at": generated_at, "mods": mods}


def write_json(output, document, compact=False):
    output.parent.mkdir(parents=True, exist_ok=True)
    if compact:
        encoded = json.dumps(document, ensure_ascii=False, separators=(",", ":")) + "\n"
    else:
        encoded = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    with output.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(encoded)


def write_readable_registry(output, sources, entries):
    """Write the human-readable catalogue document."""

    write_json(output, build_readable_registry(sources, entries))


def write_registry(output, entries):
    # Always issue a fresh signed payload. Reusing old payload bytes would keep
    # generated_at stale and would undermine the player's replay protection.
    write_json(
        output,
        {"schema": REGISTRY_SCHEMA, "generated_at": utc_now_text(), "entries": list(entries)},
    )


def build_parser():
    parser = argparse.ArgumentParser(
        description="Validate reviewed MUC entry files and resolve public GitHub Releases into one fresh unsigned registry."
    )
    parser.add_argument("--entries", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--readable-output")
    return parser


def main():
    args = build_parser().parse_args()
    token = os.environ.get("MUC_GITHUB_API_TOKEN", "").strip() or os.environ.get("GITHUB_TOKEN", "").strip()
    try:
        sources = load_entries(Path(args.entries).resolve())
        entries, warnings = resolve_registry_entries(sources, token)
        write_registry(Path(args.output).resolve(), entries)
        if args.readable_output:
            write_readable_registry(
                Path(args.readable_output).resolve(),
                sources,
                entries,
            )
    except RegistrySourceError as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        return 1
    for warning in warnings:
        print("WARNING: {}".format(warning))
    print("Validated source files: {}".format(len(sources)))
    print("Generated registry entries: {}".format(len(entries)))
    print("Unsigned registry written to: {}".format(args.output))
    if args.readable_output:
        print("Readable registry written to: {}".format(args.readable_output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
