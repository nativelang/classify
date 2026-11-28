# Classify from C

The [C example](classify.c) asks whether “This is a terrible movie” is `positive`, `negative` or `neutral`. It loads the model in your program and prints a JSON result. You can run it offline after downloading two files.

## Download the SDK and model

Start in the root of a fresh Classify checkout. Download **only the SDK archive and model ZIP** for your platform into that directory so the extraction commands select the right files. Match the SDK to the architecture of the app you are building. On Linux and macOS, `uname -m` prints `aarch64` or `arm64` for ARM64 and `x86_64` for x64.

| Platform | Portable C SDK | Model ZIP |
| --- | --- | --- |
| Linux | [ARM64 SDK][linux-arm] · [x64 SDK][linux-x64] | [Compact][compact] |
| macOS 15+ on Apple Silicon | [ARM64 SDK][mac-arm] | [Compact][compact] |
| macOS 15+ on Intel | [x64 SDK][mac-x64] | [Standard][standard] |
| Windows | [ARM64 SDK][win-arm] · [x64 SDK][win-x64] | [Standard][standard] |

Check the model ZIP against its published SHA-256. For the SDK, check the archive against the runtime entry for your platform in that model’s verified manifest. [Checksums and manifests](../../RELEASES.md#free-downloads)

## Linux

Use a C compiler and glibc and libstdc++ compatible with Debian 12 (Bookworm). On Debian, `apt install build-essential unzip` installs the build and extraction tools.

```sh
mkdir sdk
tar -xzf classify-runtime-0.1.0-*-unknown-linux-gnu.tar.gz -C sdk
unzip -q dm-classify-compact-r3.zip -d model
cc -std=c11 -Isdk/include examples/c/classify.c -Lsdk/lib -lclassify_core \
  '-Wl,-rpath,$ORIGIN/sdk/lib' -o classify-example
./classify-example model/profile.json
```

Keep the single quotes around the linker flag so Linux looks for the library relative to the executable. The Compact model returned `"category":"negative"` and `"source":"local"` on both ARM64 and x64.

## macOS

Install the Xcode Command Line Tools if you need a C compiler (`xcode-select --install`). Use the SDK and model for your Mac from the table.

```sh
mkdir sdk
tar -xzf classify-runtime-0.1.0-*-apple-darwin.tar.gz -C sdk
unzip -q dm-classify-*.zip -d model
cc -std=c11 -Isdk/include examples/c/classify.c -Lsdk/lib -lclassify_core \
  -Wl,-rpath,@executable_path/sdk/lib -o classify-example
./classify-example model/profile.json
```

On Apple Silicon the Compact model returned `"category":"negative"`.

## Windows

Open a Visual Studio 2022 Developer PowerShell targeting the SDK architecture. Install the matching [Microsoft Visual C++ v14 Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) on the machine that will run the app.

```powershell
$sdkZip = (Get-Item .\classify-runtime-0.1.0-*-pc-windows-msvc.zip).FullName
Expand-Archive -LiteralPath $sdkZip -DestinationPath sdk
mkdir model
tar.exe -xf dm-classify-standard-r1.zip -C model
cl /nologo /std:c11 /TC /Isdk\include examples\c\classify.c sdk\lib\classify_core.lib /Fe:classify-example.exe
Copy-Item sdk\bin\classify_core.dll .
.\classify-example.exe model\profile.json
```

The import library is used when building. The executable needs the DLL when it runs. On every platform, keep the extracted model files and license notices together.

[linux-arm]: https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3/classify-runtime-0.1.0-aarch64-unknown-linux-gnu.tar.gz
[linux-x64]: https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3/classify-runtime-0.1.0-x86_64-unknown-linux-gnu.tar.gz
[mac-arm]: https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-compact-r3/classify-runtime-0.1.0-aarch64-apple-darwin.tar.gz
[mac-x64]: https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-standard-r1/classify-runtime-0.1.0-x86_64-apple-darwin.tar.gz
[win-arm]: https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-standard-r1/classify-runtime-0.1.0-aarch64-pc-windows-msvc.zip
[win-x64]: https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-standard-r1/classify-runtime-0.1.0-x86_64-pc-windows-msvc.zip
[compact]: https://huggingface.co/nativelang/classify-models/resolve/47ab2a3f4280647a64e6ac307f262a74a1b4694e/models/dm-classify-compact-r3.zip
[standard]: https://huggingface.co/nativelang/classify-models/resolve/47ab2a3f4280647a64e6ac307f262a74a1b4694e/models/dm-classify-standard-r1.zip
