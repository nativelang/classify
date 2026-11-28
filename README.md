<h1 id="classify-by-nativelang">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/classify-dark.png">
    <img src="assets/classify-light.png" width="201" height="76" alt="Classify by NativeLang">
  </picture>
</h1>

Give Classify some text and a list of categories. It tells you which one fits, if any.

*Example (pseudocode)*

```text
classify("This is a terrible movie", categories=["positive", "negative", "neutral"])
```

The result is `"negative"`.

## Examples

[Start Classify on your computer](self-hosting/README.md), then pick your language. Each example shows how to call the server from your app.

[Python](examples/python/) · [JavaScript / TypeScript](examples/node/) · [Java](examples/java/) · [C#](examples/csharp/) · [Go](examples/go/) · [Rust](examples/rust/)

To run Classify directly inside a C app, follow the [C example](examples/c/). Both ways work offline after setup.

The large model and its GPU server are available under an [enterprise license](PACKAGING.md#enterprise-licensing).
