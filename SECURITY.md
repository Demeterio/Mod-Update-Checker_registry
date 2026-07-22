# Security Policy

## Supported components

Security support applies to the current official public registry infrastructure.

| Version or component | Supported |
| --- | --- |
| Current `main` branch | ✅ |
| Live signed player registry | ✅ |
| Human-readable registry and catalogue | ✅ |
| GitHub Actions validation and publication workflows | ✅ |
| Current signing key `muc-registry-2026-01` | ✅ |
| Historical deployment artifacts | ❌ |
| Unmerged branches and Pull Requests | ❌ |
| Forks or modified copies | ❌ |

Only the registry and catalogue served from the official Mod Update Checker registry domain and generated from the current `main` branch are considered supported.

## Reporting a vulnerability

Do not open a public GitHub Issue or Pull Request for a security vulnerability.

Use the repository's private vulnerability reporting feature:

1. Open the **Security** tab.
2. Select **Advisories**.
3. Select **Report a vulnerability**.

Security reports may include issues involving:

- registry signature or freshness verification;
- replay of an old signed registry;
- registry tampering or signature bypasses;
- the human-readable catalogue or script injection;
- GitHub Actions workflow security;
- accidental exposure of signing material;
- validation bypasses;
- unsafe handling of registry contributions;
- unauthorized modification of deployed registry data.

Please include, when possible, a clear description, the affected component, reproduction steps, expected and actual behavior, potential impact, and suggested mitigation.

Do not include private keys, credentials, access tokens, personal information, or player data in a public report.

I aim to acknowledge security reports within seven days. Accepted vulnerabilities will be corrected privately when appropriate before public disclosure.

## Signing-key handling

The production private key is stored only as an encrypted GitHub Actions secret. It must never be committed, uploaded as an artifact, printed in logs, copied into a Pull Request, or distributed with MUC.

The committed public key and fingerprint are intentionally public:

```text
security/muc-registry-public-key.pem
security/muc-registry-public-key.sha256
```

Pull Request workflows use an ephemeral test key and never receive the production private key.

## Signing-key rotation procedure

Key rotation must be coordinated with a MUC release because the game mod embeds the trusted public-key material and key ID.

Planned rotation procedure:

1. Generate the replacement private key in a controlled environment.
2. Store the replacement private key only in an encrypted GitHub Actions secret.
3. Derive and review the replacement public key, fingerprint, and a new unique `key_id`.
4. Publish a MUC version that trusts the replacement key before the registry switches to it.
5. Keep the registry signed with the old key during the client-update window.
6. Switch the publication workflow to the replacement secret, public key, fingerprint, and `key_id` only after the compatible MUC release is available.
7. Verify the first new signed deployment independently.
8. Revoke and securely destroy the old private key when the migration is complete.
9. Update this policy and public documentation with the active key ID.

The current MUC release trusts one active registry key. Therefore, an emergency key compromise may require temporarily stopping publication until an updated MUC build and replacement registry can be released. The compromised key must never be reused.

## Public Issues

Public Issues are appropriate for ordinary, non-sensitive problems, including incorrect registry information, broken public links, catalogue display problems, documentation corrections, and non-security feature requests.

## Scope

This policy applies only to the official Mod Update Checker registry repository, its GitHub Actions workflows, its public signing material, generated registry documents, and public catalogue.

The Sims 4, third-party mods, external download providers, user-created forks, and unofficial copies are outside the scope of this policy.
