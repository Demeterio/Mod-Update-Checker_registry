#!/usr/bin/env python3
"""Validate, canonicalize, sign, and verify the MUC central registry."""

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

REGISTRY_SCHEMA = 1
SIGNATURE_SCHEMA = 1
SIGNATURE_ALGORITHM = "RS256"
MAX_PAYLOAD_BYTES = 2 * 1024 * 1024
MAX_SIGNED_BYTES = 3 * 1024 * 1024
MAX_ENTRIES = 10000

MOD_ID_PATTERN = re.compile(
    r"^[a-z0-9_-]+\.[a-z0-9_-]+\.[0-9A-F]{16}$"
)
SEMVER_PATTERN = re.compile(
    r"^v?(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
RELEASE_TAG_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._/+\-]{0,127}$"
)
RELEASE_CHANNELS = frozenset(("stable", "prerelease"))
ROOT_FIELDS = frozenset(("schema", "generated_at", "entries"))
ENTRY_FIELDS = frozenset(
    ("mod_id", "release_channel", "version", "release_tag", "checked_at")
)


class RegistryBuildError(Exception):
    """Raised when validation or signing cannot complete safely."""


def reject_duplicate_keys(
    pairs: List[Tuple[str, Any]],
) -> Dict[str, Any]:
    result = {}  # type: Dict[str, Any]
    for key, value in pairs:
        if key in result:
            raise RegistryBuildError(
                "JSON contains duplicate key: {}".format(key)
            )
        result[key] = value
    return result


def require_string(value: object, field_name: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise RegistryBuildError("{} must be a string".format(field_name))
    normalized = value.strip()
    if not normalized:
        raise RegistryBuildError("{} must not be empty".format(field_name))
    if len(normalized) > maximum:
        raise RegistryBuildError("{} is too long".format(field_name))
    return normalized


def validate_timestamp(value: object, field_name: str) -> str:
    text = require_string(value, field_name, 64)
    try:
        parsed = datetime.fromisoformat(
            text[:-1] + "+00:00" if text.endswith("Z") else text
        )
    except (TypeError, ValueError) as exc:
        raise RegistryBuildError(
            "{} must be an ISO timestamp".format(field_name)
        ) from exc
    if parsed.tzinfo is None:
        raise RegistryBuildError(
            "{} must include a timezone".format(field_name)
        )
    return parsed.astimezone(timezone.utc).isoformat()


def validate_semver(value: object) -> str:
    version = require_string(value, "version", 128)
    match = SEMVER_PATTERN.fullmatch(version)
    if match is None:
        raise RegistryBuildError(
            "version must follow MAJOR.MINOR.PATCH SemVer syntax"
        )
    prerelease = match.group(4)
    if prerelease:
        for identifier in prerelease.split("."):
            if (
                identifier.isdigit()
                and len(identifier) > 1
                and identifier.startswith("0")
            ):
                raise RegistryBuildError(
                    "numeric prerelease identifiers must not contain leading zeroes"
                )
    return version


def load_registry(source: Path) -> Dict[str, Any]:
    try:
        raw = source.read_bytes()
    except OSError as exc:
        raise RegistryBuildError(
            "Unable to read registry source: {}".format(source)
        ) from exc
    if not raw:
        raise RegistryBuildError("Registry source must not be empty")
    if len(raw) > MAX_PAYLOAD_BYTES:
        raise RegistryBuildError("Registry source exceeds the allowed size")
    if raw.startswith(b"\xef\xbb\xbf"):
        raise RegistryBuildError("Registry source must not contain a UTF-8 BOM")
    try:
        data = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
    except RegistryBuildError:
        raise
    except (UnicodeDecodeError, TypeError, ValueError) as exc:
        raise RegistryBuildError(
            "Registry source is not valid UTF-8 JSON"
        ) from exc
    if not isinstance(data, dict):
        raise RegistryBuildError("Registry root must be an object")
    return data


def validate_registry(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    if frozenset(data.keys()) != ROOT_FIELDS:
        raise RegistryBuildError("Registry root fields are invalid")
    schema = data["schema"]
    if isinstance(schema, bool) or schema != REGISTRY_SCHEMA:
        raise RegistryBuildError("schema must be integer 1")
    validate_timestamp(data["generated_at"], "generated_at")

    entries = data["entries"]
    if not isinstance(entries, list):
        raise RegistryBuildError("entries must be an array")
    if len(entries) > MAX_ENTRIES:
        raise RegistryBuildError("Registry contains too many entries")

    validated = []  # type: List[Dict[str, Any]]
    seen = set()
    for index, raw_entry in enumerate(entries):
        label = "entry {}".format(index)
        if not isinstance(raw_entry, dict):
            raise RegistryBuildError("{} must be an object".format(label))
        if frozenset(raw_entry.keys()) != ENTRY_FIELDS:
            raise RegistryBuildError("{} fields are invalid".format(label))

        mod_id = require_string(raw_entry["mod_id"], "mod_id", 128)
        if MOD_ID_PATTERN.fullmatch(mod_id) is None:
            raise RegistryBuildError(
                "{} mod_id is invalid".format(label)
            )

        channel = require_string(
            raw_entry["release_channel"],
            "release_channel",
            32,
        ).lower()
        if channel not in RELEASE_CHANNELS:
            raise RegistryBuildError(
                "{} release_channel must be stable or prerelease".format(label)
            )

        version = validate_semver(raw_entry["version"])
        release_tag = require_string(
            raw_entry["release_tag"],
            "release_tag",
            128,
        )
        if RELEASE_TAG_PATTERN.fullmatch(release_tag) is None:
            raise RegistryBuildError(
                "{} release_tag contains unsupported characters".format(label)
            )
        checked_at = validate_timestamp(
            raw_entry["checked_at"],
            "checked_at",
        )

        key = (mod_id, channel)
        if key in seen:
            raise RegistryBuildError(
                "Duplicate mod/channel entry: {} {}".format(mod_id, channel)
            )
        seen.add(key)
        validated.append(
            {
                "mod_id": mod_id,
                "release_channel": channel,
                "version": version,
                "release_tag": release_tag,
                "checked_at": checked_at.replace("+00:00", "Z"),
            }
        )

    validated.sort(key=lambda entry: (entry["mod_id"], entry["release_channel"]))
    return validated


def canonical_payload(data: Dict[str, Any], refresh_timestamp: bool) -> bytes:
    entries = validate_registry(data)
    generated_at = (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
        if refresh_timestamp
        else validate_timestamp(data["generated_at"], "generated_at").replace(
            "+00:00", "Z"
        )
    )
    normalized = {
        "schema": REGISTRY_SCHEMA,
        "generated_at": generated_at,
        "entries": entries,
    }
    payload = json.dumps(
        normalized,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    if len(payload) > MAX_PAYLOAD_BYTES:
        raise RegistryBuildError("Canonical registry exceeds the allowed size")
    return payload


def run_openssl(arguments: List[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["openssl"] + arguments,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise RegistryBuildError("OpenSSL was not found") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.decode("utf-8", errors="replace").strip()
        raise RegistryBuildError(
            "OpenSSL failed: {}".format(detail or "unknown error")
        ) from exc


def public_key_fingerprint(public_key: Path) -> str:
    result = run_openssl(
        ["pkey", "-pubin", "-in", str(public_key), "-outform", "DER"]
    )
    return hashlib.sha256(result.stdout).hexdigest()


def derived_public_key_fingerprint(private_key: Path) -> str:
    result = run_openssl(
        ["pkey", "-in", str(private_key), "-pubout", "-outform", "DER"]
    )
    return hashlib.sha256(result.stdout).hexdigest()


def expected_fingerprint(path: Path) -> str:
    try:
        value = path.read_text(encoding="ascii").strip().lower()
    except OSError as exc:
        raise RegistryBuildError(
            "Unable to read public-key fingerprint: {}".format(path)
        ) from exc
    if re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise RegistryBuildError("Public-key fingerprint file is invalid")
    return value


def write_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".tmp",
        dir=str(path.parent),
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(str(temporary), str(path))

        # The generated registry is a public GitHub Pages file.
        # tempfile.mkstemp() creates files with private permissions (0600),
        # so explicitly make the final file readable by the Pages build.
        os.chmod(str(path), 0o644)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def sign_registry(args: argparse.Namespace) -> None:
    source = Path(args.source).resolve()
    private_key = Path(args.private_key).resolve()
    public_key = Path(args.public_key).resolve()
    fingerprint_file = Path(args.fingerprint).resolve()
    output = Path(args.output).resolve()

    if not private_key.is_file():
        raise RegistryBuildError("Private key was not found")
    if not public_key.is_file():
        raise RegistryBuildError("Public key was not found")

    expected = expected_fingerprint(fingerprint_file)
    committed = public_key_fingerprint(public_key)
    derived = derived_public_key_fingerprint(private_key)
    if committed != expected:
        raise RegistryBuildError(
            "Committed public key does not match its fingerprint file"
        )
    if derived != expected:
        raise RegistryBuildError(
            "Private signing key does not match the trusted public key"
        )

    data = load_registry(source)
    # build_registry.py assigns a new generated_at value only when
    # the resolved versions or release tags have changed.
    payload = canonical_payload(data, refresh_timestamp=False)

    with tempfile.TemporaryDirectory(prefix="muc-registry-sign-") as directory:
        temporary = Path(directory)
        payload_path = temporary / "payload.json"
        signature_path = temporary / "signature.bin"
        payload_path.write_bytes(payload)

        run_openssl(
            [
                "dgst",
                "-sha256",
                "-sign",
                str(private_key),
                "-out",
                str(signature_path),
                str(payload_path),
            ]
        )
        signature = signature_path.read_bytes()

        run_openssl(
            [
                "dgst",
                "-sha256",
                "-verify",
                str(public_key),
                "-signature",
                str(signature_path),
                str(payload_path),
            ]
        )

    envelope = {
        "signature_schema": SIGNATURE_SCHEMA,
        "key_id": args.key_id,
        "algorithm": SIGNATURE_ALGORITHM,
        "payload": base64.b64encode(payload).decode("ascii"),
        "signature": base64.b64encode(signature).decode("ascii"),
    }
    signed = (
        json.dumps(envelope, ensure_ascii=True, indent=2) + "\n"
    ).encode("utf-8")
    if len(signed) > MAX_SIGNED_BYTES:
        raise RegistryBuildError("Signed registry exceeds the allowed size")
    write_atomic(output, signed)

    print("Validated {} registry entries.".format(len(data["entries"])))
    print("Signed registry written to: {}".format(output))
    print("Public-key fingerprint: {}".format(expected))


def validate_only(args: argparse.Namespace) -> None:
    source = Path(args.source).resolve()
    data = load_registry(source)
    payload = canonical_payload(data, refresh_timestamp=False)
    print("Registry source is valid.")
    print("Entries: {}".format(len(data["entries"])))
    print("Canonical payload bytes: {}".format(len(payload)))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and sign the MUC central registry."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate the unsigned registry source without a private key.",
    )
    validate_parser.add_argument("--source", required=True)
    validate_parser.set_defaults(handler=validate_only)

    sign_parser = subparsers.add_parser(
        "sign",
        help="Validate, sign, verify, and write the signed registry envelope.",
    )
    sign_parser.add_argument("--source", required=True)
    sign_parser.add_argument("--private-key", required=True)
    sign_parser.add_argument("--public-key", required=True)
    sign_parser.add_argument("--fingerprint", required=True)
    sign_parser.add_argument("--output", required=True)
    sign_parser.add_argument(
        "--key-id",
        default="muc-registry-2026-01",
    )
    sign_parser.set_defaults(handler=sign_registry)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.handler(args)
    except RegistryBuildError as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
