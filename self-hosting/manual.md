# Docker and manual installation

Use this guide to load Classify into Docker or install a specific server archive. Each download includes the model and runs offline at `127.0.0.1:8080` without an API key. For automatic native installation, use the [server quick start](README.md).

## Choose and verify a download

### Compact r3

Download one file into an empty folder. For Docker, choose the processor used by your Linux containers. For a native server, choose the processor and operating system of the computer that will run it.

| Download | SHA-256 |
| --- | --- |
| [Docker image · ARM64](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3/classify-image-0.1.0-dm-classify-compact-r3-linux-arm64.oci.tar) | `a432db5bd87427cba5f046641c92a3aad49b4abd40afbed7c0761d18bd9e3028` |
| [Docker image · AMD64](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3/classify-image-0.1.0-dm-classify-compact-r3-linux-amd64.oci.tar) | `7a0cfc2eb99c8f3fd014671af4c062de97b0b247881b8a28fee0bd525475d128` |
| [Native server · Apple Silicon](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3/classify-server-0.1.0-dm-classify-compact-r3-aarch64-apple-darwin.tar.gz) | `64d0972c97a87128d4698aa2940b724f321094e476b41b18531aa93426395dd3` |
| [Native server · Linux ARM64](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3/classify-server-0.1.0-dm-classify-compact-r3-aarch64-unknown-linux-gnu.tar.gz) | `fe432526cb458c4df37603917e8c4e321c340e30b631b3f2571332998c674877` |
| [Native server · Linux x64](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3/classify-server-0.1.0-dm-classify-compact-r3-x86_64-unknown-linux-gnu.tar.gz) | `211b8fdb1637709e8ecb1a3c5d2be9de9b6c624cca18c8a6df93029477dc6d28` |

Run `shasum -a 256 FILENAME` on macOS or `sha256sum FILENAME` on Linux, replacing `FILENAME` with the downloaded name. In PowerShell, use `Get-FileHash FILENAME -Algorithm SHA256`. Continue only if the result matches the table.

### Standard r1

Standard supports native Windows, macOS and Linux on x64 and ARM64, and Linux containers on AMD64 and ARM64. Its archives come in two parts.

1. From the [standard release](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-standard-r1-manual), save `downloads.json`, `reassemble.py` and both parts of **one** archive in an empty folder. Choose `classify-server-` to run directly or `classify-image-` for Docker. Allow space for the parts, the restored archive and the extracted files.
2. With Python 3.8 or later, follow the [Unix or PowerShell reassembly commands](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-standard-r1-manual/README.txt). Supply the archive name from `downloads.json` and the index SHA-256 `01430ddd1a9ba0d319e561c95be4dfbe978b3f27686b6fd5b67acd091e59bf67`. The commands check the index and helper before running the helper, then check both parts and the complete archive.

## Docker

Use Docker in Linux container mode. In the download folder, load your verified `.oci.tar` file. This example starts compact r3 on ARM64.

```sh
docker load -i classify-image-0.1.0-dm-classify-compact-r3-linux-arm64.oci.tar
docker run --rm -d --name classify-server -p 127.0.0.1:8080:8080 classify:0.1.0-dm-classify-compact-r3-linux-arm64
```

For AMD64 or standard r1, substitute your image filename in the first command and the name printed after `Loaded image:` in the second. [Try a request](#try-a-request), then stop the server with `docker stop classify-server`.

## Native server

<a id="native-macos-or-linux"></a>

**macOS or Linux.** Use macOS 15 or later, or Debian 12 or a Linux distribution with compatible glibc and C++ runtime libraries. Extract your verified archive and start the server. Substitute your filename if you chose a different build.

```sh
mkdir classify-server
tar -xzf classify-server-0.1.0-dm-classify-compact-r3-aarch64-apple-darwin.tar.gz -C classify-server
cd classify-server
./classify serve --listen 127.0.0.1:8080
```

<details>
<summary>Windows (PowerShell)</summary>

Install the current [Microsoft Visual C++ v14 Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) for your server architecture. Follow the [standard r1 download and verification steps](#standard-r1) first. From the folder containing the restored ZIP, run the following commands. On ARM64, change `x86_64` to `aarch64` in the filename.

```powershell
mkdir classify-server
tar.exe -xf classify-server-0.1.0-dm-classify-standard-r1-x86_64-pc-windows-msvc.zip -C classify-server
if ($LASTEXITCODE -ne 0) { throw 'Extraction failed' }
cd classify-server
.\classify.exe serve --listen 127.0.0.1:8080
```

</details>

Keep the extracted files together and leave the terminal open while serving. Press Ctrl+C to stop.

### Optional accelerated servers

Use Metal on Apple Silicon with a compatible GPU and macOS 26 or later. Use the Linux x86-64-v3 build on a processor that supports that instruction set.

| Platform | Compact r3 server | Standard r1 server | Standard `downloads.json` SHA-256 |
| --- | --- | --- | --- |
| Apple Silicon | [Metal](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-compact-r3-metal) | [Metal, two parts](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-standard-r1-metal-manual) | `295399c5c82803f87ed131022e7d8302256bf50e3461712c0c35fd1d75a118f7` |
| Linux x64 | [x86-64-v3](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-compact-r3-v3) | [x86-64-v3, two parts](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-standard-r1-v3-manual) | `878b71990eafc1b223d29d546a4ddb84f4f3c0864a4a6fb18e6205234bf971e4` |

For compact, verify `downloads.json` using the [compact accelerated index checksums](../RELEASES.md#free-downloads), then check the server archive against its entry. For standard, use the reassembly commands in the **chosen release** and its index checksum above. Start the extracted server with the same native command.

## Try a request

When [the local health page](http://127.0.0.1:8080/health) shows `ok`, the server accepts `POST /v1/classify`. See the [Classify examples](../README.md#examples) for calls in your language and the [API reference](../SPECIFICATION.md#call-and-result) for the request and response fields.
