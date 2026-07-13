# home.html — two candidate versions (unresolved, for later review)

Found during the 2026-07-13 template restoration. Not resolved as part of that work — deferred by Ian for separate review.

## Currently installed (as of this restoration)

Source: VS Code Local History snapshot, `2026-07-09 16:20:29`
(`~/Library/Application Support/Code/User/History/28b3a361/QwoT.html`)

This matches the original restoration mapping's instruction ("home.html + WCF card from today, from VS Code history"). However, the Claude session transcripts show roughly 90 further edits to `templates/home.html` after this snapshot's timestamp, continuing from the evening of July 9 through July 13 — so this snapshot is known to be stale relative to later work.

WCF card in this version:
- Flags: 🇦🇷 🇪🇸 🇫🇷 🇬🇧
- Title: "World Cup Final Party"
- Body: a plain details list — 📍 location, 📅 date, ⚽ pickup/watch-party times
- Badge: "FREE WATCH PARTY · DONATE TO PLAY" (text only, no QR codes)
- Top CTA button: "View Event Details"

## Alternate version

Source: git commit `1b4c465` ("Restore WCF Final section on events page and homepage card"), committed 2026-07-13 09:20:42 — a manual repair made the same morning as the damage, before this restoration session started.

Retrieve with:
```
git show 1b4c465:templates/home.html
```

WCF card in this version:
- Flags: 🇧🇷 🇪🇸 🇫🇷 🇩🇪 🇦🇷 🇵🇹
- Title: "WORLD CUP FINAL PARTY"
- Date line: "SUNDAY · JULY 19 · 11AM–3PM"
- Features row: ⚽ PICKUP SOCCER · 📺 WATCH PARTY 1PM · 🍺 FOOD & DRINKS · 🆓 FREE ENTRY
- CTA: "RSVP FREE →"
- **Donate strip** (not present in the July 9 version at all): Venmo QR code (`@barebonessoccer`) and Zelle QR code (`soccerbarebones@gmail.com`), with real image assets already hosted on S3 (`bbs_venmo.jpeg`, `zelle_logo.png`)

The rest of the page also differs between the two versions — hero background image, the top hero CTA buttons ("Let's Play!" single button vs. "Log in!" / "Register!" two buttons), and some navbar-color CSS overrides. This suggests the July 9 snapshot predates a broader redesign pass that only shows up in the git-committed version.

## Recommendation (not acted on)

The `1b4c465` version is newer, more feature-complete (it's the only one with the working donate strip), and was a deliberate same-day fix — likely closer to what's actually "current." But this is Ian's call, not something to silently overwrite.
