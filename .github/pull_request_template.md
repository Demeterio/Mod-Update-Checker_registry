<!--
A Pull Request can only be created after your fork or branch contains at least
one committed file change.

If GitHub says "There is nothing to compare", follow the browser-only guide:
https://github.com/Demeterio/Mod-Update-Checker_registry/blob/main/CONTRIBUTING.md#browser-only-github-guide

Use an Issue to report incorrect registry data, a broken link, a catalogue
problem, a contribution question, or a non-security suggestion without
submitting a file change.

Never disclose a security vulnerability here. Use:
Security → Advisories → Report a vulnerability.
-->

> **New to GitHub?** This form appears only after you have changed and committed
> a file in your fork or branch. Read the
> [browser-only contribution guide](https://github.com/Demeterio/Mod-Update-Checker_registry/blob/main/CONTRIBUTING.md#browser-only-github-guide)
> before submitting.

## Summary

Describe the exact change proposed by this Pull Request.

## Change type

- [ ] Add a new mod entry
- [ ] Update an existing mod entry
- [ ] Remove or disable an entry
- [ ] Documentation or catalogue change
- [ ] Validation, test, workflow, or tooling change

## Registry entry information

Complete this section for entry additions or configuration changes. Write `N/A` for documentation or tooling-only changes.

**Mod name:**

**Creator or team:**

**Your GitHub username:**

**Mod Update Checker ID:**

```text
creator.mod_name.0123456789ABCDEF
```

**Entry file:**

```text
entries/creator.mod_name.0123456789ABCDEF.json
```

**Official mod page:**

```text
https://example.com/mod-page
```

**Your public GitHub Releases repository:**

```text
YourGitHubUsername/YourModRepository
```

## Strict entry formatting

For registry-entry changes:

- [ ] I copied the current repository template instead of an old local copy.
- [ ] No string contains accidental leading or trailing whitespace.
- [ ] `stable` and `prerelease` use exact lowercase spelling.
- [ ] Every username in `maintainers` is written in lowercase.
- [ ] The entry contains no comments, trailing commas, duplicate keys, or additional fields.
- [ ] `tag_prefix` is empty or begins with an ASCII letter or digit.
- [ ] The filename exactly matches `<mod_id>.json`.

## Release configuration

For registry-entry changes:

- [ ] My GitHub repository is public.
- [ ] At least one matching, non-draft GitHub Release is published.
- [ ] The published Release matches the configured tag prefix.
- [ ] The text after the prefix is strict SemVer without another leading `v`.
- [ ] The requested stable and/or prerelease channels are correct.
- [ ] Draft Releases are not being used as registry versions.

## Sims 4 MUC declaration

For registry-entry changes:

- [ ] My mod distribution includes a valid Sims 4 MUC declaration `.package`.
- [ ] The entry's `mod_id` exactly matches the declaration package.
- [ ] My installation instructions explain that players must separately install the MUC `.ts4script`.
- [ ] I reviewed the PDF guide included in the latest MUC Release asset marked **MODDER**.

## Ownership and authorization

For registry-entry changes:

- [ ] I am the creator, maintainer, or an authorized representative of this mod.
- [ ] I am authorized to submit or update this registry entry.
- [ ] The entry's lowercase `maintainers` list contains the correct GitHub account or accounts.
- [ ] The GitHub Releases repository is an official Release source for this mod.
- [ ] The official mod page identifies the same mod and creator.

## Repository safety

- [ ] I changed only the files required for this contribution.
- [ ] I did not add `generated/registry-v1.json`.
- [ ] I did not add `generated/registry-v1-readable.json`.
- [ ] I did not edit or replace the public signing-key files.
- [ ] I did not include passwords, tokens, private keys, personal data, or private repository information.
- [ ] This Pull Request does not disclose a security vulnerability.
- [ ] I understand that every external Pull Request requires workflow approval, automated validation, and maintainer review.
- [ ] I understand that passing automated checks does not guarantee acceptance.

## Testing and validation

Describe any local tests performed, or write `Validation workflow only`.

## Additional context

Include unusual tag naming, repository moves, shared repositories, Release-channel behavior, maintainer changes, or anything else the reviewer should know.
