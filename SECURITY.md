# Security Policy

## Supported versions

Security reports are accepted for the latest code on the default branch. Alpha builds are not production hardened.

## Reporting a vulnerability

Please use GitHub's **Report a vulnerability** feature in the repository Security tab so sensitive details are not disclosed in a public issue.

Do not include API tokens, personal images, model cache contents, or private file paths in public bug reports.

## Privacy and local processing

PortraitCut AI is designed to process user-selected images locally. The application may download model files from Hugging Face on first use. User image contents are not intended to be uploaded. Network access should be limited to model downloads and explicitly initiated update checks.

## Maintainer checklist

- Never commit .env files, tokens, private keys, personal photos, local model caches, or logs.
- Rotate any credential that has ever been committed; deleting the current file does not invalidate leaked credentials.
- Review model remote code before allowing trust_remote_code=True.
- Keep dependency alerts, secret scanning, push protection, and code scanning enabled where available.
