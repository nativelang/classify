@echo off
setlocal DisableDelayedExpansion
if "%~1"=="" goto default
if not "%~1"=="--port" goto usage
if "%~2"=="" goto usage
if not "%~3"=="" goto usage
"%~dp0classify.exe" serve --listen "127.0.0.1:%~2"
exit /b %errorlevel%
:default
"%~dp0classify.exe" serve
exit /b %errorlevel%
:usage
echo Usage: start.cmd [--port PORT] 1>&2
exit /b 2
