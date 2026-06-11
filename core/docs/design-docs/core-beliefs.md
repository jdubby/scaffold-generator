# Core Beliefs — Agent-First Development

- **The repository is the agent's entire world.** Context that is not committed —
  decisions, conventions, plans — does not exist in the next session. Write it
  down where the docs say it belongs.
- **Behavior before implementation.** A spec defines what users can do; scenarios
  make it checkable; tests make it enforceable. Code written before those exists
  tends to define its own requirements.
- **Honest grades beat green dashboards.** `docs/QUALITY_SCORE.md` works only if
  grades go down when reality does. An optimistic C is worth more than a hollow A.
- **Mechanical checks over discipline.** Anything important enough to require in
  review (formatting, types, contracts) should be enforced by a gate, not by
  memory.
- **Small, finished increments.** One failing test, the minimum code to pass it,
  refactor, evaluate. Ten finished increments beat one sprawling branch.
- **Documentation is product.** Stale instructions break the next contributor —
  human or agent — as surely as a failing build.
