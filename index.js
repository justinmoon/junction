const {app, BrowserWindow, shell} = require('electron')
const {PythonShell} = require('python-shell')

function createWindow () {
  // run junction
  PythonShell.run('electron.py', {}, function  (err, results)  {
   if  (err)  console.log(err);
  });

  // open browser windows, visit junction
  window = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nativeWindowOpen: true,
    },
  })

  window.webContents.on('new-window', (event, url, frameName, disposition, options, additionalFeatures) => {
    if (frameName === 'modal') {
      // open window as modal
      event.preventDefault()
      Object.assign(options, {
        modal: true,
        parent: mainWindow,
        width: 100,
        height: 100
      })
      event.newGuest = new BrowserWindow(options)
    }
  })
  //window.loadFile('index.html')
  window.loadURL('http://localhost:5000')
}

app.on('ready', createWindow)

app.on('window-all-closed', () => {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

