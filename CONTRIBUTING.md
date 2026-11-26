# Contributing to PortraitCut AI

Thank you for considering a contribution.

## Before opening a pull request

- Keep user photos, personal data, local model caches, model weights, logs, credentials and private configuration out of Git.
- Use synthetic or properly licensed sample assets in tests and documentation.
- Do not commit `.env`, API tokens, passwords, private keys, or local machine paths.
- Run the CPU-safe tests with `python -m pytest -q`.
- Describe behavior changes and include tests where practical.
- Do not change pinned model revisions or dependency versions without documenting compatibility and validating the inference path.

## Repository security for maintainers

- Keep Dependabot, secret scanning, push protection and CodeQL enabled where available in GitHub repository security settings.
- The Gitleaks workflow scans Git history. A clean scan does not prove that no secret was ever exposed; rotate any credential that may have been committed.
- Review the complete diff and generated files before merging.
- Do not upload private user photos or model caches into public issues or pull requests.

## Licensing contributions

By intentionally submitting a contribution for inclusion, you agree that it is submitted under the repository's Apache License 2.0, unless you and the project owner have a separate written agreement.

Do not submit third-party code, model weights, datasets, images or documentation unless you have verified that the project may use and redistribute them under compatible terms. Preserve required copyright, license and attribution notices.

## Scope

The separate white-background JavaScript utility is not currently part of this repository. Do not copy it into the project until its source, provenance and license have been reviewed.
