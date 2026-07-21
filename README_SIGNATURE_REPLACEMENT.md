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
