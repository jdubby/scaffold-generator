### python-cli reliability

- Exit codes are the API: 0 for success, distinct non-zero codes per failure
  class, asserted by tests at the CLI boundary.
- stdout carries only payload output so the tool composes in pipes; diagnostics,
  warnings, and errors go to stderr with enough context to act on.
- Every expected failure (bad input, missing file, permission denied) prints a
  clear message and exits non-zero — no raw tracebacks for user errors.
- Handle Ctrl-C and closed pipes gracefully: KeyboardInterrupt and BrokenPipeError
  end the process quietly with a non-zero code, not a stack dump.
