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

`dm-classify-1.7b-fp32-r1.zip`

### What to download together

For an embedded install, choose the runtime for your computer and the model listed with it. The native server download already includes both. The release page will link to these files.

Each language package will pin a **release manifest** by its download URL and SHA-256 fingerprint. This file lists the compatible runtime and model, so installing the same SDK version selects the same artifacts. A later SDK release can pin a different model.

For a manual install, first check the manifest’s SHA-256 against the fingerprint in the release announcement. Then use the verified manifest to find these details.

- The runtime version, native binary interface (ABI), HTTP API version and model ID. Software versions follow semantic versioning, for example `0.1.0`.
- Download links for the model and each supported computer’s runtime and server, with sizes, licenses and SHA-256 fingerprints. Verify the downloaded files before opening them. Copy the files and their notices to the offline machine.
- The Docker image name, tag and exact fingerprint (digest).

## Hosted and premium delivery

If you want NativeLang to run Classify for you, the planned paid service will offer more powerful models. Pricing, features and the service address will be announced later. You can call the service directly or configure your app to ask it only when a local result is uncertain. [How fallback works](SPECIFICATION.md#opt-in-fallback-and-paid-offerings)

If you want a premium model to run on your infrastructure, the planned license covers the delivery formats in your agreement, such as a container or a library and model bundle. The public code and guides use the [MIT License](LICENSE). Model and binary downloads carry their own terms and third-party notices.
