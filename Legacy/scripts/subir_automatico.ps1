# Script inteligente para subir a GitHub
# Detecta si Git está instalado y actúa en consecuencia

Write-Host "`n=== SUBIR A GITHUB - VultrDriveDesktop v2.0 ===" -ForegroundColor Cyan

# Verificar si Git está instalado
$gitInstalled = $false
try {
    $gitVersion = git --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        $gitInstalled = $true
        Write-Host "✅ Git encontrado: $gitVersion" -ForegroundColor Green
    }
} catch {
    $gitInstalled = $false
}

if (-not $gitInstalled) {
    Write-Host "❌ Git no está instalado" -ForegroundColor Red
    Write-Host "`nOPCIONES:" -ForegroundColor Yellow
    Write-Host "  1. Instalar Git: https://git-scm.com/download/win" -ForegroundColor White
    Write-Host "  2. Usar GitHub Desktop (más fácil): https://desktop.github.com/" -ForegroundColor White
    Write-Host "`nPara más información, lee: SUBIR_A_GITHUB_COMPLETO.md" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Git está instalado, proceder
Write-Host "`n=== PREPARANDO COMMIT ===" -ForegroundColor Cyan

# Verificar si estamos en un repositorio Git
if (-not (Test-Path ".git")) {
    Write-Host "⚠️  No es un repositorio Git. Inicializando..." -ForegroundColor Yellow
    git init
    git remote add origin https://github.com/aprendeineamx-max/VultrDriveDesktop.git
    Write-Host "✅ Repositorio inicializado" -ForegroundColor Green
}

# Ver estado
Write-Host "`n📋 Archivos modificados:" -ForegroundColor Yellow
git status --short

# Mensaje del commit
$commitMessage = @"
v2.0 - Optimizaciones completas y traducciones

Cambios principales:
- ✅ 5 idiomas completos (ES/EN/FR/DE/PT) con lazy loading
- ✅ Instalación inteligente de WinFsp (solo si no está presente)
- ✅ Limpieza automática de unidades montadas al iniciar
- ✅ Splash screen rediseñado (sin versión, título centrado)
- ✅ Soporte multi-máquina con flags optimizados
- ✅ Todos los mensajes en español con soluciones detalladas
- ✅ Inicio optimizado con QTimer.singleShot
- ✅ Portable 170MB listo para distribuir

Archivos modificados:
- app.py: Instalación condicional WinFsp + limpieza post-window
- splash_screen.py: Rediseño visual completo
- rclone_manager.py: Detección/desmontaje auto + flags multi-máquina
- ui/main_window.py: 100% traducido a español
- translations.py: 5 idiomas completos

Rendimiento: Import 24ms | Lazy 0.07ms | Cached 0.0019ms
"@

Write-Host "`n=== AÑADIENDO ARCHIVOS ===" -ForegroundColor Cyan

# Añadir archivos específicos (excluir portables y zips)
git add app.py
git add splash_screen.py
git add rclone_manager.py
git add ui/
git add translations.py
git add config_manager.py
git add s3_handler.py
git add file_watcher.py
git add backup_now.py
git add create_shortcut.py
git add setup.py
git add requirements.txt
git add compilar_y_empaquetar.ps1
git add EMPAQUETAR.bat
git add *.md
git add .gitignore
git add README_GITHUB.md
git add subir_a_github*.ps1

Write-Host "✅ Archivos añadidos" -ForegroundColor Green

# Hacer commit
Write-Host "`n=== CREANDO COMMIT ===" -ForegroundColor Cyan
git commit -m $commitMessage

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Commit creado exitosamente" -ForegroundColor Green
} else {
    Write-Host "⚠️  No hay cambios para commitear o hubo un error" -ForegroundColor Yellow
    Write-Host ""
    exit 0
}

# Preguntar antes de hacer push
Write-Host "`n=== LISTO PARA PUSH ===" -ForegroundColor Yellow
Write-Host "¿Deseas hacer push a GitHub ahora? (S/N): " -ForegroundColor White -NoNewline
$respuesta = Read-Host

if ($respuesta -eq "S" -or $respuesta -eq "s" -or $respuesta -eq "Y" -or $respuesta -eq "y") {
    Write-Host "`n=== HACIENDO PUSH ===" -ForegroundColor Cyan
    
    # Intentar push
    git push origin main 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ ÉXITO! Cambios subidos a GitHub" -ForegroundColor Green
        Write-Host "`nVer en: https://github.com/aprendeineamx-max/VultrDriveDesktop" -ForegroundColor Cyan
    } else {
        Write-Host "`n⚠️  Error al hacer push" -ForegroundColor Yellow
        Write-Host "`nPosibles causas:" -ForegroundColor White
        Write-Host "  1. No has configurado autenticación" -ForegroundColor White
        Write-Host "  2. Necesitas hacer pull primero: git pull origin main --rebase" -ForegroundColor White
        Write-Host "  3. Necesitas un Personal Access Token" -ForegroundColor White
        Write-Host "`nLee SUBIR_A_GITHUB_COMPLETO.md para más ayuda" -ForegroundColor Cyan
    }
} else {
    Write-Host "`n✅ Commit guardado localmente" -ForegroundColor Green
    Write-Host "Para hacer push después, ejecuta: git push origin main" -ForegroundColor Cyan
}

Write-Host ""
