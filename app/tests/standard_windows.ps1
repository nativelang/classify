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
        $log = Join-Path $env:USERPROFILE '.nativelang/classify/service/service.log'
        $diagnostic = if (Test-Path $log) { Get-Content $log -Tail 12 | Out-String }
        [IO.File]::WriteAllText($Result, ($_.Exception.Message + " " + $diagnostic))
        exit 1
    }
    return
}

# Hosted images can keep their built-in administrator elevated even with a
# limited scheduled task. Exercise registration as a separate ordinary user.
$name = 'classify' + [guid]::NewGuid().ToString('N').Substring(0, 10)
$work = Join-Path $env:PUBLIC $name
[void][IO.Directory]::CreateDirectory($work)
$password = ConvertTo-SecureString ([guid]::NewGuid().ToString('N') + 'aA!9') -AsPlainText -Force
try {
    $user = New-LocalUser -Name $name -Password $password -AccountExpires (Get-Date).AddHours(1)
    Add-LocalGroupMember -SID 'S-1-5-32-545' -Member $user -ErrorAction SilentlyContinue
    $credential = [pscredential]::new("$env:COMPUTERNAME\$name", $password)
    $acl = Get-Acl -LiteralPath $work
    $rule = [Security.AccessControl.FileSystemAccessRule]::new($user.SID, 'Modify', 'ContainerInherit,ObjectInherit', 'None', 'Allow')
    $acl.AddAccessRule($rule)
    Set-Acl -LiteralPath $work -AclObject $acl
    Copy-Item -LiteralPath $Cli -Destination "$work/classify.exe"
    Copy-Item -LiteralPath $PSCommandPath -Destination "$work/test.ps1"
    $shell = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
    $arguments = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "{0}\test.ps1" -Cli "{0}\classify.exe" -Result "{0}\result.txt"' -f $work
    $proc = Start-Process -FilePath $shell -ArgumentList $arguments -Credential $credential -LoadUserProfile -WorkingDirectory $work -PassThru
    if (!$proc.WaitForExit(600000)) { throw 'Standard-user test timed out' }
    $resultText = [IO.File]::ReadAllText("$work/result.txt")
    if ($resultText -ne 'passed') { throw $resultText }
    Write-Output 'Started and stopped the service using a standard local account.'
} finally {
    if ($user) { Remove-LocalUser -SID $user.SID }
    Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
}
