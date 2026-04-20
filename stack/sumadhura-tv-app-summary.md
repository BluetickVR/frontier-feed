# Sumadhura TV App — Stack Graph Summary
Source: /Users/anshulpadyal/sumadhura-tv-app (graphify-out/ persists there)

## Architecture (144 nodes, 113 edges, 38 communities)
- **Kiosk Mode & Device Admin** (24) — kiosk lockdown, device owner, admin override, lock task
- **Main Activity & React Native** (11) — React Native bridge, activity delegate, component registration
- **Diagnostics & Hardware** (11) — CEA extension check, shell exec, hardware diagnostics
- **App Configuration** (7) — JS main module, packages, developer support
- **CMS Schedule Engine** (7) — date range check, time active, schedule evaluation
- **Content Rendering** (varies) — content display on TV screens

## God Nodes
- KioskModule (degree: highest) — Android kiosk mode control
- MainActivity (degree: high) — React Native entry point
- DiagnosticsModule (degree: high) — hardware/display diagnostics
- KioskDeviceAdminReceiver (degree: high) — device admin policy
- CmsSchedule (degree: high) — schedule evaluation on device

## Technologies
- Platform: Android (Kotlin)
- Framework: React Native (bridge modules)
- Kiosk: Android Device Admin API, lock task mode
- Display: EDID/CEA extension detection, resolution diagnostics
- Scheduling: Local CMS schedule evaluation (time/date range checks)
- Build: Gradle
