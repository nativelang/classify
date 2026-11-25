# Choose how to run Classify

The first release will be free and will work offline after installation. You can run Classify inside your app or send text to a server on your own machine. Both use the same model and the same rules for choosing an answer. Neither requires an account.

## Free downloads

The first release targets Windows, macOS, and Linux for both the embedded library and the native server. The [releases page](https://github.com/nativelang/classify/releases) will list the first downloads, the languages and computers they support, and the install commands.

| If you want to… | Choose |
| --- | --- |
| Call Classify directly from your code | **Library.** Install the package for your language. It uses a native inference library (the code that runs the model) and the free model. The package may include both. |
| Call Classify over HTTP and already use Docker | **Docker image.** The server, inference library and model come installed together. |
| Run a server on your computer without Docker | **Native server.** Unpack the download for your computer and start the included server. You can install the language package alongside it. |

For example, a Python app could use the library once Python is listed as supported. Several apps sharing one machine could all call the same server. The Docker and native servers accept the same requests. [Library example](SPECIFICATION.md#first-call) · [Server instructions](self-hosting/README.md)

## Library versions and model IDs

Pin the software version and model together when you want to reproduce a result. A library version tells you which calls your code can make. A model ID tells you which model and decision settings interpret the text.

Take `dm-qwen3-32b-nf4-r1` as an example. It identifies a decision model (`dm`) in the Qwen3 family, with about 32 billion parameters (`32b`), using a 4-bit weight format (`nf4`), revision one (`r1`). This illustrates the naming scheme. The first free model will be identified in its release.

```text
dm-<family>-<size>-<precision>-r<revision>
```

Size is expressed in millions (`m`) or billions (`b`) of model parameters. Use the published download size and memory requirements to judge whether a model fits your machine. Precision describes how the main weights are stored, for example `fp32`, `bf16`, `int8` or `nf4`. The profile lists components that use a different precision. Revisions start at `r1`. Changing the weights, tokenizer, text preparation or default decision thresholds gives that family, size and precision a new revision.

### What to download together

Each release will include a list of compatible files (the **release manifest**). Use it to find these details.

- Your language package and native library versions, supported operating systems and processors, and the model ID. Software versions follow semantic versioning, for example `v0.1.0`. The list also identifies the native binary interface (ABI) and HTTP API version, such as `/v1`.
- Download links, file sizes, licenses and a SHA-256 fingerprint for each file. Verify the fingerprint against your download. If the model or library comes separately, copy it with its notices to the offline machine.
- Native server archives and the Docker image name, tag and exact image fingerprint (digest).

## Hosted and premium delivery

If you want NativeLang to run Classify for you, the planned paid service will offer more powerful models. Pricing, features and the service address will be announced later. You can call the service directly or configure your app to ask it only when a local result is uncertain. [How fallback works](SPECIFICATION.md#opt-in-fallback-and-paid-offerings)

If you want a premium model to run on your infrastructure, the planned license covers the delivery formats in your agreement, such as a container or a library and model bundle. The public code and guides use the [MIT License](LICENSE). Model and binary downloads carry their own terms and third-party notices.
