# Security

## Standards

These security standards apply to all code in this project.

- No secrets, API keys, tokens, or credentials in source code or committed
  files. Environment variables (or a secret manager) are the only approved
  channel for runtime secrets.
- All external input is validated before use; rejection paths are tested.
- Dependencies are pinned to a tested baseline; vulnerability alerts are treated
  as high-priority debt.

## Component standards

One section per declared stack component, contributed by its library module:

<!-- ASSEMBLE:security -->

## Known gaps

Track gaps in `docs/QUALITY_SCORE.md` and promote remediation plans to
`docs/exec-plans/tech-debt-tracker.md`.
