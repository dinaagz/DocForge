# DocForge uninstaller (Windows PowerShell).
$ErrorActionPreference = 'Stop'

$Purge = $false
$Dry = $false
foreach ($arg in $args) {
    if ($arg -eq '--purge') { $Purge = $true }
    if ($arg -eq '--dry-run') { $Dry = $true }
}

$Bin = Get-Command docforge -ErrorAction SilentlyContinue
if ($null -ne $Bin) {
    $cli = $Bin.Source
    $call = @('uninstall')
    if ($Dry)   { $call += '--dry-run' }
    if ($Purge) { $call += '--purge' }
    & $cli @call
    exit $LASTEXITCODE
}

$Py = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $Py) { $Py = Get-Command python3 -ErrorAction SilentlyContinue }
if ($null -eq $Py) { Write-Error "Python introuvable."; exit 1 }

$call = @('-m', 'docforge.cli', 'uninstall')
if ($Dry)   { $call += '--dry-run' }
if ($Purge) { $call += '--purge' }
& $Py.Source @call
exit $LASTEXITCODE
