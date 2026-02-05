const { app, ipcMain } = require('electron');
const fs = require('fs');

const log = (msg) => {
    fs.appendFileSync('test_log.txt', msg + '\n');
    console.log(msg);
};

log('Script START');
log('Process Type: ' + process.type);
log('Versions: ' + JSON.stringify(process.versions));

app.on('ready', () => {
    log('App READY');
    log('IPCMain exists: ' + !!ipcMain);
    if (ipcMain) {
        log('IPCMain types: ' + typeof ipcMain.handle);
    }
    app.quit();
});
