# Exercise the shipping manager with a filtered, non-administrator token on the CI VM.
param([Parameter(Mandatory)][string]$Cli, [string]$Result)
$ErrorActionPreference = 'Stop'
if ($Result) {
    try {
        $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
        if ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            throw 'The test process has an elevated token'
        }
        $state = & $Cli service start | ConvertFrom-Json
        if ($LASTEXITCODE -ne 0 -or $state.phase -ne 'ready') { throw 'Standard-user startup failed' }
        & $Cli service stop
        if ($LASTEXITCODE -ne 0) { throw 'Standard-user stop failed' }
        [IO.File]::WriteAllText($Result, 'passed')
    } catch {
        [IO.File]::WriteAllText($Result, $_.Exception.Message)
        exit 1
    }
    return
}

$name = 'NativeLang.CI.' + [guid]::NewGuid().ToString('N')
$file = Join-Path $env:TEMP ($name + '.txt')
$shell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
$arguments = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "{0}" -Cli "{1}" -Result "{2}"' -f $PSCommandPath, $Cli, $file
$action = New-ScheduledTaskAction -Execute $shell -Argument $arguments
$principal = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
try {
    Register-ScheduledTask -TaskName $name -Action $action -Principal $principal | Out-Null
    Start-ScheduledTask -TaskName $name
    $deadline = (Get-Date).AddMinutes(5)
    while (!(Test-Path -LiteralPath $file) -and (Get-Date) -lt $deadline) { Start-Sleep -Seconds 1 }
    $resultText = [IO.File]::ReadAllText($file)
    if ($resultText -ne 'passed') { throw $resultText }
    Write-Output 'Started and stopped the service using a non-administrator token.'
} finally {
    Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $file -ErrorAction SilentlyContinue
}
