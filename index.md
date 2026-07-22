# Demeterio — Mod Update Checker Public Registry

Welcome to the public registry used by **Mod Update Checker for The Sims 4** (MUC).

MUC retrieves one signed registry document containing public mod-version information. Version comparisons are performed locally in the player's game. MUC does **not** download, install, import, or execute mod files.

Once every day, this registry checks each configured public GitHub Releases repository and publishes a newly generated and signed document with a fresh timestamp. MUC verifies both the signature and the freshness of that document before using it.

Like any network request, the registry host and ordinary network infrastructure may receive connection metadata such as the player's IP address, request time, and the fixed MUC User-Agent. MUC does not transmit EA account data, installed mod IDs, installed versions, save data, or gameplay information.

## Quick links

| Resource | Link |
| --- | --- |
| Browse registered mods | [Open the human-readable catalogue](http://muc-registry.demeterio.cc/registry/) |
| Signed registry used by MUC | [View registry-v1.json](http://muc-registry.demeterio.cc/generated/registry-v1.json) |
| Human-readable registry data | [View registry-v1-readable.json](http://muc-registry.demeterio.cc/generated/registry-v1-readable.json) |
| Published entry schema | [View mod-entry.schema.json](http://muc-registry.demeterio.cc/schemas/mod-entry.schema.json) |
| Beginner mod-submission guide | [Read the browser-only instructions](https://github.com/Demeterio/Mod-Update-Checker_registry/blob/main/CONTRIBUTING.md#browser-only-github-guide) |
| Entry template | [Open the JSON template](https://github.com/Demeterio/Mod-Update-Checker_registry/blob/main/templates/mod-entry.template.json) |
| Latest MUC release and MODDER documentation | [Open the latest Release](https://github.com/Demeterio/Mod-Update-Checker/releases/latest) |
| Report a public problem | [Open an Issue](https://github.com/Demeterio/Mod-Update-Checker_registry/issues/new/choose) |
| Review proposed changes | [View Pull Requests](https://github.com/Demeterio/Mod-Update-Checker_registry/pulls) |
| Inspect the MUC source code | [Mod Update Checker on GitHub](https://github.com/Demeterio/Mod-Update-Checker) |
| Creator website | [Demeterio on Tumblr](https://demeterio.tumblr.com/) |

## For mod creators

The latest MUC Release includes a modder archive whose name contains **MODDER**. Its PDF guide explains how to create the required Sims 4 declaration `.package`, prepare public GitHub Releases, and submit a registry entry.

Registry entry values are validated strictly. Accidental leading or trailing spaces, incorrect channel capitalization, uppercase values in `maintainers`, unsupported tag prefixes, and additional JSON fields are rejected instead of being silently corrected.

A Pull Request can only be created after a contributor changes and commits a file in their fork. Beginners should follow the browser-only guide rather than starting from the Pull Requests tab.

## When an entry is not yet listed

A creator may distribute a valid declaration package before the registry Pull Request is accepted. MUC reports that the mod is not currently listed, retains any last known registry information as historical data, and continues normal gameplay.

## Security and transparency

The registry source entries, schema, building and signing code, workflows, tests, contribution history, public catalogue, signed document, public key, and fingerprint are publicly visible.

MUC rejects modified signatures, malformed payloads, registries more than seven days old, registries dated too far in the future, and registries older than the last one accepted by that installation.

The complete Mod Update Checker Python source is also available in the public mod repository for independent inspection of its network restrictions, consent handling, freshness checks, signature verification, and update-checking behavior.

MUC does not bypass privacy or security tools. A blocked registry request stops the update check without affecting normal gameplay.

Compatibility testing with ModGuard and Privacy Protector is planned. Confirmed results will be published after testing.

## Disclaimer

Mod Update Checker is an unofficial fan-made project. It is not affiliated with, authorized by, sponsored by, or endorsed by Electronic Arts or Maxis.

The Sims and all related names and trademarks belong to their respective owners.

## Copyright

Copyright © Demeterio.
