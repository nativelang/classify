# Classify a movie review in Rust

You’ll need Rust and Cargo. Use an Apple Silicon Mac with macOS 15 or later, or [Debian 12-compatible Linux](../../SPECIFICATION.md#linux-requirements) on ARM64 or x64. On Windows or an Intel Mac, [run the local server](../../self-hosting/README.md).

Create a project and add Classify.

```sh
cargo new movie
cd movie
cargo add classify --git https://github.com/nativelang/classify --tag v0.2.0
```

Replace the contents of `src/main.rs` with this code.

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

The first run downloads the model (about 1.6 GB). Later runs work offline.

```sh
cargo run
```

Expected output

```text
negative
```

If no category fits, `classify` returns `Ok(None)`.
