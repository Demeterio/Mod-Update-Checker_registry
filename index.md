# Demeterio — Mod Update Checker Public Registry

Welcome to the public registry used by **Mod Update Checker for The Sims 4** (MUC).

MUC retrieves one small signed registry document containing public mod-version information. Version comparisons are performed locally in the player's game.

Once every day, this registry checks the public GitHub Releases of each registered mod creator and republishes the latest matching stable and prerelease versions.

MUC does **not** download, install, import, or execute mod files.

## Quick links

| Resource | Link |
| --- | --- |
| Browse registered mods | [Open the human-readable catalogue](http://muc-registry.demeterio.cc/registry/) |
| Signed registry used by MUC | [View registry-v1.json](http://muc-registry.demeterio.cc/generated/registry-v1.json) |
| Human-readable registry data | [View registry-v1-readable.json](http://muc-registry.demeterio.cc/generated/registry-v1-readable.json) |
| Beginner mod-submission guide | [Read the browser-only instructions](https://github.com/Demeterio/Mod-Update-Checker_registry/blob/main/CONTRIBUTING.md#browser-only-github-guide) |
| Latest MUC release and MODDER documentation | [Open the latest Release](https://github.com/Demeterio/Mod-Update-Checker/releases/latest) |
| Report a public problem | [Open an Issue](https://github.com/Demeterio/Mod-Update-Checker_registry/issues/new/choose) |
| Review proposed changes | [View Pull Requests](https://github.com/Demeterio/Mod-Update-Checker_registry/pulls) |
| Inspect the MUC source code | [Mod Update Checker on GitHub](https://github.com/Demeterio/Mod-Update-Checker) |
| Creator website | [Demeterio on Tumblr](https://demeterio.tumblr.com/) |
| Creator GitHub profile | [Demeterio on GitHub](https://github.com/Demeterio) |

## For mod creators

The latest MUC Release includes a modder archive whose name contains **MODDER**. Its PDF guide explains how to create the required Sims 4 declaration `.package`, prepare a public GitHub repository and Releases, and submit a registry entry.

A Pull Request can only be created after a contributor changes and commits a file in their fork. Beginners should follow the browser-only guide instead of starting from the Pull Requests tab.

## Transparency

The registry sources, building code, contribution history, public catalogue, signed document, public key, and fingerprint are publicly visible.

The complete Mod Update Checker Python source is also available in the public mod repository for independent inspection of its network restrictions, consent handling, signature verification, and update-checking behavior.

MUC performs version comparisons locally and never uses the registry to install or execute mod updates.

## Compatibility with privacy and security mods

MUC does not bypass privacy or security tools. A blocked registry request stops the update check without affecting normal gameplay.

Compatibility testing with ModGuard and Privacy Protector is planned. Confirmed test results will be published after testing is complete.

## Disclaimer

Mod Update Checker is an unofficial fan-made project.

It is not affiliated with, authorized by, sponsored by, or endorsed by Electronic Arts or Maxis.

The Sims and all related names and trademarks belong to their respective owners.

## Copyright

Copyright © Demeterio.
