# Python API

`classify(text, categories) -> Optional[str]`

Returns a category ID or `None`. Invalid requests raise `ValueError`. Worker failures raise `RuntimeError`. Call `close()` to release the process-local worker.

[Working example](../../examples/python/)
