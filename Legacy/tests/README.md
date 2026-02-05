# 🧪 Tests y Pruebas - VultrDrive Desktop

Esta carpeta contiene scripts de prueba, benchmarks y tests de rendimiento.

## 📊 Scripts de Prueba

### Rendimiento
- **`benchmark_startup.py`** - Mide tiempo de inicio de la aplicación
- **`test_performance.py`** - Tests de rendimiento general

### Funcionalidad
- **`test_rclone.ps1`** - Prueba funcionalidad de Rclone
- **`test_translations.py`** - Verifica sistema de traducciones

## 🚀 Cómo Ejecutar

### Tests Python
```bash
python test_performance.py
python test_translations.py
python benchmark_startup.py
```

### Tests PowerShell
```powershell
.\test_rclone.ps1
```

## 📝 Añadir Nuevos Tests

1. Crea un nuevo archivo: `test_nombre.py` o `test_nombre.ps1`
2. Sigue la convención de nombres: `test_*.py` o `test_*.ps1`
3. Documenta qué está probando
4. Añade instrucciones de ejecución

## ⚠️ Nota

Estos tests son para desarrollo. No son necesarios para el funcionamiento del programa.

---

**Ver también**: [Scripts](../scripts/) | [Documentación](../docs/)

