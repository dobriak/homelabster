# homelabster Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-01-24

## Active Technologies

- Next.js 16+ with TypeScript 5+ + React 18+, Tailwind CSS, ShadCN UI components, js-yaml (001-homelab-dashboard)

## Project Structure

```text
app/                    # Next.js app router structure
├── (public)/           # Public routes (dashboard)
├── (admin)/            # Admin routes (protected)
├── api/                # API routes
components/             # React components
├── ui/                 # ShadCN UI components
├── dashboard/          # Dashboard components
└── admin/              # Admin components
lib/                    # Utilities and shared logic
types/                  # TypeScript type definitions
userdata/               # Configuration and images
├── config/             # YAML config files
└── images/             # Service icons
tests/                  # Test suites
├── unit/               # Unit tests
├── integration/         # Integration tests
└── e2e/                # E2E tests (Playwright)
```

## Commands

npm test && npm run lint

## Code Style

Next.js 16+ with TypeScript 5+: Follow standard conventions

## Recent Changes

- 001-homelab-dashboard: Added Next.js 16+ with TypeScript 5+ + React 18+, Tailwind CSS, ShadCN UI components, js-yaml

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
