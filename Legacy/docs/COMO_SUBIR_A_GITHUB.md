# 🔧 GUÍA: Guardar Cambios en GitHub

## ❌ PROBLEMA ACTUAL

Git no está instalado en tu sistema. Por eso aparece "0 files changed".

---

## ✅ SOLUCIÓN: Instalar Git y Subir Cambios

### Paso 1: Instalar Git

1. **Descarga Git para Windows:**
   ```
   https://git-scm.com/download/win
   ```

2. **Ejecuta el instalador:**
   - Acepta todas las opciones por defecto
   - Dura ~2 minutos

3. **Verifica la instalación:**
   ```powershell
   git --version
   ```
   Debe mostrar: `git version 2.xx.x`

---

### Paso 2: Configurar Git (Solo Primera Vez)

```powershell
# Configurar tu nombre
git config --global user.name "Tu Nombre"

# Configurar tu email (el de GitHub)
git config --global user.email "tu-email@example.com"

# Verificar
git config --list
```

---

### Paso 3: Inicializar Repositorio

```powershell
# Ir a la carpeta del proyecto
cd C:\Users\lvarg\Desktop\VultrDriveDesktop

# Inicializar Git
git init

# Agregar remote (tu repositorio)
git remote add origin https://github.com/aprendeineamx-max/VultrDriveDesktop.git

# Verificar
git remote -v
```

---

### Paso 4: Subir Cambios a GitHub

```powershell
# Ver qué archivos cambiaron
git status

# Agregar TODOS los archivos
git add .

# O agregar archivos específicos:
git add app.py
git add ui/main_window.py
git add translations.py
git add COMO_COMPILAR_Y_EMPAQUETAR.md
git add compilar_y_empaquetar.ps1

# Crear commit con mensaje
git commit -m "🌐 Traducciones 100% completas + Instalación automática WinFsp"

# Subir a GitHub
git push -u origin main
```

Si pide usuario y contraseña, usa:
- **Usuario:** Tu nombre de usuario de GitHub
- **Contraseña:** Tu Personal Access Token (no tu contraseña normal)

---

### Paso 5: Crear Personal Access Token (Si No Tienes)

1. Ve a GitHub → Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Selecciona scopes:
   - `repo` (acceso completo a repositorios)
4. Copia el token generado (guárdalo en lugar seguro)
5. Usa este token como "contraseña" al hacer `git push`

---

## ⚡ SCRIPT AUTOMÁTICO: Subir Cambios

Guarda esto como **`subir_a_github.ps1`**:

```powershell
# ====================================
#  SCRIPT: Subir Cambios a GitHub
# ====================================

Write-Host "`n=== SUBIR CAMBIOS A GITHUB ===" -ForegroundColor Cyan

# Verificar que Git está instalado
try {
    $gitVersion = git --version
    Write-Host "✅ Git instalado: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Git no está instalado" -ForegroundColor Red
    Write-Host "   Descarga desde: https://git-scm.com/download/win`n" -ForegroundColor Yellow
    exit 1
}

# Ver archivos modificados
Write-Host "`n📝 Archivos modificados:" -ForegroundColor Yellow
git status --short

# Agregar todos los archivos
Write-Host "`n➕ Agregando archivos..." -ForegroundColor Yellow
git add .

# Mostrar resumen
$filesChanged = (git diff --cached --numstat | Measure-Object).Count
Write-Host "✅ $filesChanged archivos agregados" -ForegroundColor Green

# Pedir mensaje de commit
Write-Host "`n💬 Mensaje del commit:" -ForegroundColor Yellow
$commitMessage = Read-Host "Escribe un mensaje (o Enter para usar default)"

if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = "Actualización $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}

# Crear commit
Write-Host "`n📦 Creando commit..." -ForegroundColor Yellow
git commit -m "$commitMessage"

# Subir a GitHub
Write-Host "`n⬆️ Subiendo a GitHub..." -ForegroundColor Yellow
git push

Write-Host "`n✅ CAMBIOS SUBIDOS A GITHUB" -ForegroundColor Green
Write-Host "   Ver en: https://github.com/aprendeineamx-max/VultrDriveDesktop`n" -ForegroundColor Cyan
```

**Uso:**
```powershell
.\subir_a_github.ps1
```

---

## 🔄 COMANDOS RÁPIDOS

### Ver cambios:
```powershell
git status
```

### Agregar y subir:
```powershell
git add .
git commit -m "Mensaje de cambios"
git push
```

### Descargar cambios de GitHub:
```powershell
git pull
```

### Ver historial:
```powershell
git log --oneline
```

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### Error: "git no reconocido"
**Solución:** Instala Git desde https://git-scm.com/download/win

### Error: "Permission denied"
**Solución:** Usa Personal Access Token en lugar de contraseña

### Error: "Repository not found"
**Solución:** Verifica la URL del repositorio:
```powershell
git remote -v
```

### Error: "Merge conflict"
**Solución:**
```powershell
# Ver archivos en conflicto
git status

# Resolver manualmente o aceptar tus cambios
git checkout --ours archivo.py
git add archivo.py
git commit -m "Resolver conflicto"
git push
```

---

## 📊 ESTADO ACTUAL

**Tu repositorio:** https://github.com/aprendeineamx-max/VultrDriveDesktop

**Archivos que deberías subir:**
- ✅ `app.py` (instalación automática WinFsp)
- ✅ `ui/main_window.py` (traducciones completas)
- ✅ `translations.py` (5 idiomas)
- ✅ `COMO_COMPILAR_Y_EMPAQUETAR.md`
- ✅ `compilar_y_empaquetar.ps1`
- ✅ `GUIA_RAPIDA_COMPILACION.md`
- ✅ `INSTRUCCIONES_SIMPLES.md`
- ✅ `INDICE_DOCUMENTACION.md`
- ✅ `TRADUCCIONES_COMPLETAS.md`
- ✅ `RESUMEN_PORTABLE_ACTUALIZADO.md`

---

## 🎯 RESUMEN

1. **Instala Git:** https://git-scm.com/download/win
2. **Configura Git:** nombre y email
3. **Inicializa repo:** `git init` + `git remote add origin ...`
4. **Sube cambios:** `git add .` + `git commit -m "..."` + `git push`

O usa el script: **`.\subir_a_github.ps1`**

---

**Última actualización:** 06/11/2025 04:53 a.m.
