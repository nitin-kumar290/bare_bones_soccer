# Changelog

A running log of site changes made through Claude Code, most recent first.

---

## 2026-07-30

Deployed live via `zappa update dev`. This deploy ships everything below plus the full 2026-07-26 entry further down (that one was written before testing/deploy — see it for the brand palette, nav rebuild, login redesign, and Game Catalog color migration).

### Nav (`templates/base.html`)
- **Home button**: moved from a standalone link next to the logo (site-wide, that placement didn't read as intended) into the main nav-links row, first item before Pickup — same list as Events/About/Contact on both desktop and mobile now, inheriting the same hover styling automatically.
- **"Bare Bones Soccer" wordmark hover**: added a Light Blue glow (`text-shadow`) on top of the existing scale-up hover effect.
- **Fonts are live**: self-hosted `Latienne Pro` (`LatienneEF-Medium.otf`, Medium weight — nav links, dropdown items, wordmark) and `Forma DJR Micro` (`FormaDJRMicro-Regular.ttf`, Regular weight — all other copy), pulled from Ian's Dropbox and added as `@font-face` rules in `base.html`, files stored at `myapp/static/fonts/`. Adjusted the CSS weight references (600→500, 300→400) to match the actual weights delivered rather than the aspirational ones guessed at earlier — only one weight per family exists right now, so bold/light variants would need additional files.
- **`.alert-info` message styling** (used for "You are now logged in!", "You have been logged out.", etc. site-wide): went through two passes — first a subtle light-blue-tinted transparent box, which turned out nearly invisible on dark pages like the login page (dark text on a barely-there tint against a dark background). Fixed to a solid Off White box with a Light Blue border, bold Light Blue text — reads clearly on any page background now.
- **Footer**: crest logo doubled to 192px (was too small to recognize), then all the surrounding spacing (container margin, crest margin, icon row gap/size) tightened twice in follow-up passes to compensate for the bigger logo pushing the footer's overall height up.

### Off White background sweep, round 2
- **Contact page**: root-caused why it still looked white after the original sweep — Bootstrap's own CSS sets `background-color: #fff` on `body` and loads *after* the inline site-wide rule in `base.html`, silently winning at equal specificity. Fixed by adding `!important` to the site-wide body rule (same fix applied to `.alert-info` for the same reason).
- **Partners page**: the visible sponsor-grid section was using an inline `style="background:#f8f9fa"` that the first sweep missed (the `.partners-section` CSS class I'd edited wasn't actually used anywhere in the page's HTML — dead code from an earlier version). Fixed the actual inline style.
- **Homepage**: opposite request — forced back to standard white (`body { background: #fff !important; }` inside `home.html`'s own style block, which loads after and wins over the sitewide Off White default) while keeping the bordered "card" elements that sit on top of it (`.home-content-card`) Off White. `.hbbm-section` (the photo carousel section) also reverted to white since it's a plain full-width section, not a card.

### Partners page (`templates/partners.html`)
- Removed the "Community Gallery — Coming Soon" placeholder block and its now-dead CSS.
- Added a small 32px Off White break between the inquiry form section and the footer.
- "The brands & organizations who help build Denver's soccer community:" forced to one line (`white-space: nowrap`, with a mobile fallback below 576px so it doesn't overflow small screens).
- Kize Concepts moved from last to second in the sponsor logo grid (right after Colorado Rapids).

### Game Catalog (`templates/series_catalog.html`)
- Added the same 32px Off White break between the hero and the dark header section that Partners got.
- Hero was pushing "Denver Soccer Games & Events" below the fold — reduced hero height (78vh → 65vh, briefly overcorrected to 52vh which cropped people's heads out of the photo, settled at 65vh) and shifted the crop point up (`background-position: center 40%` → `center 22%`) so the photo still frames properly at the shorter height. Trimmed the dark header's top padding too.

### Login page (`templates/login.html`)
- Scaled the entire dark panel (badge, heading, card, inputs, buttons — everything) down ~20% per Ian's request — badge 170px→136px, card 480px→384px, all internal fonts/padding reduced proportionally.
- "Forgot your username?" / "Forgot your password?" / "Don't have an account?" were hard to read at the smaller scale — bumped back up (0.75rem→0.95rem) and set to bold, with higher text opacity.

### Registration page (`templates/register.html`)
- Confirmation-email note reworded: "Once you finish account registration you will recieve an email confirmation..." → "*Once you register, you'll receive a confirmation email...", with "*Once you register" highlighted in bold Light Blue.

### Official brand palette established
- Confirmed via Ian's swatch sheet: **Royal Purple** `#290a44`, **Charcoal** `#08070b`, **Off White** `#fdf5ed`, **Light Blue** `#00b8e8`. Saved to project memory as the source of truth going forward. Legacy ad-hoc colors (`#65A2FC` blue, `#9b59f5` purple, `#0a1628`/`#0d1928` navy, `#dc3545` red, `#FFD700` gold) are being migrated out page by page.

### Site-wide (`templates/base.html`)
- **Favicon**: added the skull crest (`Primary Logo BK.png`) as `<link rel="icon">` + `apple-touch-icon`. It's black line art on a transparent background, so it may be hard to see in dark-themed browser tabs — flagged as a possible follow-up.
- **Nav — Home button**: added a "Home" link to the left of the logo, visible on desktop only (`d-none d-lg-inline-block`); mobile keeps its existing hamburger-menu Home link. Same Light Blue → Royal Purple hover/scale treatment as the rest of the nav.
- **Nav — logo lockup**: added "Bare Bones Soccer" as text next to the skull glyph (inline, side-by-side — not centered or stacked-under; those risked breaking the dropdown/mobile nav or needed a taller navbar for no real gain). Name hides below 576px to avoid nav crowding on small screens.
- **Nav — "Sign In to Play!" button**: recolored from the old purple (`#9b59f5`) to Light Blue at rest, Royal Purple on hover, matching the new palette.
- **Footer**: added the full circular crest logo (`Primary Logo BK.png`, 96px) above the icon row — the detailed seal now has a permanent home as a closing brand moment on every page, instead of being repeated as a section on every interior page (see below).
- **Removed the purple/blue gradient divider bar** (`.hero-divider`) that sat between the hero and page content on every page — flagged as visually jarring, especially once stacked against other gradient elements. Also removed a duplicate copy of the same divider that was hardcoded separately on the events page.
- **Off White sitewide**: `body { background: #fdf5ed; }` is now the site default (previously plain white, with only the login page opted in).
- **Fonts wired but blocked**: nav links + brand name now target `'Latienne Pro'` (falls back to Oswald), all other copy targets `'Forma DJR Micro'` (falls back to Barlow Semi Condensed/existing fonts). Both are commercial fonts with no free CDN embed — need either an Adobe Fonts kit ID (Forma DJR Micro, if Ian has a Creative Cloud plan) or purchased/self-hosted font files (Latienne Pro, sold by Process Type Foundry) before these actually render; site looks unchanged until then.

### Logo placement — several iterations, landed on: nav (compact) + footer (full crest) + login (hero moment) only
- Originally added a large circular badge in its own full-width section between the hero and page content on every page (`.page-logo-strip`), sized/tuned multiple times (110px → 170px, padding adjusted). Removed entirely after review — research on real comparable sites (MLS.com, VBFC, ZogSports) confirmed none of them repeat a logo section on every interior page; it was also pushing all real page content below the fold on every page. Removed from `home.html`, `events.html`, `series.html`, `series_catalog.html`, `schedule.html`, `partners.html`, `register.html`, `about.html`, and deleted the now-dead CSS from `base.html`.

### Login page (`templates/login.html`)
- Full redesign to a dark "stadium" theme: Charcoal → Royal Purple gradient panel (contained/rounded, max-width 1140px, floating on the new Off White page background rather than full-bleed — gives breathing room without recreating the old oversized white strip), glowing glass card with backdrop blur, dark-themed inputs with Light Blue focus glow, Light Blue → Royal Purple gradient submit button, Off White pulsing "Register Today" pill.
- Added the circular "Bare Bones Soccer Collective" crest badge (on an Off White plate, tightly cropped/scaled so there's minimal ring around the artwork) above the heading.
- Removed the duplicate "Sign In" h1 now that "Player Login" (promoted to `<h1>` for SEO) already conveys it.
- All copy: "Player Login" eyebrow / "Your spot in this week's games is one login away." subtitle, approved by Ian.

### Events page (`templates/events.html`)
- "Follow @barebonessoccer" button recolored from the old blue (`#65A2FC`) to Light Blue (with Charcoal text for contrast); secondary button/border switched to Off White.
- Added modest spacing (28px gap after the empty-state section, increased carousel top/bottom padding) so sections don't butt flush against each other — intentionally not a large gap.
- Carousel section background swept to Off White.

### Game Catalog (`templates/series_catalog.html`)
- Full color migration to the new 4-color palette, graphics/layout unchanged: dark header + featured/loop cards now use Charcoal → Royal Purple gradients (was old navy), accent bars/eyebrow/divider switched to Light Blue (was red), card text switched from pure white to Off White, cards section background switched from white to Off White, SVG divider fill updated to match.

### Other pages swept to Off White backgrounds
`about.html`, `home.html`, `partners.html`, and one shared rule in `myapp/static/css/styles.css` (`.title-section`, currently unused/commented out but updated for consistency).

---

## 2026-07-22

Not yet deployed — local changes only, pending a `zappa update dev` run.

### Site-wide (`templates/base.html` — applies to every page)
- **Logo swap**: replaced the old blue navbar logo (`logo_blue.png`) with the new skull glyph (`Primary Glyph W.png`, pulled straight from S3). The old logo used `mix-blend-mode: screen` to blend into the dark hero — wrong technique for the new white-on-transparent glyph, so it was dropped in favor of a `brightness(1.2)` filter applied at rest (previously only applied on hover, which is why the logo looked dim/grey normally and only "lit up" on hover). Hover state now also brightens further (`brightness(1.3)`) with a soft white glow (`drop-shadow`), and no longer dims the whole logo link to 85% opacity on hover (that opacity dip was fighting the "always white" look). Logo size increased ~15% (62px → 71px tall).
- **New circular badge** (`Primary Logo BK.png`, the "Bare Bones Soccer Collective" skull seal) added under the hero on every page, centered, settled at 195px × 195px on both desktop and mobile, with vertical padding for breathing room from both the hero above and content below.
- **Top nav strip**: background swapped from a dark `rgba(0,0,0,0.18)` overlay to a lighter `rgba(255,255,255,0.18)` — the dark strip was too dark for the new purple nav-link hover color to read against. Also thinned the strip's vertical padding (`.navbar` 15px→8px, `.custom-navbar` 12px→6px) so it takes up less real estate. Same background swap applied on `partners.html` and `series_catalog.html`, which each hardcode their own nav background (both a `<style>` override and a JS `DOMContentLoaded` override) instead of inheriting the base default.
- **Top nav link colors**: settled on blue `#00b8e8` at rest, brand purple `#290a44` on hover (site-wide).
- **Removed the World Cup Final announcement strip** entirely (the promo bar above the hero linking to the events page) — was still showing on every page except events/catalog, which had already blanked it out.

### Events page (`templates/events.html`)
- Removed the entire World Cup Final hero card, RSVP flow, post-RSVP donate section, and the now-orphaned `rsvpWCF()` JS function.
- Replaced it with a **"No Events Scheduled Right Now" empty state** — Instagram follow + "Join Weekly Pickup" CTAs — set against a real event photo (`Waldyevent1.jpeg`) with a dark navy overlay (tuned down to 0.6 opacity so the photo shows through more) and the crop position adjusted (`center 25%`) to keep people and the ball in frame.
- Copy fix: "we may open up more spots day-of" → "we will open up more spots day-of."
- Brightened the "PLAYER SPOTS FULL" badge and its supporting text — was styled washed-out/translucent (30–50% white opacity) by design for a "sold out" look; now solid gold badge with dark navy bold text, bold white supporting copy.

### Game Catalog (`templates/series_catalog.html`)
- Removed the World Cup Final featured card, replaced with a **"Stay In The Loop" card** (dark navy/gold styling matching the site's featured-card treatment) promoting Instagram and the WhatsApp group as the way to hear about the next event first.

### Homepage (`templates/home.html`)
- Replaced the World Cup Final homepage card with a new **"Events & Community"** card, built the same way as the existing "Weekly Pickup Soccer" card right above it (photo + heading/copy/button, mirrored left-right). Copy leans on the *By Soccer People, For Soccer People* slogan (italicized), covers "on the pitch and off it," and avoids naming a specific past event — written to read as evergreen/SEO-friendly rather than tied to the World Cup. Image: `waldyevent2.jpeg` (different photo than the ones already used on the events-page background and the homepage hero, so nothing repeats down the page). Removed ~150 lines of now-dead `hc-wcf-*`/`hc-now-*` CSS that only the old card used.

### Login page (`templates/login.html`)
- Wrapped the form in a centered white card (520px wide) instead of letting the username/password fields stretch full-container-width. Inputs restyled with rounded corners, padding, and a blue focus glow; labels restyled small/uppercase/grey instead of default bold black.
- The red "*A free account is required..." disclaimer was a single long line of bold uppercase red text stretching edge-to-edge — replaced with a compact bordered notice box (soft red background, smaller text) sized to the card.
- Submit button restyled from plain Bootstrap blue to a rounded brand-blue pill matching the site's other CTAs.

### Email — World Cup Series Follow-Up / Thank You (`docs/AWS_EMAILS.md`, doc-only, no standalone file in `email_templates/` per Ian's call this time)
- New follow-up/thank-you email for the Waldschänke World Cup play + watch series wrap-up. Copy broadened to thank anyone who joined "at any point during the World Cup run," not just Waldschänke regulars (though Waldschänke — ~90% of it — is still named first).
- Added a prominent navy/gold **sponsor callout** ("We couldn't run events at the level we do... without the people who back us") for Robin Gerlach and Bowman Law, positioned right after the WhatsApp CTA button. Added a smaller, bolded shoutout line underneath — with hover-enabled links — thanking New Friends Sports League and AthleteX for partnering and sharing their audience.
- Green WhatsApp-group CTA button; "not the end of fun events, just the beginning of our community" messaging.
- Photo row uses 4 real hand-picked images (both Waldschänke parking-lot pickup shots, the series winners photo, and the "By Soccer People, For Soccer People" shot last), each normalized to a uniform 140px height via `object-fit:cover` so they display consistently despite different source dimensions.

---

## 2026-07-14 (later — 2 more deploys)

Deployed live via two more `zappa update dev` runs (`https://barebonessoccer.com`).

### Site-wide (`templates/base.html` — applies to every page)
- Added a new World Cup Final promo strip above the hero on every page (built into the previously-empty `{% block announcement_bar %}` scaffold, last used for the World Cup Block Party weeks ago). Reads "🏆 WORLD CUP FINAL — PLAY + WATCH PARTY · SUN JULY 19" with a "VIEW DETAILS →" button linking to the events page; colors match the WCF card's purple/blue gradient and gold accent for consistency. Button has a glowing pulse animation and pops out (scales up) on hover. Hidden on the events page itself via a block override, since that page already has the full WCF card.
- Added the same gradient divider bar used on the events page (blue → dark purple) globally, right under the hero on every single page, for a consistent break between hero and body content. Removed the now-duplicate local copy that was only on events.html.
- The "About" nav dropdown (About Us / Sponsors & Partners) now opens on hover, not just click, site-wide.

### Partners page (`templates/partners.html`)
- Fixed the hero title ("Building Denver's Soccer Community...") rendering in a dark, hard-to-read color — it had no color set at all, defaulting to near-black against the black hero background. Now explicit white.
- Added Kize Concepts to the sponsor logo grid, linked to their site, using their real logo pulled directly from kizeconcepts.com (same hotlinking pattern already used for every other sponsor on that page).

### Events page (`templates/events.html`)
- Removed "Bare Bones Soccer Presents" eyebrow text from the World Cup Final card.

### Pickup/Series page (`templates/series.html`)
- Reduced the hero image height 20% (site default 90vh → 72vh).
- Added a new promo card under the Sport Stable card for the Broomfield/Westminster Saturday pickup, which can't be publicly advertised with details — instead promotes joining the WhatsApp group directly ("Join our WhatsApp community to see our Broomfield/Westminster Saturday pickup session — no registration, just come" / "JOIN BARE BONES WHATSAPP" button), styled with a WhatsApp-green accent to stand apart from the plain Sport Stable card. No schedule/location details are listed anywhere on the page — only the WhatsApp invite.

### WCF RSVP confirmation email (`myapp/views.py`, `register_wcf_rsvp`)
- Removed the date, pickup-time, watch-party-time, and food/drinks lines from the email body per Ian's request to simplify it.
- Removed the separate admin "New WCF RSVP — Total RSVPs: X/40" counter notification email entirely (was landing in the inbox). The player-facing confirmation email itself still automatically leaves a copy in the `soccerbarebones@gmail.com` Sent folder, which is the only signal Ian wants going forward for event signups — this pattern (no separate admin/counter email) applies to all future events too.

---

## 2026-07-14

Deployed live via `zappa update dev` (`https://barebonessoccer.com`).

### Events page — World Cup Final Party card (`templates/events.html`)
- RSVP CTA copy changed from "FREE RSVP — CLAIM YOUR SPOT →" to "RESERVE YOUR SPOT →".
- Added a bold gold "X/40 SPOTS FILLED" counter (styled as a pill/bubble) above the CTA, pulling the live `rsvp_count`; removed the old "X spots remaining · 40 max players" line.
- Moved the 11 AM / 1 PM schedule above the counter and reformatted from a 3-column boxed layout into clean centered stacked rows; dropped the separate "3 PM / Last Pickup Games" row and merged it into "11 AM - 3 PM / Pickup Soccer".
- Removed times from the feature pills (now just "⚽ PICKUP SOCCER", "📺 FREE WATCH PARTY", "🍺 FOOD & DRINKS ALL DAY") and from the date line ("SUNDAY · JULY 19", no time); removed the separate "🆓 FREE WATCH PARTY ENTRY" pill.
- Added more floating background flags (extra Spain/England/France/Argentina), trophy emojis, and a couple of soccer balls for a fuller background effect.
- Register/login note rewritten to "*Must have Bare Bones account to play. Register HERE" (HERE hyperlinked), moved to sit directly under the spots counter, and made bolder/more visible.
- **Donate section overhaul**: background changed from black to white (with every text color re-traced and updated for contrast — heading, subtitle, divider, handle, email were all originally tuned for a dark background); "Donate to Play!" heading now has a glowing pulse animation (blue) with a 👇 emoji; removed the "Venmo" label; the Venmo QR image had its baked-in "Bare Bones Soccer Collective" name/handle text and white card/shadow cropped out via a zoomed `background-image` technique (the card look was part of the source photo, not CSS); removed the divider line and the QR's white bordered wrapper for a cleaner "floating" look; replaced the previously-broken `zelle_logo.png` (confirmed dead, HTTP 403 from S3) with the newly-uploaded `zelle_logo-png.webp`, enlarged ~15%; row layout switched from flex to a 2-column grid so the Venmo handle and Zelle email line up on the same row regardless of image height differences; both handle and email are now bold and the same color.

### Registration page (`templates/register.html`, `myapp/forms.py`)
- Bolded and added an asterisk to "*Use a real email — you'll need it to activate your account."
- Removed the duplicate "Format: (123) 456-7890" hint text under the phone field, and removed the format-example placeholder from both the `phone` and `emergency_contact_phone` form fields — any format is now accepted with no prompt.

### Login page (`templates/login.html`)
- Added a missing `{% if messages %}` block — the view already generated messages (e.g. "we resent your activation link") but the template had nowhere to render them, so users saw the form reload with no feedback. No backend/logic changes, purely template rendering.

### Series/Pickup page (`templates/series.html`)
- Headline changed from "Bare Bones Soccer Series" to "Bare Bones Pickup Soccer".
- *(A URL rename from `/series/` to `/pickup/` was discussed but not applied — still live at `/series/`.)*

### SEO / meta tags (`templates/base.html` + site-wide)
- Fixed a second silent-block bug: `{% block meta_description %}` was defined by 6 page templates (about, partners, series, series_catalog, register, world_cup_block_party) but `base.html` never had a matching block to receive it, so **no page on the site has ever rendered a meta description tag**, live or local, despite that copy existing in the code for about a month. Added the missing block.
- Added Open Graph and Twitter Card meta tags site-wide (title/description/image/url), with per-page override blocks.
- Fixed invalid nested `<head><head>...</head></head>` markup in `base.html`.
- Wrote new meta descriptions for `home.html`, `events.html`, `schedule.html`, and `contact.html`, which previously had none.

### WCF RSVP confirmation email (`myapp/views.py`, `register_wcf_rsvp`)
- **Resolved** the item flagged below on 7/13: replaced the AWS SES-first send logic with the same plain Gmail SMTP `EmailMessage` pattern Brunch Ball already uses successfully (no SES at all now). Restored a missing "📅 Sunday, July 19, 2026" line in the email body. Old SES-based code preserved in Claude memory (`project_wcf_rsvp_email_fix.md`) in case of rollback.

---

## 2026-07-13

### Events page (`templates/events.html`)
- Replaced the static hero image with a looping background video (`Waldyjo.mp4`), muted/autoplay/no sound.
- Shortened the hero video height by 20% (85vh → 68vh) for a tighter banner.
- Removed the "Brunch Ball" promo block entirely (ticket cards + photo gallery) that sat beneath the World Cup Final section.
- Removed the "News" grid section.
- Added the "Bare Bones Moments" photo carousel (same component already live on the World Cup Block Party page) directly beneath the "Donate to Play!" section.
- Added simple gradient divider bars: above the World Cup Final section (below the hero), and above/below the "Donate to Play!" block — so each section reads as visually distinct instead of running together.

### Site-wide (`templates/base.html` — applies to every page)
- Added the missing `{% block hero_video %}` / `{% block hero_overlay %}` hooks to the base template. These were referenced by `partners.html` and documented in the design-system notes but never actually defined, so video-hero overrides were silently not rendering anywhere on the site. Now functional site-wide.
- Fixed the "About" nav dropdown: the `<ul class="dropdown-menu">` containing "About Us" and "Sponsors & Partners" had no toggle trigger wrapping it, so it could never open — the links existed in the HTML but were unreachable. Added a proper "About" nav-item with a Bootstrap `dropdown-toggle` trigger. Both the About page and the Partners/Sponsors page are reachable from the top nav again.
- Recolored top nav link text (Pickup, Events, Contact, Game Catalog, About/Sponsors dropdown items) from `#65A2FC` to the brand blue `#00b8e8`. Left the purple "Sign In to Play!" pill button untouched per Ian's direction.
- Recolored the footer background to `#00b8e8`.
- Removed the `@BAREBONESSOCCER` handle line from the footer.
- Footer tagline "By Soccer People, For Soccer People" — de-capitalized (was all-caps), made italic and bolder, with the leading "B" and "F" set in extra-bold black for emphasis.
- Thinned the footer's vertical padding.

### Partners page (`templates/partners.html`)
- Fixed the hero title/CTA ("Building Denver's Soccer Community Through Sponsorship, Collabs and Activations") rendering left-aligned instead of centered — the `.hero-overlay` div had no `position` set, so its centering offsets were being silently ignored. Added `position:absolute` with proper centering transform.

### Game Catalog (`templates/series_catalog.html`)
- Replaced the plain background-image "World Cup Events" card with a fully built featured event card (dark navy/red/gold styling that already existed unused in the page's CSS) showing date, time, venue, and a "EVENT DETAILS" CTA for the World Cup Final Party.
- Fixed card height mismatch with the neighboring Sport Stable card — row was using `align-items-center` (cards size to their own content) instead of `align-items-stretch` (cards match the tallest sibling). Switched to stretch + `h-100` on both cards so they now stay equal-height automatically.

### Static stylesheet (`myapp/static/css/styles.css`)
- Synced footer background and nav-link colors to match the base.html changes above (requires `collectstatic` to take effect on the deployed/S3-served version).

### Flagged, not yet fixed
- **WCF RSVP confirmation email** (`myapp/views.py:590`, `register_wcf_rsvp`) sends via AWS SES as its primary method before falling back to Gmail SMTP. This matches the exact failure pattern that caused prior Brunch Ball confirmation emails to silently fail (no SPF/DKIM on `barebonessoccer.com` for SES) — SES doesn't throw an error when this happens, so the fallback never triggers. Every other transactional email flow in the codebase was already migrated to Gmail SMTP (`EmailMessage`) directly; this one was missed. Awaiting go-ahead to apply the same fix.
