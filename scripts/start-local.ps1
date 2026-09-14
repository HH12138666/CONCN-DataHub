$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$runtimeRoot = Join-Path $projectRoot '.local/runtime'
$pythonExe = Join-Path $projectRoot '.venv/Scripts/python.exe'
New-Item -ItemType Directory -Force -Path $runtimeRoot | Out-Null
$backendPort = 8000
$portLine = Get-Content (Join-Path $projectRoot 'backend/.env') | Where-Object { $_ -match '^CONCN_PORT=([0-9]+)$' } | Select-Object -Last 1
if ($portLine) { $backendPort = [int]($portLine -split '=')[1] }
$saved = @{}
$statePath = Join-Path $runtimeRoot 'processes.json'
if (Test-Path -LiteralPath $statePath) {
    $previous = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    foreach ($property in $previous.PSObject.Properties) { $saved[$property.Name] = $property.Value }
}

if (-not (Get-NetTCPConnection -State Listen -LocalPort $backendPort -ErrorAction SilentlyContinue)) {
    $process = Start-Process -FilePath $pythonExe -ArgumentList '-X','utf8','app.py' -WorkingDirectory (Join-Path $projectRoot 'backend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeRoot 'backend.stdout.log') -RedirectStandardError (Join-Path $runtimeRoot 'backend.stderr.log') -PassThru
    $saved.backendPid = $process.Id
}
if (-not (Get-NetTCPConnection -State Listen -LocalPort 5173 -ErrorAction SilentlyContinue)) {
    $nodeExe = (Get-Command node.exe).Source
    $viteEntry = Join-Path $projectRoot 'frontend/node_modules/vite/bin/vite.js'
    $process = Start-Process -FilePath $nodeExe -ArgumentList "`"$viteEntry`"",'--host','127.0.0.1','--port','5173','--strictPort' -WorkingDirectory (Join-Path $projectRoot 'frontend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeRoot 'frontend.stdout.log') -RedirectStandardError (Join-Path $runtimeRoot 'frontend.stderr.log') -PassThru
    $saved.frontendPid = $process.Id
}
$worker = $null
if ($saved.workerPid) {
    $worker = Get-CimInstance Win32_Process -Filter "ProcessId=$($saved.workerPid)"
}
if (-not ($worker -and $worker.ExecutablePath -eq $pythonExe -and $worker.CommandLine -match 'datahub\.workers\.queue')) {
    $process = Start-Process -FilePath $pythonExe -ArgumentList '-X','utf8','-u','-m','datahub.workers.queue' -WorkingDirectory (Join-Path $projectRoot 'backend') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimeRoot 'worker.stdout.log') -RedirectStandardError (Join-Path $runtimeRoot 'worker.stderr.log') -PassThru
    $saved.workerPid = $process.Id
}
$saved | ConvertTo-Json | Set-Content -LiteralPath $statePath
for ($attempt = 0; $attempt -lt 15; $attempt++) {
    try {
        $health = Invoke-RestMethod "http://127.0.0.1:$backendPort/api/health" -TimeoutSec 3
        $page = Invoke-WebRequest 'http://127.0.0.1:5173/' -UseBasicParsing -TimeoutSec 3
        if ($health.status -eq 'ok' -and $page.StatusCode -eq 200) {
            Write-Output 'Ready: http://127.0.0.1:5173/data/view'
            Write-Output "Local website: http://127.0.0.1:$backendPort/"
            Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
                $_.AddressState -eq 'Preferred' -and $_.IPAddress -notlike '127.*' -and
                $_.IPAddress -notlike '169.254.*' -and $_.InterfaceAlias -notmatch 'vEthernet|ZeroTier'
            } | ForEach-Object { Write-Output "LAN candidate ($($_.InterfaceAlias)): http://$($_.IPAddress):$backendPort/ (requires matching firewall and same network)" }
            exit 0
        }
    } catch { }
    Start-Sleep -Seconds 1
}
throw 'Startup did not finish; inspect .local/runtime logs.'
