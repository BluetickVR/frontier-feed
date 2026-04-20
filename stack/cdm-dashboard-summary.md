# CDM Dashboard — Stack Graph Summary
Source: /Users/anshulpadyal/cdm/cdm-dashboard (graphify-out/ persists there)

## Architecture (128 nodes, 105 edges, 32 communities)
- **Auth & Device Management** (18) — auth provider, useAuth hook, device pages, time display
- **Command Dispatch UI** (12) — dispatch commands, command list, action handling
- **Migration & CSV** (12) — device CSV export/import, batch management
- **Rollout Management** (11) — create/abort/pause rollouts, progress UI
- **Content & Group Selection** (10) — content picker, group selector, item/label display
- **Remote Shell** (8) — useShellSession hook, terminal UI, session management
- **Device Grid & Map** (6) — normalized coordinates, device positioning, map view
- **Screenshot Viewer** (5) — remote screenshot display, S3 fetch

## God Nodes
- useAuth() — auth state across all pages
- handleSubmit() — form submission handler
- getNormalizedCoords() — device map positioning
- useShellSession() — remote shell hook
- dispatchCommand() — command dispatch UI

## Technologies
- Frontend: React (JSX), Vite; Styling: Tailwind CSS
- Auth: JWT + useAuth context provider
- Real-time: Socket.io client (device status, shell relay)
- Maps: Normalized coordinate system for device positioning
- Terminal: Remote shell terminal UI
