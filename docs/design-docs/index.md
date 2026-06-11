# Design Documentation Index

This directory contains design decisions and architectural choices made during
development. Reference this index to find relevant background before making changes
that cross domain or layer boundaries.

## Index

| Document | Date | Status | Summary |
|----------|------|--------|---------|
| [core-beliefs.md](./core-beliefs.md) | — | Stable | Agent-first operating principles |

## How to write a design doc

A design document captures:

1. **Context** — what problem was being solved and what constraints existed
2. **Decision** — what approach was chosen
3. **Alternatives considered** — what else was evaluated and why it was not chosen
4. **Consequences** — what this decision makes easier and harder going forward

Name the file `YYYY-MM-DD-<short-description>.md` and add a row to the index table
above. Reference it from `ARCHITECTURE.md` when it affects domain boundaries or
layering rules.
