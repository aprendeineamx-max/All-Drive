# Script para subir cambios a GitHub usando GitHub Desktop
# VultrDriveDesktop v2.0 - Con todas las optimizaciones

Write-Host "`n=== PREPARAR PARA GITHUB ===" -ForegroundColor Cyan
Write-Host "VultrDriveDesktop v2.0 - Version con optimizaciones completas`n" -ForegroundColor Green

# Información del commit
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

Rendimiento:
- Import: 24ms
- Lazy load: 0.07ms
- Cached: 0.0019ms
"@

Write-Host "MENSAJE DEL COMMIT:" -ForegroundColor Yellow
Write-Host $commitMessage -ForegroundColor White

Write-Host "`n=== INSTRUCCIONES ===" -ForegroundColor Cyan

Write-Host "`nOPCIÓN 1: Usar GitHub Desktop" -ForegroundColor Green
Write-Host "  1. Abre GitHub Desktop" -ForegroundColor White
Write-Host "  2. Ve a File > Add Local Repository" -ForegroundColor White
Write-Host "  3. Selecciona esta carpeta: $PWD" -ForegroundColor Yellow
Write-Host "  4. GitHub Desktop detectará los cambios automáticamente" -ForegroundColor White
Write-Host "  5. Escribe el mensaje de commit (copiado abajo)" -ForegroundColor White
Write-Host "  6. Click en 'Commit to main'" -ForegroundColor White
Write-Host "  7. Click en 'Push origin'" -ForegroundColor White

Write-Host "`nOPCIÓN 2: Instalar Git y usar línea de comandos" -ForegroundColor Green
Write-Host "  1. Descarga Git desde: https://git-scm.com/download/win" -ForegroundColor White
Write-Host "  2. Instala Git" -ForegroundColor White
Write-Host "  3. Ejecuta el script: .\subir_a_github.ps1" -ForegroundColor Yellow

Write-Host "`n=== ARCHIVOS QUE SE SUBIRÁN ===" -ForegroundColor Cyan
$archivosModificados = @(
    "app.py",
    "splash_screen.py",
    "rclone_manager.py",
    "ui/main_window.py",
    "translations.py",
    "compilar_y_empaquetar.ps1",
    "COMO_COMPILAR_Y_EMPAQUETAR.md",
    "GUIA_RAPIDA_COMPILACION.md",
    "TRADUCCIONES_COMPLETAS.md",
    "CORRECCIONES_FINALES.md",
    "INDICE_DOCUMENTACION.md"
)

foreach ($archivo in $archivosModificados) {
    if (Test-Path $archivo) {
        $size = (Get-Item $archivo).Length
        $sizeKB = [math]::Round($size/1KB, 2)
        Write-Host "  ✅ $archivo ($sizeKB KB)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  $archivo (no encontrado)" -ForegroundColor Yellow
    }
}

Write-Host "`n=== REPOSITORIO ===" -ForegroundColor Cyan
Write-Host "  Owner: aprendeineamx-max" -ForegroundColor White
Write-Host "  Repo: VultrDriveDesktop" -ForegroundColor White
Write-Host "  Branch: main" -ForegroundColor White
Write-Host "  URL: https://github.com/aprendeineamx-max/VultrDriveDesktop" -ForegroundColor Yellow

Write-Host "`n=== MENSAJE DE COMMIT (COPIAR) ===" -ForegroundColor Cyan
Write-Host $commitMessage -ForegroundColor White

Write-Host "`n✅ Listo para subir a GitHub!" -ForegroundColor Green
Write-Host "Usa GitHub Desktop o instala Git para continuar.`n" -ForegroundColor White
