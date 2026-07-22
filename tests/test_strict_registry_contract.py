import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_module("muc_build_registry", ROOT / "tools" / "build_registry.py")
signer = load_module("muc_build_and_sign", ROOT / "tools" / "build_and_sign_registry.py")


class StrictRegistryContractTests(unittest.TestCase):
    def valid_entry(self):
        return {
            "$schema": "../schemas/mod-entry.schema.json",
            "schema": 1,
            "mod_id": "demeterio.example_mod.0123456789ABCDEF",
            "display_name": "Example Mod",
            "creator_name": "Demeterio",
            "mod_page": "https://example.com/mod",
            "maintainers": ["demeterio"],
            "source": {
                "type": "github_releases",
                "repository": "Demeterio/Example-Mod",
                "tag_prefix": "v",
                "channels": ["stable", "prerelease"],
            },
        }

    def validate_entry(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "demeterio.example_mod.0123456789ABCDEF.json"
            return builder.validate_entry(path, data)

    def test_valid_entry_is_accepted(self):
        self.assertEqual(self.validate_entry(self.valid_entry())["tag_prefix"], "v")

    def test_whitespace_is_rejected_not_trimmed(self):
        entry = self.valid_entry()
        entry["display_name"] = " Example Mod"
        with self.assertRaises(builder.RegistrySourceError):
            self.validate_entry(entry)

    def test_maintainers_must_be_lowercase(self):
        entry = self.valid_entry()
        entry["maintainers"] = ["Demeterio"]
        with self.assertRaises(builder.RegistrySourceError):
            self.validate_entry(entry)

    def test_tag_prefix_must_start_alphanumeric(self):
        entry = self.valid_entry()
        entry["source"]["tag_prefix"] = "/release-"
        with self.assertRaises(builder.RegistrySourceError):
            self.validate_entry(entry)

    def test_signer_requires_exact_channel_and_semver(self):
        now = builder.utc_now_text()
        base = {
            "schema": 1,
            "generated_at": now,
            "entries": [{
                "mod_id": "demeterio.example_mod.0123456789ABCDEF",
                "release_channel": "stable",
                "version": "1.0.0",
                "release_tag": "v1.0.0",
                "checked_at": now,
            }],
        }
        self.assertTrue(signer.canonical_payload(base))
        for field, value in (
            ("release_channel", "Stable"),
            ("version", "v1.0.0"),
            ("version", "1.0.0 "),
        ):
            invalid = json.loads(json.dumps(base))
            invalid["entries"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(
                signer.RegistryBuildError
            ):
                signer.canonical_payload(invalid)

    def test_builder_always_issues_fresh_payload_structure(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "registry.json"
            builder.write_registry(output, [])
            data = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], 1)
        self.assertEqual(data["entries"], [])
        self.assertIn("generated_at", data)


if __name__ == "__main__":
    unittest.main()
