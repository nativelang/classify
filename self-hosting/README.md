# Install and start the Classify server

## 1. Install

Open a terminal on the computer where your app will run. In an empty folder, run the installer. It downloads the server and model (about 1.6–2.5 GB) into `classify-server`.

**macOS 15+ or Debian 12-compatible Linux**

```sh
curl -fLO https://raw.githubusercontent.com/nativelang/classify/5ce35e00d97c2d89f97d91e094a094e9e310d08c/self-hosting/install.sh && sh install.sh
```

<details>
<summary>Windows</summary>

In PowerShell, run the installer.

```powershell
curl.exe -fLO https://raw.githubusercontent.com/nativelang/classify/5ce35e00d97c2d89f97d91e094a094e9e310d08c/self-hosting/install.cmd
if ($LASTEXITCODE -eq 0) { .\install.cmd }
```

If Windows reports a missing Visual C++ runtime DLL, install the [Microsoft Visual C++ v14 Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) for your processor.

</details>

## 2. Start the server

Run the server from the same folder.

```sh
./classify-server/classify serve
```

<details>
<summary>Windows</summary>

```powershell
.\classify-server\classify.exe serve
```

</details>

When [the health page](http://127.0.0.1:8080/health) says `ok`, try [your language example](../README.md#examples) in another terminal. Press Ctrl+C in the server terminal to stop it.

<details>
<summary>Use a different port</summary>

The default port is `8080`. To use `9090`, add `--listen 127.0.0.1:9090` to the start command.

```sh
./classify-server/classify serve --listen 127.0.0.1:9090
```

Check [the health page on port 9090](http://127.0.0.1:9090/health) and use `http://127.0.0.1:9090/v1/classify` in your app.

</details>

[Docker and manual installation](manual.md)
