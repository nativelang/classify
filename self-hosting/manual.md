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

For the [standard servers and Docker images](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-standard-r1-manual), use this SHA-256 for `downloads.json`: `01430ddd1a9ba0d319e561c95be4dfbe978b3f27686b6fd5b67acd091e59bf67`. Choose a `classify-server-` archive to run directly or a `classify-image-` archive for Docker. The [accelerated server releases](#optional-accelerated-servers) have their own index checksums.

### Join the two parts

1. In an empty folder, save `downloads.json` and both parts of your chosen archive **from the same release**. Allow space for the parts, the complete archive and its extracted contents.
2. Check `downloads.json` with `shasum -a 256 downloads.json` on macOS, `sha256sum downloads.json` on Linux, or `Get-FileHash downloads.json -Algorithm SHA256` in PowerShell. Continue only if the result matches the index checksum listed for that release.
3. Open the verified index. In `archives`, find your archive’s `name` and its own `sha256` (the digest for the complete file). Set the first two variables below to those values. The examples join part 1 followed by part 2 and give the output its final name only after the complete file passes verification.

**macOS or Linux** (example for the Apple Silicon server). On Linux, use `sha256sum -c -` in place of `shasum -a 256 -c -`.

```sh
archive='classify-server-0.1.0-dm-classify-standard-r1-aarch64-apple-darwin.tar.gz'
expected='3eedbb8f729369754ace0d6daa83aea26d322723d0d499956c011b320701ba88'
cat "$archive.part-0001-of-0002" "$archive.part-0002-of-0002" > "$archive.partial" &&
  printf '%s  %s\n' "$expected" "$archive.partial" | shasum -a 256 -c - &&
  mv "$archive.partial" "$archive"
```

<details>
<summary>Windows (PowerShell, example for the x64 server)</summary>

```powershell
$Archive = 'classify-server-0.1.0-dm-classify-standard-r1-x86_64-pc-windows-msvc.zip'
$Expected = 'fa7fddf19ed3ee54294d9c791a0a9f8009954cdd7dee2b00532731d524bcea0b'
cmd.exe /d /c "copy /y /b $Archive.part-0001-of-0002+$Archive.part-0002-of-0002 $Archive.partial"
if ($LASTEXITCODE -ne 0) { throw 'Could not join both parts' }
if ((Get-FileHash "$Archive.partial" -Algorithm SHA256).Hash -ne $Expected) { throw 'Archive verification failed' }
Move-Item -LiteralPath "$Archive.partial" -Destination $Archive
```

</details>

## Docker

Use Docker in Linux container mode. In the download folder, load your verified `.oci.tar` file. This example starts compact r3 on ARM64.

```sh
docker load -i classify-image-0.1.0-dm-classify-compact-r3-linux-arm64.oci.tar
docker run --rm -d --name classify-server -p 127.0.0.1:8080:8080 classify:0.1.0-dm-classify-compact-r3-linux-arm64
```

To use port `9090` on your computer, use `-p 127.0.0.1:9090:8080`. Check [the health page on port 9090](http://127.0.0.1:9090/health) and use port `9090` in your app.

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

For compact, verify `downloads.json` using the [compact accelerated index checksums](../RELEASES.md#free-downloads), then check the server archive against its entry. For standard, [join the two parts](#join-the-two-parts) using the index checksum for that server above. Start the extracted server with the same native command.

## Try a request

When [the local health page](http://127.0.0.1:8080/health) shows `ok`, the server accepts `POST /v1/classify`. See the [Classify examples](../README.md#examples) for calls in your language and the [API reference](../SPECIFICATION.md#call-and-result) for the request and response fields.
