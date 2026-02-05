/**
 * Python Bridge - Ejecuta scripts Python del sistema legacy
 * Permite reutilizar la lógica existente de GCP/Rclone
 */

import { spawn, ChildProcess } from 'child_process'
import { ipcMain, app } from 'electron'
import path from 'path'

// Ruta al directorio Legacy
const LEGACY_PATH = path.join(__dirname, '../../Legacy')

interface PythonResult {
    success: boolean
    data?: any
    error?: string
}

// Helper type for log callback
type LogCallback = (msg: string) => void

/**
 * Ejecuta un comando Python y devuelve el resultado
 */
function runPythonScript(scriptPath: string, args: string[] = [], onLog?: LogCallback): Promise<PythonResult> {
    return new Promise((resolve) => {
        const fullPath = path.join(LEGACY_PATH, scriptPath)
        const pythonProcess = spawn('python', [fullPath, ...args], {
            cwd: LEGACY_PATH,
            env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
        })

        let stdout = ''
        let stderr = ''

        pythonProcess.stdout.on('data', (data) => {
            const str = data.toString()
            stdout += str
            if (onLog) onLog(str)
        })

        pythonProcess.stderr.on('data', (data) => {
            const str = data.toString()
            stderr += str
            if (onLog) onLog(`[STDERR] ${str}`)
        })

        pythonProcess.on('close', (code) => {
            if (code === 0) {
                try {
                    // Try to parse the LAST line as JSON result if possible, 
                    // or accumulative stdout
                    const lines = stdout.trim().split('\n')
                    const lastLine = lines[lines.length - 1]
                    const data = JSON.parse(lastLine)
                    resolve({ success: true, data })
                } catch {
                    resolve({ success: true, data: stdout.trim() })
                }
            } else {
                resolve({ success: false, error: stderr || `Exit code: ${code}` })
            }
        })

        pythonProcess.on('error', (err) => {
            resolve({ success: false, error: err.message })
        })
    })
}

/**
 * Ejecuta código Python inline
 */
function runPythonCode(code: string, onLog?: LogCallback): Promise<PythonResult> {
    return new Promise((resolve) => {
        const pythonProcess = spawn('python', ['-c', code], {
            cwd: LEGACY_PATH,
            env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
        })

        let stdout = ''
        let stderr = ''

        pythonProcess.stdout.on('data', (data) => {
            const str = data.toString()
            stdout += str
            if (onLog) onLog(str)
        })

        pythonProcess.stderr.on('data', (data) => {
            const str = data.toString()
            stderr += str
            if (onLog) onLog(`[STDERR] ${str}`)
        })

        pythonProcess.on('close', (code) => {
            if (code === 0) {
                try {
                    const lines = stdout.trim().split('\n')
                    const lastLine = lines[lines.length - 1]
                    const data = JSON.parse(lastLine)
                    resolve({ success: true, data })
                } catch {
                    resolve({ success: true, data: stdout.trim() })
                }
            } else {
                resolve({ success: false, error: stderr || `Exit code: ${code}` })
            }
        })
    })
}

/**
 * Ejecuta código Python inline y MANTIENE el proceso vivo (para sync/watchers)
 * Incluye lógica de SUPERVISOR para auto-reinicio si falla.
 */
let activeSyncProcess: ChildProcess | null = null
let restartCount = 0
const MAX_RESTARTS = 3

function startBackgroundPython(code: string, onLog: LogCallback, onEvent?: (event: any) => void): Promise<PythonResult> {
    return new Promise((resolve) => {
        let hasResolved = false

        const launch = () => {
            if (activeSyncProcess) {
                activeSyncProcess.removeAllListeners()
                activeSyncProcess.kill()
            }

            const pythonProcess = spawn('python', ['-u', '-c', code], {
                cwd: LEGACY_PATH,
                env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
            })

            activeSyncProcess = pythonProcess

            let stdout = ''
            let stderr = ''

            pythonProcess.stdout.on('data', (data) => {
                const str = data.toString()
                stdout += str

                // Procesar línea por línea para buscar eventos JSON
                str.split('\n').filter(l => l.trim()).forEach(line => {
                    try {
                        if (line.trim().startsWith('{') && line.trim().endsWith('}')) {
                            const event = JSON.parse(line)
                            if (onEvent) onEvent(event)

                            if (!hasResolved && event.success === true) {
                                hasResolved = true
                                resolve({ success: true, data: event })
                            }
                        } else {
                            if (onLog) onLog(line)
                        }
                    } catch (e) {
                        if (onLog) onLog(line)
                    }
                })
            })

            pythonProcess.stderr.on('data', (data) => {
                const str = data.toString()
                stderr += str
                if (onLog) onLog(`[STDERR] ${str}`)
            })

            pythonProcess.on('close', (code) => {
                console.log(`Python process closed with code ${code}`)
                if (code !== 0 && restartCount < MAX_RESTARTS) {
                    restartCount++
                    if (onLog) onLog(`[SYSTEM] Sync falló (Code ${code}). Reiniciando intento ${restartCount}...`)
                    setTimeout(launch, 2000)
                } else {
                    activeSyncProcess = null
                    if (!hasResolved) {
                        restartCount = 0
                        resolve({ success: false, error: stderr || `Process exited code ${code}` })
                    }
                }
            })

            pythonProcess.on('error', (err) => {
                if (onLog) onLog(`[ERROR] ${err.message}`)
                if (!hasResolved) {
                    hasResolved = true
                    resolve({ success: false, error: err.message })
                }
            })
        }

        launch()

        // Timeout de seguridad para el inicio
        setTimeout(() => {
            if (!hasResolved && activeSyncProcess) {
                hasResolved = true
                console.log('Background process fallback resolution')
                resolve({ success: true, data: { message: "Started (Timeout Fallback)" } })
            }
        }, 8000)
    })
}

function stopBackgroundPython() {
    if (activeSyncProcess) {
        restartCount = MAX_RESTARTS + 1 // Evitar reinicio
        activeSyncProcess.kill()
        activeSyncProcess = null
        return true
    }
    return false
}

/**
 * Registra los handlers IPC para GCP
 */
export function registerGCPHandlers() {
    let activeCredentialPath: string | null = null
    const fs = require('fs')
    const sessionPath = path.join(app.getPath('userData'), 'gcp_session.json')

    const getAuthHeader = () => {
        if (!activeCredentialPath) return ''
        return `import os; os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'${activeCredentialPath}';`
    }

    // Listar credenciales GCP disponibles
    ipcMain.handle('gcp:listCredentials', async () => {
        const code = `
import os, json, glob
creds_path = os.path.join(os.getcwd(), 'Claves GCP')
if not os.path.exists(creds_path):
    creds_path = 'Claves GCP'
files = glob.glob(os.path.join(creds_path, '*.json'))
result = []
for f in files:
    try:
        with open(f) as fp:
            data = json.load(fp)
            result.append({
                'path': f,
                'project_id': data.get('project_id', 'Unknown'),
                'client_email': data.get('client_email', 'Unknown')
            })
    except: pass
print(json.dumps(result))
`
        return runPythonCode(code)
    })

    // Autenticar con credenciales
    ipcMain.handle('gcp:authenticate', async (_, credPath: string) => {
        activeCredentialPath = credPath

        // Persistir sesión (actualizado: usa gcp:saveSession)
        try {
            let session = {}
            if (fs.existsSync(sessionPath)) {
                session = JSON.parse(fs.readFileSync(sessionPath, 'utf8'))
            }
            fs.writeFileSync(sessionPath, JSON.stringify({ ...session, lastCredentialPath: credPath }))
        } catch (e) {
            console.error('Error saving session:', e)
        }

        const code = `
${getAuthHeader()}
import os, json
from google.cloud import storage
try:
    client = storage.Client()
    buckets = [b.name for b in client.list_buckets()]
    print(json.dumps({'authenticated': True, 'buckets': buckets, 'project': client.project}))
except Exception as e:
    print(json.dumps({'authenticated': False, 'error': str(e)}))
`
        return runPythonCode(code)
    })

    // Listar buckets
    ipcMain.handle('gcp:listBuckets', async () => {
        const code = `
${getAuthHeader()}
import json
from google.cloud import storage
try:
    client = storage.Client()
    buckets = [{'name': b.name, 'location': b.location, 'storage_class': b.storage_class} for b in client.list_buckets()]
    print(json.dumps(buckets))
except:
    print(json.dumps([]))
`
        return runPythonCode(code)
    })

    // Listar objetos de un bucket
    ipcMain.handle('gcp:listObjects', async (_, bucketName: string, prefix: string = '') => {
        const code = `
${getAuthHeader()}
import json
from google.cloud import storage
try:
    client = storage.Client()
    bucket = client.bucket('${bucketName}')
    iterator = bucket.list_blobs(prefix='${prefix}', delimiter='/')
    blobs = list(iterator)
    objects = []
    
    # Agregar Archivos
    for blob in blobs:
        objects.append({
            'name': blob.name,
            'size': blob.size or 0,
            'updated': blob.updated.isoformat() if blob.updated else None,
            'contentType': blob.content_type,
            'fileCount': 0,
            'folderCount': 0
        })
    
    # Agregar Carpetas (prefixes) con estadísticas completas
    for p in iterator.prefixes:
        # Listar TODO bajo este prefijo para contar
        folder_blobs = list(bucket.list_blobs(prefix=p))
        folder_size = sum(b.size or 0 for b in folder_blobs)
        
        # Contar archivos (no terminan en /) y subcarpetas (terminan en /)
        file_count = len([b for b in folder_blobs if not b.name.endswith('/')])
        
        # Contar subcarpetas directas usando delimiter
        sub_iterator = bucket.list_blobs(prefix=p, delimiter='/')
        list(sub_iterator)  # Consume to get prefixes
        folder_count = len(list(sub_iterator.prefixes))
        
        objects.append({
            'name': p,
            'size': folder_size,
            'updated': None,
            'contentType': 'directory',
            'fileCount': file_count,
            'folderCount': folder_count
        })
        
    print(json.dumps(objects))
except Exception as e:
    print(f"Error: {str(e)}")
    print(json.dumps([]))
`
        return runPythonCode(code)
    })

    // Montar bucket como unidad
    ipcMain.handle('gcp:mountBucket', async (_, bucketName: string, driveLetter: string) => {
        const code = `
${getAuthHeader()}
import json, sys
sys.path.insert(0, '.')
from rclone_manager import RcloneManager
manager = RcloneManager()
success, message = manager.mount_gcp_bucket('${bucketName}', '${driveLetter}')
print(json.dumps({'success': success, 'message': message}))
`
        return runPythonCode(code)
    })

    // Desmontar unidad
    ipcMain.handle('gcp:unmountDrive', async (_, driveLetter: string) => {
        const code = `
import json, sys
sys.path.insert(0, '.')
from rclone_manager import RcloneManager
manager = RcloneManager()
success, message = manager.unmount_drive('${driveLetter}')
print(json.dumps({'success': success, 'message': message}))
`
        return runPythonCode(code)
    })

    // Listar contenido de carpeta local (para merge de vista)
    ipcMain.handle('gcp:listLocalFolder', async (_, localPath: string) => {
        const code = `
import os, json, datetime
try:
    path = r'${localPath}'
    if not os.path.exists(path):
        print(json.dumps([]))
    else:
        files = os.listdir(path)
        result = []
        for f in files:
            full = os.path.join(path, f)
            stat = os.stat(full)
            is_dir = os.path.isdir(full)
            
            # Formatear fecha para el frontend
            dt = datetime.datetime.fromtimestamp(stat.st_mtime)
            updated_iso = dt.isoformat()
            
            # Devolver objeto enriquecido
            result.append({
                'name': f,
                'size': stat.st_size,
                'updated': updated_iso,
                'contentType': 'directory' if is_dir else 'application/octet-stream',
                'isLocal': True
            })
        print(json.dumps(result))
except Exception as e:
    print(json.dumps([]))
`
        return runPythonCode(code)
    })

    // Iniciar sincronización (Optimizado para rutas relativas y slash normalization)
    ipcMain.handle('gcp:startSync', async (event, localPath: string, bucketName: string) => {
        const log = (msg: string) => event.sender.send('gcp:log', msg)
        const onEvent = (evt: any) => event.sender.send('gcp:sync_event', evt)

        const code = `
${getAuthHeader()}
import json, sys, time, os
# Add Legacy folder to path for file_watcher module
legacy_path = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'Legacy')
sys.path.insert(0, legacy_path)
sys.path.insert(0, '.')

def log_event(file, status, message=""):
    print(json.dumps({
        "type": "sync_event",
        "file": os.path.basename(file),
        "full_path": file,
        "status": status,
        "message": message
    }))
    sys.stdout.flush()

try:
    from file_watcher import RealTimeSync
    from google.cloud import storage

    class GCPAdapter:
        def __init__(self, root_path):
            self.client = storage.Client()
            self.root_path = root_path
            self.bucket = None

        def create_folder(self, bucket_name, folder_path):
            try:
                # Ensure folder path ends with slash
                if not folder_path.endswith('/'):
                    folder_path += '/'
                
                # Normalize path: prepend root folder name
                folder_name = os.path.basename(self.root_path)
                final_path = f"{folder_name}/{folder_path}".replace(os.sep, '/')
                
                self.bucket = self.client.bucket(bucket_name)
                blob = self.bucket.blob(final_path)
                blob.upload_from_string('') # Empty content for directory placeholder
                # log_event(str(final_path), "created_folder")
                return True
            except Exception as e:
                log_event(str(folder_path), "error", str(e))
                return False

        def upload_file(self, bucket_name, file_path, object_name=None):
            # Normalize path: ensure it's relative to root_path and uses Forward Slashes for GCS
            try:
                # Get the name of the synced folder (e.g., "Desktop")
                folder_name = os.path.basename(self.root_path)
                rel_path = os.path.relpath(file_path, self.root_path)
                # PREPEND folder name and FORCE FORWARD SLASHES for GCS object names
                blob_name = f"{folder_name}/{rel_path}".replace(os.sep, '/')

                log_event(file_path, "uploading")

                bucket = self.client.bucket(bucket_name)
                blob = bucket.blob(blob_name)
                blob.upload_from_filename(file_path)

                log_event(file_path, "synced")
                return True
            except Exception as e:
                log_event(file_path, "error", str(e))
                return False

        def delete_object(self, bucket_name, relative_path):
            try:
                # Normalize path for GCS
                folder_name = os.path.basename(self.root_path)
                blob_name = f"{folder_name}/{relative_path}".replace(os.sep, '/')
                
                bucket = self.client.bucket(bucket_name)
                blob = bucket.blob(blob_name)
                
                # Check if it's a folder (prefix) deletion
                # GCS is flat, but for "directory" placeholders we just delete the blob
                if blob.exists():
                    blob.delete()
                
                # Also handle recursive prefix deletion if it was a real folder
                prefix = blob_name if blob_name.endswith('/') else blob_name + '/'
                blobs_to_delete = list(bucket.list_blobs(prefix=prefix))
                if blobs_to_delete:
                    bucket.delete_blobs(blobs_to_delete)

                log_event(relative_path, "deleted")
                return True
            except Exception as e:
                log_event(relative_path, "error", str(e))
                return False

    def scan_and_upload(adapter, bucket_name, root_path):
        print(json.dumps({"type": "sync_event", "status": "scanning", "message": "Iniciando escaneo inicial..."}))
        sys.stdout.flush()
        count = 0
        try:
            # Sync root folder itself as a placeholder if active
            adapter.create_folder(bucket_name, "")
            
            for root, dirs, files in os.walk(root_path):
                # 1. Sync Directories (Empty folders support)
                for d in dirs:
                    full_dir_path = os.path.join(root, d)
                    rel_dir_path = os.path.relpath(full_dir_path, root_path)
                    adapter.create_folder(bucket_name, rel_dir_path)

                # 2. Sync Files
                for file in files:
                    full_path = os.path.join(root, file)
                    # Simple check: upload all (can be optimized later with hash check)
                    adapter.upload_file(bucket_name, full_path)
                    count += 1
            print(json.dumps({"type": "sync_event", "status": "scan_complete", "message": f"Escaneo inicial completado. {count} archivos procesados."}))
            sys.stdout.flush()
        except Exception as e:
            print(f"Error en escaneo inicial: {str(e)}")

    print(json.dumps({'success': True, 'message': 'Supervisor started'})) 
    sys.stdout.flush()

    root_path = r'${localPath}'
    adapter = GCPAdapter(root_path)
    
    # Perform initial scan before starting watcher
    scan_and_upload(adapter, '${bucketName}', root_path)

    def watcher_callback(msg):
        if "Detected" in msg:
            parts = msg.split(':')
            if len(parts) > 1:
                filename = parts[1].strip()
                log_event(filename, "pending")
        print(f"[WATCHER] {msg}")

    sync = RealTimeSync(adapter, '${bucketName}', root_path, callback=watcher_callback)
    
    success, msg = sync.start()
    if success:
        print(f"Sync Controller established: {msg}")
        sys.stdout.flush()
        while True:
            time.sleep(1)
    else:
        print(json.dumps({'success': False, 'error': msg}))

except Exception as e:
    print(json.dumps({'success': False, 'error': str(e)}))
`
        return startBackgroundPython(code, log, onEvent)
    })

    ipcMain.handle('gcp:stopSync', () => {
        const killed = stopBackgroundPython()
        return { success: killed }
    })

    // Diálogo para seleccionar carpeta
    ipcMain.handle('gcp:openDirectory', async () => {
        const { dialog } = require('electron')
        const result = await dialog.showOpenDialog({
            properties: ['openDirectory']
        })
        if (!result.canceled && result.filePaths.length > 0) {
            return { success: true, data: result.filePaths[0] }
        }
        return { success: false }
    })

    // Cargar credenciales desde archivo
    ipcMain.handle('gcp:uploadCredentials', async () => {
        const { dialog } = require('electron')
        const fs = require('fs')

        const result = await dialog.showOpenDialog({
            properties: ['openFile'],
            filters: [{ name: 'JSON', extensions: ['json'] }]
        })

        if (!result.canceled && result.filePaths.length > 0) {
            try {
                const sourcePath = result.filePaths[0]
                const fileName = path.basename(sourcePath)
                const destDir = path.join(LEGACY_PATH, 'Claves GCP')

                if (!fs.existsSync(destDir)) {
                    fs.mkdirSync(destDir, { recursive: true })
                }

                const destPath = path.join(destDir, fileName)
                fs.copyFileSync(sourcePath, destPath)

                return { success: true, data: destPath }
            } catch (e: any) {
                return { success: false, error: e.message }
            }
        }
        return { success: false }
    })

    // Subir archivo individual
    ipcMain.handle('gcp:uploadFile', async (event, bucketName: string, prefix: string = '') => {
        const { dialog } = require('electron')
        const result = await dialog.showOpenDialog({ properties: ['openFile'] })

        if (!result.canceled && result.filePaths.length > 0) {
            const localPath = result.filePaths[0]
            const fileName = path.basename(localPath)
            const objectName = prefix ? `${prefix}/${fileName}` : fileName

            // Log start
            event.sender.send('gcp:log', `Iniciando subida de archivo: ${fileName}`)

            const code = `
${getAuthHeader()}
import json
from google.cloud import storage
try:
    print("Conectando a GCP...")
    client = storage.Client()
    bucket = client.bucket('${bucketName}')
    blob = bucket.blob('${objectName}')
    print(f"Subiendo {r'${localPath}'}...")
    blob.upload_from_filename(r'${localPath}')
    print("Subida completada.")
    print(json.dumps({'success': True}))
except Exception as e:
    print(f"Error: {str(e)}")
    print(json.dumps({'success': False, 'error': str(e)}))
`
            return runPythonCode(code, (msg) => event.sender.send('gcp:log', msg))
        }
        return { success: false, cancelled: true }
    })

    // Subir carpeta completa (Recursivo)
    ipcMain.handle('gcp:uploadFolder', async (event, bucketName: string, prefix: string = '') => {
        const { dialog } = require('electron')
        const result = await dialog.showOpenDialog({ properties: ['openDirectory'] })

        if (!result.canceled && result.filePaths.length > 0) {
            const localPath = result.filePaths[0]
            const folderName = path.basename(localPath)
            const targetPrefix = prefix ? `${prefix}/${folderName}` : folderName

            event.sender.send('gcp:log', `Iniciando subida de carpeta: ${folderName}`)

            const code = `
${getAuthHeader()}
import json, os
from google.cloud import storage

def upload_folder():
    try:
        print("Conectando a GCP Storage...")
        client = storage.Client()
        bucket = client.bucket('${bucketName}')
        base_path = r'${localPath}'
        
        uploaded_count = 0
        print(f"Escaneando carpeta: {base_path}")
        
        for root, dirs, files in os.walk(base_path):
            for file in files:
                local_file = os.path.join(root, file)
                rel_path = os.path.relpath(local_file, base_path)
                blob_name = f"${targetPrefix}/{rel_path}".replace("\\\\", "/")
                
                print(f"Subiendo: {rel_path} -> {blob_name}")
                blob = bucket.blob(blob_name)
                blob.upload_from_filename(local_file)
                uploaded_count += 1
                
        print(f"Total subidos: {uploaded_count}")
        print(json.dumps({'success': True, 'count': uploaded_count}))
    except Exception as e:
        print(f"Error crítico: {str(e)}")
        print(json.dumps({'success': False, 'error': str(e)}))

upload_folder()
`
            return runPythonCode(code, (msg) => event.sender.send('gcp:log', msg))
        }
        return { success: false, cancelled: true }
    })

    // --- NEW: Cleanup Suite Handlers ---

    // Eliminar archivo/objeto (Recursivo para carpetas)
    ipcMain.handle('gcp:deleteObject', async (event, bucketName: string, objectName: string) => {
        // Use raw string in Python to handle backslashes correctly
        const escapedName = objectName.replace(/\\/g, '\\\\')
        const code = `
${getAuthHeader()}
from google.cloud import storage
import json

def delete_recursive():
    try:
        bucket_name = '${bucketName}'
        obj_name = "${escapedName}"
        print(f"Iniciando eliminación de: {obj_name} en bucket {bucket_name}")
        
        client = storage.Client()
        bucket = client.bucket(bucket_name)

        # 1. Intentar borrar el objeto exacto (si es un archivo)
        try:
            blob = bucket.blob(obj_name)
            blob.delete()
            print(f"Objeto principal {obj_name} eliminado.")
        except Exception:
            # Puede que no exista como blob simple si es una carpeta virtual, continuamos
            pass

        # 2. Búsqueda recursiva para carpetas (prefijos)
        # Añadimos / al final si no lo tiene para asegurar que tratamos como directorio
        prefix = obj_name if obj_name.endswith('/') else obj_name + '/'
        
        print(f"Buscando objetos con prefijo: {prefix}")
        blobs_to_delete = list(bucket.list_blobs(prefix=prefix))
        
        if len(blobs_to_delete) > 0:
            print(f"Encontrados {len(blobs_to_delete)} elementos hijos. Eliminando...")
            # Eliminación en lote (batch) es más robusta
            bucket.delete_blobs(blobs_to_delete)
            print("Limpieza recursiva completada.")
        
        print(json.dumps({'success': True}))

    except Exception as e:
        print(f"Error en eliminación: {str(e)}")
        print(json.dumps({'success': False, 'error': str(e)}))

delete_recursive()
`
        return runPythonCode(code, (msg) => event.sender.send('gcp:log', msg))
    })

    // Renombrar objeto
    ipcMain.handle('gcp:renameObject', async (event, bucketName: string, oldName: string, newName: string) => {
        const safeOldName = oldName.replace(/\\/g, '/')
        const safeNewName = newName.replace(/\\/g, '/')
        const code = `
${getAuthHeader()}
from google.cloud import storage
import json
try:
    old = "${safeOldName}"
    new = "${safeNewName}"
    print(f"Renombrando {old} -> {new}...")
    client = storage.Client()
    bucket = client.bucket('${bucketName}')
    blob = bucket.blob(old)
    bucket.rename_blob(blob, new)
    print("Renombrado correctamente")
    print(json.dumps({'success': True}))
except Exception as e:
    print(json.dumps({'success': False, 'error': str(e)}))
`
        return runPythonCode(code, (msg) => event.sender.send('gcp:log', msg))
    })

    // Leer contenido (Preview)
    ipcMain.handle('gcp:getFileContent', async (event, bucketName: string, objectName: string) => {
        const safeObjectName = objectName.replace(/\\/g, '/')
        const code = `
${getAuthHeader()}
from google.cloud import storage
import json
try:
    obj_name = "${safeObjectName}"
    client = storage.Client()
    bucket = client.bucket('${bucketName}')
    blob = bucket.blob(obj_name)
    
    # Read first 10KB for preview safety
    content = blob.download_as_text(start=0, end=10240) 
    print(json.dumps({'success': True, 'content': content}))
except Exception as e:
    print(json.dumps({'success': False, 'error': str(e)}))
`
        return runPythonCode(code)
    });

    // Clean Bucket (Delete ALL objects)
    ipcMain.handle('gcp:cleanBucket', async (event, bucketName: string) => {
        const code = `
${getAuthHeader()}
from google.cloud import storage
import json

def clean_bucket():
    try:
        print(f"Limpiando bucket: ${bucketName}...")
        client = storage.Client()
        bucket = client.bucket('${bucketName}')
        
        blobs = list(bucket.list_blobs())
        total = len(blobs)
        
        if total == 0:
            print("El bucket ya está vacío.")
            print(json.dumps({'success': True, 'deleted': 0}))
            return
        
        print(f"Eliminando {total} objetos...")
        bucket.delete_blobs(blobs)
        print(f"Bucket limpio. {total} objetos eliminados.")
        print(json.dumps({'success': True, 'deleted': total}))
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(json.dumps({'success': False, 'error': str(e)}))

clean_bucket()
`
        return runPythonCode(code, (msg) => event.sender.send('gcp:log', msg))
    });


    // Obtener sesión guardada
    ipcMain.handle('gcp:getSession', async () => {
        try {
            if (fs.existsSync(sessionPath)) {
                const data = fs.readFileSync(sessionPath, 'utf8')
                const session = JSON.parse(data)
                // If there's a credential path, set it as active
                if (session.lastCredentialPath) {
                    activeCredentialPath = session.lastCredentialPath
                }
                return { success: true, data: session }
            }
            return { success: true, data: {} }
        } catch (e: any) {
            return { success: false, error: e.message }
        }
    })

    ipcMain.handle('gcp:saveSession', async (_, data: any) => {
        try {
            let session = {}
            if (fs.existsSync(sessionPath)) {
                session = JSON.parse(fs.readFileSync(sessionPath, 'utf8'))
            }
            const newSession = { ...session, ...data }
            fs.writeFileSync(sessionPath, JSON.stringify(newSession))

            // Update active credential if passed
            if (data.lastCredentialPath) {
                activeCredentialPath = data.lastCredentialPath
            }

            return { success: true }
        } catch (e: any) {
            return { success: false, error: e.message }
        }
    })

    // Auto-lanzamiento al iniciar Windows
    ipcMain.handle('gcp:setAutoLaunch', async (_, enabled: boolean) => {
        try {
            app.setLoginItemSettings({
                openAtLogin: enabled,
                path: app.getPath('exe'),
                args: ['--hidden']
            })
            return { success: true }
        } catch (e: any) {
            return { success: false, error: e.message }
        }
    })

    ipcMain.handle('gcp:getAutoLaunch', async () => {
        try {
            const settings = app.getLoginItemSettings()
            return { success: true, enabled: settings.openAtLogin }
        } catch (e: any) {
            return { success: false, error: e.message }
        }
    })
}

export { runPythonScript, runPythonCode }
