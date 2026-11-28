param([Parameter(Mandatory)][string]$Definition)
$ErrorActionPreference = 'Stop'
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
if ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'The test process has an elevated token'
}
$scheduler = New-Object -ComObject Schedule.Service
$scheduler.Connect()
$folder = $scheduler.GetFolder('\')
$task = $scheduler.NewTask(0)
$task.XmlText = [IO.File]::ReadAllText($Definition)
if ($task.Principal.RunLevel -ne 0 -or $task.Principal.LogonType -ne 3) {
    throw 'The service definition must request the interactive user at least privilege'
}
# Use the shipping task definition and binary. A status query avoids starting
# a second daemon while the managed lifecycle test owns the live instance.
$task.Actions.Item(1).Arguments = 'service status'
$name = 'NativeLang.Classify.Test.' + [guid]::NewGuid().ToString('N')
$registered = $folder.RegisterTaskDefinition($name, $task, 2, $identity.User.Value, $null, 3, $null)
try {
    [void]$registered.Run($null)
    $deadline = (Get-Date).AddMinutes(1)
    do {
        Start-Sleep -Milliseconds 400
        $registered = $folder.GetTask($name)
        if ($registered.LastRunTime.Year -gt 2000 -and $registered.State -eq 3 -and $registered.LastTaskResult -eq 0) { break }
        if ((Get-Date) -ge $deadline) { throw "Task execution failed with result $($registered.LastTaskResult)" }
    } while ($true)
} finally {
    $folder.DeleteTask($name, 0)
}
Write-Output 'Verified that a non-administrator can register, run and remove the service task.'
