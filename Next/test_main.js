const { app, BrowserWindow, ipcMain } = require('electron');
console.log('DEBUG_OUTPUT_CHECK');
console.log('IPCMain exists:', !!ipcMain);
console.log('App version:', app.getVersion());
process.exit(0);
