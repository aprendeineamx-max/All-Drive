@echo off
cd /d "C:\Users\lvarg\Desktop\VultrDriveDesktop\VultrDriveDesktop"
"C:\Program Files\Git\cmd\git.exe" add README_GITHUB.md
"C:\Program Files\Git\cmd\git.exe" add SUBIR_A_GITHUB_COMPLETO.md
"C:\Program Files\Git\cmd\git.exe" add INDICE_DOCUMENTACION.md
"C:\Program Files\Git\cmd\git.exe" add subir_automatico.ps1
"C:\Program Files\Git\cmd\git.exe" status
echo.
echo Presiona Enter para hacer commit...
pause
"C:\Program Files\Git\cmd\git.exe" commit -m "v2.0 - Documentacion GitHub completa"
echo.
echo Presiona Enter para hacer push...
pause
"C:\Program Files\Git\cmd\git.exe" push origin main
echo.
echo LISTO!
pause
