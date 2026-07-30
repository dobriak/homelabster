# Homelabster Design System

A warm, technical design language inspired by instrument panels and well-crafted tools. Maritime blue anchors the palette; teal provides accent and feedback.

## Principles

- **Clarity over decoration.** Every visual choice serves comprehension — health status, service identity, navigation hierarchy.
- **One accent, used deliberately.** Teal (`--hs-accent`) appears only where it carries meaning: focus states, hover feedback, active indicators.
- **Accessible by default.** All text and interactive color combinations meet WCAG AA contrast (4.5:1). Focus indicators are always visible.
- **Dark mode is not an afterthought.** Every token has a light and dark value. Dark mode uses a deep navy base, not an inverted white.

## Tokens

All visual values derive from CSS custom properties defined in `static/app.css`. Never hardcode hex values in new CSS — always reference the token.

### Colors

| Token | Light | Dark | Usage |
|---|---|---|---|
| `--hs-bg` | `#F5F3EF` | `#0F172A` | Page background |
| `--hs-surface` | `#FFFFFF` | `#1E293B` | Card and modal surfaces |
| `--hs-primary` | `#1B3A5C` | `#7DA8C9` | Navbar, primary buttons, headings |
| `--hs-accent` | `#2A9D8F` | `#5EC4BA` | Focus rings, hover accents, active states |
| `--hs-text` | `#1E293B` | `#E2E8F0` | Primary body text |
| `--hs-muted` | `#64748B` | `#94A3B8` | Secondary text, labels, placeholders |
| `--hs-border` | `#E2E0DC` | `#334155` | Card borders, table rules, dividers |

Derived shadows:

| Token | Usage |
|---|---|
| `--hs-card-shadow` | Default card elevation |
| `--hs-card-shadow-hover` | Card hover/active elevation |
| `--hs-focus-ring` | Focus indicator on interactive elements |

### Typography

| Role | Family | Weights | Usage |
|---|---|---|---|
| Body | Inter | 400, 500, 600, 700 | All UI text, headings, labels |
| Code | JetBrains Mono | 400, 500, 600 | `<code>` elements, IPs, CIDRs |

Loaded via Google Fonts in `base.html`. The `font-family` cascade falls back to `system-ui, -apple-system, sans-serif`.

Type scale follows Bootstrap's heading classes (`h1`–`h6`). Custom refinements:
- Headings use `font-weight: 700` (display) or `600` (subheadings)
- Letter-spacing is tightened on headings (`-0.025em` to `-0.01em`)
- Table headers are uppercase with `0.03em` letter-spacing at `0.8125rem`

## Components

### Cards (`.card`)

Base styling applied to all `.card` elements:
- `border-radius: 0.75rem`
- Subtle shadow via `--hs-card-shadow`
- Smooth hover lift (`translateY(-1px)`) with enhanced shadow
- Background color from `--hs-surface`

### Service cards (`.card.service-card`)

Extends `.card` with:
- `border-left: 3px solid transparent` by default
- On hover: left border transitions to teal (`--hs-accent`), deeper lift (`translateY(-2px)`)
- Service name links transition to teal on hover

```html
<article class="card service-card h-100">
  <div class="card-body">...</div>
</article>
```

### Health indicators (`.health-indicator`)

Small circles indicating service health. Apply state via additional class:

```html
<span class="health-indicator health-healthy" role="img" aria-label="Health status: healthy"></span>
<span class="health-indicator health-unhealthy" role="img" aria-label="Health status: unhealthy"></span>
```

States: `health-healthy` (green glow), `health-unhealthy` (red glow), default (muted gray).

### Page headers (`.page-header`)

Consistent page titles with refined typography:

```html
<div class="page-header">
  <h1 class="h2 mb-0">Page title</h1>
  <p class="mb-0">Optional description.</p>
</div>
```

### Category headings (`.service-category h2`)

Service grid category labels with a subtle bottom border separator:

```html
<section class="service-category">
  <h2 class="h4 mb-3"><i class="fas fa-cloud me-2" aria-hidden="true"></i>Category name</h2>
  <!-- service cards -->
</section>
```

### Alerts

Alerts use soft background tints with a colored left border:

```html
<div class="alert alert-info">Informational message.</div>
<div class="alert alert-success">Success message.</div>
<div class="alert alert-danger">Error message.</div>
```

### Forms

Labels are `0.875rem`, `font-weight: 500`. Focus states use the teal focus ring. Helper text uses `--hs-muted`.

```html
<label class="form-label" for="example">Field name</label>
<input class="form-control" id="example" type="text">
<div class="form-text">Optional helper text.</div>
```

## Extending the system

### Adding a new color token

1. Define both light and dark values in `app.css` under `:root` and `[data-bs-theme="dark"]`
2. Name it `--hs-{purpose}` (e.g., `--hs-warning`, `--hs-success`)
3. Use it via `var(--hs-{purpose})` — never hardcode the hex

```css
:root {
  --hs-warning: #D97706;
}

[data-bs-theme="dark"] {
  --hs-warning: #FBBF24;
}
```

### Adding a new component

1. Write styles at the bottom of `app.css`, grouped with a `/* ----- Component name ----- */` comment
2. Use existing tokens for all colors, shadows, and spacing
3. Include `transition` on properties that change on hover/focus
4. Add `prefers-reduced-motion` handling if the component animates
5. Ensure focus-visible states work with the teal focus ring

### Adding a page

1. Create the template extending `base.html`
2. Use the `.page-header` pattern for the title
3. Use `.card` for content containers
4. Reference tokens, not raw values

### Accessibility checklist

Before shipping any visual change:

- [ ] Text contrast ≥ 4.5:1 (use [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/))
- [ ] Interactive elements have visible `:focus-visible` styles
- [ ] No information conveyed by color alone (use icons, text, or patterns alongside)
- [ ] Animations respect `prefers-reduced-motion: reduce`
- [ ] Images and decorative icons have appropriate `alt` or `aria-hidden`
- [ ] Form inputs have associated `<label>` elements

## File structure

```
static/
  app.css              ← Design system tokens and all custom styles
  bootstrap-5.3.8.min.css   ← Bootstrap (loaded before app.css)
  homelabster-icon.svg ← App logo
  default-service.svg  ← Fallback service icon
  favicon.ico          ← Browser tab icon

templates/
  base.html            ← Loads fonts, Bootstrap, app.css; defines navbar and layout shell
  dashboard.html       ← Main service grid view
  admin.html           ← Settings and category management
  services.html        ← Service CRUD table
  ipam.html            ← IP address management
  partials/            ← Reusable template fragments
```

CSS loads in this order: Google Fonts → Bootstrap → app.css. Custom styles override Bootstrap via specificity and `!important` where needed (e.g., navbar background, alert borders).
