# Evaluation Protocol

When acting as evaluator, you are a **skeptical reviewer, not a cheerleader**.
Your job is to find what is broken or incomplete before the task is declared done.
Default to failing a criterion unless you have positive evidence it is met.
Do not identify a problem and then talk yourself into deciding it is acceptable.

## When to run an evaluation pass

Run an evaluation pass after all quality gates in `AGENTS.md` pass and before
declaring any feature task complete. For complex tasks tracked in
`docs/exec-plans/active/`, run an evaluation pass at each milestone in the plan,
not just at the end.

The generator and evaluator are the same agent when working solo. The value of
this protocol is in the **explicit mode switch**: stop generating, read this file,
and re-examine the work as an adversary would.

## Criteria

Grade each criterion A–D using the definitions in `docs/QUALITY_SCORE.md`.
A task passes evaluation only if every criterion is **B or above**.
If any criterion is C or D, the evaluation result is **FAIL**: return detailed,
actionable feedback and do not mark the task done.

---

### 1. Behavioral fidelity

Does the implementation match the BDD scenarios in `tests/features/` and the
acceptance criteria in the corresponding product spec in `docs/product-specs/`?

| Grade | Condition |
|-------|-----------|
| A | All scenarios pass. Every acceptance criterion in the spec is exercisable. Nothing is stubbed or hardcoded. |
| B | All scenarios pass. One minor edge case from the spec is absent and recorded in the gap log. |
| C | One or more scenarios fail, or a feature exists as a stub with no real behavior behind it. |
| D | The primary acceptance criterion cannot be exercised at all. |

Probe: attempt to exercise the primary workflow end-to-end. Does it actually work,
or does it appear to work because the test mocks the part that would fail in production?

---

### 2. Boundary coverage

Are error paths, integration seams, and boundary conditions tested?

| Grade | Condition |
|-------|-----------|
| A | Every external dependency has at least one failure-path test. All public inputs are validated and their rejection paths are tested. |
| B | All critical failure paths covered. One minor gap identified and recorded in the gap log. |
| C | Happy-path tests only. Failure paths for one or more external dependencies are absent. |
| D | Unchecked exceptions propagate to the caller, or external calls have no error handling at all. |

Probe: for each function that calls an external system, ask "what happens when this
call fails?" If there is no test that answers that question, the grade is C or D.

---

### 3. Architectural integrity

Does the implementation respect the layer boundaries and domain model defined
in `ARCHITECTURE.md`?

| Grade | Condition |
|-------|-----------|
| A | No cross-layer violations. Domain concepts match the vocabulary in the product spec. No business logic in the CLI layer. |
| B | One minor violation, tracked in the gap log, not on a critical path. |
| C | Business logic present in the CLI layer, or a domain concept diverges from the spec vocabulary without explanation. |
| D | Fundamental inversion: lower layer imports from higher layer, or filesystem I/O scattered across multiple modules. |

Probe: read the CLI module. Does it contain conditional domain logic? If yes, the grade is C.

---

### 4. Code quality

Do all mechanical gates pass and is the code readable to a skeptical reviewer?

| Grade | Condition |
|-------|-----------|
| A | All gates green (`pytest`, `ruff check`, `ruff format --check`, `mypy`). No suppressed rules. Public interfaces have docstrings. No dead code. |
| B | All gates green. One or two minor readability issues noted in the gap log. |
| C | Any gate is failing, or `# type: ignore` / `# noqa` used without a documented reason in a comment. |
| D | Multiple suppressed checks, or a gate is bypassed rather than fixed. |

Probe: run all four gates. Do not accept partial green. A `# type: ignore` with no
accompanying explanation is a C regardless of other gate results.

---

## Writing evaluation feedback

When a criterion is C or D, your feedback must be structured as:

1. **Criterion** — which one failed and what grade.
2. **Observation** — the specific behavior, file, line, or test that surfaced the failure.
   Be precise: vague feedback cannot be acted on.
3. **Resolution** — a concrete description of the state that would bring the grade
   to B or above.

**Do not approve work and then add caveats.** If any criterion is below B, the
evaluation result is FAIL and the task returns for revision before it can be closed.
