# Classify a movie review in Rust

```sh
cargo add nativelang-classify
```

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

[Run Classify on Windows or an Intel Mac](../../self-hosting/README.md)
