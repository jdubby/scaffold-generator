### pytorch security

- Never load untrusted model files: pickled checkpoints execute arbitrary code.
  Use `torch.load(..., weights_only=True)` or safetensors, and verify artifact
  checksums against the model registry before loading.
- Validate and bound all inference inputs (shape, dtype, size) before they reach
  the model; oversized tensors are a denial-of-service vector.
- Model artifacts and registry credentials come from authenticated storage, not
  public URLs baked into code.
- Treat model outputs as untrusted data downstream — escape or validate before
  rendering or executing anything derived from them.
