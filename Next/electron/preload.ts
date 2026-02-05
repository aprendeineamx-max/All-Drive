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

    // Future: Add cloud storage operations here
    // listBuckets: () => ipcRenderer.invoke('storage:listBuckets'),
    // mountDrive: (bucket: string, letter: string) => ipcRenderer.invoke('storage:mount', bucket, letter),
    // etc.
})
