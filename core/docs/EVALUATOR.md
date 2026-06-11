# Evaluation Protocol

When acting as evaluator, you are a **skeptical reviewer, not a cheerleader**.
Your job is to find what is broken or incomplete before the task is declared
done. Default to failing a criterion unless you have positive evidence it is met.
Do not identify a problem and then talk yourself into accepting it.

Run an evaluation pass after all quality gates pass and before declaring any
feature task complete. The generator and evaluator are the same agent when
working solo — the value is in the explicit mode switch: stop generating, read
this file, and re-examine the work as an adversary would.

## Criteria

Grade each criterion A–D using the definitions in `docs/QUALITY_SCORE.md`.
A task passes only if every criterion is **B or above**; otherwise the result is
FAIL and the task returns for revision.

### 1. Behavioral fidelity

Do the acceptance scenarios and the product spec's criteria actually pass
end-to-end? Probe: exercise the primary workflow for real — does it work, or does
it only appear to work because a test mocks the part that would fail in
production?

### 2. Boundary coverage

Are error paths, integration seams, and boundary conditions tested? Probe: for
each call to an external system, ask "what happens when this fails?" — if no test
answers that, the grade is C or below.

### 3. Architectural integrity

Does the change respect the layers and domain model in `ARCHITECTURE.md`? Probe:
look for business logic in the entry-point layer and imports that flow upward.

### 4. Code quality

Do all mechanical gates pass without suppressed rules? A suppression without a
documented reason is a C regardless of other results.

## Writing evaluation feedback

For each criterion below B, report: the **criterion** and grade, the precise
**observation** (file, line, test), and the **resolution** that would bring it to
B. Do not approve work and then add caveats.
