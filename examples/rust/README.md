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

The first call downloads the model. Later calls work offline.

[Platforms, download sizes and Windows setup](../../SPECIFICATION.md#language-package-platform-support)
