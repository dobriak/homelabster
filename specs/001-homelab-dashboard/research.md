# Research: Homelab Service Dashboard

**Feature**: 001-homelab-dashboard
**Date**: 2026-01-24

## Overview

This document captures research findings and technical decisions for the homelab service dashboard implementation, addressing unknowns identified during planning and establishing best practices for the chosen technology stack.

---

## Technology Stack Decisions

### Next.js Version Selection

**Decision**: Next.js 16 with App Router

**Rationale**:
- App Router provides modern React Server Components for better performance
- Built-in API routes enable server-side logic without separate backend
- Server Actions simplify form handling and mutations
- Image optimization out-of-the-box for service icons
- Excellent TypeScript support

**Alternatives Considered**:
- Next.js 15 (Pages Router): Rejected - App Router is the recommended path forward
- Next.js 17+: Rejected - May be unstable, 16 provides stability with latest features

**Reference**: https://nextjs.org/docs/app

---

### TypeScript Configuration

**Decision**: TypeScript 5.5+ with strict mode enabled

**Rationale**:
- Strict mode catches type errors early, reducing runtime bugs
- Next.js 16 has excellent TypeScript support out-of-the-box
- Enables better autocomplete and refactoring
- Aligns with constitution's code quality principles

**Best Practices**:
- Enable `strict: true` in tsconfig.json
- Use `noUncheckedIndexedAccess` to prevent undefined access
- Define interfaces for all data models
- Avoid `any` types - use `unknown` for truly dynamic data

---

### Tailwind CSS + ShadCN UI

**Decision**: Tailwind CSS 3.4+ with ShadCN UI components

**Rationale**:
- Tailwind provides utility-first styling without custom CSS bloat
- ShadCN offers accessible, customizable components built on Radix UI
- Both libraries use minimal runtime code (mostly CSS)
- Excellent accessibility support out of the box
- Easy to maintain consistent design tokens

**Implementation**:
- Initialize ShadCN with `npx shadcn-ui@latest init`
- Only import components actually used (tree-shaking)
- Customize theme via tailwind.config.ts for brand colors
- Use ShadCN's built-in color tokens for constitution compliance

**Bundle Size Impact**: ~50KB gzipped for full ShadCN component set, but typically only 5-10KB per component used

---

### YAML Configuration

**Decision**: Use `js-yaml` library with TypeScript types

**Rationale**:
- Lightweight library (~20KB)
- Type-safe parsing with custom type guards
- Easy to read/edit manually by admins
- Enables git-tracked configuration changes

**Best Practices**:
- Create TypeScript interfaces for YAML schemas
- Validate YAML on load with schema validation
- Use watch mode to reload configuration changes in development
- Provide migration scripts for schema changes

**Alternatives Considered**:
- JSON: Rejected - Less human-readable, no comments
- TOML: Rejected - Less familiar, similar benefits to YAML
- SQLite/PostgreSQL: Rejected - Overkill for single-user homelab, adds infrastructure complexity

---

## Architecture Decisions

### Configuration Storage

**Decision**: File-based YAML configuration in `userdata/config/`

**Rationale**:
- Simple, no database setup required
- Easy to backup and version control
- Matches user requirements explicitly stated
- Fast enough for single-user homelab use case

**File Structure**:
```
userdata/config/
├── links.yaml          # Service links with metadata
├── categories.yaml     # Categories with display order
└── settings.yaml       # Global settings (check intervals, notification config)
```

**File Watching**: Use Next.js API route watchers or `chokidar` to reload configuration when files change (dev mode only; production uses in-memory caching with manual reload)

---

### Background Status Checking

**Decision**: Next.js Route Handlers with cron jobs or serverless scheduler

**Rationale**:
- Next.js 16 supports cron jobs via `cron` configuration in `next.config.js`
- Serverless execution avoids persistent server requirements
- Can scale automatically with Vercel/other hosting
- Simple implementation with existing Route Handlers

**Implementation Options**:
1. **Vercel Cron Jobs**: If deploying to Vercel, use built-in cron
2. **node-cron in API route**: For self-hosted, use `node-cron` triggered on server startup
3. **External scheduler**: For maximum flexibility, use external cron to hit API endpoint

**Recommended**: Option 2 for homelab deployment (self-hosted), Option 1 for Vercel deployment

**Status Check Logic**:
- Fetch service URL with `fetch()` and 10-second timeout
- Online: 2xx response within 5 seconds
- Diminished: 2xx response between 5-10 seconds or 5xx errors
- Offline: Connection error or timeout > 10 seconds
- Unknown: Check failed due to internal error (log warning)

---

### Notification System

**Decision**: Separate notification service using Nodemailer (email) and native fetch (webhooks)

**Rationale**:
- Nodemailer is standard, reliable for email (SMTP)
- Webhooks require only `fetch()` - no dependencies
- In-app alerts can use Next.js Server Actions + React state
- Keep notification logic isolated for testability

**Email Configuration**:
- Store SMTP credentials in environment variables (never in YAML)
- Support standard email providers (Gmail, SendGrid, Mailgun)
- Use template strings for email body formatting
- Retry failed deliveries with exponential backoff

**Webhook Configuration**:
- Store webhook URLs in YAML per service
- POST JSON payload with service details and status change
- Handle webhook failures gracefully (log, retry 3 times)
- Support optional webhook headers for authentication

---

## Performance Optimization

### Bundle Size Management

**Decision**: Code splitting, tree-shaking, and minimal dependencies

**Strategies**:
1. **Dynamic imports**: Load admin interface only on authenticated routes
2. **Route-based splitting**: Next.js automatically splits by route
3. **Component lazy loading**: Use `dynamic()` for heavy components
4. **Image optimization**: Next.js Image component for service icons
5. **Avoid heavy libraries**: Use native browser APIs (fetch, crypto) when possible

**Target Metrics**:
- Initial bundle (dashboard): < 300 KB gzipped
- Admin bundle: < 400 KB gzipped
- Total initial load: < 500 KB gzipped

**Monitoring**: Use Next.js Bundle Analyzer to track bundle size

---

### Search Performance

**Decision**: Client-side search with debounce for 500 services

**Rationale**:
- 500 services × 500 bytes per record = 250KB total data
- Fits easily in memory, no search index needed
- Real-time filtering without server round trips
- Simple implementation with array filter

**Implementation**:
- Load all service data on dashboard mount
- Implement search with 300ms debounce (avoid re-renders on every keystroke)
- Search across name, description, and metadata keys/values
- Update results in < 100ms for 500 services

**Alternatives Considered**:
- Server-side search with Fuse.js: Rejected - Overkill for 500 records
- Lunr.js index: Rejected - Adds bundle weight (~40KB) for minimal benefit

---

### Status Update Caching

**Decision**: In-memory cache with TTL, persisted to YAML

**Rationale**:
- Status checks happen every 60 seconds (configurable)
- Cache results to avoid repeated checks
- Persist last known status to YAML on update
- Dashboard reads from cache, not live checks

**Cache Structure**:
```typescript
interface StatusCache {
  [serviceId: string]: {
    status: 'online' | 'offline' | 'diminished' | 'unknown'
    lastChecked: Date
    responseTime: number
    statusCode: number
  }
}
```

**TTL**: 120 seconds (2x check interval) before forcing refresh

---

## Testing Strategy

### Unit Testing

**Framework**: Jest + React Testing Library

**Coverage Targets**:
- Status checker logic: 100% (critical path)
- Notification service: 90%
- Configuration parsing: 100%
- UI components: 80%

**Test Utilities**:
- Mock `fetch()` for HTTP requests
- Mock YAML file system reads
- Use `msw` (Mock Service Worker) for API route testing

---

### Integration Testing

**Framework**: React Testing Library + Jest

**Scope**:
- Dashboard page renders and sorts correctly
- Admin forms validate and submit correctly
- Configuration updates reflect on dashboard
- Search and filter functionality

**Approach**:
- Test user flows, not implementation details
- Use `screen.getByRole()` for accessibility
- Mock API responses to isolate frontend

---

### E2E Testing

**Framework**: Playwright

**Critical Flows**:
1. View dashboard, search, sort, click service tile
2. Admin login, add link, verify appears on dashboard
3. Bulk edit multiple links
4. Status badge updates after check interval

**Configuration**:
- Run in headless mode for CI
- Use fixture YAML files for test data
- Clean up test data after each run

---

## Security Considerations

### Input Validation

**Strategy**: Server-side validation + TypeScript types

**Validation Points**:
- API route handlers validate request bodies
- YAML schema validation on load
- URL validation (prevent SSRF attacks)
- Sanitize user input before display (prevent XSS)

**Libraries**:
- `zod` for runtime schema validation
- Built-in Next.js request validation

---

### Authentication

**Decision**: Simple session-based auth with hashed passwords

**Rationale**:
- Single admin user, no OAuth needed
- bcrypt for password hashing
- Session management via Next.js cookies
- HTTPS required in production

**Implementation**:
- Store hashed password in `settings.yaml`
- Use `iron-session` or Next.js cookies for session storage
- Session timeout: 24 hours
- CSRF protection via Next.js built-in tokens

**Future Enhancement**: Consider OAuth2 or multi-user support if needed

---

### Secrets Management

**Policy**: Never commit secrets to repository

**Secrets**:
- SMTP credentials (email notifications)
- Admin password (hashed)
- Webhook authentication tokens (if any)
- Next.js session secret

**Storage**:
- Environment variables (`.env.local` for development)
- Platform secrets manager for production (Vercel env vars, etc.)
- Document required env vars in README

---

## Accessibility

### WCAG 2.1 AA Compliance

**Strategy**: ShadCN components + custom ARIA labels

**Key Requirements**:
- Keyboard navigation for all interactive elements
- Color contrast ratio 4.5:1 minimum (ShadCN handles this)
- Screen reader announcements for status changes
- Focus management in forms and modals
- Skip links for navigation
- Alt text for all service icons

**Testing**:
- Automated: `axe` accessibility testing with Jest
- Manual: Keyboard-only navigation testing
- Screen reader: NVDA (Windows), VoiceOver (Mac)

---

## Deployment Considerations

### Homelab Deployment

**Options**:
1. **Docker container**: Self-contained, portable
2. **PM2 process manager**: Direct Node.js deployment
3. **Systemd service**: Native Linux service

**Recommended**: Docker container for consistency

**Docker Configuration**:
- Multi-stage build for small image size
- Mount `userdata/` as volume for configuration persistence
- Expose port 3000 (or configured port)
- Environment variables for secrets

---

### Build Optimization

**Strategies**:
- Enable SWC minification (Next.js default)
- Use `output: 'standalone'` for Docker builds
- Optimize images on build
- Tree-shake unused dependencies
- Source maps for production debugging

---

## Open Questions / Deferred Decisions

1. **Deployment Platform**: Vercel vs. self-hosted Docker? (Decision depends on user preference - both are viable)
2. **Email Provider**: Gmail SMTP vs. SendGrid vs. Mailgun? (All supported, document in README)
3. **Cron Implementation**: Vercel Cron vs. node-cron vs. external scheduler? (Implementation depends on deployment choice)
4. **Image Hosting**: Local filesystem vs. CDN vs. object storage? (User specified local, but document CDN option for scale)

---

## References

- Next.js Documentation: https://nextjs.org/docs
- ShadCN UI: https://ui.shadcn.com
- Tailwind CSS: https://tailwindcss.com
- React Testing Library: https://testing-library.com/react
- Playwright: https://playwright.dev
- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
