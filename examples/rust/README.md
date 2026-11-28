# Rust

[Start the local server](../../self-hosting/README.md). With Rust and Cargo installed, open a second terminal.

```sh
cargo new classify-example
cd classify-example
cargo add ureq@2 --features json
cargo add serde_json@1
```

Save this as `src/main.rs`.

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

```sh
cargo run
```

Prints `negative`.
