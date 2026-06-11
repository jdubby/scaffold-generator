# Security

## Standards

These security standards apply to all code in this project.

### Secrets and credentials

- No secrets, API keys, tokens, or credentials in source code or committed files.
- Environment variables are the only approved channel for runtime secrets.
- `.env` files are excluded from version control via `.gitignore`.
- If a secret is accidentally committed, treat it as compromised immediately.

### Input validation

- The stack spec is validated against a JSON schema before any filesystem operation
  begins. Malformed or invalid specs are rejected with a clear error message.
- Component names from the spec are resolved only against the known module library —
  they are never used as raw filesystem paths or shell arguments.
- Output directory paths are validated to be writable before generation begins.
  The generator never writes outside the declared output directory.

### Dependencies

- Dependencies are pinned to exact versions (`==`) in `pyproject.toml`. The pins are
  the tested baseline: a version bump is a deliberate change that runs all quality
  gates before landing.
- Known vulnerability alerts are treated as high-priority debt. Track them in
  `docs/exec-plans/tech-debt-tracker.md` and address before shipping.

## Known gaps

Track gaps in `docs/QUALITY_SCORE.md` and promote remediation plans to
`docs/exec-plans/tech-debt-tracker.md`.
