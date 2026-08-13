# Bare Bones Soccer — Project Overview

## What This Is
Bare Bones Soccer is a Denver, CO community soccer brand. The website serves as the primary hub for:
- Weekly pickup soccer registration (Sport Stable in Superior, CO on Mondays; Scheitler Rec Center in Denver on Thursdays)
- Special one-off event ticketing (e.g. Brunch Ball, World Cup Block Party, Waldschänke events)
- Community building — members register accounts, receive email updates, and join a WhatsApp group

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5.1 (Python) |
| Database | PostgreSQL via Neon (serverless, SSL required) |
| Hosting | AWS Lambda via Zappa (serverless) — two stages: `dev` (test, generic URL) and `prod` (barebonessoccer.com) |
| Static Files | AWS S3 (`bare-bones-soccer` bucket, `us-east-2`) |
| Media Files | AWS S3 (same bucket) |
| Email | AWS SES, from `no-reply@barebonessoccer.com` |
| Payments | Stripe (checkout sessions) |
| CSS Framework | Bootstrap 5.3 |
| Fonts | Oswald (headings), Barlow Semi Condensed (body), Dancing Script (accent) |
| Analytics | Google Analytics (`G-RZW0GLKZ78`), Google Ads (`AW-17617578293`), Meta Pixel (`580190001252813`) |
| Calendar | FullCalendar 6.1.6 |

**Deploy command:** `source load_env.sh && ./deploy.sh dev` to test, then `./deploy.sh prod` to go live. Both stages share the same Neon database, Stripe account, and email sending — `dev` is for verifying a deploy works, not a data/payment sandbox.

---

## Critical Architecture Notes

### Static Files (IMPORTANT)
Static files (CSS, JS, images, videos) are served from S3 — NOT locally. Any change to `myapp/static/` requires `python manage.py collectstatic` to push to S3 before it takes effect. **Template changes (HTML) are served by Django directly and take effect immediately.**

### Database
SQLite was previously used. The project now runs PostgreSQL on Neon (serverless). Connection pooling is off (`CONN_MAX_AGE: 0`) for Lambda compatibility.

### CSS Cascade Rules (Critical for Frontend Work)
- Always check: is a rule in a template (immediate) or `styles.css` (requires collectstatic)?
- `styles.css` on S3 sets `.custom-navbar { background: transparent !important; }` — do NOT rely on it for navbar styling. Navbar styles live in `base.html` inline `<style>` tag.
- CSS animations cannot override `!important` color rules — use JavaScript `setProperty` instead.
- Inline styles on elements beat class rules unless the class rule has `!important`.
- Two `!important` rules at same specificity: last in DOM order wins.

---

## Project Structure

```
bare_bones_soccer/
├── barebones/
│   ├── settings.py          # All config — AWS, DB, Stripe keys from env vars
│   └── urls.py              # Root URL conf (delegates to myapp/urls.py)
├── myapp/
│   ├── models.py            # All data models (see below)
│   ├── views.py             # All view logic + email sending
│   ├── urls.py              # All URL routes
│   ├── forms.py             # Django forms
│   └── static/css/styles.css  # Global CSS (served from S3)
├── templates/               # All Django HTML templates
│   ├── base.html            # Master layout — navbar, footer, hero section
│   └── ...                  # Page templates (all extend base.html)
└── load_env.sh              # Loads env vars for local dev and deployment
```

---

## Data Models

### `PlayerProfile`
One-to-one with Django's `User`. Stores full name, phone, DOB, age category (adult/minor), emergency contact, electronic signature, waiver agreement, and marketing opt-in. Created at registration.

### `AttendancePayment`
Tracks Stripe payments for weekly pickup games. Links user → game_date → payment_id → amount → status.

### `OneOffEvent`
Tracks tickets for special events (Brunch Ball, World Cup Block Party, etc.). Ticket types: `player`, `player_plus`, `spectator`. Links to User.

### `EventRSVP`
Free RSVPs for events. Email + event name + event date (unique together).

### `EmailUnsubscribe`
Stores unsubscribed emails. `send_email_ses()` checks this before every send — unsubscribed users never receive email.

### `Event` + `EventImage`
Admin-managed events with images stored on S3 via custom storage backends.

### `Person`
Contact form submissions (name, email, message).

---

## URL Routes (Key Pages)

| URL | Name | Template | Notes |
|---|---|---|---|
| `/` | `home` | `home.html` | Homepage |
| `/pickup/` | `series` | `series.html` | Weekly pickup info page |
| `/game-catalog/` | `series_catalog` | `series_catalog.html` | Cards for all games/events (logged-in only) |
| `/schedule/` | `schedule` | `schedule.html` | Sport Stable schedule + registration |
| `/events/` | `events` | `events.html` | All events listing |
| `/waldschanke/` | `waldschanke` | `waldschanke.html` | Brunch Ball V event + ticketing |
| `/world-cup-block-party/` | `world_cup_block_party` | `world_cup_block_party.html` | WCP event (coming soon) |
| `/register/` | `register` | `register.html` | Account creation + waiver |
| `/login/` | `login` | `login.html` | Login |
| `/game-catalog/` | `series_catalog` | `series_catalog.html` | Logged-in landing page |

---

## Email System

All email goes through AWS SES via `send_email_ses(to, subject, body_html)` in `views.py`.

**Automatic emails triggered:**
1. **Account activation** — sent at registration, user must click link to activate
2. **Welcome email** — sent after email activation, includes WhatsApp link and game info
3. **Game reminder** — sent before scheduled pickup games (triggered via AWS EventBridge)
4. **Payment confirmation** — sent after Stripe checkout success

**Unsubscribe:** Every automated email includes an unsubscribe footer. Users who unsubscribe are recorded in `EmailUnsubscribe` and permanently blocked from future emails.

**One-off emails** (e.g. event announcements) are built as raw HTML and sent manually via SES. Templates follow the same table-based layout used for cross-client compatibility.

---

## Payment Flow (Stripe)

Each event type has its own checkout session endpoint:
- `/api/create-multi-checkout-session` — weekly pickup (Sport Stable)
- `/api/create-waldschanke-checkout-session` — Brunch Ball / Waldschänke events
- `/api/create-brighton-checkout-session` — Brighton event
- `/api/create-wcbp-checkout-session` — World Cup Block Party

On success, Stripe redirects to a `*-payment-success` URL which records the `OneOffEvent` or `AttendancePayment` and sends a confirmation email.

Free spectator registration bypasses Stripe entirely via `/api/register-free-spectator`.

---

## User Registration Flow

1. User fills out `/register/` (username, email, password + player profile + waiver)
2. Account created with `is_active = False`
3. Activation email sent via Django's email backend
4. User clicks activation link → account activated
5. AWS EventBridge event `UserRegistered` fired (for downstream automation)
6. Welcome email sent via SES

---

## Design System

**Brand colors:**
- Sky blue: `#65A2FC` (primary, nav links, logo)
- Purple: `#9b59f5` (CTAs, hover states, sign-in button)
- Dark navy: `#0d1928` (backgrounds, footer border)
- Deep navy: `#0a1628` / `#102040` (dark sections)
- Red: `#dc3545` (accent rules, eyebrow labels)
- Gold: `#FFD700` (event card icons)

**Navbar:** Transparent dark strip (`rgba(0,0,0,0.18)`) across all pages, defined in `base.html` inline `<style>`. Sky blue nav links, purple pill CTA for Sign In.

**Hero sections:** Full-width background image or video, defined per-page via `{% block hero_background %}` and `{% block hero_video %}`.

**Template blocks in `base.html`:**
- `{% block hero_background %}` — hero image URL
- `{% block hero_video %}` — video element or extra hero CSS
- `{% block navbar_bg %}` — inline style attribute on `<nav>` element (for per-page strip overrides)
- `{% block navbar_logo %}` — logo override
- `{% block content %}` — page body
- `{% block title %}` — page title
- `{% block meta_description %}` — SEO description

---

## Active Events (as of May 2026)

- **Brunch Ball V** — Sunday May 17, 2026 at Waldschänke Ciders, Denver. Ticket types: Player ($), Player + Brunch ($$), Spectator (free).
- **World Cup Block Party** — Coming soon teaser live on events page.
- **Sport Stable Monday Pickup** — Weekly, Superior CO, 6:15–8:15 PM
- **Scheitler Thursday Pickup** — Weekly, Denver CO, 6:15–8:15 PM (external registration via Denver Parks)

---

## Known Gotchas

1. **No collectstatic = no CSS changes** — Never edit `styles.css` expecting it to update without running collectstatic.
2. **Lambda cold starts** — First request after inactivity is slow. Not a bug.
3. **Database connection** — Neon serverless requires `CONN_MAX_AGE: 0` to avoid stale connections on Lambda.
4. **`django.contrib.sites`** — Not in `INSTALLED_APPS`, but `get_current_site()` is used in registration. Works but uses a fallback domain.
5. **Template blocks vs static CSS** — Never put critical styling in `styles.css` that needs per-page overrides. Use inline `<style>` blocks in templates.
6. **`APP_DIRS: True`** — Django looks for templates in `templates/` first, then app directories. No duplicate templates exist in app dirs.

---

## Future Feature Ideas (Suggested)

- **League management** — Seasons, standings, team rosters (hinted at on homepage)
- **Player dashboard** — View upcoming games, payment history, profile management
- **Admin game management** — Create/cancel pickup sessions from admin, auto-notify registered players
- **Waitlist system** — Cap game attendance, waitlist overflow
- **Referral system** — Invite friends, track who brought who into the community
- **Mobile app / PWA** — Community already has WhatsApp; a PWA could centralize game info
