### postgres (database)

PostgreSQL owns persistence. The schema is code: every change is a numbered,
forward-only migration checked into the repo — no hand-edited production
schemas. Application code goes through a data-access layer that owns connection
pooling and transactions; business logic never holds a raw connection. Model the
schema deliberately (constraints, foreign keys, NOT NULL) so the database
enforces invariants instead of trusting callers.
