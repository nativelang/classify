@echo off
setlocal EnableExtensions DisableDelayedExpansion
rem Run the same pinned installer included in the Node and Python packages.
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference = 'Stop';" ^
  "$script = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString() + '.ps1');" ^
  "try {" ^
  "  curl.exe -q --fail --location --silent --show-error --proto '=https' --proto-redir '=https' -o $script 'https://raw.githubusercontent.com/nativelang/classify/42f5e74c3f6d8cd9e48ace30c6807548db0662dd/app/install.ps1';" ^
  "  if ($LASTEXITCODE -ne 0) { throw 'Could not download installer' };" ^
  "  if ((Get-FileHash -LiteralPath $script -Algorithm SHA256).Hash -ne '52c8e4f82a8feadd466190f6f64f158f29d60850145c0e6688d43bb71dc8daab') { throw 'Installer checksum failed' };" ^
  "  & $script -Server" ^
  "} finally { if (Test-Path -LiteralPath $script) { Remove-Item -LiteralPath $script } }"
exit /b %errorlevel%
