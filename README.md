# Demeterio: Mod Update Checker Public Registry

This repository hosts the public version registry used by **Mod Update Checker for The Sims 4** (MUC).

The repository stores reviewed source entries and the code used to build the registry. GitHub Actions resolves public GitHub Releases, creates a signed registry for MUC, creates a human-readable catalogue, and publishes both through GitHub Pages.

The registry does not collect player information, inspect a player's Mods folder, or receive a list of installed mods.

## Quick links

| Resource | Link |
| --- | --- |
| Human-readable mod catalogue | [Browse registered mods](http://muc-registry.demeterio.cc/registry/) |
| Signed registry used by MUC | [View registry-v1.json](http://muc-registry.demeterio.cc/generated/registry-v1.json) |
| Human-readable registry data | [View registry-v1-readable.json](http://muc-registry.demeterio.cc/generated/registry-v1-readable.json) |
| Published entry schema | [View mod-entry.schema.json](http://muc-registry.demeterio.cc/schemas/mod-entry.schema.json) |
| Contribution guide | [Read CONTRIBUTING.md](CONTRIBUTING.md) |
| Report a public problem | [Open an Issue](https://github.com/Demeterio/Mod-Update-Checker_registry/issues/new/choose) |
| Propose a registry change | [Open a Pull Request](https://github.com/Demeterio/Mod-Update-Checker_registry/pulls) |
| Mod source code | [Mod Update Checker](https://github.com/Demeterio/Mod-Update-Checker) |
| Creator website | [Demeterio on Tumblr](https://demeterio.tumblr.com/) |
| Creator GitHub profile | [Demeterio on GitHub](https://github.com/Demeterio) |

## Issues, Pull Requests, and security reports

Use the channel that matches what you are trying to do:

| You want to… | Use |
| --- | --- |
| Report an incorrect version, broken link, missing entry, catalogue display problem, or documentation problem | **Issue** |
| Suggest a non-security improvement | **Issue** |
| Add a mod entry or propose an exact change to repository files | **Pull Request** |
| Report a vulnerability, signing problem, exposed secret, or validation bypass | **Private vulnerability report under Security** |

Do not publish sensitive security information in an Issue or Pull Request.

## How the registry works

Reviewed files under `entries/` describe where a mod publishes its GitHub Releases. They do not contain a manually maintained latest-version value.

During publication, GitHub Actions:

1. validates every source entry;
2. queries the configured public GitHub Releases;
3. selects the highest valid stable and/or prerelease version;
4. builds the unsigned player registry;
5. signs the canonical player registry with the private registry key;
6. creates a separate human-readable JSON document;
7. builds and deploys the GitHub Pages site.

Generated outputs are deployment artifacts. They are not maintained manually or committed to `main`.

## Published outputs

### Signed player registry

```text
generated/registry-v1.json
```

This is the only registry document used by MUC. It is a signed JSON envelope.

### Human-readable data

```text
generated/registry-v1-readable.json
```

This contains display names, creator names, official mod pages, repositories, and resolved versions for the public catalogue. MUC does not download or use this document.

### Public catalogue

```text
registry/
```

The catalogue presents the readable registry as a searchable and sortable table.

## What the signed player registry contains

The signed payload contains public update metadata such as:

- a stable mod identifier;
- a release channel;
- the latest known version;
- the matching public release tag;
- the date on which the version information was checked.

It does not contain:

- player information;
- EA account information;
- save-game information;
- the contents of a player's Mods folder;
- a list of installed mods;
- installed mod versions;
- gameplay information;
- analytics or advertising identifiers;
- authentication credentials;
- arbitrary update-page URLs.

Official player-facing update pages remain declared locally by each compatible mod's MUC integration package.

## HTTP transparency

The signed registry used by MUC is served over HTTP:

```text
http://muc-registry.demeterio.cc/generated/registry-v1.json
```

The Python runtime included with The Sims 4 does not provide the native `_ssl` extension required by Python's standard `ssl` module. MUC therefore cannot establish a normal Python HTTPS connection with the libraries bundled with the game.

This is a technical compatibility decision, not an attempt to hide the connection.

HTTP does not provide transport encryption or built-in response authentication. For that reason, MUC verifies the cryptographic signature before decoding or using the registry payload.

## Network restrictions

The MUC network client accepts only the configured registry request:

```text
Host: muc-registry.demeterio.cc
Port: 80
Path: /generated/registry-v1.json
```

The client rejects:

- HTTPS URLs;
- alternate domains;
- alternate ports;
- credentials embedded in URLs;
- query strings;
- URL fragments;
- alternate registry paths;
- redirects;
- compressed responses;
- unsupported transfer encodings;
- oversized responses;
- responses that are not JSON.

MUC does not attempt to bypass firewalls, privacy tools such as ModGuard or Privacy Protector, security software, network-protection mods, or operating-system security settings.

If the request is blocked, the registry check stops and no additional data is retrieved.

## Registry signature

Cryptographic registry verification is enabled.

The live signed file has exactly these envelope fields:

```json
{
  "signature_schema": 1,
  "key_id": "muc-registry-2026-01",
  "algorithm": "RS256",
  "payload": "<Base64 canonical registry JSON>",
  "signature": "<Base64 RSA signature>"
}
```

The signature uses RSA PKCS#1 v1.5 with SHA-256 (`RS256`). MUC verifies the signature before decoding and validating any registry entry.

Public verification material is published under:

```text
security/muc-registry-public-key.pem
security/muc-registry-public-key.sha256
```

The private key is stored only as an encrypted GitHub Actions secret. It is never committed, published, included with the mod, or provided to Pull Request workflows.

MUC rejects the registry when:

- the signed envelope is missing or malformed;
- the signature schema, key ID, or algorithm is not trusted;
- the Base64 payload or signature is malformed;
- the payload was modified after signing;
- the signature does not match the embedded MUC public key;
- the inner registry schema or entries are invalid.

No detached `.sig` file is used.

## Contributing a mod entry

Registry entry changes are submitted through Pull Requests.

The contribution system includes:

```text
CONTRIBUTING.md
entries/
templates/mod-entry.template.json
schemas/mod-entry.schema.json
examples/
.github/pull_request_template.md
```

Contributors should:

1. read the contribution guide;
2. copy the JSON entry template;
3. review the example entry;
4. fork the repository;
5. create a branch;
6. add or update one source file under `entries/`;
7. open a Pull Request against `main`.

All submissions must pass automated validation and maintainer review before they can be merged.

## Signed payload format

The decoded signed payload uses schema version `1`:

```json
{
  "schema": 1,
  "generated_at": "2026-07-21T20:00:00Z",
  "entries": [
    {
      "mod_id": "creator.mod_name.0123456789ABCDEF",
      "release_channel": "stable",
      "version": "1.1.0",
      "release_tag": "v1.1.0",
      "checked_at": "2026-07-21T20:00:00Z"
    }
  ]
}
```

## Transparency

The source entries, code, contribution history, proposed changes, public catalogue, readable data, signed registry, public key, and public-key fingerprint are publicly visible.

MUC performs version comparisons locally and never uses the registry to download, install, import, or execute mod files.

## Disclaimer

Mod Update Checker is an unofficial fan-made project.

It is not affiliated with, authorized by, sponsored by, or endorsed by Electronic Arts or Maxis.

The Sims and all related names and trademarks belong to their respective owners.

Third-party mod names and information belong to their respective creators.

## Copyright

Copyright © Demeterio.

Permission is granted to fork and modify this repository for the purpose of proposing contributions through GitHub Pull Requests. No permission is granted to redistribute, repackage, impersonate, or operate a competing copy of the official registry or its signing infrastructure without authorization.
