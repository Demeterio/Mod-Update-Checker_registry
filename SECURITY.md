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

- registry signature verification;
- registry tampering or signature bypasses;
- the human-readable catalogue or script injection;
- GitHub Actions workflow security;
- accidental exposure of signing material;
- validation bypasses;
- unsafe handling of registry contributions;
- unauthorized modification of deployed registry data.

Please include, when possible:

- a clear description of the issue;
- the affected file, workflow, endpoint, or registry component;
- steps required to reproduce the issue;
- the expected and actual behavior;
- the potential security impact;
- any suggested mitigation.

Do not include private keys, credentials, access tokens, personal information, or player data in a public report.

I aim to acknowledge security reports within seven days. After an initial review, I will indicate whether the issue is accepted, requires additional information, or is not considered a security vulnerability.

Accepted vulnerabilities will be corrected privately when appropriate before public disclosure. Please allow reasonable time for investigation and remediation.

## Public Issues

Public Issues are appropriate for ordinary, non-sensitive problems, including:

- incorrect registry information;
- broken public links;
- catalogue display problems;
- documentation corrections;
- non-security feature requests.

## Scope

This policy applies only to the official Mod Update Checker registry repository, its GitHub Actions workflows, its public signing material, the generated registry documents, and the public catalogue.

The Sims 4, third-party mods, external download providers, user-created forks, and unofficial copies are outside the scope of this policy.
