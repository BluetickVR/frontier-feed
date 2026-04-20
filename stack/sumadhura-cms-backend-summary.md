# Sumadhura CMS Backend — Stack Graph Summary

## Architecture
- **Infra & Monitoring (CloudWatch, SSM, Alarms)** (31 components)
- **TV History & Content Sessions** (28 components)
- **S3 Upload & Media Processing** (26 components)
- **Screen Config & TV Display** (21 components)
- **Scheduling & Playlist Playback** (21 components)
- **Content Lifecycle & Scheduling** (19 components)
- **Device Profile Management** (17 components)
- **Display Resolution & Profiles** (15 components)
- **User CRUD & Auth** (14 components)
- **Socket Events & Real-time Updates** (12 components)
- **Device Identity & EDID Matching** (11 components)
- **Playlist CRUD** (9 components)
- **S3 & CDN Media Pipeline** (8 components)
- **Templates & Seeding** (5 components)
- **Rotation & Migration** (4 components)
- **Module 15** (4 components)
- **Module 16** (3 components)

## God Nodes (highest-connected)
- create() (degree: 13)
- SocketEventManager (degree: 11)
- Sumadhura CMS Backend (degree: 11)
- computeAspectRatio() (degree: 10)
- serializeDevice() (degree: 10)
- createScheduleSlot() (degree: 9)
- appendSumadhuraScreenEvent() (degree: 9)
- ensureSeeded() (degree: 8)

## Key Dependencies & Interfaces
- **accessed_via**: 1 edges (e.g., sumadhura_cms_backend -> aws_ssm)
- **authenticates_to**: 1 edges (e.g., github_repo -> deploy_keys)
- **auto_deploys**: 2 edges (e.g., staging_environment -> github_actions)
- **belongs_to_org**: 1 edges (e.g., github_repo -> convrse_ai)
- **built_with**: 1 edges (e.g., sumadhura_cms_backend -> nodejs)
- **calls**: 185 edges (e.g., set_tv_device_rotations_escaperegex -> set_tv_device_rotatio)
- **contains**: 191 edges (e.g., index_js -> index_shutdown)
- **deploys_to**: 2 edges (e.g., staging_environment -> develop_branch)
- **exposes**: 4 edges (e.g., staging_environment -> staging_api)
- **has**: 2 edges (e.g., staging_ec2 -> deploy_keys)
- **has_eip**: 2 edges (e.g., staging_ec2 -> elastic_ip_staging)
- **has_environment**: 2 edges (e.g., sumadhura_cms_backend -> staging_environment)
- **hosted_at**: 1 edges (e.g., sumadhura_cms_backend -> github_repo)
- **hosted_on**: 2 edges (e.g., mongodb -> staging_mongo_db)
- **located_in**: 2 edges (e.g., staging_ec2 -> aws_region_ap_south_1)
- **logs_to**: 1 edges (e.g., sumadhura_cms_backend -> aws_cloudwatch)
- **managed_by**: 2 edges (e.g., sumadhura_cms_backend -> pm2_runtime)
- **method**: 10 edges (e.g., socketeventmanager_socketeventmanager -> socketeventmanager_)
- **monitors**: 1 edges (e.g., cloudwatch_alarm -> pino_logger)
- **owned_by**: 1 edges (e.g., sumadhura_cms_backend -> convrse_ai)
- **reports_errors_to**: 1 edges (e.g., sumadhura_cms_backend -> sentry)
- **runs_on**: 2 edges (e.g., staging_environment -> staging_ec2)
- **triggers**: 1 edges (e.g., sns_alerts -> cloudwatch_alarm)
- **uses**: 1 edges (e.g., sumadhura_cms_backend -> pino_logger)
- **uses_database**: 2 edges (e.g., staging_environment -> staging_mongo_db)
- **uses_profile**: 1 edges (e.g., sumadhura_cms_backend -> aws_profile_opt)

## Technologies (inferred from code)
- Runtime: Node.js (Express)
- Database: MongoDB
- Storage: AWS S3, CloudFront CDN
- Real-time: Socket.io (WebSocket)
- Monitoring: CloudWatch, Sentry, SNS Alarms
- Process: PM2, systemd
- Auth: JWT, User CRUD
- Media: Image/Video processing, S3 upload pipeline
- Display: TV content management, screen config, EDID matching, playlists