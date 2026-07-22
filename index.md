# Demeterio — Mod Update Checker Public Registry

Welcome to the public registry used by **Mod Update Checker for The Sims 4** (MUC).

MUC retrieves one small signed registry document containing public mod-version information. Version comparisons are performed locally in the player's game.

MUC does **not** download, install, import, or execute mod files.

## Quick links

| Resource | Link |
| --- | --- |
| Browse registered mods | [Open the human-readable catalogue](http://muc-registry.demeterio.cc/registry/) |
| Signed registry used by MUC | [View registry-v1.json](http://muc-registry.demeterio.cc/generated/registry-v1.json) |
| Human-readable registry data | [View registry-v1-readable.json](http://muc-registry.demeterio.cc/generated/registry-v1-readable.json) |
| Public verification key | [View public key](http://muc-registry.demeterio.cc/security/muc-registry-public-key.pem) |
| Public-key fingerprint | [View fingerprint](http://muc-registry.demeterio.cc/security/muc-registry-public-key.sha256) |
| Published entry schema | [View schema](http://muc-registry.demeterio.cc/schemas/mod-entry.schema.json) |
| Contribution guide | [Read CONTRIBUTING.md](https://github.com/Demeterio/Mod-Update-Checker_registry/blob/main/CONTRIBUTING.md) |
| Report a public problem | [Open an Issue](https://github.com/Demeterio/Mod-Update-Checker_registry/issues/new/choose) |
| Propose an exact change | [Open a Pull Request](https://github.com/Demeterio/Mod-Update-Checker_registry/pulls) |
| Mod repository | [Mod Update Checker](https://github.com/Demeterio/Mod-Update-Checker) |
| Creator website | [Demeterio on Tumblr](https://demeterio.tumblr.com/) |
| Creator GitHub profile | [Demeterio on GitHub](https://github.com/Demeterio) |

## Two public registry views

### For MUC

```text
/generated/registry-v1.json
```

This is the cryptographically signed machine-readable document used by the mod.

### For people

```text
/registry/
```

This is a searchable catalogue showing registered mods, creators, official pages, repositories, stable versions, and prereleases.

The catalogue reads:

```text
/generated/registry-v1-readable.json
```

The readable document is informational and is not used by MUC.

## Why the signed registry uses HTTP

The Python runtime included with The Sims 4 does not provide the native `_ssl` extension required by Python's standard `ssl` module.

For compatibility with the game's bundled Python runtime, MUC retrieves the signed registry through a dedicated HTTP endpoint:

```text
http://muc-registry.demeterio.cc/generated/registry-v1.json
```

MUC restricts the request to one fixed host, one fixed port, and one fixed path. Alternate domains, redirects, query strings, credentials, compressed responses, and oversized responses are rejected.

## Registry signature

Cryptographic registry verification is enabled.

The signed file contains:

- signature schema `1`;
- trusted key ID `muc-registry-2026-01`;
- algorithm `RS256`;
- the canonical registry payload encoded in Base64;
- an RSA PKCS#1 v1.5 SHA-256 signature encoded in Base64.

MUC verifies the complete payload before parsing or using any registry entry.

The private signing key is stored only as an encrypted GitHub Actions secret and is never committed, published, included with the mod, or supplied to Pull Request workflows.

## Add or update a mod

Registry changes are submitted through GitHub Pull Requests.

1. Read the [contribution guide](https://github.com/Demeterio/Mod-Update-Checker_registry/blob/main/CONTRIBUTING.md).
2. Copy the [entry template](https://github.com/Demeterio/Mod-Update-Checker_registry/blob/main/templates/mod-entry.template.json).
3. Review the [example entry](https://github.com/Demeterio/Mod-Update-Checker_registry/blob/main/examples/example-mod.json).
4. Fork the repository.
5. Add or update the required source entry under `entries/`.
6. Open a Pull Request against `main`.

All submissions must pass automated validation and maintainer review.

## Report a problem

Open a public Issue for:

- incorrect registry information;
- broken catalogue or official-page links;
- catalogue display problems;
- documentation problems;
- non-security suggestions.

Submit actual entry additions and file changes through Pull Requests.

Report vulnerabilities privately through the repository's **Security** tab. Do not disclose sensitive security information publicly.

## Transparency

The source entries, code, contribution history, proposed changes, public catalogue, readable data, signed registry, public key, and key fingerprint are publicly visible.

MUC performs version comparisons locally and never uses the registry to install or execute mod updates.

## Disclaimer

Mod Update Checker is an unofficial fan-made project.

It is not affiliated with, authorized by, sponsored by, or endorsed by Electronic Arts or Maxis.

The Sims and all related names and trademarks belong to their respective owners.

## Copyright

Copyright © Demeterio.
