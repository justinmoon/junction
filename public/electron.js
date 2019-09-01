const electron = require('electron');
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;

const path = require('path');
const isDev = require('electron-is-dev');

let mainWindow;

// hacks
// FIXME: how to delay BrowserWindow until this is running
var spawn = require('child_process').spawn;
var executablePath = "./dist/dev/dev"
var spawned = spawn(executablePath)
spawned.stdout.on('data', function(data) {
    console.log('stdout: ' + data.toString());
});
spawned.stderr.on('data', function(data) {
    console.log('stderr: ' + data.toString());
});
spawned.on('exit', function (code) {
  console.log('child process exited with code ' + code.toString());
});

const sleep = (milliseconds) => {
  return new Promise(resolve => setTimeout(resolve, milliseconds))
}
// end hacks

function createWindow() {
  mainWindow = new BrowserWindow({width: 900, height: 680});
  mainWindow.loadURL('http://localhost:5000')
  //mainWindow.loadURL(isDev ? 'http://localhost:3000' : `file://${path.join(__dirname, '../build/index.html')}`);
  //if (isDev) {
    //// Open the DevTools.
    ////BrowserWindow.addDevToolsExtension('<location to your react chrome extension>');
    //mainWindow.webContents.openDevTools();
  //}
  mainWindow.on('closed', () => mainWindow = null);
}

app.on('ready', sleep(1000).then(createWindow));

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});


app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});
