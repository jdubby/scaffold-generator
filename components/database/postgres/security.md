### postgres security

- All queries are parameterized through the data-access layer; string-built SQL
  does not pass review, ever.
- The application connects with a least-privilege role: no DDL, no superuser.
  Migrations run under a separate, more privileged role.
- Connection strings and credentials come from environment variables or a
  secret manager; TLS is required for connections that leave the host.
- Row-level security or explicit tenant filters guard multi-tenant tables; a
  missing filter must fail a test, not ship.
