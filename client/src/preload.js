const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('filedrop', {
  startScan: () => ipcRenderer.invoke('discovery:start'),
  connect: id => ipcRenderer.invoke('discovery:connect', id),
  onServers: callback => {
    const listener = (_event, servers) => callback(servers);
    ipcRenderer.on('discovery:servers', listener);
    return () => ipcRenderer.removeListener('discovery:servers', listener);
  },
  onError: callback => {
    const listener = (_event, message) => callback(message);
    ipcRenderer.on('discovery:error', listener);
    return () => ipcRenderer.removeListener('discovery:error', listener);
  }
});
