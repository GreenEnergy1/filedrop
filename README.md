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
| `FILEDROP_PORT`   | `8080`         | Port                             |
| `FILEDROP_TITLE`  | `Filedrop`     | Heading shown on the page        |

To change the port for the service, edit `PORT` at the top of `install_service.bat` before installing.

## Putting it on the internet

Filedrop has no login: anyone who can reach the page can see and download everything in the folder. Only put files there that you are happy to share. For public use, run it behind Caddy or a Cloudflare Tunnel so you get HTTPS and don't have to open a port on your router.

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
