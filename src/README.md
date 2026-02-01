# Homelabster - Next.js Application

This is the Next.js 16+ application for Homelabster, a homelab services dashboard. The project uses [Bun](https://bun.sh) as the JavaScript runtime and package manager.

## Technology Stack

- **Framework**: Next.js 16.1.6 with React 19.2.3 (App Router)
- **Runtime**: Bun (replaces Node.js and npm)
- **Language**: TypeScript 5+
- **Styling**: TailwindCSS 4+ with ShadCN UI components ("new-york" style)
- **Authentication**: JWT tokens via jose library
- **Forms**: React Hook Form with Zod validation
- **UI Components**: Radix UI primitives via ShadCN

## Getting Started

### Prerequisites

Install Bun if you haven't already:
```bash
curl -fsSL https://bun.sh/install | bash
```

### Installation

Install dependencies:
```bash
bun install
```

### Development Server

Run the development server:
```bash
bun dev
```

Open [http://localhost:3000](http://localhost:3000) to see the application.

The page auto-updates as you edit files. This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to optimize and load Geist Sans and Geist Mono fonts.

### Environment Setup

Create a `.env` file in the `src/` directory with your admin credentials:
```env
ADMIN_USERNAME=your_username
ADMIN_PASSWORD=your_password
JWT_SECRET=your_secret_key
```

## Available Commands

```bash
# Development server
bun dev

# Production build
bun run build

# Start production server
bun start

# Run linter
bun run lint

# Run tests
bun run test

# Run tests in watch mode
bun run test:watch

# Run tests with coverage report
bun run test:coverage
```

## Testing

The project uses Vitest as the testing framework with React Testing Library for component testing.

### Test Structure

Tests are located in the `__tests__/` directory:

```
src/
├── __tests__/
│   ├── setup.ts         # Test setup with global mocks
│   └── lib/
│       ├── utils.test.ts         # Tests for utility functions
│       ├── validation.test.ts    # Tests for Zod schemas
│       ├── auth.test.ts          # Tests for JWT authentication
│       ├── storage.test.ts       # Tests for image storage (skipped)
│       └── data.test.ts          # Tests for data layer (skipped)
```

### Running Tests

```bash
# Run all tests once
bun run test

# Run tests in watch mode (re-runs on file changes)
bun run test:watch

# Run tests with coverage report
bun run test:coverage
```

### Test Configuration

- **Test Framework**: Vitest 4.x with TypeScript support
- **Test Environment**: happy-dom for React component testing
- **Coverage Provider**: v8 for code coverage
- **Configuration**: `vitest.config.ts`

### Current Test Coverage

- `lib/utils.ts`: 100% coverage
- `lib/validation.ts`: 100% coverage
- `lib/auth.ts`: 35.71% coverage (JWT operations and credential validation)

### Writing Tests

When adding new tests:
1. Place test files in `__tests__/` alongside the code being tested
2. Use `describe()` blocks for grouping related tests
3. Use `it()` or `test()` for individual test cases
4. Use `expect()` for assertions with Vitest matchers
5. Mock external dependencies using `vi.mock()`

Example test structure:
```typescript
import { describe, it, expect } from 'vitest';
import { myFunction } from '@/lib/myfile';

describe('myFunction', () => {
  it('should do something', () => {
    const result = myFunction('input');
    expect(result).toBe('expected output');
  });
});
```

### Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Vitest Coverage Guide](https://vitest.dev/guide/coverage.html)

## Project Structure

```
src/
├── app/
│   ├── (auth)/          # Authentication routes (login)
│   ├── admin/           # Protected admin dashboard
│   ├── api/             # API routes
│   │   ├── auth/       # Authentication endpoints
│   │   ├── images/     # Image serving
│   │   ├── settings/   # Settings management
│   │   └── tiles/      # Tile CRUD operations
│   ├── page.tsx         # Main dashboard page
│   ├── layout.tsx       # Root layout with theme provider
│   └── globals.css      # Global styles
├── components/
│   ├── admin/           # Admin-specific components
│   ├── dashboard/       # Dashboard components
│   ├── ui/              # ShadCN UI components
│   └── theme-provider.tsx
├── lib/
│   ├── auth.ts          # JWT authentication utilities
│   ├── data.ts          # Data access layer
│   ├── utils.ts         # Utility functions
│   └── validation.ts    # Zod schemas
└── proxy.ts             # Next.js 16 route protection
```

## Key Features

### Authentication
- JWT-based authentication for admin routes
- Protected via `proxy.ts` (Next.js 16 pattern)
- Credentials stored in `.env` file
- Login at `/login`, admin dashboard at `/admin`

### Route Protection
The application uses Next.js 16's `proxy.ts` (not middleware.ts) for route protection:
- All `/admin` routes require authentication
- Unauthenticated users are redirected to `/login`
- JWT tokens stored in HTTP-only cookies

### Data Storage
User data is stored externally in `../userdata/`:
- **Images**: `../userdata/images/` - Service tile icons
- **Config**: `../userdata/config/settings.json` - All application settings and tiles

### Styling
- TailwindCSS 4+ with CSS variables
- ShadCN UI components with "new-york" style preset
- Dark/light theme support via next-themes
- Responsive design

## Development Notes

### Path Aliases
The project uses TypeScript path aliases:
- `@/*` → `src/*`
- `@/components` → `components/`
- `@/lib/utils` → `lib/utils`
- `@/ui` → `components/ui/`
- `@/hooks` → `hooks/`

### Adding UI Components
Install ShadCN components using:
```bash
bunx shadcn@latest add [component-name]
```

### Working with Images
- Upload images via the admin dashboard
- Images are stored in `../userdata/images/`
- Served via `/api/images/[filename]` route
- Optimized with Next.js Image component

## Build and Deployment

### Production Build
```bash
bun run build
bun start
```

### Docker Deployment
The application is designed for Docker deployment. See the root `Dockerfile` and `docker-compose.yml` for configuration.

The `/userdata` directory must be mounted as a volume to persist data across container restarts.

## Learn More

### Next.js Resources
- [Next.js Documentation](https://nextjs.org/docs) - Learn about Next.js features and API
- [Next.js 16 Release Notes](https://nextjs.org/blog/next-16) - Latest features including proxy.ts
- [App Router Documentation](https://nextjs.org/docs/app) - App Router architecture

### Bun Resources
- [Bun Documentation](https://bun.sh/docs) - Bun runtime and package manager
- [Bun with Next.js](https://bun.sh/guides/ecosystem/nextjs) - Using Bun with Next.js

### UI Framework Resources
- [ShadCN UI](https://ui.shadcn.com/) - Component library
- [Radix UI](https://www.radix-ui.com/) - Primitive components
- [TailwindCSS](https://tailwindcss.com/) - Utility-first CSS framework

## Troubleshooting

### Bun Installation Issues
If you encounter issues with Bun, ensure you're using the latest version:
```bash
bun upgrade
```

### Build Errors
Clear the Next.js cache and rebuild:
```bash
rm -rf .next
bun run build
```

### Port Already in Use
Change the port in development:
```bash
bun dev --port 3001
```

## Contributing

When making changes:
1. Follow TypeScript strict mode conventions
2. Use existing ShadCN UI components where possible
3. Keep data storage in `../userdata/`, never in `src/`
4. Test authentication flows when modifying protected routes
5. Update this README if adding new features or changing architecture
