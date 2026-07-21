#!/usr/bin/env python3
"""Build the unsigned MUC registry from reviewed public GitHub Release sources."""

import argparse
import base64
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
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

ENTRY_SCHEMA = 1
REGISTRY_SCHEMA = 1
MAX_ENTRY_FILES = 10000
MAX_GENERATED_ENTRIES = 10000
MAX_RELEASE_PAGES = 10
RELEASES_PER_PAGE = 100
REQUEST_TIMEOUT_SECONDS = 20
GITHUB_API_VERSION = "2026-03-10"

MOD_ID_PATTERN = re.compile(
    r"^[a-z0-9_-]+\.[a-z0-9_-]+\.[0-9A-F]{16}$"
)
REPOSITORY_PATTERN = re.compile(
    r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$"
)
GITHUB_LOGIN_PATTERN = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$"
)
TAG_PREFIX_PATTERN = re.compile(r"^[A-Za-z0-9._/+\-]*$")
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
ENTRY_FIELDS = frozenset(
    (
        "$schema",
        "schema",
        "mod_id",
        "display_name",
        "creator_name",
        "mod_page",
        "maintainers",
        "source",
    )
)
SOURCE_FIELDS = frozenset(
    ("type", "repository", "tag_prefix", "channels")
)
CHANNELS = frozenset(("stable", "prerelease"))


class RegistrySourceError(Exception):
    """Raised when reviewed source data cannot produce a safe registry."""


@total_ordering
class SemVer:
    __slots__ = ("major", "minor", "patch", "prerelease", "text")

    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        prerelease: Tuple[object, ...],
        text: str,
    ) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.text = text

    @classmethod
    def parse(cls, text: str) -> "SemVer":
        match = SEMVER_PATTERN.fullmatch(text)
        if match is None:
            raise RegistrySourceError(
                "Version is not valid SemVer: {}".format(text)
            )
        prerelease_text = match.group(4)
        prerelease = []  # type: List[object]
        if prerelease_text:
            for identifier in prerelease_text.split("."):
                if identifier.isdigit():
                    if len(identifier) > 1 and identifier.startswith("0"):
                        raise RegistrySourceError(
                            "Numeric prerelease identifiers must not contain "
                            "leading zeroes: {}".format(text)
                        )
                    prerelease.append(int(identifier))
                else:
                    prerelease.append(identifier)
        return cls(
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
            tuple(prerelease),
            text,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        return (
            self.major,
            self.minor,
            self.patch,
            self.prerelease,
        ) == (
            other.major,
            other.minor,
            other.patch,
            other.prerelease,
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        core_self = (self.major, self.minor, self.patch)
        core_other = (other.major, other.minor, other.patch)
        if core_self != core_other:
            return core_self < core_other

        if not self.prerelease:
            return False if not other.prerelease else False
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
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def reject_duplicate_keys(
    pairs: List[Tuple[str, Any]],
) -> Dict[str, Any]:
    result = {}  # type: Dict[str, Any]
    for key, value in pairs:
        if key in result:
            raise RegistrySourceError(
                "JSON contains duplicate key: {}".format(key)
            )
        result[key] = value
    return result


def require_string(
    value: object,
    field_name: str,
    maximum: int,
    allow_empty: bool = False,
) -> str:
    if not isinstance(value, str):
        raise RegistrySourceError(
            "{} must be a string".format(field_name)
        )
    if value != value.strip():
        raise RegistrySourceError(
            "{} must not contain leading or trailing whitespace".format(
                field_name
            )
        )
    if not value and not allow_empty:
        raise RegistrySourceError(
            "{} must not be empty".format(field_name)
        )
    if len(value) > maximum:
        raise RegistrySourceError(
            "{} is too long".format(field_name)
        )
    return value


def validate_mod_page(value: object) -> str:
    """Validate a public review-only HTTPS page without fetching it."""

    mod_page = require_string(value, "mod_page", 2048)

    if any(character.isspace() for character in mod_page):
        raise RegistrySourceError(
            "mod_page must not contain whitespace"
        )
    if not mod_page.startswith("https://"):
        raise RegistrySourceError(
            "mod_page must use HTTPS"
        )

    try:
        parsed = urllib.parse.urlsplit(mod_page)
        # Reading the port also detects malformed port declarations.
        parsed.port
    except ValueError as exc:
        raise RegistrySourceError(
            "mod_page is not a valid HTTPS URL"
        ) from exc

    if parsed.scheme != "https":
        raise RegistrySourceError(
            "mod_page must use HTTPS"
        )
    if not parsed.netloc or parsed.hostname is None:
        raise RegistrySourceError(
            "mod_page must include a public hostname"
        )
    if parsed.username is not None or parsed.password is not None:
        raise RegistrySourceError(
            "mod_page must not contain embedded credentials"
        )

    hostname = parsed.hostname.lower().rstrip(".")
    if hostname == "localhost" or hostname.endswith(".local"):
        raise RegistrySourceError(
            "mod_page must use a public hostname"
        )

    return mod_page


def load_json(path: Path) -> Dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise RegistrySourceError(
            "Unable to read {}".format(path)
        ) from exc
    if not raw:
        raise RegistrySourceError(
            "{} must not be empty".format(path)
        )
    if raw.startswith(b"\xef\xbb\xbf"):
        raise RegistrySourceError(
            "{} must not contain a UTF-8 BOM".format(path)
        )
    try:
        data = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
    except RegistrySourceError:
        raise
    except (UnicodeDecodeError, TypeError, ValueError) as exc:
        raise RegistrySourceError(
            "{} is not valid UTF-8 JSON".format(path)
        ) from exc
    if not isinstance(data, dict):
        raise RegistrySourceError(
            "{} root must be an object".format(path)
        )
    return data


def validate_entry(path: Path, data: Dict[str, Any]) -> Dict[str, Any]:
    if frozenset(data.keys()) != ENTRY_FIELDS:
        raise RegistrySourceError(
            "{} contains invalid root fields".format(path)
        )
    if data["$schema"] != "../schemas/mod-entry.schema.json":
        raise RegistrySourceError(
            "{} has an invalid $schema path".format(path)
        )
    schema = data["schema"]
    if isinstance(schema, bool) or schema != ENTRY_SCHEMA:
        raise RegistrySourceError(
            "{} schema must be integer 1".format(path)
        )

    mod_id = require_string(data["mod_id"], "mod_id", 128)
    if MOD_ID_PATTERN.fullmatch(mod_id) is None:
        raise RegistrySourceError(
            "{} contains an invalid mod_id".format(path)
        )
    expected_filename = "{}.json".format(mod_id)
    if path.name != expected_filename:
        raise RegistrySourceError(
            "{} must be named {}".format(path, expected_filename)
        )

    display_name = require_string(
        data["display_name"],
        "display_name",
        128,
    )
    creator_name = require_string(
        data["creator_name"],
        "creator_name",
        128,
    )
    mod_page = validate_mod_page(data["mod_page"])

    maintainers = data["maintainers"]
    if (
        not isinstance(maintainers, list)
        or not 1 <= len(maintainers) <= 20
    ):
        raise RegistrySourceError(
            "{} maintainers must contain 1 to 20 GitHub usernames".format(
                path
            )
        )
    normalized_maintainers = []  # type: List[str]
    seen_maintainers = set()
    for maintainer in maintainers:
        login = require_string(maintainer, "maintainer", 39)
        if GITHUB_LOGIN_PATTERN.fullmatch(login) is None:
            raise RegistrySourceError(
                "{} contains an invalid GitHub maintainer".format(path)
            )
        lowered = login.lower()
        if lowered in seen_maintainers:
            raise RegistrySourceError(
                "{} contains a duplicate maintainer".format(path)
            )
        seen_maintainers.add(lowered)
        normalized_maintainers.append(login)

    source = data["source"]
    if not isinstance(source, dict):
        raise RegistrySourceError(
            "{} source must be an object".format(path)
        )
    if frozenset(source.keys()) != SOURCE_FIELDS:
        raise RegistrySourceError(
            "{} source contains invalid fields".format(path)
        )
    if source["type"] != "github_releases":
        raise RegistrySourceError(
            "{} source.type must be github_releases".format(path)
        )

    repository = require_string(
        source["repository"],
        "source.repository",
        201,
    )
    if REPOSITORY_PATTERN.fullmatch(repository) is None:
        raise RegistrySourceError(
            "{} source.repository must use Owner/Repository format".format(
                path
            )
        )

    tag_prefix = require_string(
        source["tag_prefix"],
        "source.tag_prefix",
        96,
        allow_empty=True,
    )
    if TAG_PREFIX_PATTERN.fullmatch(tag_prefix) is None:
        raise RegistrySourceError(
            "{} source.tag_prefix contains unsupported characters".format(
                path
            )
        )

    channels = source["channels"]
    if (
        not isinstance(channels, list)
        or not 1 <= len(channels) <= 2
    ):
        raise RegistrySourceError(
            "{} source.channels must contain one or two channels".format(
                path
            )
        )
    normalized_channels = []  # type: List[str]
    seen_channels = set()
    for channel in channels:
        if not isinstance(channel, str) or channel not in CHANNELS:
            raise RegistrySourceError(
                "{} contains an invalid release channel".format(path)
            )
        if channel in seen_channels:
            raise RegistrySourceError(
                "{} contains a duplicate release channel".format(path)
            )
        seen_channels.add(channel)
        normalized_channels.append(channel)

    return {
        "mod_id": mod_id,
        "display_name": display_name,
        "creator_name": creator_name,
        "mod_page": mod_page,
        "maintainers": normalized_maintainers,
        "repository": repository,
        "tag_prefix": tag_prefix,
        "channels": normalized_channels,
        "path": str(path),
    }


def load_entries(entries_directory: Path) -> List[Dict[str, Any]]:
    if not entries_directory.is_dir():
        raise RegistrySourceError(
            "Entries directory was not found: {}".format(entries_directory)
        )
    paths = sorted(entries_directory.glob("*.json"))
    if len(paths) > MAX_ENTRY_FILES:
        raise RegistrySourceError("Too many registry entry files")

    entries = []  # type: List[Dict[str, Any]]
    seen_mod_ids = set()
    for path in paths:
        if not path.is_file():
            continue
        entry = validate_entry(path, load_json(path))
        if entry["mod_id"] in seen_mod_ids:
            raise RegistrySourceError(
                "Duplicate mod_id: {}".format(entry["mod_id"])
            )
        seen_mod_ids.add(entry["mod_id"])
        entries.append(entry)
    return entries


def github_headers(token: str = "") -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Demeterio-MUC-Registry-Builder",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }
    if token:
        headers["Authorization"] = "Bearer {}".format(token)
    return headers


def read_json_response(request: urllib.request.Request) -> Tuple[Any, Dict[str, str]]:
    try:
        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:
            raw = response.read()
            headers = {
                key.lower(): value
                for key, value in response.headers.items()
            }
    except urllib.error.HTTPError:
        raise
    except (OSError, urllib.error.URLError) as exc:
        raise RegistrySourceError(
            "Unable to contact GitHub: {}".format(exc)
        ) from exc

    try:
        return json.loads(raw.decode("utf-8")), headers
    except (UnicodeDecodeError, TypeError, ValueError) as exc:
        raise RegistrySourceError(
            "GitHub returned invalid JSON"
        ) from exc


def request_github_json(url: str, token: str) -> Tuple[Any, Dict[str, str]]:
    attempts = [token] if token else [""]
    if token:
        attempts.append("")

    last_http_error = None  # type: Optional[urllib.error.HTTPError]
    for attempt_token in attempts:
        request = urllib.request.Request(
            url,
            headers=github_headers(attempt_token),
            method="GET",
        )
        try:
            return read_json_response(request)
        except urllib.error.HTTPError as exc:
            last_http_error = exc
            if attempt_token and exc.code in (401, 403, 404):
                continue
            detail = ""
            try:
                detail = exc.read().decode(
                    "utf-8",
                    errors="replace",
                ).strip()
            except Exception:
                pass
            raise RegistrySourceError(
                "GitHub API returned HTTP {} for {}{}".format(
                    exc.code,
                    url,
                    ": {}".format(detail[:300]) if detail else "",
                )
            ) from exc

    if last_http_error is not None:
        raise RegistrySourceError(
            "GitHub API returned HTTP {} for {}".format(
                last_http_error.code,
                url,
            )
        )
    raise RegistrySourceError(
        "Unable to contact GitHub for {}".format(url)
    )


def fetch_releases(repository: str, token: str) -> List[Dict[str, Any]]:
    owner, name = repository.split("/", 1)
    releases = []  # type: List[Dict[str, Any]]

    for page in range(1, MAX_RELEASE_PAGES + 1):
        encoded_owner = urllib.parse.quote(owner, safe="")
        encoded_name = urllib.parse.quote(name, safe="")
        url = (
            "https://api.github.com/repos/{}/{}/releases"
            "?per_page={}&page={}"
        ).format(
            encoded_owner,
            encoded_name,
            RELEASES_PER_PAGE,
            page,
        )
        data, _headers = request_github_json(url, token)
        if not isinstance(data, list):
            raise RegistrySourceError(
                "GitHub Releases response for {} is not an array".format(
                    repository
                )
            )

        for item in data:
            if isinstance(item, dict):
                releases.append(item)
        if len(data) < RELEASES_PER_PAGE:
            break
    else:
        raise RegistrySourceError(
            "{} has more than {} retrievable releases; narrow the tag "
            "strategy or increase the reviewed limit".format(
                repository,
                MAX_RELEASE_PAGES * RELEASES_PER_PAGE,
            )
        )

    return releases


def release_candidate(
    release: Dict[str, Any],
    tag_prefix: str,
    channel: str,
) -> Optional[Tuple[SemVer, str, str]]:
    if release.get("draft") is True:
        return None

    prerelease_flag = release.get("prerelease")
    if channel == "stable" and prerelease_flag is not False:
        return None
    if channel == "prerelease" and prerelease_flag is not True:
        return None

    tag_name = release.get("tag_name")
    if not isinstance(tag_name, str):
        return None
    if not tag_name.startswith(tag_prefix):
        return None
    if len(tag_name) > 128:
        raise RegistrySourceError(
            "Matching release tag is longer than 128 characters: {}".format(
                tag_name
            )
        )

    version_text = tag_name[len(tag_prefix):]
    try:
        version = SemVer.parse(version_text)
    except RegistrySourceError:
        return None

    if channel == "stable" and version.prerelease:
        return None

    published_at = release.get("published_at")
    if not isinstance(published_at, str):
        published_at = ""

    return version, tag_name, published_at


def choose_release(
    releases: Sequence[Dict[str, Any]],
    tag_prefix: str,
    channel: str,
) -> Optional[Tuple[SemVer, str, str]]:
    best = None  # type: Optional[Tuple[SemVer, str, str]]
    for release in releases:
        candidate = release_candidate(
            release,
            tag_prefix,
            channel,
        )
        if candidate is None:
            continue
        if best is None:
            best = candidate
            continue
        if candidate[0] > best[0]:
            best = candidate
            continue
        if candidate[0] == best[0] and candidate[2] > best[2]:
            best = candidate
    return best


def resolve_registry_entries(
    sources: Sequence[Dict[str, Any]],
    token: str,
) -> Tuple[List[Dict[str, str]], List[str]]:
    repository_cache = {}  # type: Dict[str, List[Dict[str, Any]]]
    generated = []  # type: List[Dict[str, str]]
    warnings = []  # type: List[str]
    checked_at = utc_now_text()

    for source in sources:
        repository = source["repository"]
        if repository not in repository_cache:
            repository_cache[repository] = fetch_releases(
                repository,
                token,
            )
        releases = repository_cache[repository]

        found_any = False
        for channel in source["channels"]:
            candidate = choose_release(
                releases,
                source["tag_prefix"],
                channel,
            )
            if candidate is None:
                if channel == "prerelease" and "stable" in source["channels"]:
                    warnings.append(
                        "{} has no matching prerelease; stable remains "
                        "available".format(source["mod_id"])
                    )
                    continue
                raise RegistrySourceError(
                    "{} has no matching published {} GitHub Release in {} "
                    "using tag prefix {!r}".format(
                        source["mod_id"],
                        channel,
                        repository,
                        source["tag_prefix"],
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

            if len(generated) > MAX_GENERATED_ENTRIES:
                raise RegistrySourceError(
                    "Generated registry contains more than "
                    "{} channel entries".format(
                        MAX_GENERATED_ENTRIES
                    )
                )

            found_any = True

        if not found_any:
            raise RegistrySourceError(
                "{} did not produce any registry entry".format(
                    source["mod_id"]
                )
            )

    generated.sort(
        key=lambda item: (
            item["mod_id"],
            item["release_channel"],
        )
    )
    return generated, warnings



def registry_identity(entries: Sequence[Dict[str, str]]) -> List[Tuple[str, str, str, str]]:
    return sorted(
        (
            item["mod_id"],
            item["release_channel"],
            item["version"],
            item["release_tag"],
        )
        for item in entries
    )


def previous_payload_if_unchanged(
    previous_signed: Optional[Path],
    new_entries: Sequence[Dict[str, str]],
) -> Optional[bytes]:
    if previous_signed is None or not previous_signed.is_file():
        return None
    try:
        envelope = load_json(previous_signed)
        payload_text = envelope.get("payload")
        if not isinstance(payload_text, str):
            return None
        payload = base64.b64decode(
            payload_text.encode("ascii"),
            validate=True,
        )
        previous = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
        if not isinstance(previous, dict):
            return None
        previous_entries = previous.get("entries")
        if not isinstance(previous_entries, list):
            return None
        if registry_identity(previous_entries) != registry_identity(new_entries):
            return None
        return payload
    except Exception:
        return None

def write_registry(
    output: Path,
    entries: Sequence[Dict[str, str]],
    previous_signed: Optional[Path] = None,
) -> bool:
    previous_payload = previous_payload_if_unchanged(
        previous_signed,
        entries,
    )
    if previous_payload is not None:
        encoded = previous_payload
        unchanged = True
    else:
        document = {
            "schema": REGISTRY_SCHEMA,
            "generated_at": utc_now_text(),
            "entries": list(entries),
        }
        encoded = (
            json.dumps(
                document,
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        ).encode("utf-8")
        unchanged = False
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(encoded)
    return unchanged


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate reviewed MUC entry files and resolve public GitHub "
            "Releases into one unsigned registry."
        )
    )
    parser.add_argument(
        "--entries",
        required=True,
        help="Directory containing one reviewed JSON file per mod.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Destination for the unsigned registry JSON.",
    )
    parser.add_argument(
        "--previous-signed",
        help=(
            "Optional current signed registry. Its exact payload is reused "
            "when versions and release tags have not changed."
        ),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    token = (
        os.environ.get("MUC_GITHUB_API_TOKEN", "").strip()
        or os.environ.get("GITHUB_TOKEN", "").strip()
    )
    try:
        sources = load_entries(Path(args.entries).resolve())
        entries, warnings = resolve_registry_entries(sources, token)
        unchanged = write_registry(
            Path(args.output).resolve(),
            entries,
            Path(args.previous_signed).resolve()
            if args.previous_signed
            else None,
        )
    except RegistrySourceError as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        return 1

    for warning in warnings:
        print("WARNING: {}".format(warning))
    print("Validated source files: {}".format(len(sources)))
    print("Generated registry entries: {}".format(len(entries)))
    print(
        "Registry payload changed: {}".format(
            "no" if unchanged else "yes"
        )
    )
    print("Unsigned registry written to: {}".format(args.output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
