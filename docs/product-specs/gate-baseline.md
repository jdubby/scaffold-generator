# Product Spec: Gate baseline

**Status:** Active
**Feature file:** `tests/features/gate_baseline.feature`

## Goal

A generated scaffold now names its quality gates as runnable commands, but nobody
has ever run them. That leaves the most important question about a fresh scaffold
unanswered: do these gates execute at all, and can they fail?

The answer matters because of how a gate is read at baseline. A gate that demands
behavior nobody has built yet is *expected* to fail against an empty scaffold —
that failure is the gate working. A gate that **passes** against a scaffold with no
implementation in it is the suspicious one: it is asserting nothing, and it will go
on asserting nothing for the life of the project. A gate that cannot run at all
tells the user which tooling the stack still needs.

`scaffold --baseline DIR` runs each gate the scaffold declares and reports which of
those three things happened, so a dead gate is caught on day one rather than after
a project has been trusting it for a year.

## Scope

### In scope

- `--baseline DIR` reads the gates from the **Quality gates** section of
  `DIR/AGENTS.md`, runs each one with `DIR` as the working directory, and reports
  a per-gate outcome and a summary.
- Outcomes: passed, failed, unavailable (the command is not installed), timed out,
  and skipped.
- `--dry-run` alongside `--baseline` prints the commands and runs nothing.
- A per-gate timeout, so one hanging gate cannot hang the run.

### Out of scope

- Judging whether a gate *should* have passed. The command decides; this reports.
  The reading above is guidance printed alongside the results, not a verdict.
- Running gates against anything but a generated scaffold directory.
- Installing missing tooling, or creating a virtual environment for the target.
- Any change to how gates are declared or assembled — that is
  `executable-gates.md`, and this feature consumes its output.

## Acceptance criteria

### AC-1: Declared gates are executed against the scaffold

Given a generated scaffold directory, when the user runs `--baseline` against it,
then every gate listed in that scaffold's **Quality gates** section is executed
with the scaffold directory as its working directory, and each gate's name,
command, and outcome are printed.

### AC-2: Outcomes are classified and the reading is explained

Given a completed baseline run, when results are printed, then each gate is marked
passed, failed, unavailable, timed out, or skipped; a summary counts each; and the
output states that failures are expected against a fresh scaffold while a passing
gate deserves scrutiny. The command exits zero whatever the gate outcomes were —
this is a diagnostic, not a gate of its own.

### AC-3: Gates are executed without a shell

Given a gate whose command contains shell syntax (`&&`, `||`, `;`, `|`, `>`, `<`,
backticks, or `$(`), when baseline runs, then that gate is **skipped** and reported
as such, naming the offending syntax, and no shell is invoked. Every other gate is
executed as an argument vector, never as a shell string. A scaffold is content that
may have come from anywhere, so no part of it is ever handed to a shell.

### AC-4: --dry-run executes nothing

Given `--baseline DIR --dry-run`, when the command runs, then each gate's name and
command are printed, no command is executed, and the output says nothing ran. This
is the safe way to inspect a scaffold whose origin the user does not trust.

### AC-5: A directory with no gates fails clearly

Given a directory with no `AGENTS.md`, or an `AGENTS.md` with no **Quality gates**
section, when the user runs `--baseline` against it, then the command exits
non-zero with an error naming what is missing, and runs nothing.

### AC-6: A hanging gate is reported, not fatal

Given a gate whose command does not terminate, when it exceeds the per-gate
timeout, then it is killed, reported as timed out with the timeout value, and the
remaining gates still run.

## Open questions

- Should `--baseline` accept a `--gate NAME` filter for re-running one gate? Not
  until a scaffold declares enough gates for the full run to be slow.
- Should a passing gate be an exit-code failure under some `--strict` flag? That
  would make baseline usable as a CI check on the generator's own library. Deferred
  until something wants to consume it that way; the classification is already in
  the output for a caller to parse.
