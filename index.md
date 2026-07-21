# Mod Update Checker Public Registry0

Welcome to the public registry used by **Mod Update Checker for The Sims 4** (or MUC).

MUC retrieves one small public registry document containing mod version information. Version comparisons are then performed locally in the player’s game.

MUC does **not** download, install, import, or execute mod files.

## Quick links

| Resource            | Link                                                                                                       |
| ------------------- | ---------------------------------------------------------------------------------------------------------- |
| Live registry       | [View registry-v1.json](http://muc-registry.demeterio.cc/generated/registry-v1.json)                       |
| Public verification key | [View public key](http://muc-registry.demeterio.cc/security/muc-registry-public-key.pem)               |
| Public-key fingerprint | [View fingerprint](http://muc-registry.demeterio.cc/security/muc-registry-public-key.sha256)             |
| Registry repository | [View on GitHub](https://github.com/Demeterio/Mod-Update-Checker_registry)                                 |
| Mod repository      | [Mod Update Checker on GitHub](https://github.com/Demeterio/Mod-Update-Checker)                            |
| Contribution guide  | [Read CONTRIBUTING.md](https://github.com/Demeterio/Mod-Update-Checker_registry/blob/main/CONTRIBUTING.md) |
| Registry templates  | [View templates](https://github.com/Demeterio/Mod-Update-Checker_registry/tree/main/templates)             |
| Example entries     | [View examples](https://github.com/Demeterio/Mod-Update-Checker_registry/tree/main/examples)               |
| Pull Requests       | [View proposed changes](https://github.com/Demeterio/Mod-Update-Checker_registry/pulls)                    |
| Creator website     | [Demeterio on Tumblr](https://demeterio.tumblr.com/)                                                       |

## What the registry contains

The registry contains public mod update information such as:

* a stable mod identifier;
* the release channel;
* the latest known version;
* the related release tag;
* the date on which the version information was checked.

The registry does not contain:

* player information;
* EA account information;
* save-game information;
* the contents of a player’s Mods folder;
* a list of installed mods;
* analytics or advertising identifiers;
* authentication credentials.

## Live registry document

The current generated and signed registry is available here:

http://muc-registry.demeterio.cc/generated/registry-v1.json

The generated document is managed through the public registry repository. Proposed additions and changes can be reviewed through GitHub Pull Requests.

## Why the registry uses HTTP

The Python runtime included with The Sims 4 does not provide the native `_ssl` extension required by Python’s standard `ssl` module.

For compatibility with the game’s bundled Python runtime, MUC retrieves the public registry through a dedicated HTTP endpoint:

```text
http://muc-registry.demeterio.cc/generated/registry-v1.json
```

The registry contains only public version information.

MUC restricts the request to one fixed domain, one fixed port, and one fixed path. Alternate domains, redirects, query strings, credentials, compressed responses, and oversized responses are rejected.

## Registry signature

Cryptographic registry verification is enabled.

The live `generated/registry-v1.json` file is a signed JSON envelope containing:

* signature schema `1`;
* trusted key ID `muc-registry-2026-01`;
* algorithm `RS256`;
* the canonical registry payload encoded in Base64;
* an RSA PKCS#1 v1.5 SHA-256 signature encoded in Base64.

MUC verifies the complete payload before parsing or using any registry entry. It rejects missing, malformed, modified, incorrectly signed, or untrusted registry documents.

The public key and fingerprint are published under `security/`. The private signing key is stored only as an encrypted GitHub Actions secret and is never committed, published, or included with the mod.

No detached `.sig` file is used.

## Add or update a mod

Registry changes are submitted through GitHub Pull Requests.

1. Read the [contribution guide](https://github.com/Demeterio/Mod-Update-Checker_registry/blob/main/CONTRIBUTING.md).
2. Copy the appropriate [entry template](https://github.com/Demeterio/Mod-Update-Checker_registry/tree/main/templates).
3. Review the available [examples](https://github.com/Demeterio/Mod-Update-Checker_registry/tree/main/examples).
4. Fork the registry repository.
5. Add or update the required entry.
6. Open a [Pull Request](https://github.com/Demeterio/Mod-Update-Checker_registry/compare).

All submissions must pass the repository’s automated validation before they can be included in the generated registry.

Do not manually edit generated files unless the contribution guide explicitly instructs you to do so.

## Transparency

The registry source, contribution history, proposed changes, generated document, public verification key, and key fingerprint are publicly visible.

MUC performs version comparisons locally and never uses the registry to install or execute mod updates.

## Disclaimer

Mod Update Checker is an unofficial fan-made project.

It is not affiliated with, authorized by, sponsored by, or endorsed by Electronic Arts or Maxis.

The Sims and all related names and trademarks belong to their respective owners.

## Copyright

Copyright © Demeterio.
