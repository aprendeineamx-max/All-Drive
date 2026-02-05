# Script para subir cambios usando el Git de VS Code o GitHub Desktop

Write-Host "`n=== SUBIR CAMBIOS A GITHUB ===" -ForegroundColor Cyan

# Buscar Git en ubicaciones comunes
$gitPaths = @(
    "C:\Program Files\Git\cmd\git.exe",
    "C:\Program Files (x86)\Git\cmd\git.exe",
    "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe",
    "$env:ProgramFiles\Git\cmd\git.exe"
)

$gitExe = $null
foreach ($path in $gitPaths) {
    if (Test-Path $path) {
        $gitExe = $path
        Write-Host "✅ Git encontrado en: $path" -ForegroundColor Green
        break
    }
}

if (-not $gitExe) {
    Write-Host "❌ No se encontró Git.exe" -ForegroundColor Red
    Write-Host "`n💡 SOLUCIÓN: Usa el Source Control de VS Code" -ForegroundColor Yellow
    Write-Host "  1. En VS Code, ve al panel 'SOURCE CONTROL' (Ctrl+Shift+G)" -ForegroundColor White
    Write-Host "  2. Verás los archivos modificados listados" -ForegroundColor White
    Write-Host "  3. Click en el botón '✓ Commit' (arriba)" -ForegroundColor White
    Write-Host "  4. Escribe el mensaje: 'v2.0 - Documentación GitHub completa'" -ForegroundColor White
    Write-Host "  5. Presiona Ctrl+Enter o click en '✓ Commit'" -ForegroundColor White
    Write-Host "  6. Click en '...' (más opciones) → 'Push'" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Git encontrado, usarlo
Write-Host "`n📋 Archivos modificados:" -ForegroundColor Yellow
& $gitExe status --short

Write-Host "`n=== AÑADIENDO ARCHIVOS ===" -ForegroundColor Cyan
& $gitExe add README_GITHUB.md
& $gitExe add SUBIR_A_GITHUB_COMPLETO.md
& $gitExe add INDICE_DOCUMENTACION.md
& $gitExe add subir_automatico.ps1
& $gitExe add subir_a_github_sin_git.ps1
& $gitExe add usar_git_en_vscode.ps1

Write-Host "✅ Archivos añadidos" -ForegroundColor Green

Write-Host "`n=== CREANDO COMMIT ===" -ForegroundColor Cyan
& $gitExe commit -m "v2.0 - Documentación GitHub completa" -m "Archivos añadidos: README_GITHUB.md, SUBIR_A_GITHUB_COMPLETO.md, INDICE_DOCUMENTACION.md, scripts de automatización"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Commit creado exitosamente" -ForegroundColor Green
    
    Write-Host "`n=== HACIENDO PUSH ===" -ForegroundColor Cyan
    & $gitExe push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n🎉 ¡ÉXITO! Cambios subidos a GitHub" -ForegroundColor Green
        Write-Host "`nVer en: https://github.com/aprendeineamx-max/VultrDriveDesktop" -ForegroundColor Cyan
    } else {
        Write-Host "`n⚠️  Error al hacer push" -ForegroundColor Yellow
        Write-Host "Intenta hacer push desde VS Code:" -ForegroundColor White
        Write-Host "  1. Ctrl+Shift+G (Source Control)" -ForegroundColor White
        Write-Host "  2. Click en '...' → 'Push'" -ForegroundColor White
    }
} else {
    Write-Host "ℹ️  No hay cambios nuevos para commitear" -ForegroundColor Cyan
}

Write-Host ""
