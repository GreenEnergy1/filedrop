const { app, BrowserWindow, ipcMain, shell } = require('electron');
const bonjour = require('bonjour')();
const http = require('node:http');
const net = require('node:net');
const path = require('node:path');

const SERVICE_TYPE = 'filedrop';
const servers = new Map();
let browser;
let mainWindow;

function makeWindow() {
  mainWindow = new BrowserWindow({
    width: 780,
    height: 620,
    minWidth: 560,
    minHeight: 460,
    title: 'Filedrop',
    icon: path.join(__dirname, 'assets', 'icon.png'),
    backgroundColor: '#f3f7ff',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  });
  mainWindow.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  mainWindow.webContents.on('will-navigate', event => event.preventDefault());
  mainWindow.loadFile(path.join(__dirname, 'index.html'));
  mainWindow.on('closed', () => { mainWindow = null; });
}

function sendServers() {
  if (!mainWindow || mainWindow.isDestroyed()) return;
  const list = [...servers.values()].sort((a, b) => a.name.localeCompare(b.name));
  mainWindow.webContents.send('discovery:servers', list);
}

function serviceToServer(service) {
  const addresses = (service.addresses || []).filter(address => net.isIP(address.split('%')[0]));
  const address = addresses.find(value => net.isIPv4(value)) || addresses[0];
  if (!address || !Number.isInteger(service.port) || service.port < 1 || service.port > 65535) return null;

  const properties = service.txt || {};
  const id = String(properties.id || service.fqdn || service.name);
  return {
    id,
    name: String(properties.name || service.name || 'Filedrop server'),
    address,
    port: service.port,
    key: id
  };
}

function startScan() {
  if (browser) {
    browser.update();
    return;
  }
  servers.clear();
  browser = bonjour.find({ type: SERVICE_TYPE, protocol: 'tcp' });
  browser.on('up', service => {
    const server = serviceToServer(service);
    if (!server) return;
    servers.set(server.key, server);
    sendServers();
  });
  browser.on('down', service => {
    const properties = service.txt || {};
    const id = String(properties.id || service.fqdn || service.name);
    servers.delete(id);
    sendServers();
  });
  browser.on('error', error => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('discovery:error', error.message || 'LAN scan failed.');
    }
  });
  browser.start();
}

function checkHealth(server) {
  return new Promise((resolve, reject) => {
    const host = server.address.split('%')[0];
    const options = {
      hostname: host,
      family: net.isIP(host),
      port: server.port,
      path: '/healthz',
      timeout: 2500
    };
    const request = http.get(options, response => {
      let body = '';
      response.setEncoding('utf8');
      response.on('data', chunk => { body += chunk; });
      response.on('end', () => {
        if (response.statusCode === 200 && body.trim() === 'ok') resolve();
        else reject(new Error('The server did not pass its health check.'));
      });
    });
    request.on('timeout', () => request.destroy(new Error('Server did not respond in time.')));
    request.on('error', reject);
  });
}

ipcMain.handle('discovery:start', () => {
  startScan();
  return [...servers.values()];
});

ipcMain.handle('discovery:connect', async (_event, id) => {
  const server = servers.get(String(id));
  if (!server) throw new Error('That server is no longer available. Scan again and retry.');
  await checkHealth(server);
  const host = server.address.includes(':') ? `[${server.address}]` : server.address;
  const url = `http://${host}:${server.port}/`;
  await shell.openExternal(url);
  return url;
});

app.whenReady().then(() => {
  makeWindow();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) makeWindow(); });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => {
  if (browser) browser.stop();
  bonjour.destroy();
});
