# Classify

Classify text locally on Apple Silicon macOS or Debian 12-compatible ARM64 and x64 Linux. The first call downloads Compact r3 and its runtime, about 1.6 GB. Later calls use the local cache.

```sh
cargo add nativelang-classify
```

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
