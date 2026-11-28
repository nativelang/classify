# C API

`classify_infer(model, request_json, &error)`

Returns a UTF-8 JSON result string. On failure, read the error string. Release returned strings with `classify_free` and close the model with `classify_close`. The C API loads the model in the calling process.

[Working example](../../examples/c/)
