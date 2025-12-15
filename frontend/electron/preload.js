/**
 * Electron Preload Script
 * Exposes safe APIs to the renderer process
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getAppPath: () => ipcRenderer.invoke('get-app-path'),
  onNewEntry: (callback) => ipcRenderer.on('new-entry', callback),
  onExcelFileSelected: (callback) => ipcRenderer.on('excel-file-selected', callback)
});
