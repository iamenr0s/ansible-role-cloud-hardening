# Changelog

## Unreleased
- Change: cloud-init configuration is parsed as YAML (merged like cloud-init does) instead of matched with regular expressions; a drop-in that is not valid YAML now fails the audit.
- Internal: the audit is one task per check, and the fail decision is two named tasks.
- Change: dropped the `linux_hardening_mode` assert that repeated `meta/argument_specs.yml` (which already rejects other values).
- Fix: `--check` reported no IMDSv1 finding (the metadata GET was skipped), and the post-remediation re-audit failed; both fixed.
- Fix: `linux_hardening_cloud_provider: auto` silently became `none` with `gather_facts: false`; the role now gathers the hardware facts it needs.
- Security: the cloud-init config read is `no_log` (it can hold passwords).
- Change: task names in sub-task files are prefixed.
- Test: the default scenario installs `python3-jsonschema`, so `cloud-init schema` validates instead of skipping.
- Docs: README adds a Role Variables table, the example uses the standalone role name with `become: true`, idempotency and check-mode notes.
- Test: the default Molecule scenario runs a `check` (dry-run remediate) step first.
- CI: every platform in `meta/main.yml` gates the release (no `continue-on-error` legs); lint runs the pinned pre-commit hooks; pre-commit adds gitleaks; actions are pinned by commit SHA; the release uses `ansible-galaxy role import` like the sibling roles.

## 1.0.0
- Split out of the iamenr0s.linux_hardening collection; no functional change.
