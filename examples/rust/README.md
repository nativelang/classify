# Rust

Create a project and install Classify.

```sh
cargo new movie
cd movie
cargo add classify --git https://github.com/nativelang/classify --tag v0.2.0
```

Save this as `src/main.rs`.

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

Run `cargo run`. It prints `negative`. The first call downloads the model and runtime. Later calls use the local cache. A successful call returns `None` when no category fits.
