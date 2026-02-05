@echo off
echo ================================
echo  VultrDriveDesktop Launcher
echo ================================
echo.

REM Intentar encontrar Python
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Iniciando con py...
    py app.py
    goto :END
)

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Iniciando con python...
    python app.py
    goto :END
)

where python3 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Iniciando con python3...
    python3 app.py
    goto :END
)

REM Si no se encuentra Python
echo ERROR: Python no encontrado
echo.
echo Por favor, instale Python desde:
echo   https://www.python.org/downloads/
echo   O desde Microsoft Store
echo.
pause
goto :END

:END
