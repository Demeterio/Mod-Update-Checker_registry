<!--
Use a Pull Request only when you are proposing actual file changes.

To report incorrect registry data, a broken link, a catalogue problem, or a
non-security suggestion without submitting a fix, open an Issue instead.

Never disclose a security vulnerability here. Use the private reporting
option under Security → Advisories → Report a vulnerability.
-->

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

**Public GitHub Releases repository:**

```text
Owner/Repository
```

## Release configuration

For registry-entry changes:

- [ ] The GitHub repository is public.
- [ ] At least one matching, non-draft GitHub Release is published.
- [ ] The published Release matches the configured tag prefix.
- [ ] Release tags contain valid semantic versions.
- [ ] The requested stable and/or prerelease channels are correct.
- [ ] Draft releases are not being used as registry versions.

## Ownership and authorization

For registry-entry changes:

- [ ] I am the creator, maintainer, or an authorized representative of this mod.
- [ ] I am authorized to submit or update this registry entry.
- [ ] The entry's `maintainers` list is accurate.
- [ ] The `mod_id` exactly matches the released MUC declaration package.
- [ ] The GitHub Releases repository is an official release source for this mod.
- [ ] The official mod page identifies the same mod and creator.

## Repository safety

- [ ] I changed only the files required for this contribution.
- [ ] I did not add `generated/registry-v1.json`.
- [ ] I did not add `generated/registry-v1-readable.json`.
- [ ] I did not edit or replace the public signing-key files.
- [ ] I did not include passwords, tokens, private keys, personal data, or private repository information.
- [ ] This Pull Request does not disclose a security vulnerability.
- [ ] I understand that passing automated checks does not guarantee acceptance.

## Testing and validation

Describe any local tests performed, or write `Validation workflow only`.

## Additional context

Include unusual tag naming, repository moves, shared repositories, release-channel behavior, maintainer changes, or anything else reviewers should know.
