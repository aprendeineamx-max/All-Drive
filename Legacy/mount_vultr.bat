@echo off
cd /d "%~dp0"
echo Montando Vultr Object Storage en Z:...
"%RcloneDir%\rclone.exe" mount vultr: Z: --config "rclone.conf" --vfs-cache-mode full
pause
