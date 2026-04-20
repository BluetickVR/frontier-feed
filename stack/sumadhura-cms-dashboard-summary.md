# Sumadhura CMS Dashboard — Stack Graph Summary
Source: /Users/anshulpadyal/sumadhura-cms-dashboard (graphify-out/ persists there)

## Architecture (364 nodes, 415 edges, 59 communities)
- **Content Upload & Media Manager** (39) — drag-drop upload, media detection, aspect ratio validation, S3
- **CMS Schedule Management** (33) — bulk schedule, cancel, screen scheduling, policy validation
- **Media Library UI** (21) — manifest thumbnails, folder/document icons, media grid
- **Device Display & Profiles** (19) — device labels, display names, compact views, EDID
- **TV Socket Real-time** (17) — WebSocket connection, TV state sync, event handling
- **Analytics & Reporting** (15) — date range filters, duration formatting, schedule views
- **Upload Pipeline** (14) — media type detection, aspect ratio check, batch upload
- **Device Profile Management** (14) — apply/clear/confirm profiles, calibration
- **Screen Selection UI** (11) — categorized screen select, group by category
- **Date/Time Utilities** (11) — date range presets, ISO math, format helpers

## God Nodes
- getErrorMessage() — central error handler
- TVSocket — WebSocket singleton for TV communication
- getDeviceDisplayName() — device labeling across views
- ScreenRow() — screen list item component
- listTemplates() — template system

## Technologies
- Frontend: React (JSX), Vite; Styling: Tailwind CSS
- Real-time: Socket.io client (TVSocket); Storage: AWS S3
- Media: Image/video upload with aspect ratio validation
- API: REST client with centralized error handling
