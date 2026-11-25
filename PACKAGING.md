# Installing and versioning Classify

The first release targets free, offline classification. You can use a language binding in your process, run a container, or install a native HTTP server alongside the binding. All three use the same native inference library, model profile and decision settings for a given release. After installation, classification works without an account, an API key or a network connection to NativeLang.

## Free downloads

The [Classify releases page](https://github.com/nativelang/classify/releases) is the planned download index. The first binary release is pending. Each release will list supported languages, operating systems and processor architectures. Use its API documentation and install instructions for your target.

| Installation | What to obtain | How your application calls it |
| --- | --- | --- |
| Embedded library | The binding for your language, its compatible native inference library for your OS and processor, and the free model bundle. A binding may bundle these dependencies. | Call `classify(text, options)` in process. A binding can also register and reuse named option sets. |
| Docker | The free OCI image pinned in the release. It includes the server executable, runtime and model. | Publish a local port and send `POST /v1/classify`. |
| Native macOS or Linux server | The server archive for your OS and processor, including the compatible runtime and model. Install your language binding as well if you want to use the embedded API or its fallback client. | Start the server and send the same HTTP request as for Docker. |

For an embedded installation, select your language and platform in the release manifest. Follow the binding’s install instructions and use its listed runtime and model if they are separate downloads. Check each download against its listed SHA-256. Copy those files and their notices into the target environment for offline use. Registry package coordinates will be published with the first binding. [API examples](SPECIFICATION.md#first-call) · [Local server commands](self-hosting/README.md)

## Library versions and model IDs

Use the Classify release tag, such as `v0.1.0`, to identify a software release. Bindings and the native runtime use semantic versions. The release manifest pins their compatible versions together with the HTTP API major version, such as `/v1`. The classifier’s learned behavior has a separate model profile ID.

```text
dm-<family>-<size>-<precision>-r<revision>
```

For example, `dm-potion-8m-fp32-r1` describes revision 1 of an 8-million-parameter family at FP32. `dm-qwen3-32b-nf4-r1` describes a nominal 32-billion-parameter family with 4-bit NF4 quantization. Both IDs and the software tag above illustrate the convention. The first shipped profile will be named in its release.

- `dm` means decision model. `m` and `b` express the family’s nominal parameter count in millions and billions. Download bytes and runtime memory are separate measurements.
- The precision field identifies the main weight format, such as `fp32`, `bf16`, `int8` or `nf4`. The profile records any mixed-precision components.
- The revision starts at `r1`. Within a family, size and precision, changed weights, tokenizer, preprocessing or default decision thresholds get a new revision. Pin the full ID and artifact digest to reproduce a configuration.

Each release manifest will give the binding package names and versions, native runtime version and ABI, supported targets, model ID, download URLs, file sizes, SHA-256 digests and license notices. For the server it will also give the native archive names and the container image tag and digest. This lets applications update a binding while deliberately retaining a compatible model profile.

## Hosted and premium delivery

NativeLang plans a paid hosted API with access to more powerful models. The endpoint, pricing and additional features will be published when available. A direct HTTP request goes to the endpoint you choose. An embedded client sends an uncertain request to a backend only when you configure fallback. [API and fallback behavior](SPECIFICATION.md#opt-in-fallback-and-paid-offerings)

Customers who license premium models can deploy them in their own infrastructure using a licensed container, a compatible library and model bundle, or both as covered by their agreement. Premium artifacts will be delivered through the licensed channel. The public SDK and guides use the [MIT License](LICENSE). Each binary or model download includes its own terms and applicable third-party notices.
