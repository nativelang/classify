# Classify

Give `classify` some text and the categories your app uses.

```rust
use classify::classify;

fn main() -> std::io::Result<()> {
    let label = classify("This is a terrible movie", &["positive", "negative", "neutral"])?;
    if let Some(label) = label {
        println!("{label}");
    }
    Ok(())
}
```

This prints `negative`. When no category fits, `classify` returns `Ok(None)`.

To install the package and run this example, follow the [Rust quick start](https://github.com/nativelang/classify/tree/main/examples/rust). It includes system requirements and first-run download details.
