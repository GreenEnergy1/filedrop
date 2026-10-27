const list = document.getElementById('server-list');
const scanButton = document.getElementById('scan-button');
const connectButton = document.getElementById('connect-button');
const scanMessage = document.getElementById('scan-message');
const selectionHint = document.getElementById('selection-hint');

let servers = [];
let selectedId = null;
let scanStarted = false;

function setMessage(message, state = '') {
  scanMessage.textContent = message;
  scanMessage.classList.toggle('empty', state !== 'scanning' && servers.length === 0);
}

function render() {
  list.replaceChildren();
  for (const server of servers) {
    const card = document.createElement('button');
    card.type = 'button';
    card.className = `server-card${selectedId === server.id ? ' selected' : ''}`;
    card.setAttribute('aria-pressed', selectedId === server.id ? 'true' : 'false');
    card.addEventListener('click', () => {
      selectedId = server.id;
      render();
    });

    const details = document.createElement('span');
    details.className = 'server-details';
    const name = document.createElement('span');
    name.className = 'server-name';
    name.textContent = server.name;
    details.append(name);

    const location = document.createElement('span');
    location.className = 'server-location';
    const address = document.createElement('span');
    address.className = 'server-address';
    const displayHost = server.address.includes(':') ? `[${server.address}]` : server.address;
    address.textContent = `${displayHost}:${server.port}`;
    const id = document.createElement('span');
    id.className = 'server-id';
    id.textContent = `ID ${server.id}`;
    location.append(address, id);

    card.append(details, location);
    list.append(card);
  }

  connectButton.disabled = !selectedId || !servers.some(server => server.id === selectedId);
  selectionHint.textContent = selectedId ? 'Connect to open this server in your browser' : 'Select a server to continue';
  if (servers.length) setMessage(`${servers.length} server${servers.length === 1 ? '' : 's'} found.`);
  else if (scanStarted) setMessage('No servers found yet. Make sure a Filedrop server is running on this network.');
}

scanButton.addEventListener('click', async () => {
  scanStarted = true;
  scanButton.disabled = true;
  scanButton.innerHTML = '<span aria-hidden="true">↻</span> Scanning';
  setMessage('Looking for Filedrop servers…', 'scanning');
  try {
    const initial = await window.filedrop.startScan();
    servers = initial;
    if (!servers.some(server => server.id === selectedId)) selectedId = null;
    render();
  } catch (error) {
    setMessage(error.message || 'Could not scan the local network.');
  } finally {
    scanButton.disabled = false;
    scanButton.innerHTML = '<span aria-hidden="true">↻</span> Scan again';
  }
});

connectButton.addEventListener('click', async () => {
  if (!selectedId) return;
  connectButton.disabled = true;
  connectButton.textContent = 'Checking…';
  setMessage('Checking the server before opening it…');
  try {
    await window.filedrop.connect(selectedId);
    setMessage('Opened in your browser.');
  } catch (error) {
    setMessage(error.message || 'Could not connect to that server.');
  } finally {
    connectButton.innerHTML = 'Connect <span aria-hidden="true">↗</span>';
    render();
  }
});

window.filedrop.onServers(nextServers => {
  servers = nextServers;
  if (!servers.some(server => server.id === selectedId)) selectedId = null;
  render();
});

window.filedrop.onError(message => setMessage(message));
