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

## Project Structure

```
homelabster/
├── src/                    # Next.js application
│   ├── app/               # Next.js App Router pages and layouts
│   ├── lib/               # Utility functions (e.g., utils.ts)
│   ├── components/        # React components (to be created)
│   └── package.json       # Node dependencies
├── userdata/              # User-generated data (external to app)
│   ├── images/           # Uploaded tile icons
│   └── config/           # settings.json for configuration
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

### Fonts
The application uses Geist Sans and Geist Mono fonts loaded via `next/font/google`.

### Environment Variables
Admin authentication credentials are stored in `.env` file (not tracked in git):
- Username and password for admin page access
- Create `.env` file in the root or `src/` directory as needed

## Deployment

The application is designed for Docker deployment:
- Dockerfile should be created for building the image
- docker-compose.yml should be created for easy deployment on Docker hosts
- The `/userdata` directory should be mounted as a volume to persist data

## Important Conventions

1. **Working Directory**: Most npm/bun commands run from the `src/` directory
2. **Data Persistence**: Always store user data in `./userdata/`, never inside `src/`
3. **Authentication**: Admin page uses simple username/password from `.env` file
4. **Styling**: Use TailwindCSS 4+ with ShadCN UI components following the "new-york" style preset
5. **TypeScript**: Strict mode is enabled (`strict: true` in tsconfig.json)
6. **Task Orchestration**: Use Task-go (Taskfile.yml) for complex orchestration tasks
