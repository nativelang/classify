# Rust API

`classify(text: &str, categories: &[&str]) -> std::io::Result<Option<String>>`

Returns `Ok(Some(id))` on a match, `Ok(None)` on abstention and `Err` on failure.

[Working example](../../examples/rust/)
