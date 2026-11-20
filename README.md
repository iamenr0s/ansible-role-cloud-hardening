[![Molecule](https://github.com/iamenr0s/ansible-role-cloud-hardening/actions/workflows/molecule.yml/badge.svg)](https://github.com/iamenr0s/ansible-role-cloud-hardening/actions/workflows/molecule.yml) ![Ansible Role](https://img.shields.io/ansible/role/d/iamenr0s/cloud_hardening) [![CodeFactor](https://www.codefactor.io/repository/github/iamenr0s/ansible-role-cloud-hardening/badge)](https://www.codefactor.io/repository/github/iamenr0s/ansible-role-cloud-hardening)

# Ansible Role: Cloud Hardening

> Standalone copy of `cloud_hardening` from the [iamenr0s.linux_hardening](https://github.com/iamenr0s/linux-hardening-collection) collection. Variables keep the collection-wide `linux_hardening_*` prefix.

Audit-first, deliberately small: two things on a cloud machine that are easy to get wrong and cheap to check. It never touches networking, never reboots and never calls a cloud API.

## What it checks

| Finding | Meaning | Remediation |
|---|---|---|
| `cloud-init ssh_pwauth` | cloud-init would enable SSH password login (`true/yes/on/1`) on the next instance | drop-in sets `false` |
| `cloud-init disable_root` | cloud-init would allow root login (`false/no/off/0`) | drop-in sets `true` |
| `cloud-init ssh_deletekeys` | host keys would be kept instead of regenerated per instance | drop-in sets `true` |
| `cloud-init stored user-data` | `/var/lib/cloud/instances/*/user-data*` readable by group or others (it often holds secrets) | `chmod go-rwx` |
| `AWS IMDSv2 required` | the metadata service answers a request **without a token** (IMDSv1 enabled), so any SSRF can read the instance role credentials | **reported only** (`fixable: false`) |

- cloud-init values are read the way cloud-init merges them: `/etc/cloud/cloud.cfg`, then `/etc/cloud/cloud.cfg.d/*.cfg` in name order, last assignment wins. A key that is **unset** is not a finding. Only an explicit bad value is.
- The drop-in is `/etc/cloud/cloud.cfg.d/99-linux-hardening.cfg` (sorts last), written only when something deviates, backed up if it changes.
- The AWS check is one HTTP GET to `169.254.169.254` with no token: `401` is compliant, `200` is a finding, no answer (blocked, IMDS disabled, not AWS) is **not** a finding. The fix lives in the EC2 API (`aws ec2 modify-instance-metadata-options --http-tokens required`), not on the machine, so the role only reports it. Provider is recognised from the DMI vendor/BIOS strings (`linux_hardening_cloud_provider: auto`); set `aws` to force or `none` to skip.
- Without cloud-init and without AWS the role says so and checks nothing.

## Safety
- cloud-init applies these keys **per instance**, so the running sshd is not touched. They matter for the next machine booted from this one (image, clone, rebuilt instance). If you rely on password login for such images, do not enable this role or override the keys.
- Instance user-data (`#cloud-config` passed at launch) can still override the drop-in; the role cannot see it.
- This role does not edit `sshd_config`. SSH settings stay owned by `ssh_hardening`; this only stops cloud-init from re-opening them.

## Modes
`audit` (default) is read-only and sets `linux_hardening_cloud_findings` (`key, expected, actual, fixable`). `remediate` needs `linux_hardening_confirm_remediation: true`; afterwards only fixable findings fail the run, so a still-enabled IMDSv1 is reported but does not fail it.

## Example
```yaml
- hosts: all
  roles:
    - role: iamenr0s.linux_hardening.cloud_hardening
      vars:
        linux_hardening_mode: remediate
        linux_hardening_confirm_remediation: true
```

## Verification
Container scenarios `default` (real `cloud-init` package; a weak config in odd spellings: quoted, commented, numeric; remediation; `cloud-init schema` accepts the drop-in; other files untouched; user-data modes; a local stand-in for the metadata service is audited as IMDSv1-open, IMDSv2-only and unreachable; then the no-cloud case), `audit` (read-only), `refuse`. Run on AlmaLinux 9, Debian 13, Ubuntu 24.04 and Fedora 44. CI runs the same.

## Rollback
Delete `/etc/cloud/cloud.cfg.d/99-linux-hardening.cfg` (or restore its backup). User-data permissions are not restored.

## Known gaps
- **No VM or real cloud test.** The metadata service is a stand-in HTTP server, never a real EC2 instance; provider auto-detection from DMI is untested on real AWS hardware.
- Only AWS is checked. Azure and GCP require a header on every metadata request (no v1/v2 distinction), so there is nothing equivalent to audit; metadata reachability by unprivileged users or containers is not checked.
- IMDS hop limit and the instance's `HttpEndpoint` setting are API-side and not visible from the host.
- Not tested on EL8/EL10; cloud-init versions older than the ones shipped on the tested distros are not exercised.
- No CIS mapping (the checks are ours).

CI & Release (maintainers)
----------------------------
A single workflow (`.github/workflows/molecule.yml`) runs lint and the full Molecule distro matrix on pushes to `main`, PRs, and `v*` tags. On `v*` tags, a `release` job publishes to Ansible Galaxy after all tests pass.

One-time setup:

```bash
# Galaxy publishing key (environment-scoped, get it from galaxy.ansible.com/ui/token)
gh secret set GALAXY_API_KEY --repo iamenr0s/ansible-role-cloud-hardening

# Code scanning notifications (Slack webhook URL; for Discord append /slack to the webhook URL)
gh secret set SECURITY_ALERT_WEBHOOK --repo iamenr0s/ansible-role-cloud-hardening
```

`.github/workflows/code-scanning-notify.yml` polls the code-scanning API every 6 hours and posts new or updated open alerts to that webhook (GitHub Actions cannot trigger on `code_scanning_alert` directly).

To release: tag a commit `vX.Y.Z` and push the tag — CI gates the Galaxy publish.

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for the
local pipeline commands and pull request checklist. This project follows the
[Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).

## Security

See [SECURITY.md](SECURITY.md) — GitHub private vulnerability reporting, no
public issues for security bugs.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

## License

This project is licensed under the [MIT License](LICENSE).

## Author Information

Author: iamenr0s

Galaxy: `iamenr0s.cloud_hardening`
