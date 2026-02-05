# Plan de Configuración

## Objetivo
Configurar VultrDriveDesktop con las credenciales de Vultr Object Storage proporcionadas para las regiones `ewr1` y `sjc1`, y lanzar la aplicación.

## Cambios Propuestos
Actualizaré `config.json` para incluir dos perfiles correspondientes a las claves proporcionadas.

### `config.json`
Añadiré los siguientes perfiles:
1.  **Vultr New Jersey (ewr1)**
    - Access Key: `4BW2T0AX55SN0V0C14UN`
    - Secret Key: `8Hjed5xmFILX0buJ5H7BB4NPaxrC1liKM9WIoRNB`
    - Host: `ewr1.vultrobjects.com`

2.  **Vultr Silicon Valley (sjc1)**
    - Access Key: `3Y3MFSZPD8XCC5IMGZWH`
    - Secret Key: `lq95CVjRWqM3CPSXp1Y7P0S8W76bQKz37CtplahX`
    - Host: `sjc1.vultrobjects.com`

Utilizaré un script de Python para actualizar la configuración de forma segura usando `ConfigManager` si es posible, o manipulación directa de JSON si invocar `ConfigManager` de forma independiente es complejo. Dado que existe `config_manager.py`, puedo importarlo en un script.

## Plan de Verificación
1.  **Verificar Configuración**: Revisar el contenido de `config.json` después de la actualización.
2.  **Lanzar Aplicación**: Ejecutar `python app.py` (o `launcher.bat`) y comprobar si inicia sin errores. Utilizaré `read_terminal` o buscaré un proceso si es posible, pero principalmente confiaré en la salida del comando de lanzamiento.
