### firebase security

- Security rules are the real access-control boundary — client checks are UX,
  not security. Every collection has explicit rules; default-deny everything
  else.
- Test security rules in CI with the emulator (allowed and denied cases per
  collection).
- Never embed service-account keys in client code or repositories; server-side
  access uses workload identity or environment-injected credentials.
