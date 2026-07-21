# Security Policy

## Supported Versions

Security support applies to the current public registry infrastructure.

| Version or component                       | Supported |
| ------------------------------------------ | --------- |
| Current `main` branch                      | ✅         |
| Live generated registry                    | ✅         |
| Current signing key `muc-registry-2026-01` | ✅         |
| Historical registry snapshots              | ❌         |
| Unmerged branches and pull requests        | ❌         |
| Forks or modified copies                   | ❌         |

Only the registry served from the official Mod Update Checker registry domain and generated from the current `main` branch is considered supported.

## Reporting a Vulnerability

Please do not open a public GitHub Issue for a security vulnerability.

Use the repository’s private vulnerability reporting feature:

1. Open the **Security** tab.
2. Select **Advisories**.
3. Select **Report a vulnerability**.

Security reports may include issues involving:

* registry signature verification;
* registry tampering or signature bypasses;
* GitHub Actions workflow security;
* accidental exposure of signing material;
* validation bypasses;
* unsafe handling of registry contributions;
* unauthorized modification of generated registry data.

Please include, when possible:

* a clear description of the issue;
* the affected file, workflow, or registry component;
* steps required to reproduce the issue;
* the expected and actual behavior;
* the potential security impact;
* any suggested mitigation or correction.

Do not include private keys, credentials, access tokens, personal information, or player data in a report.

I aim to acknowledge security reports within seven days. After an initial review, I will indicate whether the issue is accepted, requires additional information, or is not considered a security vulnerability.

Accepted vulnerabilities will be corrected privately when appropriate before public disclosure. Please allow reasonable time for investigation and remediation before publishing details.

## Public Issues

Regular bugs, registry entry corrections, documentation problems, and feature requests that do not involve a security risk may be submitted through the public GitHub Issues page.

## Scope

This security policy applies only to the official Mod Update Checker registry repository, its GitHub Actions workflows, its public signing material, and the generated registry document.

The Sims 4, third-party mods, external download providers, user-created forks, and unofficial copies are outside the scope of this policy.
