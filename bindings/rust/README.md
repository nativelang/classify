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

[Speed up startup with the local API service](https://github.com/nativelang/classify/blob/main/docs/service.md).
