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
        openDirectory: () => ipcRenderer.invoke('gcp:openDirectory'),
        uploadCredentials: () => ipcRenderer.invoke('gcp:uploadCredentials'),
        uploadFile: (bucket: string, prefix: string) => ipcRenderer.invoke('gcp:uploadFile', bucket, prefix),
        uploadFolder: (bucket: string, prefix: string) => ipcRenderer.invoke('gcp:uploadFolder', bucket, prefix),
        loadSession: () => ipcRenderer.invoke('gcp:loadSession')
    }
})
