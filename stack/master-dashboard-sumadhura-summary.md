# Master Dashboard Sumadhura — Stack Graph Summary

## Architecture
- **Business & User Admin** (9 components) — create business, create user, create role, admin login, inactive duration tracking
- **API & Session Management** (8 components) — central apiCall(), force logout, active sessions, customer/salesperson listing
- **App Shell** (3 components) — root App, routing
- **Logout & Auth** (3 components) — individual salesperson logout, session handling
- **Socket Room Monitor** (2 components) — real-time room monitoring
- **Dashboard Layout** (2 components) — layout wrapper

## God Nodes (highest-connected)
- apiCall() (degree: high) — central API client, all API calls route through this
- logoutIndividualSalesPerson() (degree: high) — session management
- getDashboardOverview() (degree: high) — dashboard data aggregation
- getAllSalesPersons() (degree: high) — salesperson listing
- getProjectSalesPersons() (degree: high) — project-level salesperson data

## Technologies
- Frontend: React (TypeScript, TSX)
- Build: Vite
- Styling: Tailwind CSS, PostCSS
- Real-time: Socket.io (room monitoring)
- API: Centralized REST client (apiCall singleton)
- Auth: Session-based, force logout capability
- Purpose: Admin dashboard for managing businesses, salespersons, customers, and monitoring active sessions
