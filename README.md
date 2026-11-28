<h1 id="classify-by-nativelang">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/classify-dark.png">
    <img src="assets/classify-light.png" width="201" height="76" alt="Classify by NativeLang">
  </picture>
</h1>

Give Classify some text and a list of categories. It tells you which one fits, if any.

First, [install and start the Classify server on your laptop or server](self-hosting/README.md). Then call it from your app.

```text
# Pseudocode
classify("This is a terrible movie", categories=["positive", "negative", "neutral"])
# The result is "negative".
```

<a id="examples"></a>

Try it in your language.

[Python](examples/python/) · [JavaScript / TypeScript](examples/node/) · [Java](examples/java/) · [C#](examples/csharp/) · [Go](examples/go/) · [Rust](examples/rust/) · [C](examples/c/)

A hosted service and a more powerful model with an [enterprise license](PACKAGING.md#enterprise-licensing) are coming soon.
