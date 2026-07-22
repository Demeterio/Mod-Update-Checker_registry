# Contributing to the Mod Update Checker Registry

Thank you for helping maintain the public Mod Update Checker registry.

This guide is written for mod creators who may be new to GitHub. You can complete the entire registry submission through a web browser; installing Git or Visual Studio Code is not required.

The registry contains public version metadata only. It does not host mod files, install updates, collect player information, or inspect a player's Mods folder.

Like any network request, the registry host and normal network infrastructure may receive ordinary connection metadata such as the player's IP address, request time, and the fixed MUC User-Agent.

## Start with the MUC modder documentation

Download the [latest Mod Update Checker release](https://github.com/Demeterio/Mod-Update-Checker/releases/latest) and choose the release asset whose name contains **MODDER**.

The PDF documentation inside that ZIP explains how to:

- create the required The Sims 4 declaration `.package`;
- choose the mod ID and installed version;
- choose the stable or prerelease channel;
- create a public GitHub repository for your mod;
- publish mod versions with GitHub Releases;
- prepare and submit your registry entry.

This `CONTRIBUTING.md` file focuses on submitting the registry JSON after the Sims 4 package and GitHub Release setup are ready.

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

**Do not begin by clicking `Pull requests → New pull request`.** GitHub can only create a Pull Request after your fork or branch contains at least one committed change. Without a change, GitHub correctly reports that there is nothing to compare.

### Use Security when you want to

Report vulnerabilities privately through **Security → Advisories → Report a vulnerability**.

Do not disclose private keys, tokens, signing weaknesses, validation bypasses, or other sensitive security information in a public Issue or Pull Request.

## Before submitting a mod entry

Your own The Sims 4 mod ZIP must already include a valid **Mod Update Checker declaration `.package` file**, or provide that declaration through a clearly identified optional MUC integration download.

The declaration `.package` is a small Sims 4 tuning package created by the mod author. It tells MUC the mod ID, installed version, release channel, and other integration information.

A player who installs this declaration `.package` must also separately install the current **Mod Update Checker `.ts4script`** in their Sims 4 Mods folder. The MUC `.ts4script` is installed by the player and is not automatically included in third-party mods.

Without the MUC `.ts4script`, the custom tuning class used by the declaration package is unavailable and the declaration may generate tuning-loading errors. Mod creators should therefore explain this requirement clearly in their installation instructions.

A valid declaration may be released before its central registry entry is accepted. In that case, MUC reports that the central entry is missing and skips the version comparison without affecting normal gameplay.

You will need:

- the exact `mod_id` declared in your Sims 4 `.package`;
- your own public GitHub repository containing your mod's published Releases;
- a public official HTTPS page describing your mod;
- at least one published, non-draft GitHub Release matching the intended tag prefix and release channel;
- Release tags containing valid semantic versions;
- authorization from the creator or maintainer to submit or maintain the entry;
- a GitHub account used to create the fork and Pull Request.

Git tags without a published GitHub Release are not sufficient.

## Browser-only GitHub guide

This is the recommended method for beginners.

### Step 1 — Sign in to GitHub

Create or sign in to the GitHub account that will maintain the registry entry.

The username of this account will normally be listed in the entry's `maintainers` field.

### Step 2 — Fork the registry

1. Open the [Mod Update Checker registry repository](https://github.com/Demeterio/Mod-Update-Checker_registry).
2. Click **Fork** near the top-right corner.
3. Keep the suggested repository name.
4. Click **Create fork**.

GitHub creates a personal copy of the registry under your own account. You will edit your fork, not Demeterio's `main` branch.

### Step 3 — Create the entry file in your fork

1. In your fork, open the `entries` folder.
2. Click **Add file**.
3. Choose **Create new file**.
4. In the filename field, enter your complete filename:

```text
yourcreatorname.yourmodname.0123456789ABCDEF.json
```

5. Open the [entry template](https://github.com/Demeterio/Mod-Update-Checker_registry/blob/main/templates/mod-entry.template.json) in another tab.
6. Copy the complete JSON template.
7. Paste it into the new file editor.
8. Replace every placeholder with your real information.

The filename must be exactly the same as your `mod_id`, followed by `.json`.

### Step 4 — Commit the change

1. Click **Commit changes**.
2. Use a short message such as:

```text
Add My Mod registry entry
```

3. When GitHub offers the choice, select **Create a new branch for this commit and start a pull request**.
4. Give the branch a simple name, for example:

```text
add-my-mod
```

5. Confirm the commit.

If GitHub commits directly to your fork's `main` branch instead, that is still workable. Return to the main page of your fork and continue with the next step.

### Step 5 — Open the Pull Request

After the commit, GitHub normally displays a yellow banner with **Compare & pull request**.

You can also:

1. open the main page of your fork;
2. click **Contribute**;
3. click **Open pull request**.

On the comparison page, verify:

```text
base repository: Demeterio/Mod-Update-Checker_registry
base branch: main
head repository: your GitHub fork
compare branch: the branch containing your entry
```

GitHub should display your new JSON file as a change.

If GitHub says **There is nothing to compare**, return to your fork and verify that:

- the JSON file exists in your fork;
- the change was committed;
- the correct compare branch is selected;
- the base repository is Demeterio's registry;
- the base branch is `main`.

### Step 6 — Complete the Pull Request form

The repository automatically inserts a Pull Request template.

Complete the requested mod information and check each applicable confirmation box. You can edit the title and description before clicking **Create pull request**.

A Pull Request cannot be created before there is a committed difference between branches. However, after the first commit you may create a **Draft Pull Request** if you want to provide information early and continue working before requesting final review.

For a normal single-entry submission, it is usually simpler to finish the JSON first and then create a regular Pull Request.

### Step 7 — Validation and review

After the Pull Request is created:

1. GitHub waits for Demeterio to approve the external workflow run.
2. The `validate` workflow checks your JSON and your public GitHub Releases.
3. Demeterio reviews the submitted files and public mod information.
4. You may be asked to correct the entry.
5. The Pull Request is merged only after validation and maintainer approval.

Never merge or close the Pull Request yourself unless you are the registry maintainer.

## File location

Each mod uses one JSON source file in the `entries/` directory.

The filename must be the exact Mod Update Checker ID followed by `.json`.

Example:

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
    "YourGitHubUsername"
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

Do not edit or replace:

```text
security/muc-registry-public-key.pem
security/muc-registry-public-key.sha256
```

The signed registry, readable registry, and catalogue are rebuilt and deployed automatically after an accepted change reaches `main`.

## Field reference

### `mod_id`

This must exactly match the identifier declared by your mod's MUC integration `.package`.

Accepted format:

```text
moddername.modname.F693BA10FC031D74
```

The creator and mod-name segments use lowercase ASCII letters, digits, underscores, or hyphens. The final section is exactly 16 uppercase hexadecimal characters.

Changing a published `mod_id` creates a different registry identity and breaks continuity for installed declarations.

### `display_name`

The public name of your mod.

It is included in the human-readable catalogue but not in the signed player registry downloaded by MUC.

### `creator_name`

Your public creator or team name.

It is included in the human-readable catalogue but not in the signed player registry.

### `mod_page`

The official public page describing your mod.

It may be:

- your official creator website;
- your public Mod The Sims or similar platform listing;
- your public project page;
- your public GitHub repository presentation page.

The URL must:

- use HTTPS;
- be publicly accessible;
- identify the same mod and creator;
- not contain embedded credentials.

The page is included as a link in the human-readable catalogue. It is not included in the signed player registry, is never opened by MUC, and is not fetched by the registry workflow.

### `maintainers`

Enter the GitHub username or usernames authorized to maintain this registry entry.

For an initial submission, this is normally **your own GitHub account name—the same account used to fork the repository and open the Pull Request**.

For example, if your GitHub profile is:

```text
https://github.com/ExampleCreator
```

use:

```json
"maintainers": [
  "ExampleCreator"
]
```

Organization-owned projects may list the GitHub accounts of the people responsible for the mod's Releases.

Changing the maintainers of an existing entry requires manual review.

### `source.type`

The only currently supported source is:

```json
"github_releases"
```

The registry workflow contacts GitHub's public Releases API for the repository named in `source.repository`. In other words, it checks **your mod's public GitHub Releases**.

The Sims 4 game and the MUC script mod do not contact your GitHub repository directly. The central registry workflow performs that check and publishes the resolved version in the signed registry.

### `source.repository`

Enter **your mod's public GitHub repository** in `Owner/Repository` form.

- `Owner` is your GitHub username or organization name.
- `Repository` is the name of your mod repository.

Example profile and repository:

```text
GitHub account: ExampleCreator
Repository name: ExampleMod
```

Registry value:

```json
"repository": "ExampleCreator/ExampleMod"
```

Do not enter the complete URL. Arbitrary hosts and API endpoints are not accepted.

Private repositories are not supported.

### `source.tag_prefix`

The exact text placed before the semantic version in your GitHub Release tags.

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

A release must be published through the **Releases** section of your public GitHub repository.

The central registry checks each registered creator's Releases every day. Most future mod versions therefore require no new registry Pull Request.

The workflow reads Release metadata only. It does not download or execute Release assets.

Recommended tags:

```text
v1.0.0
v1.1.0-beta.1
v2.0.0-rc.1
```

Avoid changing or deleting a published Release tag after it has entered the registry.

## Updating an existing entry

Most new versions require no registry Pull Request.

Publish a matching GitHub Release in your configured repository. The scheduled registry workflow detects it, rebuilds the signed registry and readable catalogue, and republishes the site.

A new Pull Request is required only when changing entry configuration, such as:

- your GitHub repository;
- your tag prefix;
- supported Release channels;
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

Every external Pull Request and every update to an existing entry requires maintainer review before it can be merged.

The maintainer may verify:

- that the submitter is connected to the mod;
- that the `mod_id` matches the released declaration `.package`;
- that the official page identifies the same mod and creator;
- that the repository and Release tags are official;
- that no generated or security-sensitive file was added or modified;
- that the entry does not impersonate another creator.

## Security reports

Do not disclose a security vulnerability in a public Issue or Pull Request.

Use the private vulnerability reporting feature described in `SECURITY.md`.
