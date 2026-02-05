import { app, BrowserWindow, ipcMain } from 'electron'
import path from 'path'
import { registerGCPHandlers } from './python-bridge'


let mainWindow: any = null

const createWindow = () => {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 900,
        minHeight: 600,
        frame: false, // Frameless for custom titlebar
        transparent: true, // For glassmorphism effects
        backgroundColor: '#00000000',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
        },
    })

    // Load the app
    if (process.env.VITE_DEV_SERVER_URL) {
        mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL)
        // mainWindow.webContents.openDevTools() // Disabled by user request
    } else {
        mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
    }

    // Start maximized
    mainWindow.maximize()
}

// Window control handlers
ipcMain.handle('window:minimize', () => mainWindow?.minimize())
ipcMain.handle('window:maximize', () => {
    if (mainWindow?.isMaximized()) {
        mainWindow.unmaximize()
    } else {
        mainWindow?.maximize()
    }
})
ipcMain.handle('window:close', () => mainWindow?.close())

// App info
ipcMain.handle('app:version', () => app.getVersion())
ipcMain.handle('app:name', () => app.getName())

app.whenReady().then(() => {
    registerGCPHandlers()
    createWindow()
})

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit()
    }
})

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow()
    }
})
