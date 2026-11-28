@echo off
setlocal EnableExtensions DisableDelayedExpansion
rem Run the same pinned installer included in the Node and Python packages.
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference = 'Stop';" ^
  "$script = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString() + '.ps1');" ^
  "try {" ^
  "  curl.exe -q --fail --location --silent --show-error --proto '=https' --proto-redir '=https' -o $script 'https://raw.githubusercontent.com/nativelang/classify/c2f9d6bb7d290055a399917599943e227dc52084/app/install.ps1';" ^
  "  if ($LASTEXITCODE -ne 0) { throw 'Could not download installer' };" ^
  "  if ((Get-FileHash -LiteralPath $script -Algorithm SHA256).Hash -ne '45503aa11aad6c2a3ca6de86d5b5847de52c3e96a3890e12937401a7e7f02023') { throw 'Installer checksum failed' };" ^
  "  & $script -Server" ^
  "} finally { if (Test-Path -LiteralPath $script) { Remove-Item -LiteralPath $script } }"
exit /b %errorlevel%
