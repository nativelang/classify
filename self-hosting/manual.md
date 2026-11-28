# Docker and manual installation

Use Docker if you want Classify to start whenever Docker starts. Download a native archive if you want to pick a specific model or build. Both include the model and can serve requests offline. For a local server that chooses the download for your computer, use the [server quick start](README.md).

## Choose and verify a download

<a id="compact-r3"></a>

### Compact

Compact is the smaller model used by the language packages. Download one file into an empty folder. For Docker, choose the processor used by your Linux containers. For a native server, choose the processor and operating system of the computer that will run it.

| Download | SHA-256 |
| --- | --- |
| [Docker image · ARM64](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3/classify-image-0.1.0-dm-classify-compact-r3-linux-arm64.oci.tar) | `a432db5bd87427cba5f046641c92a3aad49b4abd40afbed7c0761d18bd9e3028` |
| [Docker image · AMD64](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3/classify-image-0.1.0-dm-classify-compact-r3-linux-amd64.oci.tar) | `7a0cfc2eb99c8f3fd014671af4c062de97b0b247881b8a28fee0bd525475d128` |
| [Native server · Apple Silicon](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.1-dm-classify-compact-r3/classify-server-0.1.1-dm-classify-compact-r3-aarch64-apple-darwin.tar.gz) | `666b9583ff4794f1537af8b6d2b60e98c383ebb87892b990066c68a1c02d219b` |
| [Native server · Linux ARM64](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.1-dm-classify-compact-r3/classify-server-0.1.1-dm-classify-compact-r3-aarch64-unknown-linux-gnu.tar.gz) | `2daf0fde2c1a663c31e9913b0563070087d6bc8e3a02e2bb3cd0bf3295c9894a` |
| [Native server · Linux x64](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.1-dm-classify-compact-r3/classify-server-0.1.1-dm-classify-compact-r3-x86_64-unknown-linux-gnu.tar.gz) | `f245e326547df8a090ea6a2d551c0658409346451f764528b6f837dd391d74c5` |
| [Native server · Intel Mac](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3-desktop/classify-server-0.1.0-dm-classify-compact-r3-x86_64-apple-darwin.tar.gz) | `64f13c257f242d79348f75f8d5621ffb8a938d7ea4d88000a5dcf71ed0709988` |
| [Native server · Windows x64](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3-desktop/classify-server-0.1.0-dm-classify-compact-r3-x86_64-pc-windows-msvc.zip) | `683798bee161c422bd97391bd8ed194f3922314609a703d0f3a048ea94dd99cb` |
| [Native server · Windows ARM64](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3-desktop/classify-server-0.1.0-dm-classify-compact-r3-aarch64-pc-windows-msvc.zip) | `b5ef5a9dbccef6f4a69de7bb1248f6f3cb6a1fe6ffb4b20c02b41254b24aa7a5` |

Run `shasum -a 256 FILENAME` on macOS or `sha256sum FILENAME` on Linux, replacing `FILENAME` with the downloaded name. In PowerShell, use `Get-FileHash FILENAME -Algorithm SHA256`. Continue only if the result matches the table.

<a id="standard-r1"></a>

### Standard

Choose Standard for the larger model. Standard also supports Apple Silicon, Linux x64 and ARM64, and Linux containers on AMD64 and ARM64. Download both parts of the archive you choose.

For the [Standard servers and Docker images](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-standard-r1-manual), the SHA-256 checksum for `downloads.json` is `01430ddd1a9ba0d319e561c95be4dfbe978b3f27686b6fd5b67acd091e59bf67`. Choose a `classify-server-` archive to run directly or a `classify-image-` archive for Docker. The [accelerated server releases](#optional-accelerated-servers) have their own index checksums.

### Join the two parts

1. In an empty folder, save `downloads.json` and both parts of your chosen archive **from the same release**. Allow space for the parts, the complete archive and its extracted contents.
2. Check `downloads.json` with `shasum -a 256 downloads.json` on macOS, `sha256sum downloads.json` on Linux, or `Get-FileHash downloads.json -Algorithm SHA256` in PowerShell. Continue only if the result matches the index checksum listed for that release.
3. Open the verified index. In `archives`, find your archive’s `name` and its own `sha256` (the digest for the complete file). Set the first two variables below to those values. The examples join part 1 followed by part 2 and give the output its final name only after the complete file passes verification.

**macOS (Apple Silicon server)**

```sh
archive='classify-server-0.1.0-dm-classify-standard-r1-aarch64-apple-darwin.tar.gz'
expected='3eedbb8f729369754ace0d6daa83aea26d322723d0d499956c011b320701ba88'
cat "$archive.part-0001-of-0002" "$archive.part-0002-of-0002" > "$archive.partial" &&
  printf '%s  %s\n' "$expected" "$archive.partial" | shasum -a 256 -c - &&
  mv "$archive.partial" "$archive"
```

**Linux (x64 server)**

```sh
archive='classify-server-0.1.0-dm-classify-standard-r1-x86_64-unknown-linux-gnu.tar.gz'
expected='bcfb9216007748678c417f517f19405c661c6e5d3fe48fc882690e5824c668fe'
cat "$archive.part-0001-of-0002" "$archive.part-0002-of-0002" > "$archive.partial" &&
  printf '%s  %s\n' "$expected" "$archive.partial" | sha256sum -c - &&
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

Use Docker in Linux container mode. In the download folder, load your verified `.oci.tar` file. This example starts Compact on ARM64.

```sh
docker load -i classify-image-0.1.0-dm-classify-compact-r3-linux-arm64.oci.tar
docker run --rm -d --name classify-server -p 127.0.0.1:8080:8080 classify:0.1.0-dm-classify-compact-r3-linux-arm64
```

To use port `9090` on your computer, use `-p 127.0.0.1:9090:8080`. Check [the health page on port 9090](http://127.0.0.1:9090/health) and use port `9090` in your app.

For AMD64 or Standard, substitute your image filename in the first command and the name printed after `Loaded image:` in the second. [Try a request](#try-a-request), then stop the server with `docker stop classify-server`.

### Run across restarts

To start Classify whenever Docker starts, use a named container with a restart policy. After loading the ARM64 image, run this command in place of the temporary container command above.

```sh
docker run -d --name classify-server --restart unless-stopped -p 127.0.0.1:8080:8080 classify:0.1.0-dm-classify-compact-r3-linux-arm64
```

Configure Docker to start on boot or login. To pause the service, use `docker stop classify-server`. Resume with `docker start classify-server`.

## Native server

<a id="native-macos-or-linux"></a>

From the folder containing your verified archive, follow the commands for your computer. Keep just one complete server archive in that folder so the filename pattern selects your download.

**Linux ARM64 or x64.** Use Debian 12 or a distribution with compatible glibc and C++ runtime libraries.

```sh
mkdir classify-server
tar -xzf classify-server-*-unknown-linux-gnu*.tar.gz -C classify-server
cd classify-server
./classify serve --listen 127.0.0.1:8080
```

**macOS 15 or later.**

```sh
mkdir classify-server
tar -xzf classify-server-*-apple-darwin*.tar.gz -C classify-server
cd classify-server
./classify serve --listen 127.0.0.1:8080
```

<details>
<summary>Windows (PowerShell)</summary>

Install the current [Microsoft Visual C++ v14 Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) for your server architecture. Download and verify the Compact or Standard server for your processor. From the folder containing the complete ZIP, run the following commands.

```powershell
mkdir classify-server
$archive = (Get-Item .\classify-server-*-pc-windows-msvc.zip).FullName
tar.exe -xf $archive -C classify-server
if ($LASTEXITCODE -ne 0) { throw 'Extraction failed' }
cd classify-server
.\classify.exe serve --listen 127.0.0.1:8080
```

</details>

Keep the extracted files together and leave the terminal open while serving. Press Ctrl+C to stop.

### Optional accelerated servers

Use Metal on Apple Silicon with a compatible GPU and macOS 26 or later. Use the Linux x86-64-v3 build on a processor that supports that instruction set.

| Platform | Compact server | Standard server | Standard `downloads.json` SHA-256 |
| --- | --- | --- | --- |
| Apple Silicon | [Metal](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-compact-r3-metal) | [Metal, two parts](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-standard-r1-metal-manual) | `295399c5c82803f87ed131022e7d8302256bf50e3461712c0c35fd1d75a118f7` |
| Linux x64 | [x86-64-v3](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-compact-r3-v3) | [x86-64-v3, two parts](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-standard-r1-v3-manual) | `878b71990eafc1b223d29d546a4ddb84f4f3c0864a4a6fb18e6205234bf971e4` |

For Compact, verify `downloads.json` using the [Compact accelerated index checksums](../RELEASES.md#free-downloads), then check the server archive against its entry. For Standard, [join the two parts](#join-the-two-parts) using the index checksum for that server above. Start the extracted server with the same native command.

## Try a request

When [the local health page](http://127.0.0.1:8080/health) shows `ok`, the server accepts `POST /v1/classify`. In a second terminal, [send the movie request](../SPECIFICATION.md#call-and-result) and look for `negative` in the `category` field.
