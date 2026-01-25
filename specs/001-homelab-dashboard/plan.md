# Implementation Plan: Homelab Service Dashboard

**Branch**: `001-homelab-dashboard` | **Date**: 2026-01-24 | **Spec**: spec.md
**Input**: Feature specification from `/specs/001-homelab-dashboard/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a web-based dashboard for homelab administrators to view and manage service links with automated status monitoring. The application displays service tiles organized by category with real-time status badges, supports search and sorting, provides an admin interface for CRUD operations, includes automated health checks at configurable intervals, and delivers status change notifications via email/webhook.

## Technical Context

**Language/Version**: Next.js 16+ with TypeScript 5+
**Primary Dependencies**: React 18+, Tailwind CSS, ShadCN UI components, js-yaml
**Storage**: YAML files in userdata/config for configuration, file system in userdata/images for images
**Testing**: Jest + React Testing Library for unit/integration, Playwright for E2E
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge), responsive mobile (375px), tablet (768px), desktop (1024px+)
**Project Type**: web
**Performance Goals**: Page load < 3 seconds, search < 1 second across 500 services, status updates within 2 check intervals
**Constraints**: Initial bundle < 500 KB gzipped, WCAG 2.1 AA compliance, minimal external dependencies to avoid bloat
**Scale/Scope**: Up to 500 services, single admin user, homelab deployment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Code Quality**: Design ensures linting/formatting compliance, single-responsibility functions, complexity < 10, function length < 50 lines
- [x] **UX Consistency**: UI patterns align with design tokens, responsive breakpoints (375px/768px/1024px+), consistent navigation structure
- [x] **Maintainability**: Clear separation of concerns, dependency injection, externalized configuration, feature-based organization
- [x] **Documentation**: Plan includes README creation, API documentation, quickstart guide, inline comments for complex logic
- [x] **Testing**: Unit test strategy for critical paths, integration test coverage for cross-component interactions, CI/CD automation planned
- [x] **Performance**: Design meets <2s load time, <500KB initial bundle, accessibility (WCAG 2.1 AA compliance)
- [x] **Security**: Input validation strategy, no hardcoded secrets, dependency scanning plan

## Project Structure

### Documentation (this feature)

```text
specs/001-homelab-dashboard/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
app/
├── (public)/
│   ├── page.tsx                    # Dashboard page (public view)
│   └── layout.tsx                  # Root layout with navigation
├── (admin)/
│   ├── login/
│   │   └── page.tsx                # Admin login page
│   ├── dashboard/
│   │   └── page.tsx                # Admin dashboard for link management
│   └── layout.tsx                  # Admin layout with auth check
├── api/
│   ├── status/
│   │   └── route.ts                # API for status check results
│   └── admin/
│       ├── links/
│       │   ├── route.ts            # GET/POST for service links
│       │   └── [id]/
│       │       └── route.ts        # PUT/DELETE for service links
│       └── config/
│           └── route.ts            # GET/PUT for global settings
components/
├── ui/                             # ShadCN UI components
├── dashboard/
│   ├── ServiceTile.tsx             # Individual service tile component
│   ├── CategorySection.tsx         # Category section with tiles
│   ├── SearchBar.tsx               # Search functionality
│   └── SortControls.tsx            # Sort by name/status
├── admin/
│   ├── LinkForm.tsx                # Form for adding/editing links
│   ├── LinkList.tsx                # List view with bulk actions
│   └── ConfigPanel.tsx             # Global configuration panel
lib/
├── config.ts                       # YAML configuration loader/parser
├── status-checker.ts               # Automated status checking logic
├── notifications.ts                # Email/webhook notification service
└── utils.ts                        # Shared utilities
types/
└── index.ts                        # TypeScript type definitions
userdata/
├── config/
│   ├── links.yaml                  # Service links configuration
│   ├── categories.yaml             # Categories configuration
│   └── settings.yaml               # Global settings (check interval, notifications)
└── images/                         # Service icon images
scripts/
└── status-monitor.ts               # Background status check worker
tests/
├── unit/
│   ├── config.test.ts              # YAML parsing tests
│   ├── status-checker.test.ts      # Status checking logic tests
│   └── notifications.test.ts       # Notification service tests
├── integration/
│   ├── dashboard.test.ts           # Dashboard page integration tests
│   └── admin.test.ts               # Admin interface integration tests
└── e2e/
    ├── view-dashboard.spec.ts      # Playwright E2E for viewing dashboard
    ├── manage-links.spec.ts        # Playwright E2E for admin operations
    └── status-updates.spec.ts      # Playwright E2E for status updates
```

**Structure Decision**: Next.js 16+ app router structure with clear separation between public dashboard and admin interfaces. Configuration externalized to YAML files in userdata/ directory following user requirements. Components organized by feature (dashboard vs admin). Tests follow conventional unit/integration/e2e hierarchy.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | N/A | N/A |
