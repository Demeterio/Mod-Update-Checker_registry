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
            data = {
                "$schema": "../schemas/mod-entry.schema.json",
                "schema": 1,
                "mod_id": "creator.mod_name.0123456789ABCDEF",
                "display_name": "Example",
                "creator_name": "Creator",
                "maintainers": ["Creator"],
                "source": {
                    "type": "github_releases",
                    "repository": "Creator/Example",
                    "tag_prefix": "v",
                    "channels": ["stable"],
                },
            }
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(build_registry.RegistrySourceError):
                build_registry.validate_entry(
                    path,
                    build_registry.load_json(path),
                )

    @patch("build_registry.fetch_releases")
    def test_builds_registry_entries(self, fetch_releases):
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
                "mod_id": "creator.mod_name.0123456789ABCDEF",
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


    def test_builds_human_readable_registry(self):
        sources = [
            {
                "mod_id": MOD_ID,
                "display_name": "Example Mod",
                "creator_name": "Creator",
                "mod_page": "https://example.com/mod-name",
                "maintainers": ["Creator"],
                "repository": "Creator/Example",
                "tag_prefix": "v",
                "channels": ["stable", "prerelease"],
            }
        ]
        entries = [
            {
                "mod_id": MOD_ID,
                "release_channel": "stable",
                "version": "2.0.0",
                "release_tag": "v2.0.0",
                "checked_at": "2026-07-21T20:00:00Z",
            },
            {
                "mod_id": MOD_ID,
                "release_channel": "prerelease",
                "version": "2.1.0-beta.1",
                "release_tag": "v2.1.0-beta.1",
                "checked_at": "2026-07-21T20:00:00Z",
            },
        ]

        readable = build_registry.build_readable_registry(
            sources,
            entries,
        )

        self.assertEqual(readable["schema"], 1)
        self.assertEqual(
            readable["generated_at"],
            "2026-07-21T20:00:00Z",
        )
        self.assertEqual(len(readable["mods"]), 1)

        mod = readable["mods"][0]
        self.assertEqual(mod["display_name"], "Example Mod")
        self.assertEqual(
            mod["mod_page"],
            "https://example.com/mod-name",
        )
        self.assertEqual(
            mod["repository_url"],
            "https://github.com/Creator/Example",
        )
        self.assertEqual(mod["stable"]["version"], "2.0.0")
        self.assertEqual(
            mod["prerelease"]["version"],
            "2.1.0-beta.1",
        )
        self.assertEqual(
            mod["stable"]["release_url"],
            "https://github.com/Creator/Example/releases/tag/v2.0.0",
        )

    def test_writes_human_readable_registry(self):
        sources = [
            {
                "mod_id": MOD_ID,
                "display_name": "Example Mod",
                "creator_name": "Creator",
                "mod_page": "https://example.com/mod-name",
                "maintainers": ["Creator"],
                "repository": "Creator/Example",
                "tag_prefix": "v",
                "channels": ["stable"],
            }
        ]
        entries = [
            {
                "mod_id": MOD_ID,
                "release_channel": "stable",
                "version": "2.0.0",
                "release_tag": "v2.0.0",
                "checked_at": "2026-07-21T20:00:00Z",
            }
        ]

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "readable.json"
            build_registry.write_readable_registry(
                output,
                sources,
                entries,
            )
            data = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(data["mods"][0]["mod_id"], MOD_ID)
        self.assertEqual(data["mods"][0]["stable"]["version"], "2.0.0")
        self.assertNotIn("signature", data)


if __name__ == "__main__":
    unittest.main()
