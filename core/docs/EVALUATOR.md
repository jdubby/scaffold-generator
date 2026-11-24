# Evaluation Protocol

When acting as evaluator, you are a **skeptical reviewer, not a cheerleader**.
Your job is to find what is broken or incomplete before the task is declared
done. Default to failing a criterion unless you have positive evidence it is met.
Do not identify a problem and then talk yourself into accepting it.

Run an evaluation pass after all quality gates pass and before declaring any
feature task complete. A separate agent or person can evaluate the change.
When working solo, stop implementing and review from the evidence.

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

## Review handoff

Keep one record per change in the pull request or a versioned task or execution
plan. Use synthetic fixtures and public-safe findings in a public record. Keep
raw local evidence in the root `.private-review/` directory. To share restricted
evidence with an authorized evaluator, use an access-controlled location.
Give the reviewer the handoff location and access to the referenced evidence.
Use the fields below. A link to a specific CI job or artifact is enough when it
identifies the command, revision and result.

**Implementer** — start the record when the new test first fails. Before handing
over, identify the exact version a reviewer can retrieve and exercise.

- **Acceptance criterion** — spec path and criterion, plus the scenario or test.
- **Reviewed revision** — commit SHA, or base SHA and an accessible patch that
  includes new files and identifies the exact changes under review.
- **Original failing run** — test command, assertion that failed for the expected
  reason, and a reference to the run and test-only revision or patch. If the
  original evidence is missing, record **sequence unverified**. Label a later
  reproduction as such. It shows what the test detects on the earlier code.

**Evaluator** — start from that revision, the spec and the project's instructions.
Record what you personally exercised and which results you inspected. If the
implementation changes during revision, repeat the affected checks and tie the
final gate results and verdict to the updated revision.

- **Review mode** — independent (another agent or person), or self-review
  (the implementer applying the rubric).
- **Workflow exercised** — setup or fixture, command or steps, expected behavior
  and observed outcome. Include enough detail for someone else to repeat it.
- **Gate results** — each declared command, outcome and evidence for the reviewed
  revision. Identify any missing result.
- **Grades** — give a concrete observation or evidence reference for every row.

| Criterion | Grade | Evidence |
| --- | --- | --- |
| Behavioral fidelity | | |
| Boundary coverage | | |
| Architectural integrity | | |
| Code quality | | |

- **Verdict** — PASS when all required gates pass and every grade is B or above.
  Otherwise record FAIL, the finding and what would resolve it. Carry any
  unverified process claims into the verdict so the next reader can see them.

## Assign a separate evaluator

1. **Prepare the handoff.** The implementer fills in their part of the review
   record above. Give the evaluator the repository, the exact revision, and a
   handoff they can open from a fresh session. Include setup or fixture details
   needed to exercise the acceptance criterion.
2. **Open a fresh agent session.** The project owner or agent host assigns the
   review to an agent that did not implement the change. A new chat in the
   same project is sufficient. The same model can serve in both sessions.
   Give the evaluator a stable checkout. For a committed change, one option is
   `git worktree add --detach ../project-review <commit-sha>` and opening the
   new session there. For an uncommitted change, apply the handoff's exact patch
   to its stated base in a separate checkout. Follow the project's setup there.
3. **Send the assignment.** Substitute the two placeholders in the prompt below.
   The evaluator returns its report to the person or agent coordinating the
   review, who adds it to the handoff.
4. **Close or revise.** A PASS completes evaluation for the reviewed revision.
   On FAIL, give the findings to the implementer. Hand the updated revision and
   prior findings back to the evaluator to verify the fixes, check the gate
   results on that revision, and issue a fresh verdict.

```text
Independently review <revision> using the handoff at <handoff>.
Confirm that the checkout matches the revision or base plus patch. If you cannot
access it or the evidence, identify what is missing before drawing conclusions.
Read AGENTS.md, docs/EVALUATOR.md, and the linked spec and acceptance scenario.
Inspect the change and exercise the primary workflow. Record what you observed
and which gate results you reran or verified for this revision. Use the review
handoff fields to return four grades with evidence and a PASS or FAIL verdict.
Label the review independent. Return findings to the implementer for any fixes.
```
