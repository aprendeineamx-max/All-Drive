@echo off
echo ========================================
echo COPIAR ARCHIVOS AL REPOSITORIO DE GITHUB
echo ========================================
echo.

set "SOURCE=C:\Users\lvarg\Desktop\VultrDriveDesktop"
set "REPO=C:\Users\lvarg\Desktop\VultrDriveDesktop\VultrDriveDesktop"

echo Copiando archivos Python...
xcopy "%SOURCE%\*.py" "%REPO%\" /Y /I
echo.

echo Copiando archivos PowerShell...
xcopy "%SOURCE%\*.ps1" "%REPO%\" /Y /I
echo.

echo Copiando archivos Batch...
xcopy "%SOURCE%\*.bat" "%REPO%\" /Y /I
echo.

echo Copiando archivos Markdown...
xcopy "%SOURCE%\*.md" "%REPO%\" /Y /I
echo.

echo Copiando archivos de configuracion...
xcopy "%SOURCE%\*.json" "%REPO%\" /Y /I
xcopy "%SOURCE%\*.txt" "%REPO%\" /Y /I
xcopy "%SOURCE%\*.qss" "%REPO%\" /Y /I
echo.

echo Copiando carpeta ui...
xcopy "%SOURCE%\ui" "%REPO%\ui\" /E /Y /I
echo.

echo Copiando rclone...
if exist "%SOURCE%\rclone-v1.71.2-windows-amd64" (
    xcopy "%SOURCE%\rclone-v1.71.2-windows-amd64" "%REPO%\rclone-v1.71.2-windows-amd64\" /E /Y /I
)
echo.

echo ========================================
echo ARCHIVOS COPIADOS AL REPOSITORIO
echo ========================================
echo.
echo Presiona Enter para ver el estado de Git...
pause > nul

cd /d "%REPO%"
"C:\Program Files\Git\cmd\git.exe" status

echo.
echo ========================================
echo Ahora puedes hacer commit desde VS Code
echo O presiona Enter para continuar con Git...
pause
