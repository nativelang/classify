# Releases and downloads

To embed Classify in a C app, follow the [native C setup guide](examples/c/BUILD.md). For HTTP, use the [server installer](self-hosting/README.md). For Docker, see [manual installation](self-hosting/manual.md#docker).

## Free downloads

The Node.js and Python packages select Compact on Apple Silicon and Linux, and Standard on Intel Macs and Windows. For a C app, download one model ZIP and its matching SDK. The language packages and server installer download the files they need automatically.

| Model ZIP (single file) | Bytes | SHA-256 |
| --- | ---: | --- |
| [Compact](https://huggingface.co/nativelang/classify-models/resolve/47ab2a3f4280647a64e6ac307f262a74a1b4694e/models/dm-classify-compact-r3.zip) | 1,578,269,501 | `37f6090c9760d46543fff5587ba1cdeef84cf55e02723a5923a3c866364deaa9` |
| [Standard](https://huggingface.co/nativelang/classify-models/resolve/47ab2a3f4280647a64e6ac307f262a74a1b4694e/models/dm-classify-standard-r1.zip) | 2,450,864,999 | `1345fb5f8a2ec9ee30d46acc8ec4bcc28991a0c4442353d5652f83d2ce36de40` |

GitHub also carries the [Compact ZIP](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3-model/dm-classify-compact-r3.zip) and the [Standard ZIP in two parts](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-standard-r1-model-manual). To [join the two parts](self-hosting/manual.md#join-the-two-parts), use the model release’s index checksum `28c96430f276902fbd88aba50110bc73af6cec3cacc6aa2445baa09e911ecb2f`. Check the completed ZIP against the table.

| Portable C SDK | Supported platforms | Manifest SHA-256 |
| --- | --- | --- |
| [Compact manifest](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3/manifest.json) | Apple Silicon with macOS 15+, or Linux ARM64 or x64 | `249a88b696c8879e05018cf107f63399e6a3214b62f2eaa22400b48ff051d9ef` |
| [Standard manifest](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-standard-r1/manifest.json) | macOS 15+, Linux, or Windows on ARM64 or x64 | `256d64d3f8a62fb103ce9ed59eda419fb4284f2ef53281a550ee2d2de5a43d05` |

The native Linux packages require glibc and libstdc++ compatible with Debian 12 (Bookworm). On Windows, install the current [Microsoft Visual C++ v14 Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) for your app’s architecture (x64 or ARM64).

Verify the manifest with `shasum -a 256 manifest.json` on macOS, `sha256sum manifest.json` on Linux, or `Get-FileHash manifest.json -Algorithm SHA256` in PowerShell. Download your runtime from the verified manifest and check the archive against its listed SHA-256.

Accelerated SDKs use the same model ZIPs. Metal requires Apple Silicon, a compatible GPU and macOS 26 or later. The Linux x86-64-v3 SDK requires a CPU and OS with x86-64-v3 support. Each index includes the SDK URL and checksum.

| Accelerated SDK | Index SHA-256 |
| --- | --- |
| [Compact · Metal](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3-metal/downloads.json) | `5462da008089d91c6f4d8ee319c003c6828db777aa0482f988c6011c3533e829` |
| [Standard · Metal](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-standard-r1-metal/downloads.json) | `8b5d69b58e586750fb9e335840b56cb2465601ea66bd45d83f151964f7690a4f` |
| [Compact · Linux x86-64-v3](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3-v3/downloads.json) | `c4eca4254259073724ffcd530002e7945aa5ba6e211d537bb612b9dcbd65853d` |
| [Standard · Linux x86-64-v3](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-standard-r1-v3/downloads.json) | `fa23357c598ed0d52572b5b54b1adb7a0e340d6abce41e5f9383b33d065762b5` |

<a id="make-a-c-call-on-apple-silicon"></a>

## Build the C example

Download the SDK and model for your platform, then [build and run the C example](examples/c/BUILD.md).

## Licenses

The public code and guides use the [MIT License](LICENSE). See each model or binary download for its terms and third-party notices.

## Coming soon

A hosted service and a more powerful model with an enterprise license are planned.
