# Script simple para ejecutar VultrDriveDesktop
Write-Host "Iniciando VultrDriveDesktop..." -ForegroundColor Green

# Intentar encontrar Python
$pythonCommands = @("python", "py", "python3")
$pythonFound = $false

foreach ($cmd in $pythonCommands) {
    try {
        & $cmd --version 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Usando: $cmd" -ForegroundColor Gray
            & $cmd app.py
            $pythonFound = $true
            break
        }
    } catch {
        continue
    }
}

if (-not $pythonFound) {
    Write-Host "Error: Python no encontrado." -ForegroundColor Red
    Write-Host "Por favor, instale Python desde:" -ForegroundColor Yellow
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host "  O desde Microsoft Store: ms-windows-store://pdp/?productid=9PJPW5LDXLZ5" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Presione Enter para salir"
}