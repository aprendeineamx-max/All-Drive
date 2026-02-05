# Seguridad y Manejo de Credenciales

## ⚠️ IMPORTANTE: Protección de Credenciales

Este proyecto maneja credenciales sensibles de Vultr Object Storage. Es **CRÍTICO** que nunca compartas o subas tus credenciales reales a un repositorio público.

## Archivos de Configuración

### Archivos con Credenciales (NO incluir en git)

Los siguientes archivos contienen información sensible y **NO deben ser incluidos** en el control de versiones:

- `config.json` - Contiene las credenciales de acceso (Access Key y Secret Key)
- `user_preferences.json` - Contiene preferencias del usuario

Estos archivos ya están incluidos en `.gitignore` para prevenir commits accidentales.

### Archivos de Ejemplo (SÍ incluir en git)

Los siguientes archivos son plantillas seguras que pueden ser compartidas:

- `config.example.json` - Plantilla de configuración con valores de ejemplo
- `config.default.json` - Configuración por defecto sin credenciales reales

## Configuración Inicial

### Primera vez que usas el proyecto:

1. Copia el archivo de ejemplo:
   ```powershell
   Copy-Item config.example.json config.json
   ```

2. Edita `config.json` con tus credenciales reales:
   ```json
   {
       "nombre-de-tu-perfil": {
           "access_key": "TU_ACCESS_KEY_AQUI",
           "secret_key": "TU_SECRET_KEY_AQUI",
           "host_base": "lax1.vultrobjects.com"
       }
   }
   ```

3. **NUNCA** hagas commit de `config.json` con credenciales reales

## Buenas Prácticas de Seguridad

### ✅ Hacer:

- Usar `config.example.json` como plantilla
- Mantener tus credenciales en `config.json` (ignorado por git)
- Rotar tus credenciales periódicamente en el panel de Vultr
- Usar diferentes credenciales para desarrollo y producción
- Compartir solo los archivos de ejemplo

### ❌ NO Hacer:

- NO subir `config.json` con credenciales reales a git
- NO compartir tus credenciales en capturas de pantalla
- NO incluir credenciales en issues o pull requests
- NO usar las mismas credenciales en múltiples proyectos
- NO dejar credenciales en mensajes de commit

## ¿Qué hacer si subiste credenciales por error?

Si accidentalmente subiste credenciales reales a git:

1. **INMEDIATAMENTE** revoca las credenciales en el panel de Vultr
2. Genera nuevas credenciales
3. Actualiza tu `config.json` local con las nuevas credenciales
4. Limpia el historial de git (considera usar `git filter-branch` o BFG Repo-Cleaner)
5. Fuerza un push del historial limpio (ten cuidado con esto)

## Obtener Credenciales de Vultr

Para obtener tus credenciales de acceso a Vultr Object Storage:

1. Inicia sesión en [my.vultr.com](https://my.vultr.com)
2. Ve a la sección "Object Storage"
3. Selecciona tu bucket o crea uno nuevo
4. Haz clic en "Manage Keys" o "Access Keys"
5. Copia tu Access Key y Secret Key
6. Pégalas en tu `config.json` local

## Permisos Recomendados

Al crear credenciales en Vultr, usa el principio de **menor privilegio**:

- Para desarrollo: Solo permisos de lectura si es posible
- Para producción: Solo los permisos necesarios para tu aplicación
- Considera crear credenciales separadas para cada entorno

## Soporte

Si tienes preguntas sobre seguridad o manejo de credenciales:

- Revisa la [documentación de Vultr Object Storage](https://www.vultr.com/docs/vultr-object-storage/)
- Consulta las mejores prácticas de seguridad de AWS S3 (compatible con Vultr)
- Abre un issue en el repositorio (¡sin incluir credenciales!)

---

**Recuerda**: La seguridad es responsabilidad de todos. Mantén tus credenciales seguras y privadas.
