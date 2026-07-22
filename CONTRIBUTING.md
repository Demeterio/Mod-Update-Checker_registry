# Contributing to the Mod Update Checker Registry

Thank you for helping maintain the public Mod Update Checker registry.

The registry contains public version metadata only. It does not host mod files, install updates, collect player information, or inspect a player's Mods folder.

## Choose the correct channel

### Open an Issue when you want to

- report an incorrect displayed version;
- report a broken official-page or release link;
- report a missing, duplicate, or incorrectly named entry;
- report a problem with the public catalogue;
- report a documentation problem;
- suggest a non-security improvement;
- ask for clarification before preparing a contribution.

An Issue reports a problem or idea. It does not directly change repository files.

### Open a Pull Request when you want to

- add a new mod entry;
- change an existing entry configuration;
- remove or disable an entry;
- submit an exact documentation, test, workflow, or tooling correction.

A Pull Request proposes actual file changes and is subject to automated validation and maintainer review.

### Use Security when you want to

Report vulnerabilities privately through **Security → Advisories → Report a vulnerability**.

Do not disclose private keys, tokens, signing weaknesses, validation bypasses, or other sensitive security information in a public Issue or Pull Request.

## Before submitting a mod entry

The mod must already include a valid Mod Update Checker declaration package.

The declaration package is an optional MUC integration and requires the Mod Update Checker script mod to be installed. Without MUC, the custom tuning class is unavailable and the declaration may generate tuning-loading errors.

A valid declaration may be installed before its central registry entry is accepted. In that case, MUC reports the entry as missing and skips the version comparison without affecting normal gameplay.

You will need:

- the exact `mod_id` declared in the package;
- the public GitHub repository containing the mod's published Releases;
- a public official HTTPS page describing the mod;
- at least one published, non-draft GitHub Release matching the intended tag prefix and release channel;
- release tags containing valid semantic versions;
- authorization from the creator or maintainer to submit or maintain the entry.

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
4. Save the copy as `entries/<mod_id>.json`.
5. Replace every placeholder.
6. Commit only the source entry and directly related documentation.
7. Open a Pull Request against `main`.
8. Complete the Pull Request checklist.
9. Wait for the `validate` check and maintainer review.

Do not add or commit generated outputs:

```text
generated/registry-v1.json
generated/registry-v1-readable.json
```

Do not edit or replace:

```text
security/muc-registry-public-key.pem
security/muc-registry-public-key.sha256
```

The signed registry, readable registry, and catalogue are rebuilt and deployed automatically after an accepted change reaches `main`.

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

## Field reference

### `mod_id`

This must exactly match the identifier declared by the mod's MUC integration package.

Accepted format:

```text
moddername.modname.F693BA10FC031D74
```

The creator and mod-name segments use lowercase ASCII letters, digits, underscores, or hyphens. The final section is exactly 16 uppercase hexadecimal characters.

Changing a published `mod_id` creates a different registry identity and breaks continuity for installed declarations.

### `display_name`

The public name of the mod.

It is included in the human-readable catalogue but not in the signed player registry downloaded by MUC.

### `creator_name`

The public creator or team name.

It is included in the human-readable catalogue but not in the signed player registry.

### `mod_page`

The official public page describing the mod.

It may be:

- the creator's official website;
- a public Mod The Sims or similar platform listing;
- a public project page;
- the public GitHub repository presentation page.

The URL must:

- use HTTPS;
- be publicly accessible;
- identify the same mod and creator;
- not contain embedded credentials.

The page is included as a link in the human-readable catalogue. It is not included in the signed player registry, is never opened by MUC, and is not fetched by the registry workflow.

### `maintainers`

One or more GitHub usernames authorized to maintain the entry.

For an initial submission, the Pull Request author should normally be listed. Organization-owned projects may list the people responsible for releases.

Changing the maintainers of an existing entry requires manual review.

### `source.type`

The only currently supported source is:

```json
"github_releases"
```

The registry workflow contacts GitHub's public Releases API. The game does not contact the creator's repository.

### `source.repository`

The public GitHub repository in `Owner/Repository` form.

Example:

```json
"ExampleGitHubUser/ModName"
```

Do not enter a URL. Arbitrary hosts and API endpoints are not accepted.

Private repositories are not supported.

### `source.tag_prefix`

The exact text placed before the semantic version in release tags.

| Release tag | `tag_prefix` | Extracted version |
| --- | --- | --- |
| `v1.2.0` | `v` | `1.2.0` |
| `1.2.0` | empty string | `1.2.0` |
| `example-mod-v1.2.0` | `example-mod-v` | `1.2.0` |

This allows multiple mods to share one GitHub repository when each mod uses a different tag prefix.

The text after the prefix must be valid SemVer.

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

Mods installed on the `prerelease` channel may use either the stable or prerelease entry. MUC selects the highest allowed version.

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

Publish a matching GitHub Release in the configured repository. The scheduled registry workflow detects it, rebuilds the signed registry and readable catalogue, and republishes the site.

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

- Python syntax and unit tests;
- valid UTF-8 JSON;
- no duplicate JSON keys;
- exact root-field validation;
- exact filename and `mod_id` matching;
- duplicate `mod_id` detection;
- official-page HTTPS validation;
- public GitHub repository format;
- matching published GitHub Releases;
- valid semantic versions;
- stable and prerelease channel selection;
- generation of the signed-registry payload;
- generation of the human-readable registry;
- test signing with an ephemeral RSA key.

Pull Request workflows never receive the private production signing key.

## Pull Request review

Passing automation does not guarantee acceptance.

A maintainer may also verify:

- that the submitter is connected to the mod;
- that the `mod_id` matches the released declaration package;
- that the official page identifies the same mod and creator;
- that the repository and release tags are official;
- that no generated or security-sensitive file was added or modified;
- that the entry does not impersonate another creator.

## Security reports

Do not disclose a security vulnerability in a public Issue or Pull Request.

Use the private vulnerability reporting feature described in `SECURITY.md`.
