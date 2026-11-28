@echo off
setlocal EnableExtensions DisableDelayedExpansion
rem Run the same pinned installer included in the Node and Python packages.
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference = 'Stop';" ^
  "$script = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString() + '.ps1');" ^
  "try {" ^
  "  curl.exe -q --fail --location --silent --show-error --proto '=https' --proto-redir '=https' -o $script 'https://raw.githubusercontent.com/nativelang/classify/112da1944a106872cc7ea2e3914b17b69c0ba568/app/install.ps1';" ^
  "  if ($LASTEXITCODE -ne 0) { throw 'Could not download installer' };" ^
  "  if ((Get-FileHash -LiteralPath $script -Algorithm SHA256).Hash -ne 'cd23b7ead525cb176e87186f93f8fdcc400157776971a3fffbb9cc9d5909c1df') { throw 'Installer checksum failed' };" ^
  "  & $script -Server" ^
  "} finally { if (Test-Path -LiteralPath $script) { Remove-Item -LiteralPath $script } }"
exit /b %errorlevel%
