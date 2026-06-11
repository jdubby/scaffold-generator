### firebase reliability

- Run integration tests against the Firebase emulator suite, never against a
  live project; CI must not depend on production quota.
- Handle offline persistence deliberately: decide per-collection whether stale
  reads are acceptable and test reconnection behavior.
- Wrap SDK calls in the data-access layer with explicit error mapping so quota,
  permission, and network failures surface as distinct, testable errors.
