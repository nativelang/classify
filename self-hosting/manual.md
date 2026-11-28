# Run Classify on your own machine

The Classify server accepts text and categories over HTTP. Each server download includes its model and can run offline after installation. The commands below keep the service on your computer at `127.0.0.1:8080`.

Choose **compact r3** for a single-file Docker image or a native server for Apple Silicon, Linux ARM64, or Linux x64. Choose **standard r1** for native Windows or Intel macOS. Standard also supports Apple Silicon, Linux ARM64, Linux x64 and Docker. You can use either model without an API key.

## Choose and verify a download

Start in an empty folder. For **compact r3**, download one file from the [portable release](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-compact-r3). Pick the server to run directly or the image for Docker’s Linux architecture.

| Install | File | SHA-256 |
| --- | --- | --- |
| Docker on Linux ARM64 | `classify-image-0.1.0-dm-classify-compact-r3-linux-arm64.oci.tar` | `a432db5bd87427cba5f046641c92a3aad49b4abd40afbed7c0761d18bd9e3028` |
| Docker on Linux AMD64 | `classify-image-0.1.0-dm-classify-compact-r3-linux-amd64.oci.tar` | `7a0cfc2eb99c8f3fd014671af4c062de97b0b247881b8a28fee0bd525475d128` |
| Apple Silicon Mac | `classify-server-0.1.0-dm-classify-compact-r3-aarch64-apple-darwin.tar.gz` | `64d0972c97a87128d4698aa2940b724f321094e476b41b18531aa93426395dd3` |
| Linux ARM64 | `classify-server-0.1.0-dm-classify-compact-r3-aarch64-unknown-linux-gnu.tar.gz` | `fe432526cb458c4df37603917e8c4e321c340e30b631b3f2571332998c674877` |
| Linux x64 | `classify-server-0.1.0-dm-classify-compact-r3-x86_64-unknown-linux-gnu.tar.gz` | `211b8fdb1637709e8ecb1a3c5d2be9de9b6c624cca18c8a6df93029477dc6d28` |

Check the file with `shasum -a 256 FILENAME` on macOS, `sha256sum FILENAME` on Linux, or `Get-FileHash FILENAME -Algorithm SHA256` in PowerShell. Continue only if it matches the value above.

For **standard r1**, use the [multipart server and Docker release](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-standard-r1-manual). Save `downloads.json`, `reassemble.py` and **both parts of your chosen archive** in one folder. Allow space for the parts, the restored archive and its extracted contents. The index SHA-256 is `01430ddd1a9ba0d319e561c95be4dfbe978b3f27686b6fd5b67acd091e59bf67`. Follow the [release’s Unix or PowerShell commands](https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-standard-r1-manual/README.txt) with that digest and the archive name from the index. They verify the helper before running it, then verify each part and the restored file. A complete Windows example follows below.

## Docker

Use Docker in Linux container mode. For ARM64, run these commands in the folder containing the verified image.

```sh
docker load -i classify-image-0.1.0-dm-classify-compact-r3-linux-arm64.oci.tar
docker run --rm -d --name classify-server -p 127.0.0.1:8080:8080 classify:0.1.0-dm-classify-compact-r3-linux-arm64
```

For AMD64, use `amd64` in place of `arm64`. For standard r1, use your restored `.oci.tar`. In either case, the last argument to `docker run` is the exact name printed after `Loaded image:` by `docker load`. [Try a request](#try-a-request), then stop the container with `docker stop classify-server`.

## Native server

For a compatible Apple Silicon Mac running macOS 26 or later, choose the [compact Metal server](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-compact-r3-metal) or the [standard Metal server](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-standard-r1-metal-manual). For Linux x64 with x86-64-v3 support, choose the [compact v3 server](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-compact-r3-v3) or the [standard v3 server](https://github.com/nativelang/classify-artifacts/releases/tag/v0.1.0-dm-classify-standard-r1-v3-manual). For compact, use the [packaging guide’s index fingerprints](../PACKAGING.md#free-downloads) and select the server archive. For standard, use the reassembly instructions from the chosen release with its index SHA-256.

| Standard server | SHA-256 of `downloads.json` |
| --- | --- |
| Metal | `295399c5c82803f87ed131022e7d8302256bf50e3461712c0c35fd1d75a118f7` |
| Linux x86-64-v3 | `878b71990eafc1b223d29d546a4ddb84f4f3c0864a4a6fb18e6205234bf971e4` |

<a id="native-macos-or-linux"></a>

**macOS or Linux.** The native Linux builds target Debian 12 and distributions with compatible glibc and C++ runtime libraries. Use the Docker image if your host lacks those libraries. Extract the verified server archive into its own directory. This example uses compact on Apple Silicon. On Linux or for standard r1, substitute your downloaded or restored server filename.

```sh
mkdir classify-server
tar -xzf classify-server-0.1.0-dm-classify-compact-r3-aarch64-apple-darwin.tar.gz -C classify-server
cd classify-server
./classify serve --listen 127.0.0.1:8080
```

**Windows (PowerShell).** Install the current [Microsoft Visual C++ v14 Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) for the server architecture you choose (x64 or ARM64). You’ll also need Python 3.8 or newer for reassembly. From the standard r1 release, download `downloads.json`, `reassemble.py` and the two parts whose names start with the archive below. For Windows on ARM64, use the `aarch64-pc-windows-msvc.zip` archive and its two matching parts.

```powershell
$Archive = 'classify-server-0.1.0-dm-classify-standard-r1-x86_64-pc-windows-msvc.zip'
$IndexHash = '01430ddd1a9ba0d319e561c95be4dfbe978b3f27686b6fd5b67acd091e59bf67'
if ((Get-FileHash downloads.json -Algorithm SHA256).Hash -ne $IndexHash) { throw 'Index verification failed' }
$Index = Get-Content downloads.json -Raw | ConvertFrom-Json
if ((Get-FileHash reassemble.py -Algorithm SHA256).Hash -ne $Index.helper.sha256) { throw 'Helper verification failed' }
python reassemble.py --index-sha256 $IndexHash --archive $Archive
if ($LASTEXITCODE -ne 0) { throw 'Archive verification failed' }
mkdir classify-server
tar.exe -xf $Archive -C classify-server
if ($LASTEXITCODE -ne 0) { throw 'Extraction failed' }
cd classify-server
.\classify.exe serve --listen 127.0.0.1:8080
```

Keep the extracted files together so the executable can find its model. To stop the native server, press Ctrl+C in its terminal.

## Try a request

With the native server running, open a second terminal. With Docker, use the same terminal. Ask it whether a movie review is positive, negative, or neutral. The local server requires no API key.

**Windows (PowerShell)**

```powershell
$review = '{"text":"This is a terrible movie","categories":["positive","negative","neutral"]}'
Invoke-RestMethod -Uri 'http://127.0.0.1:8080/v1/classify' -Method Post -ContentType 'application/json' -Body $review
```

**macOS or Linux**

```sh
curl --request POST 'http://127.0.0.1:8080/v1/classify' \
  --header 'Content-Type: application/json' \
  --data '{
    "text": "This is a terrible movie",
    "categories": ["positive", "negative", "neutral"]
  }'
```

With compact r3, the response shows `negative` for the category and `self_hosted` for the source. Try “I neither liked nor disliked this movie.” for a `neutral` match. Compact r3 returned `unknown` for “The movie starts at seven.” [All response fields](../SPECIFICATION.md#call-and-result)
