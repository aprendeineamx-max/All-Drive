# Script para subir VultrDriveDesktop a GitHub
# Asegúrate de tener Git instalado y configurado

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Subir VultrDriveDesktop a GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Git está instalado
try {
    $gitVersion = git --version
    Write-Host "✓ Git detectado: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git no está instalado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, instala Git desde: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "Después, vuelve a ejecutar este script." -ForegroundColor Yellow
    pause
    exit
}

Write-Host ""
Write-Host "PASO 1: Inicializando repositorio Git..." -ForegroundColor Yellow

# Inicializar repositorio
git init

Write-Host "✓ Repositorio inicializado" -ForegroundColor Green
Write-Host ""

Write-Host "PASO 2: Agregando archivos..." -ForegroundColor Yellow

# Agregar todos los archivos
git add .

Write-Host "✓ Archivos agregados" -ForegroundColor Green
Write-Host ""

Write-Host "PASO 3: Creando commit inicial..." -ForegroundColor Yellow

# Crear commit
git commit -m "Initial commit: Vultr Drive Desktop - Aplicación completa de gestión de Object Storage"

Write-Host "✓ Commit creado" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Configuración de GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Ahora necesitas crear un repositorio en GitHub:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Ve a: https://github.com/new" -ForegroundColor White
Write-Host "2. Nombre del repositorio: VultrDriveDesktop" -ForegroundColor White
Write-Host "3. Descripción: Aplicación de escritorio para gestionar Vultr Object Storage" -ForegroundColor White
Write-Host "4. Selecciona: Public o Private (como prefieras)" -ForegroundColor White
Write-Host "5. NO marques 'Add a README file' (ya tenemos uno)" -ForegroundColor White
Write-Host "6. Haz clic en 'Create repository'" -ForegroundColor White
Write-Host ""

$continue = Read-Host "¿Ya creaste el repositorio en GitHub? (s/n)"

if ($continue -eq 's' -or $continue -eq 'S') {
    Write-Host ""
    $repoUrl = Read-Host "Pega la URL de tu repositorio (ejemplo: https://github.com/tu-usuario/VultrDriveDesktop.git)"
    
    if ($repoUrl) {
        Write-Host ""
        Write-Host "PASO 4: Conectando con GitHub..." -ForegroundColor Yellow
        
        # Configurar rama principal
        git branch -M main
        
        # Agregar remote
        git remote add origin $repoUrl
        
        Write-Host "✓ Repositorio remoto configurado" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "PASO 5: Subiendo a GitHub..." -ForegroundColor Yellow
        
        # Push
        git push -u origin main
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  ¡COMPLETADO!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Tu proyecto ha sido subido exitosamente a GitHub." -ForegroundColor Green
        Write-Host "Puedes verlo en: $repoUrl" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Host "✗ No se proporcionó URL del repositorio" -ForegroundColor Red
    }
} else {
    Write-Host ""
    Write-Host "Cuando hayas creado el repositorio, ejecuta estos comandos:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "git branch -M main" -ForegroundColor White
    Write-Host "git remote add origin https://github.com/tu-usuario/VultrDriveDesktop.git" -ForegroundColor White
    Write-Host "git push -u origin main" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
pause
