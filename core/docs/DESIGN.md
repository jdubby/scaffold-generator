# Documentation Principles

- The repository is the system of record. Decisions, constraints, and plans that
  live only in chat or in someone's head are invisible to the next agent session.
- Every document has one job. `AGENTS.md` navigates; `ARCHITECTURE.md` maps the
  code; product specs define behavior; `docs/QUALITY_SCORE.md` tracks honesty
  about quality. Do not duplicate content between them — link instead.
- Update documentation in the same task as the change it describes. A doc that
  trails the code is worse than no doc, because it is trusted and wrong.
- Write for a reader with no session context: spell out paths, name commands
  exactly, and convert relative dates to absolute ones.
- Prefer short documents that are actually read to long ones that are skimmed.
