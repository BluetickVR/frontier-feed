# Sumadhura CMS Backend — Stack Graph Summary
Source: /Users/anshulpadyal/sumadhura-cms-backend (graphify-out/ persists there)

## Architecture (257 nodes, 386 edges, 47 communities)
- **TV History & Content Sessions** (28) — broadcast updates, content sessions, today history
- **S3 Upload & Media Processing** (26) — S3 client, upload policy, media processing pipeline
- **Scheduling & Playlist Engine** (25) — aspect ratio matching, schedule slots, playlist merge
- **Screen Config & TV Display** (21) — rotation, screen config emission, EDID handling
- **Content Lifecycle** (19) — cascade deletion, expiry cleanup, slot computation, midnight crossing
- **Device Profile Management** (17) — apply/clear/confirm profiles, calibration, bulk ops
- **Display Resolution** (15) — aspect ratio compute, GCD, resolution parsing
- **User CRUD & Auth** (14) — create/update/delete users, safe serialization
- **Socket Events** (12) — SocketEventManager, batch emission, inventory updates
- **Playlist CRUD** (9) — create/delete/list playlists
- **S3 & CDN Pipeline** (8) — download, bucket names, CDN URLs, image/video processing

## God Nodes
- create() (degree: 13)
- SocketEventManager (degree: 11)
- computeAspectRatio() (degree: 10)
- serializeDevice() (degree: 10)
- createScheduleSlot() (degree: 9)

## Technologies
- Runtime: Node.js (Express); Database: MongoDB; Storage: AWS S3 + CloudFront CDN
- Real-time: Socket.io; Monitoring: CloudWatch, Sentry; Process: PM2, systemd
- Deploy: GitHub Actions → EC2 (ap-south-1) via SSM
