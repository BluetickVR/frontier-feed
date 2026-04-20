# CDM Android App — Stack Graph Summary
Source: /Users/anshulpadyal/cdm/cdm-android (graphify-out/ persists there)

## Architecture (162 nodes, 137 edges, 25 communities)
- **App Watchdog** (16) — foreground package detection, running package monitor, crash loop detection
- **Command Executor** (13) — command execution pipeline, internal execution, result reporting
- **Foreground Service** (13) — persistent service, notification management, watchdog lifecycle
- **Media Projection & Screenshots** (12) — screen capture, display size, projection holder
- **Socket Manager** (12) — WebSocket connect/disconnect, heartbeat, command receive
- **Device Owner & Kiosk** (10) — device admin, kiosk lock, app management
- **App Installer** (8) — silent install/uninstall, APK download, version management
- **Self-Update** (6) — CDM self-update check, APK download, install trigger
- **Diagnostics** (5) — hardware info, CEA check, shell exec

## God Nodes
- AppWatchdog — crash loop detection, foreground monitoring
- CommandExecutor — central command execution (install, uninstall, reboot, screenshot, kiosk, shell)
- CdmForegroundService — persistent Android service, lifecycle management
- MediaProjectionHolder — screen capture for remote view
- SocketManager — server communication, heartbeat, command queue

## Technologies
- Platform: Android (Kotlin); Min API: 24 (Android 7+)
- Device Admin: Device Owner API, lock task mode, kiosk
- Communication: Socket.io (heartbeat, commands, remote shell/view relay)
- Media: MediaProjection API (screenshots, remote view)
- Install: PackageInstaller API (silent install/uninstall)
- Build: Gradle
