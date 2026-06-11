### nextjs security

- Secrets live in server-only environment variables; nothing sensitive is
  prefixed `NEXT_PUBLIC_`, and no secret is read inside a client component.
- Keep the server/client boundary honest: server actions and route handlers
  re-validate authorization on every call — client-side checks are UX only.
- Set a Content-Security-Policy and the standard security headers in middleware
  or `next.config`; test that they are present.
- Sanitise anything rendered with `dangerouslySetInnerHTML`; prefer not to use
  it at all.
