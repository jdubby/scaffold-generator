### fastapi security

- All request bodies and query parameters are validated with Pydantic models;
  unvalidated `dict` payloads are not accepted into the service layer.
- Authentication and authorization run as dependencies, not inline in handlers,
  so every route's access rule is visible at its signature.
- CORS is allowlisted explicitly; never `*` in production configuration.
- Secrets come from environment variables; the settings object refuses to start
  without required values.
