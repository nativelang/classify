# Classify text from Rust

[Start the local Classify server](../../self-hosting/README.md), then open a second terminal. With Rust and Cargo installed, create a project and add the HTTP and JSON dependencies.

```sh
cargo new --bin classify-example
cd classify-example
cargo add ureq@=2.12.1 --no-default-features --features json
cargo add serde_json@=1.0.150
```

Replace `src/main.rs` with this example.

```rust
use serde_json::{json, Value};

const CLASSIFY_URL: &str = "http://127.0.0.1:8080/v1/classify";

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let result: Value = ureq::post(CLASSIFY_URL)
        .send_json(json!({
            "text": "This is a terrible movie",
            "categories": ["positive", "negative", "neutral"]
        }))?
        .into_json()?;
    println!("{}", result["category"].as_str().unwrap_or("unknown"));
    Ok(())
}
```

Run it from the project directory.

```sh
cargo run --quiet
```

The example prints `negative`.
