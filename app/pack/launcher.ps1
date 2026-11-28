if (!$Server -and $env:NATIVELANG_CLASSIFY_SERVICE -eq '1') {
    $cpu = (Get-CimInstance Win32_Processor)[0].Architecture
    switch ($cpu) {
@WINDOWS_TARGETS@
        default { throw 'Unsupported Classify service platform' }
    }
    $bin = Join-Path $env:USERPROFILE '.nativelang\classify\bin'
    [void][IO.Directory]::CreateDirectory($bin)
    $cli = Join-Path $bin 'classify.exe'
    $stamp = Join-Path $bin 'service.version'
    $lock = $null
    try {
        while (!$lock) {
            try { $lock = [IO.File]::Open((Join-Path $bin 'install.lock'), 'OpenOrCreate', 'Write', 'None') }
            catch [IO.IOException] { if (($_.Exception.HResult -band 65535) -ne 32) { throw }; Start-Sleep -Milliseconds 100 }
        }
        if (!(Test-Path -LiteralPath $cli) -or !(Test-Path -LiteralPath $stamp) -or [IO.File]::ReadAllText($stamp) -ne $sha) {
            $stage = Join-Path $bin ([guid]::NewGuid().ToString())
            [void][IO.Directory]::CreateDirectory($stage)
            try {
                $archive = Join-Path $stage 'sdk.tgz'
                & "$env:SystemRoot\System32\curl.exe" -q -fsSL --proto '=https' --proto-redir '=https' --retry 2 -o $archive "https://github.com/nativelang/classify/releases/download/service-v1.0.0/classify-service-$target.tar.gz"
                if ($LASTEXITCODE -ne 0 -or (Get-FileHash $archive -Algorithm SHA256).Hash -ne $sha) { throw 'Classify service download failed verification' }
                & "$env:SystemRoot\System32\tar.exe" -xzf $archive -C $stage
                if ($LASTEXITCODE -ne 0) { throw 'Incomplete Classify service archive' }
                Move-Item -Force -LiteralPath (Join-Path $stage 'LICENSE.txt') -Destination (Join-Path $bin 'service-LICENSE.txt')
                Move-Item -Force -LiteralPath (Join-Path $stage 'classify.exe') -Destination $cli
                [IO.File]::WriteAllText($stamp, $sha)
            } finally { Remove-Item -Recurse -Force -LiteralPath $stage }
        }
    } finally { if ($lock) { $lock.Dispose() } }
    Write-Output $cli
    return
}
