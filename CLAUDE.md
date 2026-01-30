# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Homelabster is a simple web application for organizing a directory of links to services hosted in home labs. It displays services as tiles with icons, links, and optional descriptions, featuring a search bar to filter by name or description. The application runs internally only and stores data in external directories.

**Pages:**
- Default page: Dashboard displaying service tiles
- Administration page: Protected by username/password authentication (credentials from .env file)
  - Tab 1: CRUD operations for service tiles
  - Tab 2: General settings (theme, password management, etc.)

## Technology Stack

- **Framework**: Next.js 16+ with React 19+ (App Router)
- **Styling**: TailwindCSS 4+ with ShadCN UI components ("new-york" style)
- **Language**: TypeScript 5+
- **Runtime**: Bun (for package management and runtime)
- **Build Tool**: Task-go for orchestration (https://taskfile.dev/docs/guide)
- **Authentication**: JWT tokens via jose library
- **Forms**: React Hook Form with Zod validation

## Project Structure

```
homelabster/
├── src/                    # Next.js application
│   ├── app/               # Next.js App Router pages and layouts
│   │   ├── (auth)/       # Route group for authentication pages
│   │   │   └── login/    # Login page
│   │   ├── admin/        # Admin dashboard (protected)
│   │   ├── api/          # API routes
│   │   └── page.tsx      # Main dashboard page
│   ├── lib/               # Utility functions and server logic
│   ├── components/        # React components
│   ├── proxy.ts          # Next.js 16 proxy for route protection
│   └── package.json       # Node dependencies
├── userdata/              # User-generated data (external to app)
│   ├── images/           # Uploaded tile icons
│   └── config/           # settings.json for configuration
├── Dockerfile            # Docker image build configuration
├── docker-compose.yml    # Docker deployment orchestration
├── Taskfile.yml          # Task-go orchestration tasks
└── README.md
```

## Development Commands

All commands should be run from the `src/` directory unless otherwise specified:

```bash
# Install dependencies (from src/ directory)
bun install

# Run development server (from src/ directory)
bun dev
# Opens at http://localhost:3000

# Build for production (from src/ directory)
bun run build

# Start production server (from src/ directory)
bun start

# Run linter (from src/ directory)
bun run lint
```

## Architecture Notes

### Path Aliases
The project uses TypeScript path aliases defined in `tsconfig.json`:
- `@/*` maps to `src/*`
- Configured for ShadCN UI with specific aliases:
  - `@/components` → components
  - `@/lib/utils` → lib/utils
  - `@/ui` → components/ui
  - `@/hooks` → hooks

### ShadCN UI Configuration
The project uses ShadCN UI with these settings (from `components.json`):
- Style: "new-york"
- RSC (React Server Components): enabled
- CSS Variables: enabled
- Base color: neutral
- Icon library: lucide-react

### Data Storage
All user-generated data must be stored in `./userdata/` (external to the Next.js app directory):
- **Images**: `./userdata/images/` - uploaded tile icons
- **Configuration**: `./userdata/config/settings.json` - all configuration data

**Important**: The application should not use SQLite as originally mentioned in the README - it uses JSON file storage in `./userdata/config/settings.json`.

### Route Protection (proxy.ts)
Next.js 16 uses `proxy.ts` instead of the legacy `middleware.ts` pattern:
- Located at `src/proxy.ts`
- Protects `/admin` routes with JWT-based authentication
- Exports a `proxy()` function (not `middleware()`)
- Redirects unauthenticated requests to `/login`
- Uses the `jose` library for JWT token verification
- Token stored in `auth-token` cookie

**Important**: When adding new protected routes, ensure they match the pattern in the proxy config matcher.

### Fonts
The application uses Geist Sans and Geist Mono fonts loaded via `next/font/google`.

### Environment Variables
Admin authentication credentials are stored in `.env` file (not tracked in git):
- Username and password for admin page access
- Create `.env` file in the root or `src/` directory as needed

### Authentication Flow
1. User navigates to `/admin`
2. `proxy.ts` checks for valid JWT token in cookies
3. If no token or invalid token, redirects to `/login`
4. Login page (in `(auth)` route group) validates credentials against `.env`
5. On success, sets JWT token cookie and redirects to `/admin`
6. Subsequent `/admin` requests are authenticated via proxy.ts

## Deployment

The application is configured for Docker deployment:
- `Dockerfile` exists in the root directory for building the image
- `docker-compose.yml` exists in the root directory for orchestrated deployment
- The `/userdata` directory must be mounted as a volume to persist data
- Docker setup handles both the Next.js application and data persistence

## Important Conventions

1. **Working Directory**: Most npm/bun commands run from the `src/` directory
2. **Data Persistence**: Always store user data in `./userdata/`, never inside `src/`
3. **Authentication**: Admin page uses JWT-based authentication with credentials from `.env` file
4. **Route Protection**: Next.js 16 uses `proxy.ts` (not `middleware.ts`) for route protection - see src/proxy.ts
5. **Styling**: Use TailwindCSS 4+ with ShadCN UI components following the "new-york" style preset
6. **TypeScript**: Strict mode is enabled (`strict: true` in tsconfig.json)
7. **Task Orchestration**: Use Task-go (Taskfile.yml) for complex orchestration tasks
