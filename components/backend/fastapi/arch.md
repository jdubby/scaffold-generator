### fastapi (backend)

FastAPI owns the HTTP layer: routing, request/response models, and dependency
injection. Route handlers stay thin — they validate input via Pydantic models,
call a service function, and shape the response. Business logic lives in plain
services that import nothing from FastAPI, so it is testable without an HTTP
client.
