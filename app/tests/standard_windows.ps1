param([Parameter(Mandatory)][string]$Cli)
$ErrorActionPreference = 'Stop'
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'The test process has an elevated token'
}
try {
    $state = & $Cli service start | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0 -or $state.phase -ne 'ready') { throw 'Non-elevated service startup failed' }
} finally {
    & $Cli service stop
    if ($LASTEXITCODE -ne 0) { throw 'Non-elevated service stop failed' }
}
Write-Output 'Started and stopped the service from a non-administrator token.'
