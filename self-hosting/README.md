# Install and start the Classify server

Run these steps on the laptop or server where your app will run.

## 1. Install once

With Python 3.8 or later installed, open a terminal in an empty folder. These commands download Classify and its model (about 1.6–2.5 GB).

**macOS 15+ or Debian 12-compatible Linux**

```sh
curl -fLO https://raw.githubusercontent.com/nativelang/classify/a21ce7604c869e18e78145f2cd49a703346b56a9/self-hosting/start-classify.py && python3 start-classify.py install
```

<details>
<summary>Windows (PowerShell)</summary>

Install the [Microsoft Visual C++ v14 Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) for your processor if needed.

```powershell
curl.exe -fLO https://raw.githubusercontent.com/nativelang/classify/a21ce7604c869e18e78145f2cd49a703346b56a9/self-hosting/start-classify.py
if ($LASTEXITCODE -eq 0) { py -3 start-classify.py install }
```

</details>

## 2. Start the server

Run this command from the same folder.

```sh
python3 start-classify.py start
```

<details>
<summary>Windows (PowerShell)</summary>

```powershell
py -3 start-classify.py start
```

</details>

Leave the terminal open. When [the local health page](http://127.0.0.1:8080/health) says `ok` on that machine, run [your language example](../README.md#examples) in a second terminal. Press Ctrl+C to stop. To use Classify again, repeat step 2.

[Docker and manual installation](manual.md)
