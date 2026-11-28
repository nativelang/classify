<h1 id="classify-by-nativelang">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/classify-dark.png">
    <img src="assets/classify-light.png" width="201" height="76" alt="Classify by NativeLang">
  </picture>
</h1>

Give Classify some text and a list of categories. It tells you which one fits, if any.

To call Classify over HTTP, [install and start it on your laptop or server](self-hosting/README.md).

```text
# Pseudocode
classify("This is a terrible movie", categories=["positive", "negative", "neutral"])
# The result is "negative".
```

<a id="examples"></a>

Choose your language.

[Python](examples/python/) · [JavaScript / TypeScript](examples/node/) · [Java](examples/java/) · [C#](examples/csharp/) · [Go](examples/go/) · [Rust](examples/rust/) · [C](examples/c/)

[API reference](SPECIFICATION.md)

A hosted service and a more powerful model with an enterprise license are coming soon.
