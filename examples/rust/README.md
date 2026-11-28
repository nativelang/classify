# Classify a movie review in Rust

In your Rust project, add Classify.

```sh
cargo add nativelang-classify
```

Replace the contents of `src/main.rs` with this code.

```rust
use classify::classify;

fn main() -> std::io::Result<()> {
    let label = classify("This is a terrible movie", &["positive", "negative", "neutral"])?;
    if let Some(label) = label {
        println!("{label}"); // negative
    }
    Ok(())
}
```

The first run downloads the model (about 1.6 GB). Later runs work offline.

```sh
cargo run
```

If no category fits, `classify` returns `Ok(None)`.

[Run Classify on Windows or an Intel Mac](../../self-hosting/README.md)
