# Filedrop LAN Discovery Plan

## Goal

Make it easy to find and connect to Filedrop servers on the same local network without asking users to look up or type IP addresses. The client is planned for Windows, macOS, Linux, and Android.

## Agreed first-version experience

1. Open the client.
2. Start a scan for Filedrop servers on the local network.
3. Show the discovered servers in a simple list.
4. Select a server and choose **Connect**.
5. Open that server's Filedrop page in the system browser; browsing and downloading remain in the browser for the first version.

The client should make scanning and connecting clear, show a useful empty state when no servers are found, and allow the user to scan again.

## Server discovery design

- Keep the Flask server as the file-serving layer.
- Use a fixed default port of `1080`, configurable in the same way as other server settings.
- Listen on all network interfaces so other devices on the LAN can connect.
- Advertise the server using mDNS / DNS-SD with service type `_filedrop._tcp.local`.
- Advertise a friendly instance name, port, and a stable per-installation server ID. Keep any TXT metadata minimal and non-sensitive.
- Generate the server ID once and persist it in the server's settings. It should survive restarts and changes to the friendly name or IP address.
- Resolve discovered services to a reachable address and have the client open that address and port in the browser. Treat a `.local` hostname as a convenience, not a dependency.
- Use the existing health endpoint if present; confirm its route during implementation and add it if missing so the client can distinguish a responding server from a stale discovery result.

## Client design

- Build the desktop client in JavaScript and package it with Node tooling for Windows, macOS, and Linux. Android remains a target, but needs a mobile JavaScript runtime and platform-specific discovery integration because Electron does not target Android. Keep the DNS-SD contract and simple scan/connect flow consistent across clients.
- Scan only when requested by the user in the first version; show scan progress and provide a rescan action.
- Display each result with its friendly name and stable ID. The resolved address and port can be shown as secondary or diagnostic details.
- Handle duplicate friendly names by making the stable ID or address available to distinguish entries.
- On connect, open the discovered server URL in the system browser.
- Handle permission prompts and platform-specific multicast/network discovery requirements, especially on Android.
- If a platform cannot perform mDNS discovery reliably, document the limitation and consider a manual address fallback in a later iteration.

## Delivery stages

### Stage 1: LAN-ready server

- Confirm the current server configuration and health route.
- Set the default port to `1080` while preserving environment/configuration overrides.
- Keep binding to `0.0.0.0`.
- Persist a stable server ID and configurable friendly name.
- Add mDNS / DNS-SD advertisement lifecycle management: announce while the server is running and withdraw on shutdown.
- Update launchers, Windows service setup, firewall guidance, and README configuration documentation for the chosen port and discovery behavior.

### Stage 2: Minimal discovery client

- Desktop framework selected: Electron, with the Node `bonjour` package for mDNS/DNS-SD scanning and electron-builder for distributables.
- Implemented initial Windows/macOS/Linux client flow: open, scan, list, select, health-check, and launch in the system browser.
- Desktop app shows friendly names and IDs, with scan and connection status states.
- Remaining: install dependencies, run the app, and validate discovery and packaging on supported desktop systems.
- Android remains in this stage as a separate client target; choose a mobile JavaScript runtime and mDNS integration, accounting for Android local-network permissions and multicast behavior.

### Stage 3: Client's own file browser

- Add an in-client file listing and file detail view as an alternative to launching the system browser.
- Support downloads and the existing server behaviors, including filtering and on-demand SHA-256 checksums.
- Keep external-browser launch available as a user choice.

## Later enhancements to consider

- Remember recently connected servers and allow pinning favorites.
- Show server status, address, port, share title, and version where useful.
- Add optional file metadata, thumbnails, and device badges.
- Add an optional access token or other lightweight trust mechanism for shared networks.
- Consider automatic scanning or background refresh only if it is useful and behaves well with mobile battery and permission limits.
- Consider pairing or stronger authentication if the intended trust model expands beyond a trusted LAN.

## Security and network assumptions

- Discovery is for local-network convenience; it is not authentication.
- The server currently has no login, so anyone who can reach it may be able to list and download shared files. Share only files intended for that audience.
- Keep the service intended for LAN use and do not recommend router port forwarding or public exposure as part of this plan.
- A token can be considered as an opt-in later enhancement; the first version should clearly communicate the local-trust model.
- Account for host firewall prompts/rules and networks that block multicast or isolate wireless clients.

## Open implementation choices

- Choose the JavaScript mobile runtime and discovery adapter for Android; Electron covers desktop only.
- Decide how the server ID and friendly name are stored alongside the current `settings.json` configuration.
- Confirm whether `/healthz` already exists and define its response before wiring client health checks.
- Decide whether first-version connect launches the browser immediately or presents a brief server detail/confirmation screen.
