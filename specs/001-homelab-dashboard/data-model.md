# Data Model: Homelab Service Dashboard

**Feature**: 001-homelab-dashboard
**Date**: 2026-01-24

## Overview

This document defines the data model for the homelab service dashboard, including entities, attributes, relationships, validation rules, and state transitions.

---

## Entities

### ServiceLink

Represents a homelab service with all configuration and status information.

**Attributes**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | string | Yes | Auto-generated | Unique identifier (UUID v4) |
| `name` | string | Yes | - | Human-readable service name |
| `url` | string | Yes | - | Service URL (must be valid HTTP/HTTPS) |
| `icon` | string | No | `null` | Icon image path or URL |
| `description` | string | No | `null` | Brief service description |
| `categoryId` | string | Yes | - | Reference to Category entity |
| `metadata` | Record<string, string> | No | `{}` | Searchable key-value pairs |
| `status` | Status | Yes | `unknown` | Current service status |
| `checkInterval` | number | No | `null` | Override global check interval (seconds), `null` uses global |
| `notificationEnabled` | boolean | No | `false` | Whether to send notifications for this service |
| `notificationConditions` | NotificationCondition[] | No | `[]` | When to send notifications |
| `lastChecked` | Date | No | `null` | Timestamp of last status check |
| `createdAt` | Date | Yes | Now | Timestamp when service was created |
| `updatedAt` | Date | Yes | Now | Timestamp when service was last updated |

**Validation Rules**:
- `name`: 1-100 characters, no leading/trailing whitespace
- `url`: Valid URL with http:// or https:// scheme
- `icon`: If provided, must be valid URL or relative path to `userdata/images/`
- `description`: Max 500 characters
- `categoryId`: Must reference existing category
- `metadata`: Max 10 key-value pairs, keys max 50 chars, values max 200 chars
- `checkInterval`: If provided, must be >= 30 seconds

**Relationships**:
- Belongs to `Category` (many-to-one)
- Has many `StatusCheck` records (one-to-many)
- Has many `Notification` records (one-to-many)

---

### Category

Groups related services together.

**Attributes**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | string | Yes | Auto-generated | Unique identifier (UUID v4) |
| `name` | string | Yes | - | Category name |
| `displayOrder` | number | Yes | 0 | Order for display on dashboard (lower = first) |
| `createdAt` | Date | Yes | Now | Timestamp when category was created |
| `updatedAt` | Date | Yes | Now | Timestamp when category was last updated |

**Validation Rules**:
- `name`: 1-50 characters, no leading/trailing whitespace, unique
- `displayOrder`: Non-negative integer

**Relationships**:
- Has many `ServiceLink` entities (one-to-many)

---

### StatusCheck

Record of an automated health check for a service.

**Attributes**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | string | Yes | Auto-generated | Unique identifier (UUID v4) |
| `serviceId` | string | Yes | - | Reference to ServiceLink entity |
| `statusCode` | number | Yes | - | HTTP status code (or 0 for connection error) |
| `responseTime` | number | Yes | - | Response time in milliseconds (or -1 for timeout/error) |
| `status` | Status | Yes | - | Resulting service status |
| `checkedAt` | Date | Yes | Now | Timestamp when check was performed |
| `error` | string | No | `null` | Error message if check failed |

**Validation Rules**:
- `statusCode`: 0 (connection error) or 100-599
- `responseTime`: -1 (error) or >= 0 milliseconds
- `error`: Max 500 characters if provided

**Relationships**:
- Belongs to `ServiceLink` (many-to-one)

---

### Notification

Record of a status change notification sent.

**Attributes**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | string | Yes | Auto-generated | Unique identifier (UUID v4) |
| `serviceId` | string | Yes | - | Reference to ServiceLink entity |
| `previousStatus` | Status | Yes | - | Status before change |
| `newStatus` | Status | Yes | - | Status after change |
| `method` | NotificationMethod | Yes | - | How notification was sent |
| `sentAt` | Date | Yes | Now | Timestamp when notification was sent |
| `delivered` | boolean | Yes | - | Whether delivery was successful |
| `error` | string | No | `null` | Error message if delivery failed |

**Validation Rules**:
- `error`: Max 500 characters if provided

**Relationships**:
- Belongs to `ServiceLink` (many-to-one)

---

### AdminUser

Represents an administrator with login credentials.

**Attributes**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | string | Yes | Auto-generated | Unique identifier (UUID v4) |
| `username` | string | Yes | "admin" | Login username |
| `passwordHash` | string | Yes | - | Bcrypt-hashed password (cost 10) |
| `createdAt` | Date | Yes | Now | Timestamp when admin was created |

**Validation Rules**:
- `username`: 3-50 characters, alphanumeric plus underscore
- `passwordHash`: Valid bcrypt hash (60 chars)

**Note**: For initial deployment, a single admin user is sufficient. Multi-user support can be added later if needed.

---

### Settings

Global application settings.

**Attributes**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `globalCheckInterval` | number | Yes | 60 | Default status check interval in seconds |
| `statusTimeout` | number | Yes | 5 | Seconds before status considered "diminished" |
| `checkTimeout` | number | Yes | 10 | Seconds before check times out (offline) |
| `notificationEmail` | string | No | `null` | Default email address for notifications |
| `smtpHost` | string | No | `null` | SMTP server hostname |
| `smtpPort` | number | No | 587 | SMTP server port |
| `smtpSecure` | boolean | No | true | Use TLS for SMTP |
| `smtpUser` | string | No | `null` | SMTP username |
| `smtpPassword` | string | No | `null` | SMTP password (stored in env, not YAML) |
| `updatedAt` | Date | Yes | Now | Timestamp when settings were last updated |

**Validation Rules**:
- `globalCheckInterval`: >= 30 seconds
- `statusTimeout`: 1-30 seconds
- `checkTimeout`: 5-60 seconds, must be > statusTimeout
- `smtpPort`: 25, 465, 587, or 2525
- `notificationEmail`: Valid email format if provided

**Note**: SMTP password is stored in environment variables, not in YAML file, for security.

---

## Enums

### Status

Service status enum.

```typescript
type Status = 'online' | 'offline' | 'diminished' | 'unknown';
```

**Status Determination Logic**:
- `online`: HTTP 2xx response within `statusTimeout` seconds
- `diminished`: HTTP 2xx response between `statusTimeout` and `checkTimeout` seconds, or HTTP 5xx response
- `offline`: Connection error, timeout > `checkTimeout`, or HTTP 4xx (except 429)
- `unknown`: Internal error during check (log warning)

---

### NotificationMethod

Notification delivery method.

```typescript
type NotificationMethod = 'email' | 'webhook' | 'in-app';
```

---

### NotificationCondition

Conditions for triggering notifications.

```typescript
type NotificationCondition = 'offline' | 'online' | 'diminished' | 'any';
```

**Logic**:
- `offline`: Notify only when transitioning to offline status
- `online`: Notify only when transitioning to online status
- `diminished`: Notify only when transitioning to diminished status
- `any`: Notify on any status change

---

## Relationships Diagram

```
Category (1) --------< (N) ServiceLink
                         |
                         | (N)
                         v
                    StatusCheck
                         ^
                         | (1)
                         |
ServiceLink (1) --------< (N) Notification
```

---

## YAML File Schemas

### links.yaml

```yaml
links:
  - id: "550e8400-e29b-41d4-a716-446655440000"
    name: "Home Assistant"
    url: "https://homeassistant.local:8123"
    icon: "/userdata/images/home-assistant.png"
    description: "Smart home automation hub"
    categoryId: "550e8400-e29b-41d4-a716-446655440001"
    metadata:
      type: "automation"
      location: "server"
    status: "online"
    checkInterval: null
    notificationEnabled: true
    notificationConditions:
      - "offline"
    lastChecked: "2026-01-24T12:00:00Z"
    createdAt: "2026-01-24T10:00:00Z"
    updatedAt: "2026-01-24T10:00:00Z"
```

---

### categories.yaml

```yaml
categories:
  - id: "550e8400-e29b-41d4-a716-446655440001"
    name: "Home Automation"
    displayOrder: 0
    createdAt: "2026-01-24T10:00:00Z"
    updatedAt: "2026-01-24T10:00:00Z"
  - id: "550e8400-e29b-41d4-a716-446655440002"
    name: "Media"
    displayOrder: 1
    createdAt: "2026-01-24T10:00:00Z"
    updatedAt: "2026-01-24T10:00:00Z"
```

---

### settings.yaml

```yaml
globalCheckInterval: 60
statusTimeout: 5
checkTimeout: 10
notificationEmail: "admin@example.com"
smtpHost: "smtp.gmail.com"
smtpPort: 587
smtpSecure: true
smtpUser: "your-email@gmail.com"
# smtpPassword: stored in SMTP_PASSWORD env var
updatedAt: "2026-01-24T10:00:00Z"
```

---

## State Transitions

### ServiceLink Status Transition

```
[initial] -> unknown
unknown -> online (successful check)
unknown -> offline (check failed)
unknown -> diminished (slow check)
online -> offline (check failed)
online -> diminished (response slowed)
online -> unknown (internal error)
diminished -> online (speed improved)
diminished -> offline (check failed)
diminished -> unknown (internal error)
offline -> online (check succeeded)
offline -> diminished (check succeeded but slow)
offline -> unknown (internal error)
```

**Note**: All status changes trigger notifications if configured and conditions match.

---

## Indexes

For performance optimization (when/if migrating to database):

1. `ServiceLink.categoryId` - Filter by category
2. `ServiceLink.status` - Filter by status for sorting
3. `ServiceLink.name` - Full-text search by name
4. `StatusCheck.serviceId` + `checkedAt` - Query recent checks per service
5. `Notification.serviceId` + `sentAt` - Query notification history

For YAML-based implementation:
- Load all data into memory on startup
- Use in-memory filtering/searching (sufficient for 500 services)
- Write changes to YAML immediately on mutation

---

## Data Migration Strategy

### Versioning

Each YAML file includes a `version` field for schema migration support.

```yaml
version: "1.0.0"
links: [...]
```

### Migration Process

1. Check `version` field in YAML
2. If version mismatch, run migration script
3. Update `version` field after successful migration
4. Backup old YAML before migration

**Example Migration**:
- v1.0.0 → v1.1.0: Add `notificationEnabled` field (default false)

---

## Validation Implementation

### Zod Schemas

Use Zod for runtime validation:

```typescript
import { z } from 'zod';

const ServiceLinkSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(100).trim(),
  url: z.string().url(),
  icon: z.string().url().or(z.string().startsWith('/userdata/images/')).nullable(),
  description: z.string().max(500).nullable(),
  categoryId: z.string().uuid(),
  metadata: z.record(z.string().min(1).max(50), z.string().max(200)).max(10),
  status: z.enum(['online', 'offline', 'diminished', 'unknown']),
  checkInterval: z.number().int().positive().nullable(),
  notificationEnabled: z.boolean(),
  notificationConditions: z.array(z.enum(['offline', 'online', 'diminished', 'any'])),
  lastChecked: z.coerce.date().nullable(),
  createdAt: z.coerce.date(),
  updatedAt: z.coerce.date(),
});
```

---

## References

- Feature Specification: `/specs/001-homelab-dashboard/spec.md`
- Research Document: `/specs/001-homelab-dashboard/research.md`
