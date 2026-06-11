# Reliability

## Standards

These reliability standards apply to all production code in this project.

- All error paths are tested. Every external dependency has at least one
  failure-path test.
- Errors propagate explicitly — no silent catches that swallow failures.
- User-facing errors carry enough context to diagnose the problem without log
  access.
- External dependencies sit behind interfaces that test doubles can substitute.

## Component standards

One section per declared stack component, contributed by its library module:

<!-- ASSEMBLE:reliability -->

## Known gaps

Track gaps in `docs/QUALITY_SCORE.md` and promote remediation plans to
`docs/exec-plans/tech-debt-tracker.md`.
