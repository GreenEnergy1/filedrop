# Filedrop Discovery Client

The first client is a small Electron desktop app. It discovers `_filedrop._tcp.local` servers, displays their friendly name, ID, and address, checks `/healthz`, and opens the selected server in the system browser.

Electron packages one JavaScript application for Windows, macOS, and Linux. Android is not an Electron target; an Android client remains a planned follow-up using a JavaScript mobile runtime and a platform-specific discovery adapter. The server discovery format and screen flow should remain compatible.

## Develop

Install Node.js 20 or newer, then from this directory run:

```sh
npm install
npm start
```

Press **Scan** to find services on the current LAN. The operating system firewall or network may block multicast DNS. Both the server and client must be on a network that permits local multicast discovery.

## Package

Run the command on the target operating system (cross-building is not guaranteed):

```sh
npm run dist:win
npm run dist:mac
npm run dist:linux
```

Build artifacts are written to `dist/`. macOS signing and notarization are not configured yet.
