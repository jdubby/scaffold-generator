### pytorch (inference)

PyTorch owns model inference. Inference code lives behind a service interface
(load, preprocess, predict, postprocess) so application code never imports
torch directly — models can be swapped, quantized, or mocked in tests without
touching callers. Model weights are versioned artifacts referenced by an exact
identifier, never "latest"; the model file is data, not part of the source tree.
