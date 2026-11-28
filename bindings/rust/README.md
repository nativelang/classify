# Classify

Give `classify` some text and the categories your app uses.

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

[Rust quickstart](https://github.com/nativelang/classify/tree/main/examples/rust)
