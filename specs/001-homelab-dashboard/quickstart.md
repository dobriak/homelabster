# Quickstart Guide: Homelab Service Dashboard

**Feature**: 001-homelab-dashboard
**Last Updated**: 2026-01-24

## Overview

This guide will help you get the homelab service dashboard running in your environment in under 15 minutes.

---

## Prerequisites

Before you begin, ensure you have:

- **Node.js** 18.17 or later
- **npm** 9.0 or later (comes with Node.js)
- **Git** for cloning the repository
- **Text editor** (VS Code recommended)

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd homelabster
```

### 2. Install Dependencies

```bash
npm install
```

This will install:
- Next.js 16+ and React 18+
- TypeScript 5+
- Tailwind CSS
- ShadCN UI components
- js-yaml for configuration
- Testing libraries (Jest, Playwright)

### 3. Initialize ShadCN UI

```bash
npx shadcn-ui@latest init
```

Accept the defaults:
- Style: Default
- Base color: Slate
- CSS variables: Yes

### 4. Create User Data Directory

```bash
mkdir -p userdata/config userdata/images
```

### 5. Initialize Configuration Files

Create `userdata/config/settings.yaml`:

```yaml
version: "1.0.0"
globalCheckInterval: 60
statusTimeout: 5
checkTimeout: 10
notificationEmail: null
smtpHost: null
smtpPort: 587
smtpSecure: true
smtpUser: null
updatedAt: 2026-01-24T10:00:00Z
```

Create `userdata/config/categories.yaml`:

```yaml
version: "1.0.0"
categories:
  - id: default-category-1
    name: General
    displayOrder: 0
    createdAt: 2026-01-24T10:00:00Z
    updatedAt: 2026-01-24T10:00:00Z
```

Create `userdata/config/links.yaml`:

```yaml
version: "1.0.0"
links: []
```

### 6. Set Up Environment Variables

Create `.env.local`:

```bash
# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-me-to-secure-password

# Session Secret (generate with: openssl rand -base64 32)
SESSION_SECRET=your-session-secret-here

# SMTP Configuration (for notifications, optional)
SMTP_PASSWORD=your-smtp-password
```

**Important**: Change `ADMIN_PASSWORD` to a secure password and `SESSION_SECRET` to a random value.

Generate a secure session secret:

```bash
openssl rand -base64 32
```

### 7. Initialize Admin User

Run the setup script to create the admin user:

```bash
npm run setup-admin
```

This will hash your password and create the admin account.

---

## Running the Application

### Development Mode

```bash
npm run dev
```

The dashboard will be available at: **http://localhost:3000**

- **Public Dashboard**: http://localhost:3000/
- **Admin Login**: http://localhost:3000/admin/login

### Production Build

```bash
npm run build
npm start
```

---

## First Steps

### 1. Access the Admin Panel

Navigate to http://localhost:3000/admin/login and log in with:
- Username: `admin`
- Password: (your password from `.env.local`)

### 2. Add a Category

1. Click "Categories" in the admin navigation
2. Click "Add Category"
3. Enter a name (e.g., "Home Automation")
4. Set display order (lower numbers appear first)
5. Click "Save"

### 3. Add a Service Link

1. Click "Links" in the admin navigation
2. Click "Add Link"
3. Fill in the required fields:
   - **Name**: e.g., "Home Assistant"
   - **URL**: e.g., "https://homeassistant.local:8123"
   - **Category**: Select your category
4. Optional fields:
   - **Icon**: Path to image in `userdata/images/` or URL
   - **Description**: Brief description
   - **Metadata**: Key-value pairs for search (e.g., `type: automation`, `location: server`)
5. Configure status checking:
   - **Check Interval**: Leave blank for global default (60 seconds)
   - **Enable Notifications**: Check to receive status change alerts
6. Click "Save"

### 4. View the Dashboard

Navigate to http://localhost:3000/ to see your service tile:
- Click the tile to open the service URL
- Status badge shows current service health (green = online, red = offline, yellow = slow, gray = unknown)

### 5. Add More Services

Repeat steps 2-3 to add all your homelab services. Tips:
- Organize services by category for better organization
- Add metadata for easier searching
- Use custom icons (place images in `userdata/images/`)

---

## Status Checking

The dashboard automatically checks service status based on your configuration:

- **Global Default**: Every 60 seconds (configurable in settings)
- **Per-Service Override**: Set custom interval on individual links
- **Status Determination**:
  - **Online**: Responds within 5 seconds with 2xx status
  - **Diminished**: Responds between 5-10 seconds or with 5xx error
  - **Offline**: No response, timeout, or 4xx error
  - **Unknown**: Internal check error

### Configure Global Settings

1. Navigate to "Settings" in admin panel
2. Adjust:
   - **Global Check Interval**: How often to check all services (min 30 seconds)
   - **Status Timeout**: Seconds before status considered "diminished" (1-30 seconds)
   - **Check Timeout**: Seconds before check times out (5-60 seconds)
3. Click "Save"

---

## Notifications

### Email Notifications

Configure email notifications to receive alerts when services change status:

1. Navigate to "Settings" in admin panel
2. Fill in SMTP configuration:
   - **Notification Email**: Email address to receive alerts
   - **SMTP Host**: e.g., `smtp.gmail.com`
   - **SMTP Port**: 587 (TLS) or 465 (SSL)
   - **SMTP Secure**: Check for TLS
   - **SMTP User**: Your email address
3. Set `SMTP_PASSWORD` in `.env.local` (not in settings YAML)
4. Click "Save"
5. Enable notifications on individual service links

**Example Email Providers**:

| Provider | SMTP Host | Port | Secure |
|----------|-----------|------|--------|
| Gmail | smtp.gmail.com | 587 | Yes |
| SendGrid | smtp.sendgrid.net | 587 | Yes |
| Mailgun | smtp.mailgun.org | 587 | Yes |

### Notification Conditions

For each service link, configure when to send notifications:
- **Offline**: Only when service goes offline
- **Online**: Only when service comes online
- **Diminished**: Only when service becomes slow
- **Any**: Notify on any status change

---

## Adding Custom Icons

### Using Local Images

1. Place image files in `userdata/images/` directory
2. Supported formats: PNG, JPG, SVG, WEBP
3. Recommended size: 64x64 pixels
4. In link form, set icon path: `/userdata/images/your-icon.png`

### Using URLs

You can also use external image URLs:
- Set icon to full URL: `https://example.com/icon.png`
- Ensure CORS headers allow external access if needed

### Using Icon Libraries

For ShadCN UI icons, use Lucide React icons:
- Icons will be rendered using Lucide icon font
- Specify icon name in link form (e.g., `home`, `server`, `database`)

---

## Search and Filter

The public dashboard includes powerful search capabilities:

### Search

- Search bar filters services by **name**, **description**, and **metadata**
- Results update in real-time as you type
- Case-insensitive matching

### Sort

Click sort controls to reorder tiles:
- **Alphabetical (A-Z)**: Sort by service name
- **Status**: Sort by status (online → diminished → offline → unknown)

---

## Bulk Actions

The admin panel supports bulk operations:

### Bulk Edit Categories

1. Navigate to "Links"
2. Select multiple links using checkboxes
3. Choose "Change Category" from bulk actions
4. Select target category
5. Click "Apply"

### Bulk Delete

1. Select multiple links
2. Choose "Delete" from bulk actions
3. Confirm deletion

---

## Troubleshooting

### Dashboard Shows All Services as "Unknown"

**Cause**: Status checker not running or configuration error

**Solution**:
1. Check console logs for errors
2. Verify service URLs are accessible
3. Ensure `userdata/config/links.yaml` exists and is valid YAML
4. Restart the application: `npm run dev`

### Can't Log In to Admin Panel

**Cause**: Incorrect credentials or session issue

**Solution**:
1. Verify username/password in `.env.local`
2. Clear browser cookies
3. Reset admin password: `npm run reset-admin-password`

### Status Checks Not Working

**Cause**: Network issue or service behind authentication

**Solution**:
1. Check if services are accessible from dashboard server
2. For services requiring authentication, status checks may fail (expected)
3. Adjust timeout settings if services are slow to respond

### SMTP Email Not Sending

**Cause**: Incorrect SMTP configuration or firewall issue

**Solution**:
1. Verify SMTP credentials in `.env.local` and settings
2. Check firewall allows outbound SMTP (port 587 or 465)
3. Test SMTP connection manually: `telnet smtp.gmail.com 587`
4. For Gmail, enable "Less Secure Apps" or use App Password

### Configuration Changes Not Reflecting

**Cause**: YAML file not reloaded (production mode)

**Solution**:
1. In development, changes auto-reload
2. In production, restart the application after configuration changes
3. Verify YAML syntax is correct (no trailing spaces, proper indentation)

---

## Deployment

### Docker Deployment (Recommended)

1. Build Docker image:

```bash
docker build -t homelab-dashboard .
```

2. Run container:

```bash
docker run -d \
  -p 3000:3000 \
  -v $(pwd)/userdata:/app/userdata \
  -e ADMIN_USERNAME=admin \
  -e ADMIN_PASSWORD=your-secure-password \
  -e SESSION_SECRET=your-session-secret \
  homelab-dashboard
```

3. Access at http://localhost:3000

### PM2 Deployment (Linux)

1. Install PM2: `npm install -g pm2`
2. Start application: `pm2 start npm --name "homelab-dashboard" -- start`
3. Configure startup: `pm2 startup` and `pm2 save`

### Systemd Service (Linux)

Create `/etc/systemd/system/homelab-dashboard.service`:

```ini
[Unit]
Description=Homelab Service Dashboard
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/homelabster
ExecStart=/usr/bin/npm start
Restart=on-failure
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable homelab-dashboard
sudo systemctl start homelab-dashboard
```

---

## Security Best Practices

1. **Change Default Password**: Always change the admin password from `.env.local`
2. **Use HTTPS**: Enable HTTPS in production (configure reverse proxy like Nginx)
3. **Secure Session Secret**: Generate a random, long session secret
4. **Environment Variables**: Never commit `.env.local` to version control
5. **Regular Updates**: Keep dependencies up to date: `npm update`
6. **Backup Configuration**: Regularly backup `userdata/config/` directory
7. **Limit Access**: Restrict admin panel access to trusted networks (via firewall)

---

## Performance Tips

1. **Optimize Images**: Compress images in `userdata/images/` (use TinyPNG or ImageOptim)
2. **Adjust Check Intervals**: Balance monitoring frequency with server load
3. **Use CDN**: For production, consider serving images via CDN
4. **Monitor Bundle Size**: Check bundle size with: `npm run analyze`
5. **Enable Compression**: Ensure gzip/brotli compression is enabled in web server

---

## Next Steps

- Customize the dashboard theme via Tailwind config
- Add custom notifications (webhooks, Slack, etc.)
- Integrate with your homelab automation platform
- Set up automated backups of configuration files
- Configure reverse proxy (Nginx/Apache) for SSL termination

---

## Getting Help

- **Documentation**: Check `/docs/` directory for detailed guides
- **Issues**: Report bugs on GitHub issues
- **Discussions**: Ask questions in GitHub Discussions

---

## Version

This guide is for version 1.0.0 of the homelab service dashboard.
