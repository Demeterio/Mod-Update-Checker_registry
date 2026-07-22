#!/usr/bin/env python3
"""Strictly validate, canonicalize, sign, and verify the MUC registry."""

import argparse
import base64
import hashlib
import hmac
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

MOD_ID_PATTERN = re.compile(r"^[a-z0-9_-]+\.[a-z0-9_-]+\.[0-9A-F]{16}$")
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
RELEASE_TAG_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/+\-]{0,127}$")
RELEASE_CHANNELS = frozenset(("stable", "prerelease"))
ROOT_FIELDS = frozenset(("schema", "generated_at", "entries"))
ENTRY_FIELDS = frozenset(("mod_id", "release_channel", "version", "release_tag", "checked_at"))
ENVELOPE_FIELDS = frozenset(("signature_schema", "key_id", "algorithm", "payload", "signature"))


class RegistryBuildError(Exception):
    """Raised when validation or signing cannot complete safely."""


def reject_duplicate_keys(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise RegistryBuildError("JSON contains duplicate key: {}".format(key))
        result[key] = value
    return result


def require_string(value, field_name, maximum):
    if not isinstance(value, str):
        raise RegistryBuildError("{} must be a string".format(field_name))
    if value != value.strip():
        raise RegistryBuildError(
            "{} must not contain leading or trailing whitespace".format(field_name)
        )
    if not value:
        raise RegistryBuildError("{} must not be empty".format(field_name))
    if len(value) > maximum:
        raise RegistryBuildError("{} is too long".format(field_name))
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise RegistryBuildError("{} must not contain control characters".format(field_name))
    return value


def validate_timestamp(value, field_name):
    text = require_string(value, field_name, 64)
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    except (TypeError, ValueError) as exc:
        raise RegistryBuildError("{} must be an ISO timestamp".format(field_name)) from exc
    if parsed.tzinfo is None:
        raise RegistryBuildError("{} must include a timezone".format(field_name))
    return parsed.astimezone(timezone.utc).isoformat()


def validate_semver(value):
    version = require_string(value, "version", 128)
    match = SEMVER_PATTERN.fullmatch(version)
    if match is None:
        raise RegistryBuildError("version must follow MAJOR.MINOR.PATCH SemVer syntax")
    prerelease = match.group(4)
    if prerelease:
        for identifier in prerelease.split("."):
            if identifier.isdigit() and len(identifier) > 1 and identifier.startswith("0"):
                raise RegistryBuildError(
                    "numeric prerelease identifiers must not contain leading zeroes"
                )
    return version


def load_json_file(source: Path, maximum: int, label: str):
    try:
        raw = source.read_bytes()
    except OSError as exc:
        raise RegistryBuildError("Unable to read {}: {}".format(label, source)) from exc
    if not raw:
        raise RegistryBuildError("{} must not be empty".format(label))
    if len(raw) > maximum:
        raise RegistryBuildError("{} exceeds the allowed size".format(label))
    if raw.startswith(b"\xef\xbb\xbf"):
        raise RegistryBuildError("{} must not contain a UTF-8 BOM".format(label))
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicate_keys)
    except RegistryBuildError:
        raise
    except (UnicodeDecodeError, TypeError, ValueError) as exc:
        raise RegistryBuildError("{} is not valid UTF-8 JSON".format(label)) from exc
    if not isinstance(data, dict):
        raise RegistryBuildError("{} root must be an object".format(label))
    return data


def load_registry(source: Path):
    return load_json_file(source, MAX_PAYLOAD_BYTES, "Registry source")


def validate_registry(data):
    if frozenset(data.keys()) != ROOT_FIELDS:
        raise RegistryBuildError("Registry root fields are invalid")
    if isinstance(data["schema"], bool) or data["schema"] != REGISTRY_SCHEMA:
        raise RegistryBuildError("schema must be integer 1")
    generated_at = validate_timestamp(data["generated_at"], "generated_at")
    entries = data["entries"]
    if not isinstance(entries, list):
        raise RegistryBuildError("entries must be an array")
    if len(entries) > MAX_ENTRIES:
        raise RegistryBuildError("Registry contains too many entries")

    validated = []
    seen = set()
    for index, raw_entry in enumerate(entries):
        label = "entry {}".format(index)
        if not isinstance(raw_entry, dict) or frozenset(raw_entry.keys()) != ENTRY_FIELDS:
            raise RegistryBuildError("{} fields are invalid".format(label))
        mod_id = require_string(raw_entry["mod_id"], "mod_id", 128)
        if MOD_ID_PATTERN.fullmatch(mod_id) is None:
            raise RegistryBuildError("{} mod_id is invalid".format(label))
        channel = require_string(raw_entry["release_channel"], "release_channel", 32)
        if channel not in RELEASE_CHANNELS:
            raise RegistryBuildError(
                "{} release_channel must be exactly stable or prerelease".format(label)
            )
        version = validate_semver(raw_entry["version"])
        release_tag = require_string(raw_entry["release_tag"], "release_tag", 128)
        if RELEASE_TAG_PATTERN.fullmatch(release_tag) is None:
            raise RegistryBuildError("{} release_tag contains unsupported characters".format(label))
        checked_at = validate_timestamp(raw_entry["checked_at"], "checked_at")
        key = (mod_id, channel)
        if key in seen:
            raise RegistryBuildError("Duplicate mod/channel entry: {} {}".format(mod_id, channel))
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
    return generated_at, validated


def canonical_payload(data):
    generated_at, entries = validate_registry(data)
    normalized = {
        "schema": REGISTRY_SCHEMA,
        "generated_at": generated_at.replace("+00:00", "Z"),
        "entries": entries,
    }
    payload = json.dumps(normalized, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(payload) > MAX_PAYLOAD_BYTES:
        raise RegistryBuildError("Canonical registry exceeds the allowed size")
    return payload


def run_openssl(arguments: List[str]):
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
        raise RegistryBuildError("OpenSSL failed: {}".format(detail or "unknown error")) from exc


def public_key_fingerprint(public_key: Path):
    return hashlib.sha256(
        run_openssl(["pkey", "-pubin", "-in", str(public_key), "-outform", "DER"]).stdout
    ).hexdigest()


def derived_public_key_fingerprint(private_key: Path):
    return hashlib.sha256(
        run_openssl(["pkey", "-in", str(private_key), "-pubout", "-outform", "DER"]).stdout
    ).hexdigest()


def expected_fingerprint(path: Path):
    try:
        value = path.read_text(encoding="ascii").strip().lower()
    except OSError as exc:
        raise RegistryBuildError("Unable to read public-key fingerprint: {}".format(path)) from exc
    if re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise RegistryBuildError("Public-key fingerprint file is invalid")
    return value


def write_atomic(path: Path, content: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(str(temporary), str(path))
        os.chmod(str(path), 0o644)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def sign_registry(args):
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
    if public_key_fingerprint(public_key) != expected:
        raise RegistryBuildError("Committed public key does not match its fingerprint file")
    if derived_public_key_fingerprint(private_key) != expected:
        raise RegistryBuildError("Private signing key does not match the trusted public key")

    payload = canonical_payload(load_registry(source))
    with tempfile.TemporaryDirectory(prefix="muc-registry-sign-") as directory:
        temporary = Path(directory)
        payload_path = temporary / "payload.json"
        signature_path = temporary / "signature.bin"
        payload_path.write_bytes(payload)
        run_openssl([
            "dgst", "-sha256", "-sign", str(private_key),
            "-out", str(signature_path), str(payload_path),
        ])
        signature = signature_path.read_bytes()
        run_openssl([
            "dgst", "-sha256", "-verify", str(public_key),
            "-signature", str(signature_path), str(payload_path),
        ])

    key_id = require_string(args.key_id, "key_id", 128)
    envelope = {
        "signature_schema": SIGNATURE_SCHEMA,
        "key_id": key_id,
        "algorithm": SIGNATURE_ALGORITHM,
        "payload": base64.b64encode(payload).decode("ascii"),
        "signature": base64.b64encode(signature).decode("ascii"),
    }
    signed = (json.dumps(envelope, ensure_ascii=True, indent=2) + "\n").encode("utf-8")
    if len(signed) > MAX_SIGNED_BYTES:
        raise RegistryBuildError("Signed registry exceeds the allowed size")
    write_atomic(output, signed)
    print("Validated {} registry entries.".format(len(json.loads(payload.decode("utf-8"))["entries"])))
    print("Signed registry written to: {}".format(output))
    print("Public-key fingerprint: {}".format(expected))


def validate_only(args):
    payload = canonical_payload(load_registry(Path(args.source).resolve()))
    print("Registry source is valid.")
    print("Entries: {}".format(len(json.loads(payload.decode("utf-8"))["entries"])))
    print("Canonical payload bytes: {}".format(len(payload)))


def decode_canonical_base64(value, field_name, maximum):
    text = require_string(value, field_name, maximum)
    try:
        decoded = base64.b64decode(text.encode("ascii"), validate=True)
    except (UnicodeEncodeError, ValueError, TypeError) as exc:
        raise RegistryBuildError("{} is not canonical Base64".format(field_name)) from exc
    if not hmac.compare_digest(base64.b64encode(decoded).decode("ascii"), text):
        raise RegistryBuildError("{} is not canonical Base64".format(field_name))
    return decoded


def verify_signed(args):
    signed_path = Path(args.source).resolve()
    public_key = Path(args.public_key).resolve()
    fingerprint_file = Path(args.fingerprint).resolve()
    expected = expected_fingerprint(fingerprint_file)
    if public_key_fingerprint(public_key) != expected:
        raise RegistryBuildError("Committed public key does not match its fingerprint file")

    envelope = load_json_file(signed_path, MAX_SIGNED_BYTES, "Signed registry")
    if frozenset(envelope.keys()) != ENVELOPE_FIELDS:
        raise RegistryBuildError("Signed registry envelope fields are invalid")
    if isinstance(envelope["signature_schema"], bool) or envelope["signature_schema"] != SIGNATURE_SCHEMA:
        raise RegistryBuildError("signature_schema is unsupported")
    if require_string(envelope["algorithm"], "algorithm", 16) != SIGNATURE_ALGORITHM:
        raise RegistryBuildError("signature algorithm is unsupported")

    expected_key_id = require_string(args.key_id, "expected key_id", 128)
    actual_key_id = require_string(envelope["key_id"], "key_id", 128)
    if not hmac.compare_digest(actual_key_id, expected_key_id):
        raise RegistryBuildError("Signed registry key_id is not trusted")

    payload = decode_canonical_base64(envelope["payload"], "payload", MAX_SIGNED_BYTES)
    signature = decode_canonical_base64(envelope["signature"], "signature", MAX_SIGNED_BYTES)
    if len(payload) > MAX_PAYLOAD_BYTES:
        raise RegistryBuildError("Signed payload exceeds the allowed size")

    try:
        payload_data = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
    except RegistryBuildError:
        raise
    except (UnicodeDecodeError, TypeError, ValueError) as exc:
        raise RegistryBuildError("Signed payload is not valid registry JSON") from exc

    canonical = canonical_payload(payload_data)
    if not hmac.compare_digest(payload, canonical):
        raise RegistryBuildError("Signed payload is valid JSON but is not canonical")

    with tempfile.TemporaryDirectory(prefix="muc-registry-verify-") as directory:
        temporary = Path(directory)
        payload_path = temporary / "payload.json"
        signature_path = temporary / "signature.bin"
        payload_path.write_bytes(payload)
        signature_path.write_bytes(signature)
        run_openssl([
            "dgst", "-sha256", "-verify", str(public_key),
            "-signature", str(signature_path), str(payload_path),
        ])

    print("Signed registry signature is valid.")
    print("Trusted key ID: {}".format(actual_key_id))
    print("Public-key fingerprint: {}".format(expected))


def build_parser():
    parser = argparse.ArgumentParser(description="Validate, sign, and verify the MUC central registry.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--source", required=True)
    validate_parser.set_defaults(handler=validate_only)

    sign_parser = subparsers.add_parser("sign")
    sign_parser.add_argument("--source", required=True)
    sign_parser.add_argument("--private-key", required=True)
    sign_parser.add_argument("--public-key", required=True)
    sign_parser.add_argument("--fingerprint", required=True)
    sign_parser.add_argument("--output", required=True)
    sign_parser.add_argument("--key-id", default="muc-registry-2026-01")
    sign_parser.set_defaults(handler=sign_registry)

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--source", required=True)
    verify_parser.add_argument("--public-key", required=True)
    verify_parser.add_argument("--fingerprint", required=True)
    verify_parser.add_argument("--key-id", default="muc-registry-2026-01")
    verify_parser.set_defaults(handler=verify_signed)
    return parser


def main():
    args = build_parser().parse_args()
    try:
        args.handler(args)
    except RegistryBuildError as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
