# Sumadhura CMS Dashboard — Stack Graph Summary

## Architecture
- **Content Upload & Media Manager** (39 components) — drag-drop upload, media type detection, aspect ratio validation, S3 upload
- **CMS Schedule Management** (33 components) — bulk schedule, cancel schedule, screen scheduling
- **Media Library UI** (21 components) — manifest thumbnails, folder/document icons, media grid
- **Device Display & Profiles** (19 components) — device labels, display names, compact views
- **TV Socket Real-time** (17 components) — WebSocket connection, event handling, TV state sync
- **Analytics & Reporting** (15 components) — date range filters, duration formatting, schedule views
- **Upload Pipeline** (14 components) — media type detection, aspect ratio check, batch upload
- **Device Profile Management** (14 components) — apply/clear/confirm device profiles, calibration
- **Screen Selection UI** (11 components) — categorized screen select, group by category
- **Date/Time Utilities** (11 components) — date range presets, ISO date math, format helpers

## God Nodes (highest-connected)
- getErrorMessage() (degree: high) — central error handler
- TVSocket (degree: high) — WebSocket singleton for TV communication
- getDeviceDisplayName() (degree: high) — device labeling across views
- ScreenRow() (degree: high) — screen list item component
- listTemplates() (degree: high) — template system

## Technologies
- Frontend: React (JSX), Vite
- Styling: Tailwind CSS (inferred from icon components)
- Real-time: Socket.io client (TVSocket class)
- Storage: AWS S3 (upload policies, CDN URLs)
- Media: Image/video upload with aspect ratio validation
- State: React hooks pattern
- API: REST client with error handling
