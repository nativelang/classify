<h1 id="classify-by-nativelang">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark-mode.png">
    <img src="assets/logo-light-mode.png" width="201" height="76" alt="Classify by NativeLang">
  </picture>
</h1>

Give Classify some text and a list of categories. It tells you which one fits, if any.

```text
# Pseudocode
classify("This is a terrible movie", categories=["positive", "negative", "neutral"])  # "negative"
```

<a id="examples"></a>

## Try Classify in your language

[Python](examples/python/) · [JavaScript / TypeScript](examples/node/) · [Java](examples/java/) · [C#](examples/csharp/) · [Go](examples/go/) · [Rust](examples/rust/)

The first call downloads the model for your platform. Later calls work offline. Your text stays on your computer, and there’s no per-token fee.

[Platforms and download sizes](docs/platforms.md) · [Other ways to run Classify](self-hosting/README.md) · [API reference](docs/API.md)
