# DocForge - installe les slash commands Claude Code dans le profil utilisateur
# Usage : powershell -ExecutionPolicy Bypass -File install-commands.ps1
# A relancer apres chaque mise a jour de DocForge

$dest = "$env:USERPROFILE\.claude\commands"
$src  = "$PSScriptRoot\.claude\commands"

Write-Host "DocForge - installation des commandes Claude Code" -ForegroundColor Cyan
Write-Host "Source      : $src"
Write-Host "Destination : $dest"
Write-Host ""

if (-not (Test-Path $dest)) {
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    Write-Host "Dossier cree : $dest" -ForegroundColor Green
}

if (-not (Test-Path $src)) {
    Write-Error "Dossier source introuvable : $src"
    Write-Host "Ce script doit etre execute depuis le dossier DocForge."
    exit 1
}

$files = Get-ChildItem "$src\docforge*.md"
$count = 0

foreach ($file in $files) {
    $target = Join-Path $dest $file.Name
    Copy-Item $file.FullName $target -Force
    Write-Host "  OK  $($file.Name)" -ForegroundColor Green
    $count++
}

Write-Host ""
Write-Host "$count commande(s) installee(s)." -ForegroundColor Cyan
Write-Host "Redemarrez Claude Code pour les voir apparaitre (ex: /docforge-run)."
