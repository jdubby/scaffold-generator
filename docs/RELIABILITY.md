# Reliability

## Standards

These reliability standards apply to all production code in this project.

### Error handling

- All error paths are tested. Every external dependency has at least one failure-path
  test.
- Errors propagate explicitly — no silent catches that swallow failures.
- User-facing errors carry enough context to diagnose the problem without log access.
- Do not use bare `except Exception` without re-raising or structured handling.

### External dependencies

- Filesystem reads (spec files, component modules, core templates) are wrapped behind
  interfaces that can be substituted in tests.
- Schema validation failures surface as structured errors with the offending field
  and a remediation hint, not a raw exception traceback.
- Unknown components produce a placeholder and a warning — they never raise an
  unhandled exception.

### Test coverage targets

| Layer                         | Target                                              |
|-------------------------------|-----------------------------------------------------|
| Spec loader (business logic)  | 100% branch coverage                                |
| Resolver                      | 100% branch coverage including placeholder path     |
| Assembler                     | 100% branch coverage for each assembly rule         |
| Writer                        | Critical paths via BDD scenarios                    |
| CLI                           | Primary workflows covered by BDD scenarios          |

### Observability

- CLI errors are printed to stderr with enough context to identify the offending spec
  field or missing file.
- Warnings (unknown components) are printed to stdout, clearly distinguishable from
  errors.
- No logging of filesystem paths that contain user secrets or credentials.

## Known gaps

Track gaps in `docs/QUALITY_SCORE.md` and promote remediation plans to
`docs/exec-plans/tech-debt-tracker.md`.
