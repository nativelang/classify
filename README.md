# Classify by NativeLang

Give Classify a short piece of text and the options your application understands. It returns one of your option IDs, or `unknown` when it can’t confidently choose one.

For example, a scheduling app might offer `reschedule` and `cancel`. “Can we move Friday’s appointment to Monday?” points to `reschedule`. “Where is my appointment?” falls outside both options. Your application decides how to handle the result.

```text
result = classify(text, options)
```

This repository contains the proposed v1 API and packaging guides. The first SDK, native runtime, free model download and server image are planned. Published versions and their supported platforms will appear on [GitHub Releases](https://github.com/nativelang/classify/releases).

| How you want to use Classify | Planned offering |
| --- | --- |
| Call it inside your application | Free language binding, native inference library and offline model |
| Run a local HTTP endpoint in Docker | Free image with the server, runtime and model installed |
| Use a local endpoint without Docker | Free native server for macOS or Linux, usable alongside the language binding |
| Call a service operated by NativeLang | Paid API with more powerful models. Features and availability will be announced later. |
| Run a premium model on your infrastructure | Licensed image or library and model bundle, according to the license |

Start with the [API and examples](SPECIFICATION.md), [install and download guide](PACKAGING.md), or [local server guide](self-hosting/README.md).

The public integration source and documentation use the [MIT License](LICENSE). Runtime binaries, models and third-party assets carry the terms listed with each release.
