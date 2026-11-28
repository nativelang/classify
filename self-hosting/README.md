# Run Classify locally

Start the server once and your apps can send it text. If [the server already says `ok`](http://127.0.0.1:8080/health), go straight to [your language example](../README.md#examples).

You'll need Python 3.8 or later. Open a terminal in an empty folder and run the commands for your computer. The first run downloads the server and model (about 1.6–2.5 GB).

**macOS 15+ or Debian 12-compatible Linux**

```sh
curl -fLO https://raw.githubusercontent.com/nativelang/classify/263d5307015adf4bfc55372a55063946e2515ef3/self-hosting/start-classify.py && python3 start-classify.py
```

**Windows (PowerShell)**

Install the [Microsoft Visual C++ v14 Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) for your processor if needed.

```powershell
curl.exe -fLO https://raw.githubusercontent.com/nativelang/classify/263d5307015adf4bfc55372a55063946e2515ef3/self-hosting/start-classify.py
if ($LASTEXITCODE -eq 0) { py -3 start-classify.py }
```

Leave the terminal open. When [the health page](http://127.0.0.1:8080/health) shows `ok`, run [your language example](../README.md#examples) in a second terminal. Press Ctrl+C to stop the server. Next time, run `python3 start-classify.py` (Windows: `py -3 start-classify.py`) from the same folder.

[Docker and manual installation](manual.md)
