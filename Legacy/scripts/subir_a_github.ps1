# ====================================
#  SCRIPT: Subir Cambios a GitHub
# ====================================
# VultrDriveDesktop - Automatización Git

Write-Host "`n=== SUBIR CAMBIOS A GITHUB ===" -ForegroundColor Cyan
Write-Host "Repositorio: aprendeineamx-max/VultrDriveDesktop`n" -ForegroundColor White

# Verificar que Git está instalado
try {
    $gitVersion = git --version 2>$null
    Write-Host "✅ Git instalado: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Git no está instalado" -ForegroundColor Red
    Write-Host "`nPara instalar Git:" -ForegroundColor Yellow
    Write-Host "  1. Descarga: https://git-scm.com/download/win" -ForegroundColor White
    Write-Host "  2. Ejecuta el instalador" -ForegroundColor White
    Write-Host "  3. Reinicia PowerShell" -ForegroundColor White
    Write-Host "  4. Vuelve a ejecutar este script`n" -ForegroundColor White
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar si es un repositorio Git
if (-not (Test-Path ".git")) {
    Write-Host "⚠️  No es un repositorio Git" -ForegroundColor Yellow
    Write-Host "`nInicializando repositorio..." -ForegroundColor Yellow
    
    git init
    git remote add origin https://github.com/aprendeineamx-max/VultrDriveDesktop.git
    
    Write-Host "✅ Repositorio inicializado" -ForegroundColor Green
}

# Ver archivos modificados
Write-Host "`n📝 Archivos modificados:" -ForegroundColor Yellow
git status --short

$statusOutput = git status --short
if ([string]::IsNullOrWhiteSpace($statusOutput)) {
    Write-Host "✅ No hay cambios para subir" -ForegroundColor Green
    Write-Host "`n" 
    Read-Host "Presiona Enter para salir"
    exit 0
}

# Preguntar si continuar
Write-Host "`n¿Quieres subir estos cambios a GitHub?" -ForegroundColor Yellow
$continue = Read-Host "Escribe 'si' para continuar"

if ($continue -ne "si") {
    Write-Host "❌ Cancelado por el usuario`n" -ForegroundColor Red
    exit 0
}

# Agregar todos los archivos
Write-Host "`n➕ Agregando archivos..." -ForegroundColor Yellow
git add .

# Mostrar resumen
$filesChanged = (git diff --cached --numstat | Measure-Object).Count
Write-Host "✅ $filesChanged archivos agregados" -ForegroundColor Green

# Pedir mensaje de commit
Write-Host "`n💬 Mensaje del commit:" -ForegroundColor Yellow
Write-Host "   (Presiona Enter para usar mensaje automático)" -ForegroundColor Gray
$commitMessage = Read-Host "Mensaje"

if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = "Actualización $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}

# Crear commit
Write-Host "`n📦 Creando commit..." -ForegroundColor Yellow
git commit -m "$commitMessage"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al crear commit" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Subir a GitHub
Write-Host "`n⬆️  Subiendo a GitHub..." -ForegroundColor Yellow
Write-Host "   (Esto puede tardar unos segundos...)" -ForegroundColor Gray

git push -u origin main 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n⚠️  Error al subir. Posibles causas:" -ForegroundColor Yellow
    Write-Host "   1. No has configurado tu usuario de GitHub" -ForegroundColor White
    Write-Host "   2. Necesitas un Personal Access Token" -ForegroundColor White
    Write-Host "`nConfigura Git con:" -ForegroundColor Yellow
    Write-Host "   git config --global user.name 'Tu Nombre'" -ForegroundColor Cyan
    Write-Host "   git config --global user.email 'tu-email@example.com'" -ForegroundColor Cyan
    Write-Host "`nCrea un Personal Access Token en:" -ForegroundColor Yellow
    Write-Host "   https://github.com/settings/tokens`n" -ForegroundColor Cyan
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "`n✅ CAMBIOS SUBIDOS A GITHUB EXITOSAMENTE" -ForegroundColor Green
Write-Host "`nVer cambios en:" -ForegroundColor White
Write-Host "   https://github.com/aprendeineamx-max/VultrDriveDesktop" -ForegroundColor Cyan
Write-Host "`n"
Read-Host "Presiona Enter para salir"
