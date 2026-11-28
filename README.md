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

Your app can label reviews or sort support tickets locally, without calling a hosted language model or paying per token.

<a id="examples"></a>

Try Classify in your language.

1. [Install and start Classify](self-hosting/README.md).
2. Run an example in your language.

   [Python](examples/python/) · [JavaScript / TypeScript](examples/node/) · [Java](examples/java/) · [C#](examples/csharp/) · [Go](examples/go/) · [Rust](examples/rust/) · [C](examples/c/)

[API reference](SPECIFICATION.md)

A hosted service and a more powerful model with an enterprise license are coming soon.
