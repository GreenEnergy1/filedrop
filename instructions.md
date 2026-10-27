# Agent Instructions

## Start of each session

1. Read this file, then read `plan.md` and the relevant project files before editing.
2. Treat `plan.md` as the product plan and follow its delivery order. If the user changes direction, update the plan to match before implementing the new direction.
3. Check the current working tree and preserve existing user changes. Keep work focused on the active stage.
4. Do not build a later-stage feature unless the user asks or the plan explicitly makes it part of the active stage.

## Project rules

- The server is the existing Flask/Waitress app. Keep it intended for a trusted LAN; discovery does not provide authentication.
- The discovery service is `_filedrop._tcp.local`; retain the stable server ID, friendly name, advertised port, and `/healthz` check contract.
- The first client uses JavaScript and Electron for Windows, macOS, and Linux. It scans on demand and opens a healthy server in the system browser. Do not move file browsing into the client until the plan's later browser stage.
- Keep the client visual style aligned with the served page: use the same blue palette and quiet, spacious layout. When changing colors, compare against the design tokens in `static/style.css`.
- Android is a planned separate packaging/runtime iteration. Preserve the DNS-SD contract and keep the UI flow simple so the Android client can share the experience.
- Keep Electron renderer isolation enabled. Expose only narrow, validated operations through the preload bridge; do not give the renderer Node access.
- Use `settings.json` for persistent server settings and preserve existing keys when updating it.
- Keep `README.md`, `client/README.md`, and `plan.md` consistent with implemented behavior.

## End-of-session handoff

This file is the single current handoff, not an append-only diary. At the end of each implementation session:

1. Replace the **Current Handoff** section below with the new current state, completed work, constraints discovered, and the next concrete task.
2. Remove obsolete session-specific notes instead of accumulating them. Keep the stable project rules above.
3. Update `plan.md` when scope, decisions, or delivery status changes; do not erase its product requirements or future-stage ideas.
4. Report what changed, what was checked, and any checks blocked by missing tools or environment.

## Current Handoff

- Server discovery stage is implemented in the working tree: port `1080`, persistent server ID, mDNS advertisement, and Windows firewall guidance.
- The Electron JavaScript client now has the first scan/list/select/connect flow for Windows, macOS, and Linux. Android still needs its own compatible runtime and discovery adapter.
- No Node/npm runtime was available in the previous session, so dependency installation, launch, and packaging were not verified. Check tool availability before attempting those steps.
- Next: inspect the client changes, install dependencies when Node/npm are available, then run and validate discovery against the Python server. Address compatibility issues before beginning Android packaging.
