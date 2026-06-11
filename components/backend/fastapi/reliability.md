### fastapi reliability

- Every endpoint returns structured error responses (problem-details style) for
  expected failures; unexpected exceptions map to a generic 500 via one handler,
  never a traceback to the client.
- Downstream calls (database, third-party APIs) carry timeouts and have at least
  one failure-path test each.
- Health and readiness endpoints exist from day one so deploys can be gated on
  them.
