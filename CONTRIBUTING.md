# Contributing to the Mod Update Checker Registry

Thank you for helping maintain the public Mod Update Checker registry.

This guide is written for mod creators who may be new to GitHub. The entire registry submission can be completed through a web browser; Git and Visual Studio Code are not required.

The registry contains public version metadata only. It does not host mod files, install updates, collect player information, or inspect a player's Mods folder.

## Start with the MUC modder documentation

Download the [latest Mod Update Checker release](https://github.com/Demeterio/Mod-Update-Checker/releases/latest) and choose the Release asset whose name contains **MODDER**.

The PDF documentation inside that ZIP explains how to:

- create the required The Sims 4 declaration `.package`;
- choose the permanent mod ID and installed version;
- choose the stable or prerelease channel;
- create a public GitHub repository for the mod;
- publish mod versions with GitHub Releases;
- prepare and submit the registry entry.

This `CONTRIBUTING.md` file focuses on the registry JSON submission after the Sims 4 package and GitHub Release setup are ready.

## Choose the correct GitHub feature

### Open an Issue when you want to

- report an incorrect displayed version;
- report a broken official-page or Release link;
- report a missing, duplicate, or incorrectly named entry;
- report a public catalogue problem;
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

**Do not begin by clicking `Pull requests → New pull request`.** GitHub can only create a Pull Request after your fork or branch contains at least one committed change. Without a change, GitHub correctly reports that there is nothing to compare.

### Use Security when you want to

Report vulnerabilities privately through **Security → Advisories → Report a vulnerability**.

Do not disclose private keys, tokens, signing weaknesses, validation bypasses, or other sensitive information in a public Issue or Pull Request.

## Before submitting a mod entry

Your own The Sims 4 mod ZIP must already include a valid **Mod Update Checker declaration `.package` file**, or provide that declaration through a clearly identified optional MUC integration download.

The declaration package tells MUC the mod ID, installed version, release channel, display name, and official player-facing update page.

A player who installs this declaration package must separately install the current **Mod Update Checker `.ts4script`**. Third-party creators should not silently bundle the MUC script mod.

A valid declaration may be released before its public registry entry is accepted. MUC then reports that the mod is not currently listed, preserves any last known registry information, skips the current comparison, and continues normal gameplay.

You will need:

- the exact `mod_id` declared in the Sims 4 package;
- a public GitHub repository containing published Releases;
- a public official HTTPS page describing the mod;
- at least one published, non-draft GitHub Release matching the intended prefix and channel;
- Release tags containing valid SemVer after the prefix;
- authorization from the creator or maintainer;
- a GitHub account used to create the fork and Pull Request.

Git tags without a published GitHub Release are not sufficient.

## Browser-only GitHub guide

This is the recommended method for beginners.

### Step 1 — Sign in to GitHub

Create or sign in to the GitHub account that will maintain the entry.

The username of this account will normally be listed in `maintainers`, written in lowercase in the JSON file.

### Step 2 — Fork the registry

1. Open the [Mod Update Checker registry repository](https://github.com/Demeterio/Mod-Update-Checker_registry).
2. Click **Fork** near the top-right corner.
3. Keep the suggested repository name.
4. Click **Create fork**.

GitHub creates a personal copy under your account. Edit your fork, not Demeterio's `main` branch.

### Step 3 — Create the entry file in your fork

1. In your fork, open the `entries` folder.
2. Click **Add file**.
3. Choose **Create new file**.
4. Enter the complete filename:

```text
yourcreatorname.yourmodname.0123456789ABCDEF.json
```

5. Open the current [entry template](https://github.com/Demeterio/Mod-Update-Checker_registry/blob/main/templates/mod-entry.template.json) in another tab.
6. Copy the complete JSON template.
7. Paste it into the new file editor.
8. Replace every placeholder with real information.

The filename must be exactly the same as `mod_id`, followed by `.json`.

### Step 4 — Check strict formatting before committing

The validator does not repair data. It rejects malformed values so that errors are visible to the contributor.

Check that:

- no string begins or ends with an accidental space;
- `stable` and `prerelease` use exact lowercase spelling;
- every `maintainers` username is lowercase;
- `tag_prefix` is empty or begins with a letter or digit;
- `mod_id` uses lowercase creator/mod segments and a 16-character uppercase hexadecimal suffix;
- no field has been added or removed;
- the JSON has no comments, trailing commas, or duplicate keys.

### Step 5 — Commit the change

1. Click **Commit changes**.
2. Use a short message such as:

```text
Add My Mod registry entry
```

3. When GitHub offers the choice, select **Create a new branch for this commit and start a pull request**.
4. Give the branch a simple name, such as `add-my-mod`.
5. Confirm the commit.

If GitHub commits directly to your fork's `main`, that is still workable.

### Step 6 — Open the Pull Request

After the commit, GitHub normally displays **Compare & pull request**.

You can also open the fork's main page and click **Contribute → Open pull request**.

Verify the comparison:

```text
base repository: Demeterio/Mod-Update-Checker_registry
base branch: main
head repository: your GitHub fork
compare branch: the branch containing your entry
```

GitHub should display the new JSON file as a change.

If GitHub says **There is nothing to compare**, return to the fork and verify that the file exists, the change was committed, the correct compare branch is selected, and the base repository and branch are correct.

### Step 7 — Complete the Pull Request form

The repository automatically inserts a Pull Request template.

Complete the requested mod information and check every applicable confirmation box. A Draft Pull Request can be created after the first committed difference when you want to provide context before the entry is final.

### Step 8 — Validation and review

After the Pull Request is created:

1. GitHub may wait for Demeterio to approve the external workflow run.
2. The validation workflow checks the JSON and public GitHub Releases.
3. The workflow creates and verifies a test signature with an ephemeral key; it never receives the production key.
4. Demeterio reviews the submitted files and public mod information.
5. You may be asked to correct the entry.
6. The Pull Request is merged only after validation and maintainer approval.

## File location

Each mod uses one JSON source file in `entries/`.

```text
entries/moddername.modname.F693BA10FC031D74.json
```

Do not place multiple mods in one file.

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
    "yourgithubusername"
  ],
  "source": {
    "type": "github_releases",
    "repository": "YourGitHubUsername/YourModRepository",
    "tag_prefix": "v",
    "channels": [
      "stable",
      "prerelease"
    ]
  }
}
```

Do not add or commit generated outputs:

```text
generated/registry-v1.json
generated/registry-v1-readable.json
```

Do not edit or replace signing material:

```text
security/muc-registry-public-key.pem
security/muc-registry-public-key.sha256
```

The signed registry, readable registry, and catalogue are rebuilt and deployed automatically after an accepted change reaches `main`.

## Strict validation rules

The schema helps editors identify basic mistakes. The Python builder remains the final authority for URL parsing, public-host checks, Release resolution, and other semantic rules.

The builder rejects values rather than trimming, lowercasing, or otherwise changing them.

### Exact strings

These are invalid:

```text
" Mod Name"
"Mod Name "
"Stable"
" prerelease"
"examplecreator "
```

Correct the source file instead of expecting the workflow to normalize it.

### `mod_id`

The value must exactly match the identifier declared by the MUC integration package.

```text
moddername.modname.F693BA10FC031D74
```

The first two segments accept lowercase ASCII letters, digits, underscores, and hyphens. The final segment is exactly 16 uppercase hexadecimal characters.

The filename must be exactly:

```text
<mod_id>.json
```

Changing a published `mod_id` creates a different registry identity and breaks continuity.

### `display_name`

The public mod name used in the readable catalogue.

Rules:

- 1 to 128 characters;
- no leading or trailing whitespace;
- no control characters or line breaks.

### `creator_name`

The public creator or team name used in the readable catalogue.

It follows the same whitespace and control-character restrictions as `display_name`.

### `mod_page`

The official public page describing the mod.

It must:

- use HTTPS;
- include a public hostname;
- contain no whitespace;
- contain no embedded username or password;
- not use `localhost` or a `.local` hostname.

The page is used only by the human-readable catalogue and review process. It is not included in the signed player registry and is never fetched by MUC.

### `maintainers`

List the GitHub usernames authorized to maintain the entry.

Registry usernames must be written in lowercase, even when a profile is commonly displayed with capitalization. GitHub usernames are treated case-insensitively, while the registry uses one canonical lowercase representation so `uniqueItems` and the Python builder enforce the same contract.

Example:

```json
"maintainers": [
  "examplecreator"
]
```

Rules:

- 1 to 20 usernames;
- lowercase ASCII letters, digits, and hyphens only;
- no leading or trailing hyphen;
- no duplicates;
- no leading or trailing whitespace.

Changing maintainers requires manual review.

### `source.type`

The only supported value is:

```json
"github_releases"
```

### `source.repository`

Enter the public mod repository in `Owner/Repository` form:

```json
"repository": "ExampleCreator/ExampleMod"
```

Do not enter a complete URL. Private repositories are not supported.

The schema and builder reject missing segments, leading or trailing punctuation, consecutive dots, whitespace, arbitrary URLs, and additional path components.

### `source.tag_prefix`

This is the exact text placed before the SemVer portion of each Release tag.

| Release tag | `tag_prefix` | Extracted version |
| --- | --- | --- |
| `v1.2.0` | `v` | `1.2.0` |
| `1.2.0` | empty string | `1.2.0` |
| `example-mod-v1.2.0` | `example-mod-v` | `1.2.0` |

The prefix may be empty. A non-empty prefix must begin with an ASCII letter or digit and may then contain letters, digits, dots, underscores, slashes, plus signs, or hyphens.

These examples are rejected:

```text
/release-
-version-
 prefix
```

The text after the prefix must be strict SemVer and must not begin with another `v` unless that `v` is part of the configured prefix.

### `source.channels`

Accepted values are exactly:

```text
stable
prerelease
```

The values are case-sensitive. `Stable`, `Prerelease`, and values containing spaces are rejected.

A stable entry is generated from the highest matching published non-draft Release where GitHub's `prerelease` flag is false and the extracted SemVer is not a prerelease.

A prerelease entry is generated from the highest matching published non-draft Release where GitHub's `prerelease` flag is true.

Mods installed on the `stable` channel use only the stable entry. Mods installed on the `prerelease` channel may use either the stable or prerelease entry; MUC selects the highest allowed version.

If prerelease is configured but no matching prerelease currently exists, the build may omit that channel and continue when a stable Release exists.

## Release requirements

A Release must be published through the **Releases** section of the public GitHub repository. A Git tag by itself is not enough.

Recommended tags:

```text
v1.0.0
v1.1.0-beta.1
v2.0.0-rc.1
```

Avoid changing or deleting a published Release tag after it has entered the registry.

The workflow reads Release metadata only. It does not download or execute Release assets.

## Updating an existing entry

Most new versions require no registry Pull Request. Publish a matching GitHub Release in the configured repository and the scheduled workflow will rebuild the registry.

A new Pull Request is required when changing:

- the public GitHub repository;
- the tag prefix;
- supported Release channels;
- maintainers;
- the official mod page;
- the public creator or mod name;
- the permanent mod ID.

## Automated validation

Pull Request validation includes:

- Python compilation and unit tests;
- strict UTF-8 JSON parsing;
- rejection of duplicate JSON keys;
- exact root and nested field validation;
- exact whitespace and case validation;
- schema and Python-builder contract tests;
- exact filename and `mod_id` matching;
- duplicate `mod_id` detection;
- HTTPS official-page validation;
- public GitHub repository format;
- matching published GitHub Releases;
- strict SemVer validation;
- stable and prerelease channel selection;
- generation of a fresh unsigned registry;
- canonical payload validation;
- test signing with an ephemeral RSA key;
- independent verification of the completed signed envelope;
- generation of the human-readable registry.

Pull Request workflows never receive the private production signing key.

## Pull Request review

Passing automation does not guarantee acceptance.

The maintainer may verify:

- that the submitter is connected to the mod;
- that `mod_id` matches the released declaration package;
- that the official page identifies the same mod and creator;
- that the repository and Release tags are official;
- that the lowercase `maintainers` list represents authorized accounts;
- that no generated or security-sensitive file was added or modified;
- that the entry does not impersonate another creator.

## Security reports

Do not disclose a security vulnerability in a public Issue or Pull Request. Use the private vulnerability reporting feature described in `SECURITY.md`.
