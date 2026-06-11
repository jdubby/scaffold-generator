# Align validation and CLI failures with the documented contract

**Status:** Completed 2026-06-10
**Started:** 2026-06-10
**Debt item:** tech-debt-tracker.md → "Align validation and CLI failures with the
documented contract" (High). Stderr routing was completed 2026-06-10; this plan
covers the remaining scope.

## Goal

Bring the implementation up to the contract documented in `docs/SECURITY.md` and
`docs/RELIABILITY.md`:

1. **Schema-backed spec validation** — validate the parsed YAML against a JSON
   schema (the `jsonschema` dependency is already declared) instead of manual field
   checks. Failures surface as structured errors naming the offending field with a
   remediation hint. The schema also constrains `name` and component names to slug
   patterns so spec values are never usable as raw filesystem paths.
2. **Output-path writability preflight** — validate the output directory can be
   created (does not exist; nearest existing ancestor is writable) before any
   generation work begins.

## Approach

1. Extend the product spec: note schema-pattern rejection under AC-3 and add AC-6
   for unwritable output paths.
2. Add Gherkin scenarios: invalid component name is rejected (AC-3); unwritable
   output path fails before generation with no partial output (AC-6).
3. Bind new steps in `tests/step_defs/test_scaffold_generation.py`; show failures.
4. Add failing unit tests: schema validation in `test_spec.py` (bad component type,
   path-traversal name, non-slug project name), `ScaffoldWriter.preflight` in
   `test_writer.py`, CLI stderr routing for preflight failures in `test_cli.py`.
5. Implement minimum: JSON schema + error translation in `spec.py`;
   `ScaffoldWriter.preflight` in `writer.py`; CLI wiring (preflight after dest
   resolution, before resolve/assemble) in `cli.py`.
6. Quality gates, evaluator pass, update `docs/QUALITY_SCORE.md` and the tracker
   (mark item resolved), move this plan to completed.

## Out of scope

- Dependency pinning policy (separate Medium item).
- Migrating tests off live `tmp_path` writes (separate Medium item).
