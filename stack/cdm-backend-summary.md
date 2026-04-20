# CDM Backend — Stack Graph Summary
Source: /Users/anshulpadyal/cdm/cdm-backend (graphify-out/ persists there)

## Architecture (129 nodes, 143 edges, 38 communities)
- **Rollout Engine** (16) — staged rollouts, canary/rolling, abort/pause/resume
- **Command Dispatch** (12) — command queue, dispatch, idempotency, offline handling
- **Socket & Dashboard Namespace** (12) — device/dashboard WebSocket namespaces, broadcast
- **Metrics & Command Pipeline** (12) — CloudWatch publish, command status, IO setup
- **Shell & Remote View** (10) — remote shell sessions, timeout, buffered logging
- **Webhook & Alerting** (8) — HMAC-signed webhooks, retry, DLQ, offline alerting
- **Device Registry** (8) — write-through in-memory + DB hybrid, heartbeat
- **Migration** (6) — CSV import/export, batch device management
- **Auth & Tenant** (5) — multi-tenant, JWT, scoped API keys, platform admin

## God Nodes
- send() (degree: highest) — WebSocket message dispatch
- start() — service initialization
- dispatch() — command dispatch core
- create() — entity creation
- rolloutQuery() — rollout state queries

## Technologies
- Runtime: Node.js (Express); Database: MongoDB; Storage: AWS S3 (screenshots)
- Real-time: Socket.io (device + dashboard namespaces)
- Monitoring: CloudWatch custom metrics (60s), Winston JSON logging
- Deploy: Docker Compose, EC2, NGINX reverse proxy
- MDM: 2000 devices, ~100 sites, command queue with TTL
