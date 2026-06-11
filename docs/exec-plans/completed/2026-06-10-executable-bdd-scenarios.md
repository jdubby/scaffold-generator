# Make scaffold-generation BDD scenarios executable

**Status:** Completed 2026-06-10
**Started:** 2026-06-10
**Debt item:** tech-debt-tracker.md → "Make scaffold-generation BDD scenarios executable" (High)

## Goal

Bind every scenario in `tests/features/scaffold_generation.feature` to executable
pytest-bdd step definitions so `pytest` collects and runs the acceptance criteria.

## Approach

1. Confirm green baseline (`pytest`, `ruff check`, `ruff format --check`, `mypy src tests`).
2. Add `tests/step_defs/test_scaffold_generation.py` binding all six scenarios via
   `pytest_bdd.scenarios()`. Steps drive the real CLI through `click.testing.CliRunner`
   with temp component-library and core-template directories.
3. Run the suite. Scenarios asserting stderr routing (AC-3 and the `--validate`
   rejection) are expected to fail: the CLI currently echoes errors to stdout.
   This is the documented-contract gap already tracked under "Align validation and
   CLI failures with the documented contract".
4. Per the delivery loop: add a failing unit test for stderr routing, then make the
   minimal CLI change (`click.echo(..., err=True)` on error paths) to satisfy it.
   The remaining scope of that debt item (schema-backed validation, output-path
   preflight) stays open and untouched.
5. Re-run all quality gates.
6. Update `docs/QUALITY_SCORE.md` (BDD grade + gap log), mark the debt item resolved,
   note partial progress on the validation-contract item, and move this plan to
   `docs/exec-plans/completed/`.

## Out of scope

- Schema-backed spec validation and output-path writability preflight (rest of the
  validation-contract debt item).
- Migrating existing unit tests off live `tmp_path` writes (separate Medium item).
  New step definitions follow the existing suite's `tmp_path` pattern for now.
