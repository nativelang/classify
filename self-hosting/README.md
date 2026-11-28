# Install and start the Classify server

## 1. Install

Open a terminal on the computer where your app will run. In an empty folder, run the installer. It downloads the server and model (about 1.6–2.5 GB) into `classify-server`.

**macOS 15+ or Debian 12-compatible Linux**

```sh
curl -fLO https://raw.githubusercontent.com/nativelang/classify/120966b8f282730af7f3e22b7e09c3e742a64c3c/self-hosting/install.sh && sh install.sh
```

<details>
<summary>Windows</summary>

In PowerShell, run the installer.

```powershell
curl.exe -fLO https://raw.githubusercontent.com/nativelang/classify/120966b8f282730af7f3e22b7e09c3e742a64c3c/self-hosting/install.cmd
if ($LASTEXITCODE -eq 0) { .\install.cmd }
```

If Windows reports a missing Visual C++ runtime DLL, install the [Microsoft Visual C++ v14 Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) for your processor.

</details>

## 2. Start the server

From the same folder, start the server. It listens at `http://127.0.0.1:8080` by default.

```sh
./classify-server/start
```

On Windows, run `.\classify-server\start.cmd`. The launcher starts the native executable (`classify serve` or `classify.exe serve`).

When [the health page](http://127.0.0.1:8080/health) says `ok`, [send a request](../SPECIFICATION.md#call-and-result) in another terminal. Press Ctrl+C in the server terminal to stop it.

### Use a different port

```sh
./classify-server/start --port 9090
```

On Windows, run `.\classify-server\start.cmd --port 9090`. Check [the health page on port 9090](http://127.0.0.1:9090/health) and use `http://127.0.0.1:9090/v1/classify` for requests.

<details>
<summary>Already installed Classify?</summary>

If your server folder is missing `start` or `start.cmd`, add just the launcher. Run this from the folder containing `classify-server`.

**macOS or Linux**

```sh
curl -fL https://raw.githubusercontent.com/nativelang/classify/90bbb5b0921ae8f013af100e08a100cf0dcdf45b/self-hosting/start -o classify-server/start && chmod +x classify-server/start
```

**Windows**

```powershell
curl.exe -fL https://raw.githubusercontent.com/nativelang/classify/90bbb5b0921ae8f013af100e08a100cf0dcdf45b/self-hosting/start.cmd -o classify-server/start.cmd
```

For a manually extracted archive, the native executable accepts `--listen`. For example, on macOS or Linux run `./classify-server/classify serve --listen 127.0.0.1:9090`.

</details>

For the larger **Standard r1** model, [choose a server for your platform](manual.md#standard-r1). To keep Classify running across restarts, [run it as a Docker service](manual.md#run-across-restarts).
