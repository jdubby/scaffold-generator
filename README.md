# Scaffold Generator

Generates a project scaffold from a structured YAML stack spec by composing
pre-authored component modules. Core tenets — BDD/TDD delivery loop, evaluator
protocol, design quality criteria, contract validation — are preserved regardless
of the stack.

## What it does

```bash
scaffold spec.yml -o ./my-project
```

Reads `spec.yml`, resolves each declared component to a module in the component
library, and assembles a complete scaffold in `./my-project` (via `-o`/`--output`). Unknown components
produce clearly-marked placeholder sections rather than failing.

The repo bundles the component library (`components/`) and the stack-agnostic
core templates (`core/`), used by default when `--components-dir`/`--core-dir`
are not given. Bundled modules: react-native and nextjs (frontend), fastapi and
python-cli (backend), firebase and postgres (database), pytorch (inference). To add a
module, see `components/MODULE_AUTHORING.md`.

```bash
scaffold --list-components     # list all available component modules by category
scaffold --validate spec.yml   # validate a spec without generating output
```

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
├── examples/               # Example stack spec, kept valid by tests
├── src/
│   └── scaffold_generator/
│       ├── cli.py          # Entry point and argument parsing
│       ├── spec.py         # YAML spec loading and schema validation
│       ├── resolver.py     # Component resolution and placeholder generation
│       ├── assembler.py    # Template and fragment assembly
│       ├── writer.py       # Filesystem output
│       ├── validator.py    # Contract validation on generated output
│       └── filesystem.py   # Filesystem boundary (real + in-memory implementations)
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
