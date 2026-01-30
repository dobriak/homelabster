# Homelabster

A simple, elegant web application for organizing links to your homelab services.

## Purpose

Homelabster helps homelab enthusiasts easily organize and access their self-hosted services through a beautiful dashboard. Display your services as tiles with icons, URLs, and descriptions - no more remembering internal IPs and ports!

**Key Features:**
- Responsive tile-based dashboard with search functionality
- Admin panel for managing service tiles
- Light/dark theme support
- Simple file-based storage (no database required)
- Docker-ready for easy deployment

## Pages

### Dashboard (/)
A clean, searchable dashboard displaying all your homelab services as clickable tiles.

### Admin Panel (/admin)
Protected by username/password authentication with two tabs:

**Tab 1: Tiles**
- Create, edit, and delete service tiles
- Upload custom icons (PNG, JPG, SVG)
- Reorder tiles with custom sort order

**Tab 2: Settings**
- Configure site name
- Set theme preference (light/dark/system)

Authentication credentials are configured via environment variables for security.

## Technology Stack

- **Next.js 16+** with React 19+ (App Router)
- **TailwindCSS 4+** with ShadCN UI components
- **TypeScript 5+**
- **Bun** runtime and package management
- **Task-go** for orchestration

## Data Storage

All user-generated data is stored in `./userdata/`:
- **Images**: `./userdata/images/` - Uploaded tile icons
- **Configuration**: `./userdata/config/settings.json` - All tiles and settings

No database required - everything is stored in JSON format for simplicity and portability.

## Quick Start

### Development

1. Install dependencies:
   ```bash
   cd src
   bun install
   ```

2. Set up environment variables:
   ```bash
   # Copy .env file to src directory or project root
   cp ../.env .env
   ```

3. Run development server:
   ```bash
   bun dev
   ```

4. Open http://localhost:3000

**Default credentials:**
- Username: `admin`
- Password: `admin` (change in `.env` file)

### Production Deployment

#### Docker Compose (Recommended)

1. Create/update `.env` file in project root:
   ```env
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your_secure_password
   JWT_SECRET=your_generated_secret
   ```

   Generate a secure JWT secret:
   ```bash
   openssl rand -base64 32
   ```

2. Start the application:
   ```bash
   docker-compose up -d
   ```

3. Access the dashboard at http://localhost:3000

**Important:** The `./userdata` directory is mounted as a volume for data persistence.

#### Docker Build

```bash
docker build -t homelabster .
docker run -d \
  -p 3000:3000 \
  -e ADMIN_USERNAME=admin \
  -e ADMIN_PASSWORD=your_password \
  -e JWT_SECRET=your_secret \
  -v $(pwd)/userdata:/app/userdata \
  homelabster
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ADMIN_USERNAME` | Admin panel username | `admin` |
| `ADMIN_PASSWORD` | Admin panel password | `admin` |
| `JWT_SECRET` | Secret key for JWT tokens | (required) |
| `NODE_ENV` | Environment mode | `development` |

### Sample Data

The application includes sample tiles for common homelab services (Proxmox, Pi-hole, Home Assistant, Portainer). Delete or modify these in the admin panel after first login.

## Project Structure

```
homelabster/
├── src/                    # Next.js application
│   ├── app/               # App Router pages & API routes
│   ├── components/        # React components
│   ├── lib/               # Utilities and data layer
│   └── types/             # TypeScript types
├── userdata/              # User data (mounted as volume)
│   ├── images/           # Uploaded icons
│   └── config/           # settings.json
├── Dockerfile            # Docker image configuration
├── docker-compose.yml    # Docker Compose setup
└── README.md
```

## Development Commands

From the `src/` directory:

```bash
bun install      # Install dependencies
bun dev          # Run development server
bun build        # Build for production
bun start        # Start production server
bun run lint     # Run linter
```

## Features

- **Responsive Design**: Automatically adapts to mobile, tablet, and desktop screens
- **Dark Mode**: Full theme support with system detection
- **Search**: Real-time client-side filtering by name or description
- **Image Upload**: Drag-and-drop icon uploads with preview
- **Toast Notifications**: User-friendly feedback for all actions
- **JWT Authentication**: Secure admin panel access
- **File-based Storage**: No database setup required

## Security Notes

- Change default admin credentials immediately
- Generate a strong JWT secret for production
- Run the application behind a reverse proxy (Nginx, Traefik, etc.)
- The app is designed for internal network use only

## Contributing

This is a personal homelab project, but suggestions and improvements are welcome!

## License

MIT License - feel free to use and modify for your homelab.
