@echo off
setlocal EnableExtensions DisableDelayedExpansion
if exist "classify-server" (
    echo classify-server already exists. To install a new copy, run this installer from another folder. 1>&2
    exit /b 1
)

set "cpu="
for /f %%A in ('powershell.exe -NoProfile -Command "if ([Environment]::Is64BitOperatingSystem) { (Get-CimInstance Win32_Processor -ErrorAction Stop)[0].Architecture }"') do set "cpu=%%A"
if "%cpu%"=="9" (
    set "target=x86_64"
    set "digest=fa7fddf19ed3ee54294d9c791a0a9f8009954cdd7dee2b00532731d524bcea0b"
) else if "%cpu%"=="12" (
    set "target=aarch64"
    set "digest=7463ae150d1aa12fa2ce0f6b2c1a9c8723b56de862d1fe87180684648bd63030"
) else (
    echo Classify requires 64-bit Windows on x64 or ARM64. 1>&2
    exit /b 1
)

set "release=https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-standard-r1-manual"
set "archive=classify-server-0.1.0-dm-classify-standard-r1-%target%-pc-windows-msvc.zip"
set "stage=.classify-install-%RANDOM%-%RANDOM%"
mkdir "%stage%" || exit /b 1

for %%P in (0001 0002) do (
    echo Downloading part %%P of 0002...
    curl.exe -q --fail --location --retry 2 --output "%stage%\%%P" "%release%/%archive%.part-%%P-of-0002" || goto failed
)
copy /b "%stage%\0001"+"%stage%\0002" "%stage%\server.zip" >nul || goto failed
del "%stage%\0001" "%stage%\0002" || goto failed

powershell.exe -NoProfile -Command "if ((Get-FileHash -LiteralPath '%stage%\server.zip' -Algorithm SHA256 -ErrorAction Stop).Hash -ne '%digest%') { throw 'Archive checksum failed.' }" || goto failed
mkdir "%stage%\server" || goto failed
tar.exe -xf "%stage%\server.zip" -C "%stage%\server" || goto failed
powershell.exe -NoProfile -Command "$ErrorActionPreference = 'Stop'; [IO.Directory]::Move('%stage%\server', 'classify-server')" || goto failed
rmdir /s /q "%stage%"
echo Installed. Start the server with .\classify-server\classify.exe serve
exit /b 0

:failed
rmdir /s /q "%stage%"
echo Classify installation failed. 1>&2
exit /b 1
