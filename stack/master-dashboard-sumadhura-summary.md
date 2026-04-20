# Master Sumadhura CMS — Orchestration Hub
Source: /Users/anshulpadyal/master-sumadhura-cms

## Role
Central hub for Claude Code. No code of its own — orchestrates work across:
- sumadhura-cms-backend (Node.js API + MongoDB + S3 + Socket.io)
- sumadhura-cms-dashboard (React + Vite + Tailwind + Socket.io client)
- sumadhura-tv-app (Android Kotlin + React Native, kiosk mode)

## Cross-repo connections (from graph analysis)
- Backend SocketEventManager ←→ Dashboard TVSocket (real-time bridge)
- Backend computeAspectRatio() ←→ Dashboard computeAspectRatio() (shared logic)
- Backend Device Profile API ←→ Dashboard Device Profile Management UI
- Backend CMS Schedule API ←→ TV App CmsSchedule (local evaluation)
- Backend S3 upload pipeline ←→ Dashboard upload UI ←→ TV App content display
- Backend serializeDevice() ←→ Dashboard getDeviceDisplayName() (device data flow)

## Total across all repos
- 765 nodes, 914 edges across 3 codebases
- God nodes span repos: SocketEventManager (backend) ↔ TVSocket (dashboard)
