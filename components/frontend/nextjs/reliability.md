### nextjs reliability

- Every route segment ships `error.tsx` and `loading.tsx`; a failing data fetch
  degrades to a recovery view, never an unstyled stack trace.
- Server actions validate input and return typed error states the UI can render;
  thrown errors are the exceptional path, not the API.
- Treat third-party calls in server components as fallible: timeouts, fallbacks,
  and at least one failure-path test each.
- `next build` runs in CI — a route that fails to compile or prerender must fail
  the pipeline, not the deploy.
