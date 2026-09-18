# DocForge installer (PowerShell).
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

Write-Host "── DocForge installer ──"

python -m pip install --user -r requirements.txt

python -m docforge.cli init
python -m docforge.cli doctor

Write-Host "`nDocForge est installé. Lancez :`n  python -m docforge.cli run"
