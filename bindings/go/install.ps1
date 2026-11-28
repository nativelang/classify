# Install a pinned native build. In package mode stdout is the UTF-8 executable path.
param([switch]$Server)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
if (!$Server -and $env:NATIVELANG_CLASSIFY_SERVICE -eq '1') {
    $cpu = (Get-CimInstance Win32_Processor)[0].Architecture
    switch ($cpu) {
        12 { $target = 'windows-arm64'; $sha = '99519421a468ba933382f55e0700983331e40eb4a984939d6b28372eaab22645' }
        9 { $target = 'windows-amd64'; $sha = 'd918b2055e456568ddafd82318baa607cb0e4cba3be4bff668b724baa45ab31f' }
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
$releases = @'
platform,target,version,model,tag,parts,sha256
Darwin/arm64,aarch64-apple-darwin,0.1.1,compact-r3,v0.1.1-dm-classify-compact-r3,1,666b9583ff4794f1537af8b6d2b60e98c383ebb87892b990066c68a1c02d219b
Darwin/x86_64,x86_64-apple-darwin,0.1.0,compact-r3,v0.1.0-dm-classify-compact-r3-desktop,1,64f13c257f242d79348f75f8d5621ffb8a938d7ea4d88000a5dcf71ed0709988
Linux/aarch64,aarch64-unknown-linux-gnu,0.1.1,compact-r3,v0.1.1-dm-classify-compact-r3,1,2daf0fde2c1a663c31e9913b0563070087d6bc8e3a02e2bb3cd0bf3295c9894a
Linux/x86_64,x86_64-unknown-linux-gnu,0.1.1,compact-r3,v0.1.1-dm-classify-compact-r3,1,f245e326547df8a090ea6a2d551c0658409346451f764528b6f837dd391d74c5
Windows/ARM64,aarch64-pc-windows-msvc,0.1.0,compact-r3,v0.1.0-dm-classify-compact-r3-desktop,1,b5ef5a9dbccef6f4a69de7bb1248f6f3cb6a1fe6ffb4b20c02b41254b24aa7a5
Windows/AMD64,x86_64-pc-windows-msvc,0.1.0,compact-r3,v0.1.0-dm-classify-compact-r3-desktop,1,683798bee161c422bd97391bd8ed194f3922314609a703d0f3a048ea94dd99cb
'@ | ConvertFrom-Csv
$cpu = (Get-CimInstance Win32_Processor)[0].Architecture
$platform = switch ($cpu) { 9 { 'Windows/AMD64' } 12 { 'Windows/ARM64' } }
$nativeSystem = if ([Environment]::Is64BitProcess) { "$env:SystemRoot\System32" } else { "$env:SystemRoot\Sysnative" }
$release = $releases | Where-Object platform -eq $platform
if (!$release -or ![Environment]::Is64BitOperatingSystem) { throw 'Classify requires x64 or ARM64 Windows.' }
$model = "dm-classify-$($release.model)"
$tag = $release.tag
$root = if ($Server) { (Get-Location).ProviderPath } else { Join-Path $env:USERPROFILE ".nativelang\classify\$tag" }
$target = $release.target
$folder = if ($Server) { 'classify-server' } else { $target }
$install = Join-Path $root $folder
$exe = Join-Path $install 'classify.exe'
function Test-Install($dir) {
    foreach ($file in 'classify.exe', 'model/profile.json', 'model/model.gguf') {
        if (!(Test-Path -LiteralPath (Join-Path $dir $file) -PathType Leaf)) { return $false }
    }
    return $true
}
function Get-Download($url, $file) {
    & "$nativeSystem\curl.exe" -q --fail --location --silent --show-error --retry 2 --proto '=https' --proto-redir '=https' --output $file $url
    if ($LASTEXITCODE -ne 0) { throw "Download failed for $url" }
}
function Test-Digest($file, $expected) {
    if ((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash -ne $expected) { throw "Checksum failed for $file" }
}
if (!$Server -and (Test-Install $install)) { Write-Output $exe; return }
[void][IO.Directory]::CreateDirectory($root)
$lock = $null
$stage = $null
try {
    if (!$Server) {
        $lockFile = Join-Path $root ".$target.lock"
        while (!$lock) {
            try { $lock = [IO.File]::Open($lockFile, 'OpenOrCreate', 'Write', 'None') }
            catch [IO.IOException] {
                if (($_.Exception.HResult -band 0xffff) -ne 32) { throw }
                Start-Sleep -Milliseconds 250
            }
        }
        if (Test-Install $install) { Write-Output $exe; return }
    }
    if (Test-Path -LiteralPath $install) { throw "Installation folder already exists at $install. Move it aside before trying again." }
    # Cache installs hold the lock, so an interrupted download can be discarded on retry.
    $stage = if ($Server) { Join-Path $root ('.classify-' + [guid]::NewGuid()) } else { Join-Path $root ".$target.partial" }
    if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
    [void][IO.Directory]::CreateDirectory($stage)
    $archive = Join-Path $stage 'server.zip'
    $name = "classify-server-$($release.version)-$model-$target.zip"
    $url = "https://github.com/nativelang/classify-artifacts/releases/download/$tag"
    [Console]::Error.WriteLine("Downloading $model for $target...")
    $parts = [int]$release.parts
    if ($parts -eq 1) { Get-Download "$url/$name" $archive }
    else {
        $partFile = Join-Path $stage 'part'
        for ($i = 1; $i -le $parts; $i++) {
            $suffix = 'part-{0:d4}-of-{1:d4}' -f $i, $parts
            if ($i -eq 1) { Get-Download "$url-manual/$name.$suffix" $archive; continue }
            Get-Download "$url-manual/$name.$suffix" $partFile
            $out = [IO.File]::Open($archive, 'Append', 'Write')
            try {
                $part = [IO.File]::OpenRead($partFile)
                try { $part.CopyTo($out) } finally { $part.Dispose() }
            } finally { $out.Dispose() }
            [IO.File]::Delete($partFile)
        }
    }
    Test-Digest $archive $release.sha256
    $unpacked = Join-Path $stage 'unpacked'
    [void][IO.Directory]::CreateDirectory($unpacked)
    & "$nativeSystem\tar.exe" -xf $archive -C $unpacked
    if ($LASTEXITCODE -ne 0 -or !(Test-Install $unpacked)) { throw 'Incomplete Classify archive.' }
    if ($Server) {
        $launcher = Join-Path $unpacked 'start.cmd'
        Get-Download 'https://raw.githubusercontent.com/nativelang/classify/90bbb5b0921ae8f013af100e08a100cf0dcdf45b/self-hosting/start.cmd' $launcher
        Test-Digest $launcher 'f892d07461aaa995f6befd45c54e1e38b81d656a5f4ac30f92c0dc5de7d7ae5c'
    }
    [IO.Directory]::Move($unpacked, $install)
} finally {
    try { if ($stage -and (Test-Path -LiteralPath $stage)) { Remove-Item -LiteralPath $stage -Recurse -Force } }
    finally { if ($lock) { $lock.Dispose() } }
}
if ($Server) { Write-Output 'Installed. Start the server with .\classify-server\start.cmd' }
else { Write-Output $exe }
