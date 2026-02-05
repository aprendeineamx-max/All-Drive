import { contextBridge, ipcRenderer } from 'electron'

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the whole object
contextBridge.exposeInMainWorld('electronAPI', {
    // Window controls
    minimize: () => ipcRenderer.invoke('window:minimize'),
    maximize: () => ipcRenderer.invoke('window:maximize'),
    close: () => ipcRenderer.invoke('window:close'),

    // App info
    getVersion: () => ipcRenderer.invoke('app:version'),
    getAppName: () => ipcRenderer.invoke('app:name'),

    // GCP Operations
    gcp: {
        listCredentials: () => ipcRenderer.invoke('gcp:listCredentials'),
        authenticate: (credPath: string) => ipcRenderer.invoke('gcp:authenticate', credPath),
        listBuckets: () => ipcRenderer.invoke('gcp:listBuckets'),
        listObjects: (bucket: string, prefix: string) => ipcRenderer.invoke('gcp:listObjects', bucket, prefix),
        mountBucket: (bucket: string, drive: string) => ipcRenderer.invoke('gcp:mountBucket', bucket, drive),
        unmountDrive: (drive: string) => ipcRenderer.invoke('gcp:unmountDrive', drive),
        startSync: (localPath: string, bucketName: string) => ipcRenderer.invoke('gcp:startSync', localPath, bucketName),
        stopSync: () => ipcRenderer.invoke('gcp:stopSync'),
        getDesktopPath: () => ipcRenderer.invoke('gcp:getDesktopPath'),
        openDirectory: () => ipcRenderer.invoke('gcp:openDirectory'),
        uploadCredentials: () => ipcRenderer.invoke('gcp:uploadCredentials'),
        uploadFile: (bucket: string, prefix: string) => ipcRenderer.invoke('gcp:uploadFile', bucket, prefix),
        uploadFolder: (bucket: string, prefix: string) => ipcRenderer.invoke('gcp:uploadFolder', bucket, prefix),
        onLog: (callback: (message: string) => void) => {
            const subscription = (_: any, msg: string) => callback(msg)
            ipcRenderer.on('gcp:log', subscription)
            return () => ipcRenderer.removeListener('gcp:log', subscription)
        },
        onSyncEvent: (callback: (event: any) => void) => {
            const subscription = (_: any, evt: any) => callback(evt)
            ipcRenderer.on('gcp:sync_event', subscription)
            return () => ipcRenderer.removeListener('gcp:sync_event', subscription)
        },
        listLocalFolder: (path: string) => ipcRenderer.invoke('gcp:listLocalFolder', path),
        loadSession: () => ipcRenderer.invoke('gcp:loadSession'),
        saveSession: (data: any) => ipcRenderer.invoke('gcp:saveSession', data),
        deleteObject: (bucket: string, objectName: string) => ipcRenderer.invoke('gcp:deleteObject', bucket, objectName),
        renameObject: (bucket: string, oldName: string, newName: string) => ipcRenderer.invoke('gcp:renameObject', bucket, oldName, newName),
        getFileContent: (bucket: string, objectName: string) => ipcRenderer.invoke('gcp:getFileContent', bucket, objectName)
    }
})
