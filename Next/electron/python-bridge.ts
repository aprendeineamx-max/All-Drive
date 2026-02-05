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

/**
 * Ejecuta un comando Python y devuelve el resultado
 */
function runPythonScript(scriptPath: string, args: string[] = []): Promise<PythonResult> {
    return new Promise((resolve) => {
        const fullPath = path.join(LEGACY_PATH, scriptPath)
        const pythonProcess = spawn('python', [fullPath, ...args], {
            cwd: LEGACY_PATH,
            env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
        })

        let stdout = ''
        let stderr = ''

        pythonProcess.stdout.on('data', (data) => {
            stdout += data.toString()
        })

        pythonProcess.stderr.on('data', (data) => {
            stderr += data.toString()
        })

        pythonProcess.on('close', (code) => {
            if (code === 0) {
                try {
                    const data = JSON.parse(stdout.trim())
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
function runPythonCode(code: string): Promise<PythonResult> {
    return new Promise((resolve) => {
        const pythonProcess = spawn('python', ['-c', code], {
            cwd: LEGACY_PATH,
            env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
        })

        let stdout = ''
        let stderr = ''

        pythonProcess.stdout.on('data', (data) => {
            stdout += data.toString()
        })

        pythonProcess.stderr.on('data', (data) => {
            stderr += data.toString()
        })

        pythonProcess.on('close', (code) => {
            if (code === 0) {
                try {
                    const data = JSON.parse(stdout.trim())
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
 * Registra los handlers IPC para GCP
 */
export function registerGCPHandlers() {
    let activeCredentialPath: string | null = null

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

        // Persistir sesión
        try {
            const fs = require('fs')
            const sessionPath = path.join(app.getPath('userData'), 'gcp_session.json')
            fs.writeFileSync(sessionPath, JSON.stringify({ lastCredentialPath: credPath }))
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
    blobs = list(bucket.list_blobs(prefix='${prefix}', delimiter='/'))
    objects = []
    for blob in blobs:
        objects.append({
            'name': blob.name,
            'size': blob.size,
            'updated': blob.updated.isoformat() if blob.updated else None,
            'content_type': blob.content_type
        })
    print(json.dumps(objects))
except:
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

    // Iniciar sincronización
    ipcMain.handle('gcp:startSync', async (_, localPath: string, bucketName: string) => {
        const code = `
${getAuthHeader()}
import json, sys
sys.path.insert(0, '.')
from file_watcher import RealTimeSync
from google.cloud import storage

class GCPAdapter:
    def __init__(self):
        self.client = storage.Client()
    def upload_file(self, bucket_name, file_path, object_name=None):
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(object_name or file_path)
        blob.upload_from_filename(file_path)
        return True

adapter = GCPAdapter()
sync = RealTimeSync(adapter, '${bucketName}', r'${localPath}')
success, msg = sync.start()
print(json.dumps({'success': success, 'message': msg}))
`
        return runPythonCode(code)
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

    // Gestión de Sesión
    const sessionPath = path.join(app.getPath('userData'), 'gcp_session.json')
    const fs = require('fs')

    ipcMain.handle('gcp:loadSession', async () => {
        try {
            if (fs.existsSync(sessionPath)) {
                const session = JSON.parse(fs.readFileSync(sessionPath, 'utf8'))
                if (session.lastCredentialPath) {
                    // Restaurar autenticación automáticamente
                    activeCredentialPath = session.lastCredentialPath
                    return { success: true, data: session }
                }
            }
        } catch (e) {
            console.error('Error loading session:', e)
        }
        return { success: false }
    })
}

export { runPythonScript, runPythonCode }
