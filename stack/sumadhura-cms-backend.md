# Graph Report - .  (2026-04-20)

## Corpus Check
- Corpus is ~39,784 words - fits in a single context window. You may not need a graph.

## Summary
- 288 nodes · 422 edges · 48 communities detected
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 66 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Infra & Monitoring (CloudWatch, SSM, Alarms)|Infra & Monitoring (CloudWatch, SSM, Alarms)]]
- [[_COMMUNITY_TV History & Content Sessions|TV History & Content Sessions]]
- [[_COMMUNITY_S3 Upload & Media Processing|S3 Upload & Media Processing]]
- [[_COMMUNITY_Screen Config & TV Display|Screen Config & TV Display]]
- [[_COMMUNITY_Scheduling & Playlist Playback|Scheduling & Playlist Playback]]
- [[_COMMUNITY_Content Lifecycle & Scheduling|Content Lifecycle & Scheduling]]
- [[_COMMUNITY_Device Profile Management|Device Profile Management]]
- [[_COMMUNITY_Display Resolution & Profiles|Display Resolution & Profiles]]
- [[_COMMUNITY_User CRUD & Auth|User CRUD & Auth]]
- [[_COMMUNITY_Socket Events & Real-time Updates|Socket Events & Real-time Updates]]
- [[_COMMUNITY_Device Identity & EDID Matching|Device Identity & EDID Matching]]
- [[_COMMUNITY_Playlist CRUD|Playlist CRUD]]
- [[_COMMUNITY_S3 & CDN Media Pipeline|S3 & CDN Media Pipeline]]
- [[_COMMUNITY_Templates & Seeding|Templates & Seeding]]
- [[_COMMUNITY_Rotation & Migration|Rotation & Migration]]
- [[_COMMUNITY_Module 15|Module 15]]
- [[_COMMUNITY_Module 16|Module 16]]
- [[_COMMUNITY_Module 17|Module 17]]
- [[_COMMUNITY_Module 18|Module 18]]
- [[_COMMUNITY_Module 19|Module 19]]
- [[_COMMUNITY_Module 20|Module 20]]
- [[_COMMUNITY_Module 21|Module 21]]
- [[_COMMUNITY_Module 22|Module 22]]
- [[_COMMUNITY_Module 23|Module 23]]
- [[_COMMUNITY_Module 24|Module 24]]
- [[_COMMUNITY_Module 25|Module 25]]
- [[_COMMUNITY_Module 26|Module 26]]
- [[_COMMUNITY_Module 27|Module 27]]
- [[_COMMUNITY_Module 28|Module 28]]
- [[_COMMUNITY_Module 29|Module 29]]
- [[_COMMUNITY_Module 30|Module 30]]
- [[_COMMUNITY_Module 31|Module 31]]
- [[_COMMUNITY_Module 32|Module 32]]
- [[_COMMUNITY_Module 33|Module 33]]
- [[_COMMUNITY_Module 34|Module 34]]
- [[_COMMUNITY_Module 35|Module 35]]
- [[_COMMUNITY_Module 36|Module 36]]
- [[_COMMUNITY_Module 37|Module 37]]
- [[_COMMUNITY_Module 38|Module 38]]
- [[_COMMUNITY_Module 39|Module 39]]
- [[_COMMUNITY_Module 40|Module 40]]
- [[_COMMUNITY_Module 41|Module 41]]
- [[_COMMUNITY_Module 42|Module 42]]
- [[_COMMUNITY_Module 43|Module 43]]
- [[_COMMUNITY_Module 44|Module 44]]
- [[_COMMUNITY_Module 45|Module 45]]
- [[_COMMUNITY_Module 46|Module 46]]
- [[_COMMUNITY_Module 47|Module 47]]

## God Nodes (most connected - your core abstractions)
1. `create()` - 13 edges
2. `SocketEventManager` - 11 edges
3. `Sumadhura CMS Backend` - 11 edges
4. `computeAspectRatio()` - 10 edges
5. `serializeDevice()` - 10 edges
6. `createScheduleSlot()` - 9 edges
7. `appendSumadhuraScreenEvent()` - 9 edges
8. `ensureSeeded()` - 8 edges
9. `loadProfileMapForDevices()` - 8 edges
10. `broadcastScheduleToScreen()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `run()` --calls--> `create()`  [INFERRED]
  scripts/seed-cms-users.js → src/controllers/cmsUser.controller.js
- `createPlaylist()` --calls--> `create()`  [INFERRED]
  src/controllers/sumadhura.playlist.controller.js → src/controllers/cmsUser.controller.js
- `processEdidReading()` --calls--> `normalizeEdidPayload()`  [INFERRED]
  src/sockets/tv.socket.js → src/utils/edidFingerprint.js
- `processEdidReading()` --calls--> `parseResolutionString()`  [INFERRED]
  src/sockets/tv.socket.js → src/utils/aspectRatio.js
- `processEdidReading()` --calls--> `computeAspectRatio()`  [INFERRED]
  src/sockets/tv.socket.js → src/utils/aspectRatio.js

## Communities

### Community 0 - "Infra & Monitoring (CloudWatch, SSM, Alarms)"
Cohesion: 0.08
Nodes (31): AWS CloudWatch Logs, AWS Profile: opt, AWS Region ap-south-1, AWS SSM Session Manager, CloudWatch Error Alarm, Convrse.ai, EC2 Deploy Keys (ed25519, read-only), develop branch (+23 more)

### Community 1 - "TV History & Content Sessions"
Cohesion: 0.12
Nodes (22): broadcastTVListUpdate(), endContentSession(), getOrCreateTodayHistory(), getTodayDateString(), getTodayHistory(), logAssignment(), logUnassignment(), startContentSession() (+14 more)

### Community 2 - "S3 Upload & Media Processing"
Cohesion: 0.11
Nodes (13): getS3Client(), getUploadPolicy(), processMedia(), createUploadPolicy(), deleteSection(), generatePreloadPriority(), getAllProjectsManifest(), getBucketName() (+5 more)

### Community 3 - "Screen Config & TV Display"
Cohesion: 0.18
Nodes (16): coerceStoredRotation(), emitScreenConfigForDevice(), emitScreenConfigPayload(), emitSumadhuraScreenConfigForTvId(), getDeviceScreenRotation(), getScreenHistory(), ingestThrottledTelemetry(), normalizeDeviceId() (+8 more)

### Community 4 - "Scheduling & Playlist Playback"
Cohesion: 0.2
Nodes (17): getOrientation(), reMergeAfterSlotRemoval(), withScreenLock(), scheduleFromPlaylist(), broadcastScheduleToScreen(), cancelAllScheduleSlotsForScreen(), cancelScheduleSlot(), createScheduleSlot() (+9 more)

### Community 5 - "Content Lifecycle & Scheduling"
Cohesion: 0.2
Nodes (17): cascadeContentDeletion(), cleanupExpiredContent(), buildLoopItem(), buildSlot(), computeScheduleMerge(), crossesMidnight(), extractLoopItems(), mergeLoopItems() (+9 more)

### Community 6 - "Device Profile Management"
Cohesion: 0.24
Nodes (13): applyDeviceProfile(), clearDeviceCalibration(), clearDeviceProfile(), confirmDeviceProfile(), getAllDevices(), isOnline(), loadProfileMapForDevices(), mergeDevices() (+5 more)

### Community 7 - "Display Resolution & Profiles"
Cohesion: 0.27
Nodes (13): computeAspectRatio(), gcd(), parseResolutionString(), createProfile(), deleteProfile(), duplicateProfile(), ensureSeeded(), getProfile() (+5 more)

### Community 8 - "User CRUD & Auth"
Cohesion: 0.18
Nodes (6): create(), remove(), toSafeUser(), update(), run(), createSchedule()

### Community 9 - "Socket Events & Real-time Updates"
Cohesion: 0.21
Nodes (1): SocketEventManager

### Community 10 - "Device Identity & EDID Matching"
Cohesion: 0.27
Nodes (8): aspectRatiosMatch(), edidMatchesProfile(), fingerprintsMatch(), identityOf(), normalizeEdidPayload(), syntheticHash(), computeBlastRadius(), processEdidReading()

### Community 11 - "Playlist CRUD"
Cohesion: 0.28
Nodes (4): createPlaylist(), minutesToTime(), splitTimeRange(), timeToMinutes()

### Community 12 - "S3 & CDN Media Pipeline"
Cohesion: 0.39
Nodes (4): downloadFromS3(), getBucketName(), getS3Client(), uploadToS3()

### Community 13 - "Templates & Seeding"
Cohesion: 0.7
Nodes (4): ensureSeeded(), getTemplate(), listTemplates(), seedSystemTemplates()

### Community 14 - "Rotation & Migration"
Cohesion: 0.83
Nodes (3): escapeRegex(), run(), setRotationForId()

### Community 15 - "Module 15"
Cohesion: 0.5
Nodes (0): 

### Community 16 - "Module 16"
Cohesion: 0.67
Nodes (0): 

### Community 17 - "Module 17"
Cohesion: 1.0
Nodes (0): 

### Community 18 - "Module 18"
Cohesion: 1.0
Nodes (0): 

### Community 19 - "Module 19"
Cohesion: 1.0
Nodes (0): 

### Community 20 - "Module 20"
Cohesion: 1.0
Nodes (0): 

### Community 21 - "Module 21"
Cohesion: 1.0
Nodes (0): 

### Community 22 - "Module 22"
Cohesion: 1.0
Nodes (0): 

### Community 23 - "Module 23"
Cohesion: 1.0
Nodes (0): 

### Community 24 - "Module 24"
Cohesion: 1.0
Nodes (0): 

### Community 25 - "Module 25"
Cohesion: 1.0
Nodes (0): 

### Community 26 - "Module 26"
Cohesion: 1.0
Nodes (0): 

### Community 27 - "Module 27"
Cohesion: 1.0
Nodes (0): 

### Community 28 - "Module 28"
Cohesion: 1.0
Nodes (0): 

### Community 29 - "Module 29"
Cohesion: 1.0
Nodes (0): 

### Community 30 - "Module 30"
Cohesion: 1.0
Nodes (0): 

### Community 31 - "Module 31"
Cohesion: 1.0
Nodes (0): 

### Community 32 - "Module 32"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "Module 33"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "Module 34"
Cohesion: 1.0
Nodes (0): 

### Community 35 - "Module 35"
Cohesion: 1.0
Nodes (0): 

### Community 36 - "Module 36"
Cohesion: 1.0
Nodes (0): 

### Community 37 - "Module 37"
Cohesion: 1.0
Nodes (0): 

### Community 38 - "Module 38"
Cohesion: 1.0
Nodes (0): 

### Community 39 - "Module 39"
Cohesion: 1.0
Nodes (0): 

### Community 40 - "Module 40"
Cohesion: 1.0
Nodes (0): 

### Community 41 - "Module 41"
Cohesion: 1.0
Nodes (0): 

### Community 42 - "Module 42"
Cohesion: 1.0
Nodes (0): 

### Community 43 - "Module 43"
Cohesion: 1.0
Nodes (0): 

### Community 44 - "Module 44"
Cohesion: 1.0
Nodes (0): 

### Community 45 - "Module 45"
Cohesion: 1.0
Nodes (0): 

### Community 46 - "Module 46"
Cohesion: 1.0
Nodes (0): 

### Community 47 - "Module 47"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **15 isolated node(s):** `Staging API (api.staging.sumadhura.cms.convrse.ai)`, `Prod API (api.sumadhura.cms.convrse.ai)`, `Staging Dashboard (staging.sumadhura.cms.convrse.ai)`, `Prod Dashboard (sumadhura.cms.convrse.ai)`, `AWS SSM Session Manager` (+10 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Module 17`** (2 nodes): `index.js`, `shutdown()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 18`** (2 nodes): `run()`, `clear-sumadhura-schedule-slots.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 19`** (2 nodes): `cmsUserAuth()`, `cmsUserAuth.middleware.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 20`** (2 nodes): `resolveKey()`, `jwtAuthManager.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 21`** (2 nodes): `resolveKey()`, `jwtIssuer.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 22`** (2 nodes): `startHeartbeatMonitor()`, `heartbeat.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 23`** (2 nodes): `getMongoConnection()`, `mongo.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 24`** (2 nodes): `login()`, `cmsAuth.controller.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 25`** (2 nodes): `tvSchedule.service.js`, `startScheduleExecutor()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 26`** (1 nodes): `ecosystem.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 27`** (1 nodes): `logger.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 28`** (1 nodes): `tvAssignment.schema.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 29`** (1 nodes): `sumadhura.tv.screen.schedule.schema.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 30`** (1 nodes): `tvHistory.schema.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 31`** (1 nodes): `tvSchedule.schema.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 32`** (1 nodes): `cmsUser.schema.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 33`** (1 nodes): `sumadhura.cms.schema.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 34`** (1 nodes): `sumadhura.screen.profile.schema.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 35`** (1 nodes): `sumadhura.schedule.slot.schema.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 36`** (1 nodes): `sumadhura.cms.manifest.schema.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 37`** (1 nodes): `sumadhura.content.playlist.schema.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 38`** (1 nodes): `sumadhura.screen.event.schema.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 39`** (1 nodes): `cms.device.schema.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 40`** (1 nodes): `sumadhura.screen.template.schema.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 41`** (1 nodes): `tv.routes.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 42`** (1 nodes): `tvHistory.routes.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 43`** (1 nodes): `tvSchedule.routes.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 44`** (1 nodes): `cmsUser.routes.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 45`** (1 nodes): `sumadhura.cms.routes.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 46`** (1 nodes): `cms.device.routes.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module 47`** (1 nodes): `cmsAuth.routes.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create()` connect `User CRUD & Auth` to `TV History & Content Sessions`, `Scheduling & Playlist Playback`, `Device Profile Management`, `Display Resolution & Profiles`, `Playlist CRUD`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Why does `computeAspectRatio()` connect `Display Resolution & Profiles` to `Device Identity & EDID Matching`, `S3 Upload & Media Processing`, `Scheduling & Playlist Playback`, `Device Profile Management`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **Why does `saveContent()` connect `S3 Upload & Media Processing` to `Device Identity & EDID Matching`, `Scheduling & Playlist Playback`, `Display Resolution & Profiles`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `create()` (e.g. with `run()` and `createProfile()`) actually correct?**
  _`create()` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Sumadhura CMS Backend` (e.g. with `Convrse.ai` and `Node.js`) actually correct?**
  _`Sumadhura CMS Backend` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `computeAspectRatio()` (e.g. with `processEdidReading()` and `putScreenResolution()`) actually correct?**
  _`computeAspectRatio()` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Staging API (api.staging.sumadhura.cms.convrse.ai)`, `Prod API (api.sumadhura.cms.convrse.ai)`, `Staging Dashboard (staging.sumadhura.cms.convrse.ai)` to the rest of the system?**
  _15 weakly-connected nodes found - possible documentation gaps or missing edges._