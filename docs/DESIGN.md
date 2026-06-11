# Design

## Documentation principles

Documentation in this project is treated as a first-class artifact. It is maintained
by the same agent that makes the code change, in the same task, before the PR is
opened. See `docs/design-docs/core-beliefs.md` §4.

### When to update README.md

Update `README.md` in the same task whenever any of the following changes:

- Installation or bootstrap steps
- Commands for running, testing, linting, or type checking
- Project structure or major architectural boundaries
- Externally visible behavior, interfaces, or supported workflows
- Required environment variables, services, or credentials

Keep the README suitable for a GitHub repository: clear purpose, working setup
instructions, concise architecture overview, current quality commands, no stale
or contradictory sections.

### When to write an execution plan

Create a plan file in `docs/exec-plans/active/` before starting work when:

- The task requires more than three non-trivial implementation steps
- The approach involves a significant architectural change
- The correct approach is uncertain and options need to be weighed

Name the plan `YYYY-MM-DD-<short-description>.md`. Include: goal, approach, open
questions, and ordered steps. Move to `docs/exec-plans/completed/` when done.

### When to write a design doc

Create a file in `docs/design-docs/` when:

- A significant architectural decision is being made that future agents need to
  understand
- A trade-off was chosen that is not obvious from the code

Reference the design doc from `ARCHITECTURE.md` when it affects domain layering
or dependency rules. Add it to `docs/design-docs/index.md`.

### When to add a product spec

Create a file in `docs/product-specs/` when a new user-facing feature is being
implemented that has acceptance criteria that should survive refactors. Reference
the spec from the BDD feature file that covers it. Add it to
`docs/product-specs/index.md`.

## Change discipline

Keep changes small and traceable to the active behavior. Do not add frameworks,
infrastructure, or abstractions until tests justify them. If an assumption is made,
state it in the task summary.
