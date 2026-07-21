import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_registry


MOD_ID = "creator.mod_name.0123456789ABCDEF"


def valid_entry_data():
    return {
        "$schema": "../schemas/mod-entry.schema.json",
        "schema": 1,
        "mod_id": MOD_ID,
        "display_name": "Example",
        "creator_name": "Creator",
        "mod_page": "https://example.com/mod-name",
        "maintainers": ["Creator"],
        "source": {
            "type": "github_releases",
            "repository": "Creator/Example",
            "tag_prefix": "v",
            "channels": ["stable"],
        },
    }


class BuildRegistryTests(unittest.TestCase):
    def test_selects_highest_stable_and_prerelease(self):
        releases = [
            {
                "draft": False,
                "prerelease": False,
                "tag_name": "v1.0.0",
                "published_at": "2026-01-01T00:00:00Z",
            },
            {
                "draft": False,
                "prerelease": False,
                "tag_name": "v1.2.0",
                "published_at": "2026-02-01T00:00:00Z",
            },
            {
                "draft": False,
                "prerelease": True,
                "tag_name": "v1.3.0-beta.1",
                "published_at": "2026-03-01T00:00:00Z",
            },
        ]
        stable = build_registry.choose_release(releases, "v", "stable")
        prerelease = build_registry.choose_release(
            releases,
            "v",
            "prerelease",
        )
        self.assertEqual(stable[0].text, "1.2.0")
        self.assertEqual(prerelease[0].text, "1.3.0-beta.1")

    def test_entry_filename_must_match_mod_id(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wrong.json"
            path.write_text(
                json.dumps(valid_entry_data()),
                encoding="utf-8",
            )

            with self.assertRaises(build_registry.RegistrySourceError):
                build_registry.validate_entry(
                    path,
                    build_registry.load_json(path),
                )

    def test_mod_page_is_required(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "{}.json".format(MOD_ID)
            data = valid_entry_data()
            del data["mod_page"]
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaises(build_registry.RegistrySourceError):
                build_registry.validate_entry(
                    path,
                    build_registry.load_json(path),
                )

    def test_mod_page_requires_https(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "{}.json".format(MOD_ID)
            data = valid_entry_data()
            data["mod_page"] = "http://example.com/mod-name"
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(
                build_registry.RegistrySourceError,
                "must use HTTPS",
            ):
                build_registry.validate_entry(
                    path,
                    build_registry.load_json(path),
                )

    def test_mod_page_rejects_embedded_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "{}.json".format(MOD_ID)
            data = valid_entry_data()
            data["mod_page"] = (
                "https://user:password@example.com/mod-name"
            )
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(
                build_registry.RegistrySourceError,
                "must not contain embedded credentials",
            ):
                build_registry.validate_entry(
                    path,
                    build_registry.load_json(path),
                )

    def test_valid_mod_page_is_preserved_for_review(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "{}.json".format(MOD_ID)
            path.write_text(
                json.dumps(valid_entry_data()),
                encoding="utf-8",
            )

            validated = build_registry.validate_entry(
                path,
                build_registry.load_json(path),
            )

            self.assertEqual(
                validated["mod_page"],
                "https://example.com/mod-name",
            )

    @patch("build_registry.fetch_releases")
    def test_builds_registry_entries_without_mod_page(
        self,
        fetch_releases,
    ):
        fetch_releases.return_value = [
            {
                "draft": False,
                "prerelease": False,
                "tag_name": "v2.0.0",
                "published_at": "2026-04-01T00:00:00Z",
            }
        ]
        sources = [
            {
                "mod_id": MOD_ID,
                "display_name": "Example",
                "creator_name": "Creator",
                "mod_page": "https://example.com/mod-name",
                "maintainers": ["Creator"],
                "repository": "Creator/Example",
                "tag_prefix": "v",
                "channels": ["stable"],
            }
        ]

        entries, warnings = build_registry.resolve_registry_entries(
            sources,
            "",
        )

        self.assertEqual(warnings, [])
        self.assertEqual(entries[0]["version"], "2.0.0")
        self.assertEqual(entries[0]["release_tag"], "v2.0.0")
        self.assertNotIn("mod_page", entries[0])
        self.assertEqual(
            frozenset(entries[0].keys()),
            frozenset(
                (
                    "mod_id",
                    "release_channel",
                    "version",
                    "release_tag",
                    "checked_at",
                )
            ),
        )


if __name__ == "__main__":
    unittest.main()
