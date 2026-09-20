# DocForge — bootstrap installer for Windows PowerShell.
#
# Usage (from anywhere):
#   irm https://raw.githubusercontent.com/dinaagz/DocForge/main/install.ps1 | iex
#
# Or from a local checkout:
#   .\install.ps1

$ErrorActionPreference = 'Stop'

$Repo   = 'dinaagz/DocForge'
$Branch = if ($env:DOCFORGE_BRANCH) { $env:DOCFORGE_BRANCH } else { 'main' }

function Info($m) { Write-Host "  › $m" -ForegroundColor Cyan }
function OK  ($m) { Write-Host "  ✓ $m" -ForegroundColor Green }
function Warn($m) { Write-Host "  ! $m" -ForegroundColor Yellow }
function Err ($m) { Write-Host "  ✗ $m" -ForegroundColor Red }

Write-Host "─────────────────────────────────────────────"
Write-Host "  DocForge installer"
Write-Host "─────────────────────────────────────────────"

# ── 1. Detect Python ≥ 3.9 ─────────────────────────────
$PythonBin = $null
foreach ($cand in @('python', 'python3', 'py')) {
    $exe = Get-Command $cand -ErrorAction SilentlyContinue
    if ($null -ne $exe) {
        $ver = & $exe.Source -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>$null
        if ($ver -match '^\d+\.\d+$') {
            $parts = $ver.Split('.')
            if ([int]$parts[0] -ge 3 -and [int]$parts[1] -ge 9) {
                $PythonBin = $exe.Source
                break
            }
        }
    }
}
if (-not $PythonBin) {
    Err "Aucun Python >= 3.9 detecte. Installez Python depuis https://python.org."
    exit 2
}
Info "Python: $PythonBin"

# ── 2. Locate source tree ─────────────────────────────
$Here = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
$Source = $null
if (Test-Path (Join-Path $Here 'docforge/_version.py')) {
    $Source = $Here
} else {
    Info "Aucun checkout local — telechargement de $Repo@$Branch"
    $Tmp = Join-Path $env:TEMP ("docforge-" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $Tmp -Force | Out-Null
    $Archive = Join-Path $Tmp 'src.zip'
    $Url = "https://codeload.github.com/$Repo/zip/refs/heads/$Branch"
    Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $Archive
    Expand-Archive -Path $Archive -DestinationPath $Tmp -Force
    $Source = (Get-ChildItem -Path $Tmp -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'docforge/_version.py') } | Select-Object -First 1).FullName
    if (-not $Source) {
        Err "Archive telechargee mais docforge/_version.py introuvable."
        exit 3
    }
    OK "Extrait dans $Source"
}

# ── 3. Call the Python installer ──────────────────────
$env:PYTHONPATH = $Source
Info "Installation de DocForge…"
& $PythonBin -m docforge.cli install --source $Source
if ($LASTEXITCODE -ne 0) { Err "Installation echouee (code $LASTEXITCODE)"; exit $LASTEXITCODE }

# ── 4. Path hint ──────────────────────────────────────
Write-Host ""
OK "Installation terminee."
Write-Host ""
& $PythonBin -c "from docforge.installer.bootstrap import path_hint; print('  '+path_hint())"
Write-Host ""
Write-Host "Verifiez :"
Write-Host "  docforge --version"
Write-Host "  docforge doctor"
