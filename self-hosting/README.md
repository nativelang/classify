# Install and start the Classify server

Install Classify on the same computer as your app.

## 1. Install once

With Python 3.8 or later, run the installer in an empty folder. It selects the server for your computer and downloads it with the model (about 1.6–2.5 GB).

**macOS 15+ or Debian 12-compatible Linux**

```sh
curl -fLO https://raw.githubusercontent.com/nativelang/classify/7856092ac26637fa7d1bac026df94b2020b3da10/self-hosting/start-classify.py && python3 start-classify.py install
```

<details>
<summary>Windows (PowerShell)</summary>

Install the [Microsoft Visual C++ v14 Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) for your processor if needed.

```powershell
curl.exe -fLO https://raw.githubusercontent.com/nativelang/classify/7856092ac26637fa7d1bac026df94b2020b3da10/self-hosting/start-classify.py
if ($LASTEXITCODE -eq 0) { py -3 start-classify.py install }
```

</details>

## 2. Start the server

In the same folder, run the start command.

```sh
python3 start-classify.py start
```

<details>
<summary>Windows (PowerShell)</summary>

```powershell
py -3 start-classify.py start
```

</details>

When [the health page](http://127.0.0.1:8080/health) says `ok`, leave the server running and try [your language example](../README.md#examples) in another terminal. Press Ctrl+C in the server terminal to stop it. Repeat step 2 to restart.

[Docker and manual installation](manual.md)
