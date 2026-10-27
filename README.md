# FileZ

A tiny Flask app that serves a folder of files as a simple downloads page. On first run, choose the folder to share (for example, a folder on your Desktop or in Documents). Files appear with their size, date, a download button, and an on-demand SHA-256 checksum. It runs through Waitress and can be installed as a background Windows service.

## Features

- Lists every file in `files/` (subfolders included), newest first
- One-click downloads
- Filter box to find a file by name
- SHA-256 checksum on request, handy for unsigned installers
- Hidden files (names starting with `.`) are never listed or served
- Path traversal is blocked
- Runs as a Windows service with automatic start and restart on crash

## Run it

**Windows**

```bat
run.bat
```

**Linux/macOS**

```bash
./run.sh
```

On first run, the launcher asks for the folder to serve. Enter its full path, or press Enter to use the default `files/` folder. The choice is saved in `settings.json`, and changes to that folder appear without restarting. Run `python setup.py` to choose a different folder later.

## Discovery client

The JavaScript desktop client is in [`client/`](client/). It scans the LAN for Filedrop servers and opens the selected server in the system browser. See [`client/README.md`](client/README.md) for development and packaging instructions. The Electron client targets Windows, macOS, and Linux; Android packaging is planned separately.

## Install as a Windows service

1. Download [NSSM](https://nssm.cc) and put `nssm.exe` on your `PATH`.
2. Open a terminal **as Administrator** in this folder.
3. Run:

```bat
install_service.bat
```

The script creates the virtual environment, asks which folder to serve, registers the `Filedrop` service (starts at boot, restarts if it crashes), writes logs to `logs\filedrop.log`, opens the firewall port, and starts it. To change the folder later, stop the service, run `python setup.py`, then restart it. To remove it, run `uninstall_service.bat`. Your files are not touched.

Manage it later with `nssm restart Filedrop`, `nssm stop Filedrop`, or the Services app.

## Configuration

Set these environment variables before starting (for the service, edit them with `nssm edit Filedrop`):

| Variable          | Default        | Purpose                          |
| ----------------- | -------------- | -------------------------------- |
| `FILEDROP_DIR`    | saved setup choice, otherwise `./files` | Folder to serve (overrides the saved choice) |
| `FILEDROP_HOST`   | `0.0.0.0`      | Interface to listen on           |
| `FILEDROP_PORT`   | `1080`         | Port                             |
| `FILEDROP_TITLE`  | `Filedrop`     | Heading shown on the page        |
| `FILEDROP_NAME`   | hostname-based Filedrop name | Friendly name advertised to discovery clients |

The server advertises `_filedrop._tcp.local` over mDNS/DNS-SD while it is running. The advertisement includes its friendly name, persistent server ID, and port. The server ID is stored in `settings.json` and remains stable across restarts. Devices on networks that block multicast may not see the advertisement.

The Windows service installer allows the configured TCP port and mDNS UDP port 5353 through Windows Firewall for the local subnet. To change the service port, edit `PORT` at the top of `install_service.bat` before installing.

## Putting it on the internet

Filedrop has no login: anyone who can reach the page can see and download everything in the folder. Only put files there that you are happy to share. Discovery is not authentication. Keep the server on a trusted local network and do not forward its port from your router.

## Project structure

```
filedrop/
├── app.py                  # Flask app: page, download, checksum routes
├── config.py               # Settings read from environment variables
├── requirements.txt
├── templates/index.html    # The downloads page
├── static/style.css
├── files/                  # Put the files to share here
├── run.bat / run.sh        # Run in a console
├── install_service.bat     # Install as a Windows service (NSSM)
└── uninstall_service.bat
```
