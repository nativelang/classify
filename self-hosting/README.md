# Install and start the Classify server

If several scripts use Classify, one server can keep the model loaded between runs. Each script sends its text and categories over HTTP and gets a result back.

To load the model directly in a C program, follow the [C example](../examples/c/). To run the server in a container, follow the [Docker guide](manual.md#docker).

## 1. Install

Open a terminal in an empty folder. The installer creates a `classify-server` folder and downloads Compact (about 1.6 GB) for your operating system and processor.

**macOS or Linux.** Use this command on macOS 15 or later (Apple Silicon or Intel) or Debian 12-compatible Linux (ARM64 or x64).

```sh
curl -fLO https://raw.githubusercontent.com/nativelang/classify/df1003c024ff9db2cb203589ed671c142d59f7bb/self-hosting/install.sh && sh install.sh
```

<details>
<summary>Windows</summary>

On x64 or ARM64 Windows, run this in PowerShell.

```powershell
curl.exe -fLO https://raw.githubusercontent.com/nativelang/classify/df1003c024ff9db2cb203589ed671c142d59f7bb/self-hosting/install.cmd
if ($LASTEXITCODE -eq 0) { .\install.cmd }
```

If Windows reports a missing Visual C++ runtime DLL, install the [Microsoft Visual C++ v14 Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) for your processor.

</details>

## 2. Start the server

From the same folder, start the server. It listens at `http://127.0.0.1:8080` by default.

```sh
./classify-server/start
```

On Windows, run `.\classify-server\start.cmd`.

## 3. Classify a movie review

Leave the server terminal open. When the [health page](http://127.0.0.1:8080/health) says `ok`, open a second terminal and [run the movie request](../SPECIFICATION.md#call-and-result). Look for `negative` in the `category` field. Press Ctrl+C in the server terminal when you’re done.

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

For the larger **Standard** model, [choose a server for your platform](manual.md#standard). To keep Classify running across restarts, [run it as a Docker service](manual.md#run-across-restarts).
