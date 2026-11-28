<h1 id="classify-by-nativelang">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark-mode.png">
    <img src="assets/logo-light-mode.png" width="201" height="76" alt="Classify by NativeLang">
  </picture>
</h1>

Give Classify some text and a list of categories. It tells you which one fits, if any.

```text
# Pseudocode
classify("This is a terrible movie", categories=["positive", "negative", "neutral"])
# The result is "negative".
```

Turn a sentence into a value you can use in a `switch` statement. Classify runs locally, so you don’t need a large language model API.

<a id="examples"></a>

Try Classify in your language.

[Python](examples/python/) · [JavaScript / TypeScript](examples/node/) · [Java](examples/java/) · [C#](examples/csharp/) · [Go](examples/go/) · [Rust](examples/rust/)

These packages run on macOS 15+ on Apple Silicon or Debian 12-compatible Linux on ARM64 or x64. Your first call downloads the small model (about 1.6 GB). Other apps can use the same download.

[Advanced options](SPECIFICATION.md#deployment-options) · [API reference](SPECIFICATION.md#call-and-result)

A hosted service and a more powerful model with an enterprise license are coming soon.
