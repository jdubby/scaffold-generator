# Scaffold Generator

Packages a reusable engineering method for coding agents into a project repository.
Choose a technology stack in YAML and receive agent instructions, architecture and
engineering standards, quality-check commands, and a structured home for product
requirements and project knowledge.

The method asks an agent to define behavior, demonstrate a failing test, implement
in small increments, run the project's checks, and critically evaluate the result
before declaring the work complete. Shared instructions and pre-authored component
modules keep that process consistent across supported stacks.

**Start with [The engineering method](docs/ENGINEERING_METHOD.md)** to understand
what you get, how an agent is expected to work, and what you need to configure.
The generated scaffold supplies the working process and supporting files;
application code and project-specific tests still need to be built.

## The method you get

- **A delivery loop:** spec → acceptance scenario → failing unit test → minimum
  implementation → refactor → quality gates → evaluation.
- **Project context:** a short `AGENTS.md` directs the agent to requirements,
  architecture, standards, and known gaps maintained in the repository.
- **Stack-specific rules:** selected modules contribute architecture, security,
  reliability, repository locations, and quality commands.
- **A completion standard:** the evaluator checks behavior, boundaries,
  architecture, and code quality; any criterion below B sends the work back for
  revision.

These instructions guide an agent that reads and follows them. The generator
checks scaffold structure and selected gate properties; it does not supervise
the agent or certify the resulting application.

## What it does

```bash
scaffold spec.yml -o ./my-project
```

Reads `spec.yml`, resolves each declared component to a module in the component
library, and assembles a complete scaffold in the directory given by `-o`/`--output`.
Unknown components produce clearly-marked placeholder sections rather than failing.

The repo bundles the component library (`components/`) and the stack-agnostic
core templates (`core/`), used by default when `--components-dir`/`--core-dir`
are not given. Bundled modules: react-native and nextjs (frontend), fastapi and
python-cli (backend), firebase and postgres (database), pytorch (inference). To add a
module, see `components/MODULE_AUTHORING.md`.

```bash
scaffold --list-components     # available modules by category, with gate counts
scaffold --validate spec.yml   # validate a spec without generating output
```

Generated output is contract-checked before the command finishes. Findings print as
warnings and never change the exit code: a missing required file, an unresolved
assembly marker, an `AGENTS.md` over its line limit, or a `ci.yml` gate that cannot
fail. A module missing a required fragment, or shipping a malformed one, is an error
instead — the command names the module and the field, and writes nothing.

## Quality gates

Each component module declares its gate commands as data in a `checks.yml` fragment:

```yaml
gates:
  - name: lint
    run: ruff check .
  - name: test
    run: pytest
```

Those commands are assembled into the **Quality gates** section of the generated
`AGENTS.md`, grouped by component, so the delivery loop's gate step names exactly what
to run. A command two components share is listed once. A module whose checks are
inherently project-specific declares `gates: []`, which states "none of my own"; an
absent fragment is an incomplete module and fails generation.

A module that declares a gate its own `ci.yml` never runs is reported as a warning —
the declaration and the CI job are meant to be one source of truth.

### Checking that the gates run

```bash
scaffold --baseline ./my-project            # run that scaffold's declared gates
scaffold --baseline ./my-project --dry-run  # print the commands, run nothing
```

`--baseline` runs the gates a generated scaffold declares and classifies each one:

| Outcome | Meaning |
|---------|---------|
| `passed` | The command exited 0. |
| `failed` | The command exited non-zero, with its summary line. |
| `unavailable` | The command is not installed on this machine. |
| `skipped` | The command contains shell syntax, so nothing ran. |
| `timed out` | The command exceeded the per-gate timeout. |

Use the baseline to inspect what the scaffold's commands actually do. A **failed**
gate can expose missing implementation, but can also mean configuration or
dependencies are missing. A **passed** gate may be legitimate, or may cover no
meaningful behavior yet. An **unavailable** gate names tooling the stack still
needs. Inspect the reason and coverage before treating any outcome as evidence
of application quality.

Baseline is a diagnostic, not a gate of its own: it exits zero whatever the outcomes
were, and non-zero only when the target cannot be read.

Gate commands are executed as an argument vector, never through a shell, and a command
containing shell syntax is skipped rather than executed. Use `--dry-run` to inspect a
scaffold whose origin you do not trust. See `docs/SECURITY.md`.

## Importing a scaffold package

Upstream tools (e.g. product-laboratory) export a *scaffold package*: a
directory holding a `stack-spec.yml` plus content files — product specs, exec
plans, Gherkin feature files, a domain map — already laid out at their final
scaffold-relative paths. Pass the package directory instead of a spec file:

```bash
scaffold ./snapsell-scaffold -o ./snapsell
```

This generates the scaffold from the package's spec, then overlays the content
files into the output, creating directories as needed. Two files get special
treatment:

- files under `docs/product-specs/` are also added to the index table in
  `docs/product-specs/index.md`;
- `docs/domain-map.md` is consumed — its table rows are merged into the
  **Domain map** section of `ARCHITECTURE.md` instead of the file being copied.

`stack-spec.yml` itself and hidden files (`.DS_Store`) are not copied. The
command ends with a summary of everything it placed.

## Spec format

A stack spec is a small YAML file. A complete, runnable example ships at
[`examples/stack-spec.yml`](examples/stack-spec.yml):

```yaml
name: vocal-app        # required — plain slug; default output directory name
platform: mobile       # required — one of: mobile, web, hybrid, backend
frontend:              # each category is an optional list of module names
  - react-native
backend:
  - fastapi
database:
  - firebase
# inference: []        # empty categories may be omitted entirely
```

Rules, enforced by JSON-schema validation before any generation work:

- `name` and `platform` are required; the four category keys (`frontend`,
  `backend`, `database`, `inference`) are optional lists.
- `name` and every component name must be a plain slug — letters, digits, `.`,
  `_`, `-`, with no path separators and no leading dot. Anything else is
  rejected with an error naming the offending field.
- Component names are matched against the library
  (`scaffold --list-components`). A name with no matching module produces a
  clearly-marked placeholder section and a stdout warning, not a failure.
- Invalid specs exit non-zero with the error on stderr and write nothing.

## Project layout

```
├── AGENTS.md
├── ARCHITECTURE.md
├── README.md
├── pyproject.toml
├── components/             # Bundled module library + MODULE_AUTHORING.md
├── core/                   # Stack-agnostic templates assembled into every scaffold
├── docs/                   # Engineering method, generator specs, and project knowledge
├── examples/               # Example stack spec, kept valid by tests
├── src/
│   └── scaffold_generator/
│       ├── cli.py          # Entry point and argument parsing
│       ├── spec.py         # YAML spec loading and schema validation
│       ├── resolver.py     # Component resolution and placeholder generation
│       ├── gates.py        # Module-declared quality gates: parse, render, drift
│       ├── assembler.py    # Template and fragment assembly
│       ├── importer.py     # Scaffold-package overlay (specs, plans, domain map)
│       ├── writer.py       # Filesystem output
│       ├── validator.py    # Contract validation on generated output
│       ├── baseline.py     # Runs a generated scaffold's gates and classifies them
│       ├── filesystem.py   # Filesystem boundary (real + in-memory implementations)
│       └── runner.py       # Command boundary (real + fake implementations)
└── tests/
    ├── conftest.py
    ├── features/           # Gherkin scenarios
    ├── step_defs/          # BDD step implementations
    └── unit/               # Unit tests per module
```

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .[dev]
```

## Quality commands

```bash
pytest
ruff check .
ruff format --check .
mypy src tests
```

## Definition of done

A change is not complete until:

- the behavior is described in a BDD scenario grounded in a product spec
- at least one failing test existed before the implementation
- all quality gates pass
- mocks replace live filesystem and network calls in tests
- this README accurately describes the current state of the project
