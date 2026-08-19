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

### Executing a scaffold's gates

`--baseline` runs commands that are declared inside the target scaffold. A scaffold
may have come from anywhere, so its content is treated as untrusted input:

- Commands are executed as an argument vector (`shell=False`), never as a shell
  string. Nothing read out of a scaffold is ever handed to a shell.
- A command containing shell syntax (`&&`, `||`, `;`, `|`, `>`, `<`, backticks, or
  `$(`) is reported and skipped rather than executed. There is no flag to override
  this — a gate that needs a shell should be split into gates that do not.
- Every gate runs under a timeout, so one command cannot hang the run.
- `--baseline --dry-run` prints the commands without executing any of them. It is
  the way to inspect a scaffold whose origin is not trusted.

Running `--baseline` is an explicit request to execute that scaffold's commands.
Point it at scaffolds you trust, and use `--dry-run` first when you do not.

### Dependencies

- Dependencies are pinned to exact versions (`==`) in `pyproject.toml`. The pins are
  the tested baseline: a version bump is a deliberate change that runs all quality
  gates before landing.
- Known vulnerability alerts are treated as high-priority debt. Track them in
  `docs/exec-plans/tech-debt-tracker.md` and address before shipping.

## Known gaps

Track gaps in `docs/QUALITY_SCORE.md` and promote remediation plans to
`docs/exec-plans/tech-debt-tracker.md`.
