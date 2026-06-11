# Agent Workflow

## Core mandate

Behavior first, tests second, implementation third. Do not write or modify
production code until the expected behavior is defined and at least one failing
automated test exists for the next increment.

## Delivery loop

1. **Spec** — check `docs/product-specs/` for a spec covering the work. If none
   exists, write one before any scenario or code.
2. **BDD** — write or update an acceptance scenario before implementation begins.
3. **TDD** — write one failing unit test. Run the suite and show the failure.
4. **Implement minimum** — only enough code to make the active failing test pass.
5. **Refactor** — clean up only after the suite is green.
6. **Quality gates** — run every gate this project defines (test runner, linter,
   formatter, type checker). All must pass.
7. **Evaluate** — apply `docs/EVALUATOR.md` before marking the task complete.

## Repository map

| What | Where |
|------|-------|
<!-- ASSEMBLE:agents -->

## Knowledge base

The `docs/` directory is the system of record. Pull in context before starting
non-trivial work. Anything not in the repository is invisible to the agent.

| Context                        | Location                               |
|--------------------------------|----------------------------------------|
| Agent-first principles         | `docs/design-docs/core-beliefs.md`     |
| Architecture and layers        | `ARCHITECTURE.md`                      |
| Product specs (feature scope)  | `docs/product-specs/`                  |
| Quality grades by domain       | `docs/QUALITY_SCORE.md`                |
| Evaluation protocol            | `docs/EVALUATOR.md`                    |
| Known technical debt           | `docs/exec-plans/tech-debt-tracker.md` |
| Documentation principles       | `docs/DESIGN.md`                       |
| Reliability standards          | `docs/RELIABILITY.md`                  |
| Security standards             | `docs/SECURITY.md`                     |

## Mocking rules

- No live network calls or subprocess invocations in unit tests.
- Mock at application boundaries; give each external dependency an interface a
  test double can substitute.
- Every external boundary needs at least one failure-path test.

## README maintenance

`README.md` is part of the product. Update it in the same task whenever setup,
commands, structure, or visible behavior changes.

## Change discipline

Do not add frameworks, infrastructure, or abstractions until tests justify them.
State assumptions in task summaries. Keep this file under 120 lines — it is a
navigator pointing into `docs/`, not a manual.
