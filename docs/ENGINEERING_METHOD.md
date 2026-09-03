# The engineering method

Scaffold Generator installs a reusable engineering method into a project
repository. It gives a coding agent a defined way to understand a task, implement
it, verify it, and leave useful context for the next contributor.

You choose a technology stack. The generator combines a shared delivery process
with the selected components' engineering rules and quality commands. You can
also supply product requirements, acceptance scenarios, execution plans, and a
domain map through a scaffold package.

The result is a starting point for disciplined agent-assisted development.
Application code, project-specific tests, and deployment configuration still need
to be built. The generator assembles pre-authored files without calling a language
model; your coding agent performs the subsequent development work.

## Who this is for

The method is intended for developers and teams that want consistent working
practices across agent sessions and projects. It is particularly useful when:

- Several projects should share the same development and review expectations.
- Requirements and decisions need to survive changes of agent or contributor.
- A technology stack needs concrete architecture, security, and reliability rules.
- Completion needs to be supported by tests and reviewable evidence.

Adopting it means maintaining the repository's specifications and documentation,
writing tests before production implementation, and revising work that fails
evaluation. These are ongoing responsibilities for the agent and its human
collaborators.

## What arrives in your repository

The table describes output from the bundled templates. Links point to the source
templates so you can inspect the actual instructions before generating a project.

| Generated artifact | What you get |
| --- | --- |
| [`AGENTS.md`](../core/AGENTS.md) | The delivery loop, exact component quality commands, repository navigation, mocking rules, and change discipline. |
| [`ARCHITECTURE.md`](../core/ARCHITECTURE.md) | Selected components' responsibilities and guidance, dependency rules, and a domain map to complete or import. |
| [`docs/product-specs/index.md`](../core/docs/product-specs/index.md) | A specification template and index for goals, scope, acceptance criteria, and open questions. |
| [`docs/EVALUATOR.md`](../core/docs/EVALUATOR.md) | A skeptical review protocol with four criteria and a threshold for accepting work. |
| [`docs/SECURITY.md`](../core/docs/SECURITY.md) and [`docs/RELIABILITY.md`](../core/docs/RELIABILITY.md) | Shared standards plus rules contributed by the selected components. |
| [`docs/DESIGN.md`](../core/docs/DESIGN.md) and [`docs/design-docs/core-beliefs.md`](../core/docs/design-docs/core-beliefs.md) | Documentation responsibilities and the reasoning behind the method. |
| [`docs/QUALITY_SCORE.md`](../core/docs/QUALITY_SCORE.md) and [`docs/exec-plans/tech-debt-tracker.md`](../core/docs/exec-plans/tech-debt-tracker.md) | Initially ungraded quality records and a place to track deficiencies and remediation. |
| [`ci.yml`](../core/ci.yml) | CI configuration assembled from shared and component jobs, including unfinished gates that deliberately fail until configured. |
| [`README.md`](../core/README.md) | A starting structure for project purpose, setup, commands, and contributor guidance. |

The scaffold also provides `tests/features/` and `docs/exec-plans/active/`.
A plain stack specification does not invent product requirements, feature
scenarios, or an execution plan. A supplied package can populate those locations;
its product specs are indexed and its domain-map rows are merged into the
architecture document. See [package import](../README.md#importing-a-scaffold-package).

This guide explains the method to visitors to the generator repository. The
generated `AGENTS.md` and supporting documents carry the working instructions
into each new project. This guide itself is not copied into generated projects.

## How an agent is expected to work

Before non-trivial work, the agent reads the relevant repository context. The
generated `AGENTS.md` is a short navigator into that context, with a 120-line
limit checked by the generator. Specifications explain the intended behavior;
architecture and standards constrain how it is implemented.

The bundled workflow then requires this sequence:

| Step | Expected action | What makes progress reviewable |
| --- | --- | --- |
| 1. Specify | Find a product spec covering the work. If none exists, write one before a scenario or code. | A goal, scope, acceptance criteria, and explicit open questions. |
| 2. Describe acceptance behavior | Write or update an acceptance scenario before implementation. | An observable outcome grounded in the spec. This is behavior-driven development, or BDD. |
| 3. Demonstrate a failing test | Write one failing unit test, run the suite, and show the failure. | Evidence that the test detects the missing behavior. This starts test-driven development, or TDD. |
| 4. Implement the minimum | Write enough production code to make the active test pass. | A small change tied to the behavior being developed. |
| 5. Refactor | Clean up after the suite is green. | Improved structure while existing behavior stays covered. |
| 6. Run quality gates | Run every command listed in the generated quality-gates section. All must pass. | Results from the stack's declared checks. |
| 7. Evaluate | Apply `docs/EVALUATOR.md` before declaring the feature complete. Revise work that fails. | A judgment about behavior, boundaries, architecture, and code quality. |

This sequence is an instruction to the agent, not an automatically scheduled
workflow. The generator does not run the development loop, collect its history,
or prove that a test failed before the implementation was written.

## What changes with the technology stack

The shared delivery process remains the same. Each component adds six fragments:
architecture, reliability, security, repository navigation, CI, and quality-command
declarations. The authoring guide requires concrete, checkable rules.

For example:

- **FastAPI** keeps business logic in services, validates requests, puts
  authentication and authorization in dependencies, and requires timeouts and
  failure-path tests for downstream calls.
- **PostgreSQL** requires parameterized queries, separate application and migration
  privileges, and tenant-isolation checks where applicable.
- **Next.js** defaults to server components and asks the agent to make client
  boundaries explicit.

The component file named `agents.md` contributes one repository-map row. Most of
the substantive component instructions are assembled into `ARCHITECTURE.md`,
`docs/SECURITY.md`, and `docs/RELIABILITY.md`. Following those references is part
of using the method.

Component `checks.yml` files declare commands that appear in the generated
`AGENTS.md`; identical command strings are listed once. Some components declare
no gates of their own and need project-specific checks. A selected component that
has no library module produces marked placeholders for the team to complete.

See [the component library and authoring contract](../components/MODULE_AUTHORING.md).
Assembly combines the supplied guidance; it does not prove that every possible
combination of components is compatible.

## How completion is evaluated

Passing the quality commands is followed by a separate review step. The evaluator
is instructed to seek positive evidence and investigate gaps in four areas:

| Criterion | Question the agent must answer |
| --- | --- |
| Behavioral fidelity | Does the primary workflow satisfy the spec and acceptance scenarios when exercised end to end? Could a mock be hiding the failure? |
| Boundary coverage | Are error paths, integration seams, external-dependency failures, and boundary conditions tested? |
| Architectural integrity | Does the change respect the project's layers, domain model, and dependency direction? |
| Code quality | Do the mechanical gates pass, and are any rule suppressions justified? |

Each criterion receives an A–D grade using the generated quality-score
definitions. All four must be B or above. A lower grade requires a precise
observation and a resolution that would bring the work to the threshold; the
agent returns to revision before marking the feature complete.

The same agent may implement and evaluate. The template makes the switch of role
explicit, but this remains self-review unless another reviewer is involved.
Grades are judgments supported by evidence, not independently certified scores.

## An example of the method in use

Suppose a FastAPI/PostgreSQL application needs a customer to view an order they
own. This is an illustration of the workflow, not an application bundled with
the generator.

1. **Define the behavior.** The product spec explains who can view an order, what
   is returned, and how missing or unauthorized orders should be handled.
2. **Describe acceptance.** Write scenarios for the owner viewing the order and
   another customer being unable to view it.
3. **Start with a failing unit test.** Test the first service behavior using a
   substitute for the data-access boundary. Run it and observe the intended
   failure.
4. **Implement and refactor incrementally.** Keep the HTTP handler thin and apply
   the component rules for access control and database queries. Repeat for the
   remaining behavior and failure paths.
5. **Verify the boundaries.** Exercise the relevant HTTP and database integration
   in a test environment. Unit-test doubles alone cannot demonstrate that tenant
   isolation works in the real query path.
6. **Run gates and evaluate.** Run the declared commands, then check the complete
   behavior against the spec and standards. Resolve missing evidence or defects
   before declaring completion.
7. **Preserve context.** Update the documentation affected by the change and
   record any remaining minor gaps and follow-up work.

The method connects the product requirement, component rules, implementation,
and completion evidence throughout the task.

## What is checked, and what depends on people and agents

| Mechanism | Current scope |
| --- | --- |
| Spec and module validation | Rejects invalid stack specs and missing or invalid required module content handled by the generator. |
| Scaffold contract checks | Warns about missing required paths, unresolved assembly markers, an oversized `AGENTS.md`, malformed CI YAML, and steps containing only recognized no-op commands. |
| Gate-to-CI comparison | Warns when a declared command's text is absent from the component's CI fragment. This does not prove that CI executes the command. |
| Gate baseline | Runs the commands parsed from the generated `AGENTS.md` and reports passed, failed, unavailable, skipped, or timed-out outcomes. It does not assess test quality. |
| Agent instructions and evaluator | Depend on the agent reading and following them, and on the evidence being reviewed. They are not enforced by the generator's execution. |

Contract warnings do not fail generation. Baseline outcomes do not cause a
nonzero exit status; inability to read the target does. A failed gate may indicate
missing behavior or missing setup, and a passed gate may or may not cover useful
behavior. Review the cause and coverage.

The method is intended to improve consistency and verifiability. The repository's
generator tests do not establish a measured improvement in agent adherence,
application quality, or development speed.

## Starting a project with the method

1. **Choose the stack and provide product context.** Use a stack spec or import
   a package with the requirements, scenarios, plans, and domain map you already
   have. Follow the [generation instructions](../README.md#what-it-does).
2. **Review the generated guidance.** Complete relevant placeholders, define the
   actual code layout and architecture, and resolve incompatible assumptions
   before implementing affected features.
3. **Configure your agent to read it.** Ensure your chosen tool loads `AGENTS.md`
   and can follow its references. Instruction loading varies by tool; generation
   does not configure every agent integration.
4. **Establish the development environment and checks.** Create the application
   structure, dependencies, test tooling, and configuration. Adapt command paths
   to the real layout and keep the instructions and CI commands aligned. Review
   commands with `scaffold --baseline ./my-project --dry-run` before running them.
5. **Activate CI.** For GitHub Actions, place the generated `ci.yml` under
   `.github/workflows/`. Configure the jobs and replace deliberate `exit 1`
   placeholders with meaningful project checks. The root-level file is not an
   active GitHub Actions workflow by itself.
6. **Deliver the first increment using the loop.** Maintain project documentation
   alongside implementation and use the evaluator before calling the feature done.

The current bundled method uses one general delivery loop; it does not provide
separate workflows for every task type. Teams must decide how to adapt it when
adopting it. Changes to generated instructions become that project's maintained
method.

Generation requires a new output directory. Updates to the generator's templates
are not automatically propagated to existing projects. The surrounding SDLC
still supplies product decisions, source-control review, deployment, monitoring,
and incident response. The scaffold supplies the working instructions and records
that connect development decisions to those activities.
