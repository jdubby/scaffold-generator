### pytorch reliability

- Every model version ships with a pinned evaluation set and minimum-quality
  threshold; deploying a model that regresses below it must fail mechanically.
- Inference calls carry timeouts and bounded batch sizes; overload degrades to
  queuing or rejection, never unbounded memory growth.
- The service starts and answers health checks without a GPU, falling back to
  CPU or a stub — environment differences must not take the whole app down.
- Log model version and latency per request so quality drift is attributable.
