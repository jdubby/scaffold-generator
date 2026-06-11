### postgres reliability

- Migrations run against a disposable database in CI on every change; a
  migration that cannot apply cleanly from zero fails the pipeline.
- Every query path carries a statement timeout; the data-access layer maps
  connection exhaustion, serialization failures, and timeouts to distinct,
  testable errors — retry only the retryable ones.
- Integration tests run against a real PostgreSQL service container, not a
  SQLite stand-in; SQL dialect differences are where bugs hide.
- Backups are only real if restores are tested; document and exercise the
  restore path.
