# Contributing to the Mod Update Checker (MUC) Registry

Thank you for helping maintain the public Mod Update Checker registry.

The registry contains public version metadata only. It does not host mod files, install updates, collect player information, or inspect a player's Mods folder.

## Before submitting

Your mod must already include a valid Mod Update Checker declaration package.

The declaration package is an optional MUC integration and requires the Mod Update Checker script mod to be installed. Without MUC, the custom tuning class is unavailable and the declaration may generate tuning-loading errors.

A valid declaration may be installed before its central registry entry is accepted. In that case, MUC reports the entry as missing and skips the version comparison without affecting normal gameplay.

You will need:

- the exact `mod_id` declared in the package;
- the public GitHub repository containing the mod's published Releases;
- a public official page describing the mod, such as the creator's website, a public platform listing, or the public GitHub repository presentation page;
- at least one published, non-draft GitHub Release matching the intended tag prefix and release channel;
- release tags that contain a valid semantic version;
- authorization from the creator or maintainer to submit or maintain the registry entry.

Git tags without a published GitHub Release are not sufficient.

## File location

Each mod uses one JSON source file in the `entries/` directory.

The filename must be the exact Mod Update Checker ID followed by `.json`.

Example:

```text
entries/moddername.modname.F693BA10FC031D74.json
```

Do not place multiple mods in one file.

## Create an entry

1. Fork this repository.
2. Create a branch in your fork.
3. Copy `templates/mod-entry.template.json`.
4. Save the copy under `entries/<mod_id>.json`.
5. Replace every placeholder.
6. Commit only the source entry and any directly related documentation.
7. Open a Pull Request against `main`.

Do not edit these generated or security-sensitive files:

```text
generated/registry-v1.json
security/muc-registry-public-key.pem
security/muc-registry-public-key.sha256
```

The generated registry is rebuilt and signed automatically after an accepted change reaches `main`.

## Entry format

```json
{
  "$schema": "../schemas/mod-entry.schema.json",
  "schema": 1,
  "mod_id": "moddername.modname.F693BA10FC031D74",
  "display_name": "Mod Name",
  "creator_name": "Modder Name",
  "mod_page": "https://example.com/mod-name",
  "maintainers": [
    "ExampleGitHubUser"
  ],
  "source": {
    "type": "github_releases",
    "repository": "ExampleGitHubUser/ModName",
    "tag_prefix": "v",
    "channels": [
      "stable",
      "prerelease"
    ]
  }
}
```

### `mod_id`

This must exactly match the identifier declared by the mod's Mod Update Checker integration package.

The accepted format is:

```text
moddername.modname.F693BA10FC031D74
```

The creator and mod-name segments use lowercase ASCII letters, digits, underscores, or hyphens. The final section is exactly 16 uppercase hexadecimal characters.

Changing a published `mod_id` creates a different registry identity and breaks continuity for installed declarations.

### `display_name`

The public name of the mod. This is used only for review and documentation. It is not included in the registry downloaded by players.

### `creator_name`

The public creator or team name. This is used only for review and documentation.

### `mod_page`

The public official page describing the mod.

It may be:

- the creator's official website;
- a public Mod The Sims or similar platform listing;
- a public project page;
- the public GitHub repository presentation page.

The URL must use HTTPS and must not contain embedded credentials.

This value is used only for manual review and registry documentation. It is not included in the registry downloaded by players, is never opened by MUC, and is not fetched automatically by the registry workflow.

### `maintainers`

One or more GitHub usernames authorized to maintain the entry.

For an initial submission, the Pull Request author should normally be listed here. Organization-owned projects may list the people responsible for releases.

Changing the maintainers of an existing entry requires manual review.

### `source.type`

Currently, the only supported source is:

```json
"github_releases"
```

The registry workflow contacts GitHub's public Releases API. The game does not contact the mod creator's repository.

### `source.repository`

The public GitHub repository in `Owner/Repository` form.

Example:

```json
"ExampleGitHubUser/ModName"
```

Do not enter a URL. Arbitrary hosts and arbitrary API endpoints are not accepted.

Private repositories are not supported.

### `source.tag_prefix`

The exact text placed before the semantic version in release tags.

Examples:

| Release tag | `tag_prefix` | Extracted version |
| --- | --- | --- |
| `v1.2.0` | `v` | `1.2.0` |
| `1.2.0` | empty string | `1.2.0` |
| `example-mod-v1.2.0` | `example-mod-v` | `1.2.0` |

This allows multiple mods to share one GitHub repository when each mod uses a different tag prefix.

The text after the prefix must be a valid semantic version.

### `source.channels`

Accepted values:

```text
stable
prerelease
```

A stable entry is generated from the highest matching published GitHub Release where:

- `draft` is `false`;
- `prerelease` is `false`;
- the tag matches `tag_prefix`;
- the extracted version is valid SemVer;
- the extracted version is not itself a prerelease version.

A prerelease entry is generated from the highest matching published GitHub Release where:

- `draft` is `false`;
- `prerelease` is `true`;
- the tag matches `tag_prefix`;
- the extracted version is valid SemVer.

Mods installed on the `stable` channel use only the stable registry entry.

Mods installed on the `prerelease` channel may use either the stable or prerelease entry. The Mod Update Checker client selects the highest allowed version.

If `prerelease` is requested but no matching prerelease currently exists, the build omits that channel and continues when a stable release exists.

## Release requirements

A release must be published through the GitHub Releases interface.

The workflow reads release metadata only. It does not download or execute release assets.

Recommended tags:

```text
v1.0.0
v1.1.0-beta.1
v2.0.0-rc.1
```

Avoid changing or deleting a published release tag after it has entered the registry.

## Updating an existing entry

Most new versions require no registry Pull Request.

Publish a matching GitHub Release in the configured repository. The scheduled registry workflow will detect it, rebuild the registry, sign it, and publish it.

A new Pull Request is required only when changing entry configuration, such as:

- the GitHub repository;
- the tag prefix;
- supported release channels;
- maintainers;
- the official mod page;
- the public creator or mod name.

## Automated validation

Pull Requests are checked automatically.

Validation includes:

- valid UTF-8 JSON;
- no duplicate JSON keys;
- schema and field validation;
- exact filename and `mod_id` matching;
- duplicate `mod_id` detection;
- public GitHub repository format;
- matching published GitHub Releases;
- valid HTTPS format for the official mod page;
- valid semantic versions;
- valid stable and prerelease channel selection.

Pull Request workflows never receive the private registry signing key.

## Pull Request review

Passing automation does not guarantee acceptance.

A maintainer may also verify:

- that the submitter is connected to the mod;
- that the `mod_id` matches the released package;
- that the official mod page identifies the same mod and creator;
- that the repository and release tags are official;
- that no generated or security-sensitive file was modified;
- that the entry does not impersonate another creator.

## Security reports

Do not disclose a security vulnerability in a public Issue or Pull Request.

Use the private vulnerability reporting feature described in `SECURITY.md`.
