# Core Beliefs

These are the agent-first operating principles for this project. They explain why the
rules in `AGENTS.md` exist. When a guideline feels arbitrary, the answer is here.

## 1. Behavior before implementation

Writing a Gherkin scenario or failing test before production code forces explicit
intent. It prevents speculative generality and gives the agent a falsifiable target.
A failing test is not a problem — it is the starting point.

## 2. The repository is the only source of truth

From the agent's point of view, anything that cannot be accessed in-context while
running effectively does not exist. Slack threads, Google Docs, verbal agreements, and
tribal knowledge are invisible to the system. If a decision, convention, or principle
matters, it belongs in a versioned markdown file the agent can read.

## 3. No live calls in automated tests

Live network, database, filesystem, and cloud calls in automated tests introduce
non-determinism, environment coupling, and slow feedback loops. Mock at the
application boundary. Integration tests that require live systems are explicitly
marked and run separately.

## 4. Documentation is part of the product

`README.md` and the `docs/` directory are not optional deliverables. They are updated
in the same task as the code change that makes them stale. Stale documentation is
a defect.

## 5. Prefer boring dependencies

Technologies with stable APIs, strong type support, and wide representation in
training data are easier for agents to reason about. Avoid opaque upstream behavior.
It is sometimes cheaper to implement a narrow, well-tested helper than to wrap a
library whose internals the agent cannot inspect or validate.

## 6. Enforce invariants mechanically, not by convention

Rules that matter are encoded in linters, type checkers, or structural tests — not
in prose that can be ignored. When a guideline becomes important enough to matter
on every PR, it becomes a lint rule with an agent-legible error message that includes
the remediation instruction.

## 7. Plans are first-class artifacts

For complex or multi-step work, create an execution plan in `docs/exec-plans/active/`
before implementation begins. A plan is a markdown file with the goal, approach, open
questions, and steps. It is checked in, visible to the agent on future runs, and moved
to `docs/exec-plans/completed/` when the work is done.

## 8. Quality debt is tracked and paid down continuously

Known gaps are recorded in `docs/exec-plans/tech-debt-tracker.md` and reflected in
`docs/QUALITY_SCORE.md`. Technical debt that is not tracked is debt that compounds
invisibly. Small continuous paydown beats infrequent large cleanups.
