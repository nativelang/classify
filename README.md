<h1 id="classify-by-nativelang">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/classify-dark.png">
    <img src="assets/classify-light.png" width="201" height="76" alt="Classify by NativeLang">
  </picture>
</h1>

Classify text from categories you choose.

*Example (pseudocode)*

```text
classify("This is a terrible movie", categories=["good", "bad"])
```

The result is `"bad"`.

## Install and use

The first release is in development. Downloads and install commands will appear on [GitHub Releases](https://github.com/nativelang/classify/releases).

- **Use Classify in your app.** [Library installation guide](PACKAGING.md#free-downloads) · [Make your first call](SPECIFICATION.md#first-call)
- **Run Classify on your machine.** [Set up the server with Docker or directly on Windows, macOS, or Linux](self-hosting/README.md) · [Send a request](self-hosting/README.md#try-a-request)
- **Run the large model on your infrastructure.** The model and its GPU serving software are available under an enterprise license. [Enterprise licensing](PACKAGING.md#enterprise-licensing)

The free edition will run locally without an API key. The [planned hosted service](SPECIFICATION.md#opt-in-fallback-and-paid-offerings) will use an API key.
