# Run Classify

Use the C SDK to classify text inside your app, or run a [local HTTP server](self-hosting/README.md) that several apps can call. Both work offline after installation.

## Free downloads

For the C SDK, download **one model ZIP** and **one runtime archive** for your operating system and processor. A self-contained server or offline Docker image already includes its model.

| Model ZIP (single file) | Bytes | SHA-256 |
| --- | ---: | --- |
| [Compact r3](https://huggingface.co/nativelang/classify-models/resolve/47ab2a3f4280647a64e6ac307f262a74a1b4694e/models/dm-classify-compact-r3.zip) | 1,578,269,501 | `37f6090c9760d46543fff5587ba1cdeef84cf55e02723a5923a3c866364deaa9` |
| [Standard r1](https://huggingface.co/nativelang/classify-models/resolve/47ab2a3f4280647a64e6ac307f262a74a1b4694e/models/dm-classify-standard-r1.zip) | 2,450,864,999 | `1345fb5f8a2ec9ee30d46acc8ec4bcc28991a0c4442353d5652f83d2ce36de40` |

GitHub also carries the [compact ZIP](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3-model/dm-classify-compact-r3.zip) and the [standard ZIP in two parts](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-standard-r1-model-manual). For the latter, follow the release’s reassembly instructions and verify the complete ZIP against the table.

| Portable C SDK | Supported platforms | Manifest SHA-256 |
| --- | --- | --- |
| [Compact r3 manifest](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3/manifest.json) | macOS 15+ on Apple Silicon; Linux ARM64 or x64 | `249a88b696c8879e05018cf107f63399e6a3214b62f2eaa22400b48ff051d9ef` |
| [Standard r1 manifest](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-standard-r1/manifest.json) | macOS 15+, Linux, or Windows on ARM64 or x64 | `256d64d3f8a62fb103ce9ed59eda419fb4284f2ef53281a550ee2d2de5a43d05` |

The native Linux packages require glibc and libstdc++ compatible with Debian 12 (Bookworm). On Windows, install the current [Microsoft Visual C++ v14 Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) for your app’s architecture (x64 or ARM64).

Save the manifest, verify its SHA-256, then find your platform’s runtime URL and archive checksum in it. On macOS run `shasum -a 256 manifest.json`, on Linux use `sha256sum manifest.json`, or in PowerShell use `Get-FileHash manifest.json -Algorithm SHA256`. Check the archive the same way before unpacking it.

Optional accelerated SDKs use the same model ZIPs. Choose Metal for an Apple Silicon Mac with a compatible GPU and macOS 26 or later, or x86-64-v3 for a Linux x64 host that supports that instruction set. Each index lists exact filenames, download URLs and checksums.

| Accelerated SDK | Index SHA-256 |
| --- | --- |
| [Compact r3 · Metal](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3-metal/downloads.json) | `5462da008089d91c6f4d8ee319c003c6828db777aa0482f988c6011c3533e829` |
| [Standard r1 · Metal](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-standard-r1-metal/downloads.json) | `8b5d69b58e586750fb9e335840b56cb2465601ea66bd45d83f151964f7690a4f` |
| [Compact r3 · Linux x86-64-v3](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3-v3/downloads.json) | `c4eca4254259073724ffcd530002e7945aa5ba6e211d537bb612b9dcbd65853d` |
| [Standard r1 · Linux x86-64-v3](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-standard-r1-v3/downloads.json) | `fa23357c598ed0d52572b5b54b1adb7a0e340d6abce41e5f9383b33d065762b5` |

## Make a C call on Apple Silicon

The [C example](examples/c/classify.c) classifies “This is a terrible movie” using the categories `positive`, `negative`, and `neutral`. With a C compiler installed, start in the root of a checkout of this repository. Save the compact ZIP and its [Apple Silicon portable SDK](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3/classify-runtime-0.1.0-aarch64-apple-darwin.tar.gz) there. First verify the two archives.

```sh
shasum -a 256 -c - <<'SUMS'
37f6090c9760d46543fff5587ba1cdeef84cf55e02723a5923a3c866364deaa9  dm-classify-compact-r3.zip
3b4d801ea490fe149ed15ce441269caba2541ae7c16da0f3ed236a6bcbb1ada8  classify-runtime-0.1.0-aarch64-apple-darwin.tar.gz
SUMS
```

When both files report `OK`, unpack them, compile the example and run it.

```sh
mkdir sdk
tar -xzf classify-runtime-0.1.0-aarch64-apple-darwin.tar.gz -C sdk
unzip -q dm-classify-compact-r3.zip -d model
cc -std=c11 -Isdk/include examples/c/classify.c -Lsdk/lib -lclassify_core \
  -Wl,-rpath,@executable_path/sdk/lib -o classify-example
./classify-example model/profile.json
```

The compact portable SDK returned `"status":"matched"`, `"category":"negative"` and `"source":"local"` on Apple Silicon. For repeated requests, open the profile once, reuse the handle and free each returned string with `classify_free`. Keep the extracted model directory and notices together.

On Linux, use the SDK for your CPU and change the linker option to `'-Wl,-rpath,$ORIGIN/sdk/lib'`. On Windows, use the matching MSVC developer shell, include `sdk\include`, link `sdk\lib\classify_core.lib`, and place `sdk\bin\classify_core.dll` beside your executable.

## Hosted and premium delivery

If you want NativeLang to run Classify for you, the planned paid service will offer more powerful models. Pricing, features and the service address will be announced later. You can call the service directly or configure your app to ask it only when a local result is uncertain. [How fallback works](SPECIFICATION.md#opt-in-fallback-and-paid-offerings)

### Enterprise licensing

NativeLang offers the large classification model and its GPU serving software under an enterprise license for deployment on your infrastructure. To discuss terms and private delivery, [open a licensing inquiry](https://github.com/nativelang/classify/issues/new). Issues are public, so keep the initial inquiry general.

The public code and guides use the [MIT License](LICENSE). Model and binary downloads carry their own terms and third-party notices.
