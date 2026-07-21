# Mod Update Checker Public Registry

This repository hosts the public version registry used by **Mod Update Checker for The Sims 4** (or MUC).

The registry provides public mod version information. It does not collect player information, inspect a player’s Mods folder, or receive a list of installed mods.

## Quick links

| Resource               | Link                                                                                             |
| ---------------------- | ------------------------------------------------------------------------------------------------ |
| Live registry JSON     | [View registry-v1.json](http://muc-registry.demeterio.cc/generated/registry-v1.json)             |
| Registry repository    | [View on GitHub](https://github.com/Demeterio/Mod-Update-Checker_registry)                       |
| Mod source code        | [Mod-Update-Checker on GitHub](https://github.com/Demeterio/Mod-Update-Checker)                  |
| Registry Pull Requests | [View proposed registry changes](https://github.com/Demeterio/Mod-Update-Checker_registry/pulls) |
| Creator website        | [Demeterio on Tumblr](https://demeterio.tumblr.com/)                                             |

## What the registry contains

The generated registry contains public update metadata such as:

* a stable mod identifier;
* a release channel;
* the latest known version;
* a public release tag;
* the date on which the version information was checked.

The registry does not contain:

* player information;
* EA account information;
* save-game information;
* the contents of a player’s Mods folder;
* a list of installed mods;
* installed mod versions;
* gameplay information;
* analytics or advertising identifiers;
* authentication credentials.

The registry also does not provide arbitrary player-facing URLs.

Official update pages remain declared locally by each compatible mod’s integration package.

## Live registry document

The current generated registry is available here:

http://muc-registry.demeterio.cc/generated/registry-v1.json

The registry source, commit history, and proposed changes are publicly visible through GitHub.

## HTTP transparency

The live registry is served over HTTP:

```text
http://muc-registry.demeterio.cc/generated/registry-v1.json
```

The Python runtime included with The Sims 4 does not provide the native `_ssl` extension required by Python’s standard `ssl` module.

Because of this runtime limitation, the script mod cannot establish a normal Python HTTPS connection using the libraries bundled with the game.

MUC therefore retrieves the public registry through a dedicated HTTP endpoint.

This is a technical compatibility decision, not an attempt to hide the connection.

HTTP does not provide transport encryption or built-in response authentication. The registry contains only public version information, but its authenticity still needs to be verified.

For that reason, MUC is being designed to verify a cryptographic signature before using a retrieved registry document.

## Network restrictions

The MUC network client accepts only the configured registry request.

It is restricted to:

```text
Host: muc-registry.demeterio.cc
Port: 80
Path: /generated/registry-v1.json
```

The client rejects:

* HTTPS URLs;
* alternate domains;
* alternate ports;
* credentials embedded in URLs;
* query strings;
* URL fragments;
* alternate registry paths;
* redirects;
* compressed responses;
* unsupported transfer encodings;
* oversized responses;
* responses that are not JSON.

MUC does not attempt to bypass firewalls, privacy tools (e.g. ModGuard, Privacy Protector), security tools, network protection mods, or operating-system security settings.

If the request is blocked, the registry check simply stops and no additional data is retrieved.

## Registry signature

Cryptographic registry verification is enabled.

The live file is:

```text
generated/registry-v1.json
```

This file is a signed JSON envelope with exactly these fields:

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

Public verification material is published here:

```text
security/muc-registry-public-key.pem
security/muc-registry-public-key.sha256
```

The private key is stored only as an encrypted GitHub Actions secret. It is never committed, published, included with the mod, or provided to pull-request workflows.

MUC rejects the registry when:

* the signed envelope is missing or malformed;
* the signature schema, key ID, or algorithm is not trusted;
* the Base64 payload or signature is malformed;
* the payload was modified after signing;
* the signature does not match the embedded MUC public key;
* the inner registry schema or entries are invalid.

No detached `generated/registry-v1.json.sig` file is used.

## Contributing a mod entry

Registry changes will be submitted through GitHub Pull Requests.

The public contribution system will include:

```text
CONTRIBUTING.md
templates/mod-entry.template.json
schemas/mod-entry.schema.json
examples/
.github/pull_request_template.md
```

These resources will explain:

* how to create a registry entry;
* which fields are required;
* which values are accepted;
* how entries are validated;
* how to submit a Pull Request;
* how an existing entry can be updated.

Once public submissions are open, contributors will be able to:

1. read the contribution guide;
2. copy the JSON entry template;
3. validate the entry against the published schema;
4. review the example entries;
5. fork the repository;
6. create a branch for the entry;
7. commit the completed JSON file;
8. open a Pull Request.

Proposed changes can be reviewed publicly on the [Pull Requests page](https://github.com/Demeterio/Mod-Update-Checker_registry/pulls).

All submissions must pass automated schema and content validation before they can be merged.

## Generated files

The following file is generated from reviewed registry entries:

```text
generated/registry-v1.json
```

It should not be edited manually.

Once cryptographic signing is enabled, the following file will also be generated automatically:

```text
generated/registry-v1.json.sig
```

## Registry format

The generated registry uses schema version 1:

```json
{
  "schema": 1,
  "generated_at": "2026-07-20T12:05:00Z",
  "entries": [
    {
      "mod_id": "creator.mod_name.0123456789ABCDEF",
      "release_channel": "stable",
      "version": "1.1.0",
      "release_tag": "v1.1.0",
      "checked_at": "2026-07-20T12:00:00Z"
    }
  ]
}
```

The registry contains public version metadata only. It does not contain player information.

## Review existing changes

Registry activity can be inspected publicly:

* [Open Pull Requests](https://github.com/Demeterio/Mod-Update-Checker_registry/pulls)
* [Commit history](https://github.com/Demeterio/Mod-Update-Checker_registry/commits/main)
* [Generated registry source](https://github.com/Demeterio/Mod-Update-Checker_registry/blob/main/generated/registry-v1.json)

## Related project

The Mod Update Checker source code, XML examples, tests, and technical documentation are available here:

[github.com/Demeterio/Mod-Update-Checker](https://github.com/Demeterio/Mod-Update-Checker)

Additional information and creator updates are available here:

[demeterio.tumblr.com](https://demeterio.tumblr.com/)

## Disclaimer

Mod Update Checker is an unofficial fan-made project.

It is not affiliated with, authorized by, sponsored by, or endorsed by Electronic Arts or Maxis.

The Sims and all related names and trademarks belong to their respective owners.

## Copyright

Copyright © Demeterio.

Do not redistribute, copy, modify, or repackage this project without permission.
