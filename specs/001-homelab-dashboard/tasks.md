# Tasks: Homelab Service Dashboard

**Input**: Design documents from `/specs/001-homelab-dashboard/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL and NOT included - not explicitly requested in feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Next.js app router structure: `app/`, `components/`, `lib/`, `types/`, `userdata/`, `scripts/`, `tests/`
- Public dashboard: `app/(public)/`
- Admin dashboard: `app/(admin)/`
- API routes: `app/api/`
- UI components: `components/ui/`, `components/dashboard/`, `components/admin/`
- Shared logic: `lib/`
- Types: `types/`
- Configuration: `userdata/config/`, `userdata/images/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create Next.js 16+ project with TypeScript 5+ and App Router
- [ ] T002 Install dependencies: React 18+, Tailwind CSS, ShadCN UI, js-yaml, bcrypt
- [ ] T003 [P] Initialize TypeScript with strict mode configuration in tsconfig.json
- [ ] T004 [P] Configure Tailwind CSS with custom design tokens
- [ ] T005 Initialize ShadCN UI components with default configuration
- [ ] T006 [P] Create directory structure per plan.md (app/, components/, lib/, types/, userdata/, scripts/, tests/)
- [ ] T007 [P] Create userdata directories: userdata/config/ and userdata/images/
- [ ] T008 [P] Create initial YAML config files: userdata/config/links.yaml, categories.yaml, settings.yaml with version field
- [ ] T009 [P] Create TypeScript type definitions in types/index.ts (ServiceLink, Category, Status, Settings, etc.)
- [ ] T010 [P] Set up environment variable template in .env.example with ADMIN_USERNAME, ADMIN_PASSWORD, SESSION_SECRET, SMTP_PASSWORD

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T011 Implement configuration loader in lib/config.ts to parse YAML files (links.yaml, categories.yaml, settings.yaml)
- [ ] T012 [P] Create TypeScript interfaces for YAML configs in types/index.ts (LinksConfig, CategoriesConfig, SettingsConfig)
- [ ] T013 [P] Implement utility functions in lib/utils.ts (UUID generation, URL validation, date formatting)
- [ ] T014 Implement status checker in lib/status-checker.ts with HTTP request logic and status determination (online/offline/diminished/unknown)
- [ ] T015 [P] Create background status monitor script in scripts/status-monitor.ts to run periodic checks
- [ ] T016 [P] Implement notification service in lib/notifications.ts for email/webhook notifications
- [ ] T017 Create ShadCN UI components needed for dashboard: Button, Card, Input, Badge, Select, Dialog
- [ ] T018 [P] Set up ShadCN Card component in components/ui/card.tsx
- [ ] T019 [P] Set up ShadCN Button component in components/ui/button.tsx
- [ ] T020 [P] Set up ShadCN Badge component in components/ui/badge.tsx
- [ ] T021 [P] Set up ShadCN Input component in components/ui/input.tsx
- [ ] T022 [P] Set up ShadCN Select component in components/ui/select.tsx
- [ ] T023 [P] Set up ShadCN Dialog component in components/ui/dialog.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Dashboard (Priority: P1) 🎯 MVP

**Goal**: Display public dashboard with service tiles organized by category, with search and sort functionality

**Independent Test**: Can be tested by creating sample YAML configs with services, verifying dashboard displays tiles correctly, search filters results, and sort reorders tiles

### Implementation for User Story 1

- [ ] T024 [P] [US1] Create root layout in app/(public)/layout.tsx with navigation structure and Tailwind styling
- [ ] T025 [P] [US1] Create ServiceTile component in components/dashboard/ServiceTile.tsx with name, icon, description, status badge
- [ ] T026 [P] [US1] Implement status badge rendering in ServiceTile component (green=online, red=offline, yellow=diminished, gray=unknown)
- [ ] T027 [P] [US1] Add click handler to ServiceTile to open service URL in new tab
- [ ] T028 [US1] Create CategorySection component in components/dashboard/CategorySection.tsx to render tiles grouped by category
- [ ] T029 [P] [US1] Create SearchBar component in components/dashboard/SearchBar.tsx with input field and real-time filtering
- [ ] T030 [P] [US1] Implement search debounce in SearchBar (300ms delay) to avoid excessive re-renders
- [ ] T031 [P] [US1] Create SortControls component in components/dashboard/SortControls.tsx with sort by name/status buttons
- [ ] T032 [US1] Create public dashboard page in app/(public)/page.tsx that loads YAML config and renders tiles
- [ ] T033 [P] [US1] Implement search functionality in dashboard page to filter tiles by name, description, and metadata
- [ ] T034 [P] [US1] Implement sort functionality in dashboard page (alphabetical by name, by status: online→diminished→offline→unknown)
- [ ] T035 [P] [US1] Add responsive breakpoints to dashboard (mobile 375px, tablet 768px, desktop 1024px+)
- [ ] T036 [US1] Create API route in app/api/status/route.ts to return all service statuses for dashboard
- [ ] T037 [P] [US1] Implement status caching in status route to avoid redundant checks
- [ ] T038 [US1] Handle empty state in dashboard page when no services are configured
- [ ] T039 [US1] Handle category sections with no services in dashboard page
- [ ] T040 [US1] Add WCAG 2.1 AA accessibility to dashboard (keyboard navigation, color contrast, screen reader labels)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Manage Service Links (Priority: P1)

**Goal**: Provide admin interface with authentication for CRUD operations on service links and categories

**Independent Test**: Can be tested by logging into admin panel, creating/editing/deleting links, performing bulk updates, verifying changes appear on dashboard

### Implementation for User Story 2

- [ ] T041 [P] [US2] Create admin layout in app/(admin)/layout.tsx with authentication check middleware
- [ ] T042 [P] [US2] Implement authentication middleware in lib/auth.ts to verify admin session
- [ ] T043 [P] [US2] Create admin login page in app/(admin)/login/page.tsx with username/password form
- [ ] T044 [P] [US2] Implement session management in lib/auth.ts using Next.js cookies and SESSION_SECRET
- [ ] T045 [P] [US2] Create LinkForm component in components/admin/LinkForm.tsx for adding/editing service links
- [ ] T046 [P] [US2] Implement form validation in LinkForm (name 1-100 chars, URL validation, required fields)
- [ ] T047 [P] [US2] Create LinkList component in components/admin/LinkList.tsx with checkboxes and bulk actions
- [ ] T048 [P] [US2] Implement bulk update functionality in LinkList (change category, delete)
- [ ] T049 [P] [US2] Create ConfigPanel component in components/admin/ConfigPanel.tsx for global settings (check interval, SMTP)
- [ ] T050 [US2] Create admin dashboard page in app/(admin)/dashboard/page.tsx with LinkList and LinkForm
- [ ] T051 [P] [US2] Implement LinkList API route in app/api/admin/links/route.ts (GET for list, POST for create)
- [ ] T052 [P] [US2] Implement LinkDetail API route in app/api/admin/links/[id]/route.ts (PUT for update, DELETE)
- [ ] T053 [P] [US2] Implement categories API route in app/api/admin/categories/route.ts (GET list, POST create)
- [ ] T054 [P] [US2] Implement category detail API route in app/api/admin/categories/[id]/route.ts (PUT update, DELETE)
- [ ] T055 [P] [US2] Implement config API route in app/api/admin/config/route.ts (GET settings, PUT update)
- [ ] T056 [P] [US2] Create login API route in app/api/admin/login/route.ts with bcrypt password verification
- [ ] T057 [P] [US2] Implement YAML file writing in lib/config.ts for API routes to persist changes
- [ ] T058 [P] [US2] Add UUID generation for new services and categories in API routes
- [ ] T059 [P] [US2] Implement category reordering in ConfigPanel (displayOrder field)
- [ ] T060 [P] [US2] Add metadata key-value input in LinkForm (max 10 pairs, keys 50 chars, values 200 chars)
- [ ] T061 [P] [US2] Implement service icon upload handling in LinkForm (save to userdata/images/)
- [ ] T062 [US2] Handle form validation errors with inline error messages in LinkForm
- [ ] T063 [US2] Add session timeout (24 hours) and logout functionality to admin panel
- [ ] T064 [US2] Prevent deletion of categories that have services assigned (return 400 error)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Automated Status Checking (Priority: P2)

**Goal**: Automatically check service health at configurable intervals and update status badges

**Independent Test**: Can be tested by configuring check intervals, creating links to known-up/down services, verifying status badges update after each interval

### Implementation for User Story 3

- [ ] T065 [P] [US3] Enhance status checker in lib/status-checker.ts to support per-service check intervals
- [ ] T066 [P] [US3] Implement global check interval from settings.yaml in status checker (default 60 seconds)
- [ ] T067 [P] [US3] Add per-service check interval override in status checker (checkInterval field in ServiceLink)
- [ ] T068 [P] [US3] Implement status determination logic: online (<5s, 2xx), diminished (5-10s or 5xx), offline (error or timeout>10s), unknown (internal error)
- [ ] T069 [P] [US3] Update ServiceLink status in YAML after each check via lib/config.ts
- [ ] T070 [US3] Schedule background status monitor in Next.js or using node-cron in scripts/status-monitor.ts
- [ ] T071 [P] [US3] Implement check timeout handling (10 seconds default, configurable in settings.yaml)
- [ ] T072 [P] [US3] Add lastChecked timestamp update to ServiceLink in YAML after each check
- [ ] T073 [P] [US3] Implement status cache invalidation to force refresh after 2 intervals (TTL: 120 seconds)
- [ ] T074 [P] [US3] Add logging for status checks (service name, old status, new status, response time)
- [ ] T075 [US3] Handle status checker errors gracefully (log warning, set status to unknown)
- [ ] T076 [US3] Add manual "refresh status" button in admin LinkList to trigger immediate check

**Checkpoint**: All user stories (US1, US2, US3) should now be independently functional

---

## Phase 6: User Story 4 - Status Change Notifications (Priority: P3)

**Goal**: Send email/webhook notifications when service statuses change

**Independent Test**: Can be tested by configuring notifications, taking a service offline, verifying notification arrives via configured method

### Implementation for User Story 4

- [ ] T077 [P] [US4] Enhance notification service in lib/notifications.ts to send email via Nodemailer
- [ ] T078 [P] [US4] Implement SMTP configuration from settings.yaml in notification service
- [ ] T079 [P] [US4] Add webhook notification support in notification service using fetch()
- [ ] T080 [P] [US4] Implement in-app notification storage (Notification entity in memory or YAML)
- [ ] T081 [P] [US4] Add notification conditions in notification service (offline, online, diminished, any)
- [ ] T082 [P] [US4] Implement notification condition matching in status checker (only send if conditions match)
- [ ] T083 [US4] Trigger notifications from status checker when status changes (and conditions match)
- [ ] T084 [P] [US4] Implement notification retry logic with exponential backoff (3 attempts max)
- [ ] T085 [P] [US4] Add notification delivery status tracking (delivered boolean, error message)
- [ ] T086 [P] [US4] Create notification preferences UI in LinkForm (enable checkbox, condition dropdown)
- [ ] T087 [P] [US4] Add global notification email setting to ConfigPanel component
- [ ] T088 [P] [US4] Implement webhook headers support in notification service (for authentication)
- [ ] T089 [P] [US4] Add notification history display in admin dashboard (recent notifications table)
- [ ] T090 [US4] Handle SMTP password from environment variable (SMTP_PASSWORD) not YAML

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T091 [P] Create README.md with installation, configuration, and deployment instructions
- [ ] T092 [P] Add TypeScript type checking to npm scripts (npm run typecheck)
- [ ] T093 [P] Configure ESLint with Next.js rules and constitution compliance (complexity < 10, function length < 50)
- [ ] T094 [P] Configure Prettier for code formatting
- [ ] T095 [P] Add npm scripts: dev, build, start, lint, typecheck
- [ ] T096 [P] Create Dockerfile for containerized deployment with multi-stage build
- [ ] T097 [P] Create docker-compose.yml for easy homelab deployment with volume mounts
- [ ] T098 [P] Create setup-admin script in package.json to initialize admin user with bcrypt password hashing
- [ ] T099 Add responsive design testing verification (mobile, tablet, desktop breakpoints)
- [ ] T100 [P] Optimize images in userdata/images/ for web (WebP format, lazy loading)
- [ ] T101 [P] Add bundle analyzer to check initial load size (< 500 KB gzipped)
- [ ] T102 [P] Implement error boundary components for dashboard and admin pages
- [ ] T103 [P] Add loading states to dashboard and admin pages while data loads
- [ ] T104 Add keyboard navigation verification for all interactive elements
- [ ] T105 [P] Add color contrast verification for WCAG 2.1 AA compliance (4.5:1 minimum)
- [ ] T106 [P] Create API documentation in README with example requests/responses
- [ ] T107 [P] Add troubleshooting section to README for common issues
- [ ] T108 [P] Create example configuration files in userdata/config/examples/
- [ ] T109 [P] Add version field tracking to YAML files for future migrations
- [ ] T110 Create migration script for YAML schema changes (version field comparison)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 3 (P2): Can start after Foundational - Integrates with US1/US2 but independent
  - User Story 4 (P3): Can start after Foundational - Integrates with US3 but independent
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May use data from US1/US2 but self-contained
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Depends on US3 for status change detection

### Within Each User Story

- Utility functions before components
- Base UI components before feature components
- Components before pages
- Pages before API routes (or parallel)
- API routes before integration

### Parallel Opportunities

- **Setup Phase**: All T003-T010 marked [P] can run in parallel
- **Foundational Phase**: All T012, T013, T015-T023 marked [P] can run in parallel
- **User Story 1**: T024-T031 marked [P] can run in parallel (different components)
- **User Story 2**: T041-T048 marked [P] can run in parallel (different components/APIs)
- **User Story 3**: T065-T074 marked [P] can run in parallel (different aspects of status checking)
- **User Story 4**: T077-T089 marked [P] can run in parallel (different notification methods)
- **Polish Phase**: All T091-T109 marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all ServiceTile, CategorySection, SearchBar, SortControls components together:
Task: "Create ServiceTile component in components/dashboard/ServiceTile.tsx"
Task: "Create CategorySection component in components/dashboard/CategorySection.tsx"
Task: "Create SearchBar component in components/dashboard/SearchBar.tsx"
Task: "Create SortControls component in components/dashboard/SortControls.tsx"

# Launch all API and responsive tasks together:
Task: "Create API route in app/api/status/route.ts"
Task: "Implement search functionality in dashboard page"
Task: "Implement sort functionality in dashboard page"
Task: "Add responsive breakpoints to dashboard"
```

---

## Parallel Example: User Story 2

```bash
# Launch all admin components together:
Task: "Create admin layout in app/(admin)/layout.tsx"
Task: "Implement authentication middleware in lib/auth.ts"
Task: "Create admin login page in app/(admin)/login/page.tsx"
Task: "Implement session management in lib/auth.ts"

# Launch all form and list components together:
Task: "Create LinkForm component in components/admin/LinkForm.tsx"
Task: "Create LinkList component in components/admin/LinkList.tsx"
Task: "Create ConfigPanel component in components/admin/ConfigPanel.tsx"

# Launch all API routes together:
Task: "Implement LinkList API route in app/api/admin/links/route.ts"
Task: "Implement categories API route in app/api/admin/categories/route.ts"
Task: "Implement config API route in app/api/admin/config/route.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (View Dashboard)
4. **STOP and VALIDATE**: Test public dashboard with sample YAML configs
5. Demo dashboard tiles, search, and sort functionality

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Demo MVP (public dashboard)
3. Add User Story 2 → Test independently → Deploy full dashboard (public + admin)
4. Add User Story 3 → Test independently → Deploy with status monitoring
5. Add User Story 4 → Test independently → Deploy with notifications
6. Polish phase → Production-ready application

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (dashboard components)
   - Developer B: User Story 2 (admin components)
   - Developer C: API routes and status checking
3. Stories complete and integrate independently
4. Polish phase can be distributed across team

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are NOT included - not explicitly requested in feature specification
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks include exact file paths for LLM execution
- Phase 2 (Foundational) MUST complete before any user story work
- User Stories 1 and 2 (both P1) can be developed in parallel after Foundational
- User Stories 3 and 4 depend on earlier stories but are independently testable
