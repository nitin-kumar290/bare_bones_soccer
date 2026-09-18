# AWS One-Off Emails

Archive of every one-off/blast email built for manual sending (AWS SES console, etc. — these are not sent automatically by the Django app). Most recent first. Corresponding standalone files also live in `email_templates/` for direct use/copy-paste.

To add a new one: tell Claude to "put this in the AWS email doc" after finishing a one-off email, and it gets appended here automatically.

---

## Footy League 6v6 Co-Ed Indoor Launch — Soccer Post Denver — 2026-09-15

Standalone file: `email_templates/denverfooty_6v6_coed_launch.html`.

One-off blast announcing the first indoor league, a 6v6 co-ed league run in partnership with Soccer Post Denver (725 S Jason St). Thursdays 6:30–9pm, first game October 1st, 8 games + playoffs, pro jerseys, trained refs. $648/team or $65/free agent, with early-bird and newsletter discounts. Flyer graphic (soccer_post_league.png) carries the pricing/specs. Two CTAs: a glowing green "CLAIM 20% DISCOUNT!" button linking to the Footy League newsletter signup (discount unlocked by joining), and a gold/navy "REGISTER TODAY!" button linking straight to the LeagueApps registration page. Standard unsubscribe footer.

```html
<!DOCTYPE html>
<html>
<head>
<style>
.cta-register:hover {
    box-shadow:0 0 30px 8px rgba(255,215,0,0.55), 0 6px 20px rgba(0,0,0,0.3) !important;
    transform:translateY(-2px);
}
.cta-register {
    transition:all 0.2s ease !important;
    display:inline-block;
}
.cta-discount:hover {
    box-shadow:0 0 34px 10px rgba(0,230,118,0.75), 0 6px 20px rgba(0,0,0,0.3) !important;
    transform:translateY(-2px);
}
.cta-discount {
    transition:all 0.2s ease !important;
    display:inline-block;
}
</style>
</head>
<body>

<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
<tr>
<td align="center">
<table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto; font-family:Arial, Helvetica, sans-serif; color:#111;">

<!-- Eyebrow -->
<tr>
<td style="padding:32px 20px 4px; text-align:center;">
<span style="font-size:11px; letter-spacing:3px; text-transform:uppercase; color:#0d1928; font-weight:900;">NEW INDOOR LEAGUE ❗</span>
</td>
</tr>

<!-- Header -->
<tr>
<td style="font-size:26px; line-height:34px; text-align:center; font-weight:bold; padding:6px 20px 14px; color:#08070b; white-space:nowrap;">
⚽ Our First Indoor League Is Here ⚽
</td>
</tr>

<!-- Intro -->
<tr>
<td style="font-size:16px; line-height:28px; text-align:center; padding:0 24px 28px; color:#444;">
We're adding a 6v6 co-ed indoor league, teamed up with <b>Soccer Post Denver</b>. Thursdays, 6:30&ndash;9pm, first game October 1st. Sign up by yourself, with friends, or as a full team &mdash; details below.
</td>
</tr>

<!-- Location -->
<tr>
<td style="font-size:14px; line-height:22px; text-align:center; padding:0 20px 14px; color:#0d1928; font-weight:bold;">
📍 Soccer Post Denver &mdash; 725 S Jason St, Denver, CO
</td>
</tr>

<!-- Flyer graphic -->
<tr>
<td style="padding:0 20px 28px;">
<img src="https://bare-bones-soccer.s3.amazonaws.com/images/soccer_post_league.png" alt="New 6v6 Co-ed League: 8 games + playoffs, professional jerseys, trained referees, good vibes. Thursdays 6:30-9pm, first game Oct 1st. $648/team or $65/free agent with early bird and newsletter discounts." width="100%" style="display:block; width:100%; max-width:560px; border-radius:10px; margin:0 auto;">
</td>
</tr>

<!-- Discount CTA -->
<tr>
<td align="center" style="padding:0 20px 36px;">
<p style="font-size:15px; line-height:24px; color:#111; margin:0 0 16px; font-weight:700;">🔥 SAVE 20% &mdash; use link to Join Footy League Newsletter before you register</p>
<a href="https://www.denverfooty.com/#:~:text=when%20it%20rains%3F-,Join%20Our%20Email%20List!,-Email"
   class="cta-discount"
   style="background:linear-gradient(135deg, #00e676 0%, #00b84f 100%); color:#08070b; font-size:17px; font-weight:bold; letter-spacing:1px; text-transform:uppercase; text-decoration:none; padding:16px 40px; border-radius:50px; box-shadow:0 0 24px 6px rgba(0,230,118,0.55), 0 6px 20px rgba(0,0,0,0.25);">
CLAIM 20% DISCOUNT!
</a>
</td>
</tr>

<!-- CTA -->
<tr>
<td align="center" style="padding:0 20px 36px;">
<a href="https://denverfooty.leagueapps.com/leagues/soccer-(indoor)/5141440-2026-fall--thursdays--denver-soccer-post--6v6-coed--p3"
   class="cta-register"
   style="background:linear-gradient(135deg, #0d1928 0%, #290a44 100%); color:#FFD700; font-size:17px; font-weight:bold; letter-spacing:1px; text-transform:uppercase; text-decoration:none; padding:16px 40px; border-radius:50px; box-shadow:0 0 22px 4px rgba(255,215,0,0.35), 0 6px 20px rgba(0,0,0,0.25);">
REGISTER TODAY!
</a>
</td>
</tr>

<!-- Closing -->
<tr>
<td style="font-size:15px; line-height:26px; text-align:center; padding:0 20px 28px;">
See you on the pitch,<br>
<b>— The Bare Bones Crew</b>
</td>
</tr>

<!-- Unsubscribe -->
<tr>
<td>
<p style="font-size:11px; color:#777; border-top:1px solid #eee; padding:10px 20px 20px; margin:0; text-align:center;">
You are receiving this email as a Bare Bones Soccer member. If you have received this email in error and/or no longer wish to receive email reminders, <a href="https://barebonessoccer.com/unsubscribe/" style="color:#777;">Unsubscribe</a>.
</p>
</td>
</tr>

</table>
</td>
</tr>
</table>

</body>
</html>
```

---

## Backyard 3v3 Tournament — Automated Registration Emails — 2026-09-06

**Note:** unlike everything else in this doc, these are not one-off/blast emails — they're sent automatically by the Django app (Gmail SMTP) at the moments described below, mirroring the same pattern as the Waldy Street League registration emails. Archived here per request for reference. Live in `myapp/views.py`.

### Captain confirmation — `send_tournament_captain_confirmation_email`
Fires right after the captain's Stripe payment succeeds. Branches on payment mode:
- **Individual pay-in**: confirms their own $20 spot, then hands them the team's private invite link in a copy-paste box to send to teammates (need 3–6 total, coed).
- **Team prepay**: confirms the full roster payment and lists out the named teammates, noting each will get their own claim email.

```html
<!DOCTYPE html>
<html>
<body>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
<tr>
    <td align="center" style="padding:0;">
    <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
        <tr>
        <td align="center" style="padding:24px;">
            <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">

            <tr>
                <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold; color:#290a44;">
                ⚽ BACKYARD 3V3 TOURNAMENT CONFIRMATION
                </td>
            </tr>

            <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>

            <tr>
                <td style="font-size:16px; line-height:24px; text-align:center;">
                    You're all set! Details below.
                </td>
            </tr>

            <!-- Individual pay-in path -->
            <tr>
                <td style="font-size:16px; padding:24px 24px 8px; text-align:center; line-height:26px;">
                💰 <b>$20 paid</b> — your spot is locked in<br>
                🧢 <b>Team:</b> {team.team_name}
                </td>
            </tr>
            <tr><td style="height:12px; line-height:12px;">&nbsp;</td></tr>
            <tr>
                <td style="padding:0 24px 8px; text-align:center;">
                <table role="presentation" align="center" cellspacing="0" cellpadding="0" style="border:1.5px solid #00b8e8; border-radius:10px; background:#f5fbfd;">
                    <tr>
                        <td style="padding:16px 20px; text-align:center; font-size:14px; line-height:22px;">
                        <b>Share this with your teammates:</b><br>
                        You need 3&ndash;6 players total, coed &mdash; each person pays their own $20 spot. Send them the link BELOW!<br><br>
                        <span style="font-family:monospace; font-size:13px; color:#08070b; background:#fff; border:1px solid #ddd; border-radius:6px; padding:8px 12px; display:inline-block; margin-top:4px; word-break:break-all;">{invite_link}</span>
                        <br><br>
                        <b>Copy &amp; paste to your teammates so they can sign up!</b>
                        </td>
                    </tr>
                </table>
                </td>
            </tr>

            <!-- OR team prepay path (replaces the block above) -->
            <!--
            <tr>
                <td style="font-size:16px; padding:24px; text-align:center; line-height:26px;">
                💰 <b>${team.prepaid_amount} paid</b> for {team.prepaid_roster_size} players<br>
                🧢 <b>Team:</b> {team.team_name}
                </td>
            </tr>
            <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>
            <tr>
                <td style="font-size:15px; padding:0 24px; text-align:center; line-height:24px;">
                <b>Your Roster:</b><br>{teammate names, one per line}
                </td>
            </tr>
            <tr><td style="height:14px; line-height:14px;">&nbsp;</td></tr>
            <tr>
                <td style="font-size:13px; padding:0 24px; text-align:center; line-height:20px; color:#555;">
                Each teammate above will get their own email to confirm their spot with a Bare Bones account &mdash; everyone needs one for game-day roster verification.
                </td>
            </tr>
            -->

            <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

            <tr>
                <td style="font-size:14px; padding:0 24px; line-height:22px; text-align:center; color:#555;">
                📅 See you <b>October 2nd</b> at Insight Soccer Training &mdash; start time and bracket will be posted soon.
                </td>
            </tr>

            <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

            <tr>
                <td style="font-size:16px; line-height:24px; text-align:center;">
                See you on the pitch!
                <br>
                The Bare Bones Crew
                </td>
            </tr>

            </table>
        </td>
        </tr>
    </table>
    </td>
</tr>
</table>

</body>
</html>
```

### Teammate claim link — `send_tournament_claim_email`
Sent to each named-but-unpaid roster spot on a team-prepay team, right after the captain's payment clears. Asks them to confirm their spot with a Bare Bones account.

```html
<!DOCTYPE html>
<html>
<body>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
<tr>
    <td align="center" style="padding:0;">
    <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
        <tr>
        <td align="center" style="padding:24px;">
            <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">

            <tr>
                <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold; color:#290a44;">
                ⚽ YOU'RE ON THE ROSTER
                </td>
            </tr>

            <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>

            <tr>
                <td style="font-size:16px; padding:0 24px; line-height:24px; text-align:center;">
                {first_name}, your captain already paid your $20 for <b>{team_name}</b> in the Backyard 3v3 Tournament. One last step &mdash; confirm your spot with a Bare Bones account so we can verify you on game day.
                </td>
            </tr>

            <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

            <tr>
                <td style="padding:0 24px; text-align:center;">
                <a href="{claim_link}" style="color:#fdf5ed; background:linear-gradient(135deg, #00b8e8 0%, #290a44 100%); padding:12px 28px; border-radius:50px; text-decoration:none; font-weight:bold; display:inline-block;">Confirm My Spot</a>
                </td>
            </tr>

            <tr><td style="height:16px; line-height:16px;">&nbsp;</td></tr>

            <tr>
                <td style="font-size:13px; padding:0 24px; line-height:20px; text-align:center; color:#555;">
                New account? Activate it via email first, then click this link again &mdash; logging in alone won't confirm your spot. Log in or create a free account.
                </td>
            </tr>

            <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

            <tr>
                <td style="font-size:14px; padding:0 24px; line-height:22px; text-align:center; color:#555;">
                📅 See you <b>October 2nd</b> at Insight Soccer Training &mdash; start time and bracket will be posted soon.
                </td>
            </tr>

            <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

            <tr>
                <td style="font-size:16px; line-height:24px; text-align:center;">
                See you on the pitch!
                <br>
                The Bare Bones Crew
                </td>
            </tr>

            </table>
        </td>
        </tr>
    </table>
    </td>
</tr>
</table>

</body>
</html>
```

### Teammate joined via invite link — `send_tournament_player_join_confirmation_email`
Sent to a teammate right after they pay their own $20 via a captain's shared invite link (individual pay-in path).

```html
<!DOCTYPE html>
<html>
<body>
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
<tr>
    <td align="center" style="padding:0;">
    <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto;">
        <tr>
        <td align="center" style="padding:24px;">
            <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; font-family:Arial, Helvetica, sans-serif; color:#111;">

            <tr>
                <td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold; color:#290a44;">
                ⚽ BACKYARD 3V3 TOURNAMENT CONFIRMATION
                </td>
            </tr>

            <tr><td style="height:8px; line-height:8px;">&nbsp;</td></tr>

            <tr>
                <td style="font-size:16px; line-height:24px; text-align:center;">
                    You're on the roster! Details below.
                </td>
            </tr>

            <tr>
                <td style="font-size:16px; padding:24px; text-align:center; line-height:26px;">
                💰 <b>$20 paid</b> — your spot is locked in<br>
                🧢 <b>Team:</b> {team_name}<br>
                👥 <b>Roster:</b> {roster_count}/6 paid
                </td>
            </tr>

            <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

            <tr>
                <td style="font-size:14px; padding:0 24px; line-height:22px; text-align:center; color:#555;">
                📅 See you <b>October 2nd</b> at Insight Soccer Training &mdash; start time and bracket will be posted soon.
                </td>
            </tr>

            <tr><td style="height:20px; line-height:20px;">&nbsp;</td></tr>

            <tr>
                <td style="font-size:16px; line-height:24px; text-align:center;">
                See you on the pitch!
                <br>
                The Bare Bones Crew
                </td>
            </tr>

            </table>
        </td>
        </tr>
    </table>
    </td>
</tr>
</table>

</body>
</html>
```

---

## Waldy Street League — Launch Announcement — 2026-08-25

Standalone file: `email_templates/waldy_street_league_launch.html`.

One-off blast to all accounts announcing the Waldy Street League. Excited "Heard the News?!" opener, quick league specs card (4v4, Wednesday nights 6:30–8:30 PM, starts 9/9, 18+ coed), pricing ($50 own way / $40 prepay), a one-line free agency mention, then a big glowing cyan/purple "Register Your Spot!" button linking straight to the live league page to let it do the rest of the selling. Three-photo row at the bottom (Waldygroup, Waldypickup, Waldypickup2). Standard unsubscribe footer.

```html
<!DOCTYPE html>
<html>
<head>
<style>
.cta-register:hover {
    box-shadow:0 0 30px 8px rgba(0,184,232,0.75), 0 6px 20px rgba(0,0,0,0.3) !important;
    transform:translateY(-2px);
}
.cta-register {
    transition:all 0.2s ease !important;
    display:inline-block;
}
</style>
</head>
<body>

<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
<tr>
<td align="center">
<table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto; font-family:Arial, Helvetica, sans-serif; color:#111;">

<!-- Eyebrow -->
<tr>
<td style="padding:32px 20px 4px; text-align:center;">
<span style="font-size:11px; letter-spacing:3px; text-transform:uppercase; color:#00b8e8; font-weight:900;">Heard the News?!</span>
</td>
</tr>

<!-- Header -->
<tr>
<td style="font-size:26px; line-height:34px; text-align:center; font-weight:bold; padding:6px 20px 14px; color:#08070b;">
⚽ Waldy Street League Is Here
</td>
</tr>

<!-- Intro -->
<tr>
<td style="font-size:16px; line-height:28px; text-align:center; padding:0 24px 28px; color:#444;">
Denver's newest street soccer league is kicking off at <b>Waldschänke Ciders</b> — 4v4, under the lights, with $5 cider pours and a patio full of your new favorite Wednesday night. Grab your squad (or don't — we'll explain) and get in before spots are gone.
</td>
</tr>

<!-- League details card -->
<tr>
<td style="padding:0 20px 28px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:linear-gradient(135deg, #08070b 0%, #290a44 100%); border-radius:14px;">
<tr>
<td style="padding:26px 24px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0">
<tr>
<td width="50%" style="padding:8px 6px; text-align:center; vertical-align:top;">
<div style="font-size:20px; font-weight:bold; color:#fdf5ed;">4v4</div>
<div style="font-size:11px; letter-spacing:1px; text-transform:uppercase; color:rgba(253,245,237,0.6); margin-top:2px;">On the Court</div>
</td>
<td width="50%" style="padding:8px 6px; text-align:center; vertical-align:top;">
<div style="font-size:20px; font-weight:bold; color:#fdf5ed;">Wed Nights</div>
<div style="font-size:11px; letter-spacing:1px; text-transform:uppercase; color:rgba(253,245,237,0.6); margin-top:2px;">6:30&ndash;8:30 PM</div>
</td>
</tr>
<tr>
<td width="50%" style="padding:8px 6px; text-align:center; vertical-align:top;">
<div style="font-size:20px; font-weight:bold; color:#00b8e8;">Starts 9/9</div>
<div style="font-size:11px; letter-spacing:1px; text-transform:uppercase; color:rgba(253,245,237,0.6); margin-top:2px;">7&ndash;8 Week Season</div>
</td>
<td width="50%" style="padding:8px 6px; text-align:center; vertical-align:top;">
<div style="font-size:20px; font-weight:bold; color:#fdf5ed;">18+ &middot; Coed</div>
<div style="font-size:11px; letter-spacing:1px; text-transform:uppercase; color:rgba(253,245,237,0.6); margin-top:2px;">1 Female Player Req'd</div>
</td>
</tr>
</table>
</td>
</tr>
</table>
</td>
</tr>

<!-- Pricing -->
<tr>
<td style="font-size:15px; line-height:26px; text-align:center; padding:0 28px 8px; color:#222;">
💰 <b>$50/player</b> on your own, or <b>$40/player</b> when you prepay your whole team (5&ndash;8 players).
</td>
</tr>

<!-- Free agency -->
<tr>
<td style="font-size:15px; line-height:26px; text-align:center; padding:0 28px 32px; color:#555;">
Don't have a full team? No problem — <b>join as a free agent</b> and we'll place you on a roster with an open spot.
</td>
</tr>

<!-- CTA -->
<tr>
<td align="center" style="padding:0 20px 36px;">
<a href="https://barebonessoccer.com/leagues/waldy-street-league/"
   class="cta-register"
   style="background:linear-gradient(135deg, #00b8e8 0%, #290a44 100%); color:#fdf5ed; font-size:17px; font-weight:bold; letter-spacing:1px; text-transform:uppercase; text-decoration:none; padding:16px 40px; border-radius:50px; box-shadow:0 0 22px 4px rgba(0,184,232,0.55), 0 6px 20px rgba(0,0,0,0.25);">
Register Your Spot!
</a>
</td>
</tr>

<!-- Photo row -->
<tr>
<td style="padding:0 20px 8px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0">
<tr>
<td width="33.33%" style="padding:3px;">
    <img src="https://bare-bones-soccer.s3.amazonaws.com/images/Waldygroup.JPEG" alt="Waldy Street League group" width="100%" height="180" style="display:block; border-radius:8px; width:100%; height:180px; object-fit:cover;">
</td>
<td width="33.33%" style="padding:3px;">
    <img src="https://bare-bones-soccer.s3.amazonaws.com/images/Waldypickup.JPG" alt="Waldy Street League pickup" width="100%" height="180" style="display:block; border-radius:8px; width:100%; height:180px; object-fit:cover;">
</td>
<td width="33.33%" style="padding:3px;">
    <img src="https://bare-bones-soccer.s3.amazonaws.com/images/Waldypickup2.JPG" alt="Waldy Street League pickup" width="100%" height="180" style="display:block; border-radius:8px; width:100%; height:180px; object-fit:cover;">
</td>
</tr>
</table>
</td>
</tr>

<!-- Closing -->
<tr>
<td style="font-size:15px; line-height:26px; text-align:center; padding:28px 20px 28px;">
See you on the pitch,<br>
<b>— Bare Bones Soccer</b>
</td>
</tr>

<!-- Unsubscribe -->
<tr>
<td>
<p style="font-size:11px; color:#777; border-top:1px solid #eee; padding:10px 20px 20px; margin:0; text-align:center;">
You are receiving this email as a Bare Bones Soccer member. If you have received this email in error and/or no longer wish to receive email reminders, <a href="https://barebonessoccer.com/unsubscribe/" style="color:#777;">Unsubscribe</a>.
</p>
</td>
</tr>

</table>
</td>
</tr>
</table>

</body>
</html>
```

---

## World Cup Series Follow-Up — Thank You — 2026-07-22

Doc-only entry, no standalone file in `email_templates/`.

Follow-up/thank-you email for the World Cup play + watch series wrapping up (primarily Waldschänke, ~90% of it, but worded to cover anyone who joined anywhere during the World Cup run). Includes a 3-photo static row (not a real carousel — those don't render in Gmail/Outlook) with placeholder `src` values for Ian to swap in hand-picked photos. Message: this isn't the end of fun events, just the beginning of the community, more news coming, stuff happening behind the scenes. Green WhatsApp-group CTA button. Prominent navy/gold sponsor callout ("couldn't do this without them") for Robin Gerlach and Bowman Law, plus a brief shoutout line for New Friends Sports League and AthleteX.

```html
<!DOCTYPE html>
<html>
<head>
<style>
.cta-whatsapp:hover {
    background-color:#1da851 !important;
    box-shadow:0 0 26px 6px rgba(37,211,102,0.65), 0 6px 20px rgba(0,0,0,0.3) !important;
    transform:translateY(-2px);
}
.cta-whatsapp {
    transition:all 0.2s ease !important;
    display:inline-block;
}
.shoutout-link:hover {
    color:#FFD700 !important;
    text-decoration:underline !important;
}
.shoutout-link {
    transition:color 0.2s ease !important;
}
</style>
</head>
<body>

<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
<tr>
<td align="center">
<table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto; font-family:Arial, Helvetica, sans-serif; color:#111;">

<!-- Header -->
<tr>
<td style="font-size:20px; line-height:28px; text-align:center; font-weight:bold; padding:24px 10px 6px;">
⚽🏆 Thank You, Bare Bones Community!
</td>
</tr>

<!-- Intro -->
<tr>
<td style="font-size:16px; line-height:26px; text-align:center; padding:0 20px 24px; color:#444;">
The Waldschänke World Cup play + watch series is officially in the books — and whether you were there every week or just came out to join us at any point during the World Cup run, thank you for being part of it.
</td>
</tr>

<!-- PHOTO GRID (2x2 — static, most compatible across email clients) -->
<tr>
<td style="padding:0 20px 8px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0">
<tr>
<td width="50%" style="padding:3px;">
    <img src="https://bare-bones-soccer.s3.amazonaws.com/images/Waldyparkinglot.jpeg" alt="Waldschänke parking lot pickup soccer" width="100%" height="260" style="display:block; border-radius:6px; width:100%; height:260px; object-fit:cover;">
</td>
<td width="50%" style="padding:3px;">
    <img src="https://bare-bones-soccer.s3.amazonaws.com/images/Waldyparkinglot2.jpeg" alt="Waldschänke parking lot pickup soccer" width="100%" height="260" style="display:block; border-radius:6px; width:100%; height:260px; object-fit:cover;">
</td>
</tr>
<tr>
<td width="50%" style="padding:3px;">
    <img src="https://bare-bones-soccer.s3.amazonaws.com/images/Waldywinners.jpeg" alt="Waldschänke World Cup series winners" width="100%" height="260" style="display:block; border-radius:6px; width:100%; height:260px; object-fit:cover;">
</td>
<td width="50%" style="padding:3px;">
    <img src="https://bare-bones-soccer.s3.amazonaws.com/images/bysoccerpeople_forsoccerpeople.JPG" alt="By Soccer People, For Soccer People" width="100%" height="260" style="display:block; border-radius:6px; width:100%; height:260px; object-fit:cover;">
</td>
</tr>
</table>
</td>
</tr>

<!-- SPACER -->
<tr><td style="height:28px;"></td></tr>

<!-- BODY -->
<tr>
<td style="font-size:15px; line-height:26px; padding:0 28px; text-align:left; color:#555;">
But don't call this goodbye — this isn't the end of fun events, it's just the beginning of our community.<br><br>
We've got plenty more news to look forward to, and there's a lot happening behind the scenes right now that we can't wait to share. Stay tuned.
</td>
</tr>

<!-- SPACER -->
<tr><td style="height:24px;"></td></tr>

<!-- WHATSAPP CTA -->
<tr>
<td style="background:#0d1928; text-align:center; padding:28px 20px; border-radius:10px;">
<p style="font-size:15px; line-height:24px; color:rgba(255,255,255,0.85); margin:0 0 16px;">Want to be first to hear what's next? Join the community group.</p>
<a href="https://chat.whatsapp.com/IzHQHb1UODABuoABqXotvm" class="cta-whatsapp" style="background-color:#25D366; color:#0d1928; padding:16px 44px; text-decoration:none; font-size:17px; font-weight:bold; border-radius:6px; display:inline-block; box-shadow:0 0 22px 5px rgba(37,211,102,0.45), 0 6px 20px rgba(0,0,0,0.3);">💬 JOIN OUR WHATSAPP →</a>
</td>
</tr>

<!-- SPACER -->
<tr><td style="height:24px;"></td></tr>

<!-- SPONSOR CALLOUT -->
<tr>
<td style="padding:0 20px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#0d1928; border-radius:14px;">
<tr>
<td style="text-align:center; padding:28px 24px;">
<p style="font-size:11px; letter-spacing:2.5px; text-transform:uppercase; color:#FFD700; font-weight:900; margin:0 0 10px;">A Real Thank You</p>
<p style="font-size:16px; line-height:26px; color:#fff; margin:0 0 20px; font-weight:700;">We couldn't run events at the level we do — parking lot pickup, watch parties, prizes and all — without the people who back us.</p>
<p style="font-size:15px; line-height:28px; color:rgba(255,255,255,0.9); margin:0;">
<a href="https://www.instagram.com/robin.gerlach/" style="color:#FFD700; font-weight:bold; text-decoration:none;">Robin Gerlach</a> — your Denver footy realtor<br>
303 957 6397 for all homebuying needs<br>
<a href="https://coloradopersonalinjuryhelp.com/" style="color:#FFD700; font-weight:bold; text-decoration:none;">Bowman Law Personal Injury Firm</a>
</p>
<p style="font-size:12px; line-height:20px; color:rgba(255,255,255,0.55); margin:16px 0 0;">
Thanks to <a href="https://www.instagram.com/newfriendssportsleague/" class="shoutout-link" style="color:rgba(255,255,255,0.85); font-weight:bold; text-decoration:none;"><b>New Friends Sports League</b></a> and <a href="https://www.instagram.com/athletex.official/" class="shoutout-link" style="color:rgba(255,255,255,0.85); font-weight:bold; text-decoration:none;"><b>AthleteX</b></a> for partnering with us and sharing your audience.
</p>
</td>
</tr>
</table>
</td>
</tr>

<!-- SPACER -->
<tr><td style="height:24px;"></td></tr>

<!-- CLOSING -->
<tr>
<td style="font-size:17px; line-height:30px; text-align:center; padding:0 20px 24px;">
<b>Thanks for being part of this — here's to what's next.</b> 🏆<br><br>
<b>— The Bare Bones Crew</b>
</td>
</tr>

<!-- UNSUBSCRIBE -->
<tr>
<td>
<p style="font-size:11px; color:#777; border-top:1px solid #eee; padding:10px 20px 20px; margin:0; text-align:center;">
You are receiving this email as a Bare Bones Soccer member. If you have received this email in error and/or no longer wish to receive email reminders, <a href="https://barebonessoccer.com/unsubscribe/" style="color:#777;">Unsubscribe</a>.
</p>
</td>
</tr>

</table>
</td>
</tr>
</table>

</body>
</html>
```

---

## World Cup Final Reminder Blast — 2026-07-16

File: `email_templates/wcf_final_reminder_blast.html`

Reminder email for the World Cup Final Party (Sunday, July 19). Covers pickup soccer (11AM–3PM), patio watch party (TVs, kickoff at 1PM), free/no-ticket watch party, donation-based pickup, prizes. Glowing gold CTA button linking to the events page to RSVP a player spot. Venmo/Zelle donate block (same as the RSVP confirmation email) sits right under the CTA, with a short standalone note below it about pickup possibly running long. Sponsor mentions for Robin Gerlach and Bowman Law. No photo — just the styled navy/gold event details block for now.

```html
<!DOCTYPE html>
<html>
<head>
<style>
.cta-rsvp:hover {
    background-color:#ffe033 !important;
    box-shadow:0 0 26px 6px rgba(255,215,0,0.85), 0 6px 20px rgba(0,0,0,0.3) !important;
    transform:translateY(-2px);
}
.cta-rsvp {
    transition:all 0.2s ease !important;
    display:inline-block;
}
</style>
</head>
<body>

<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
<tr>
<td align="center">
<table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto; font-family:Arial, Helvetica, sans-serif; color:#111;">

<!-- Header -->
<tr>
<td style="font-size:20px; line-height:28px; text-align:center; font-weight:bold; padding:24px 10px 6px;">
⚽🏆 World Cup Final — This Sunday!
</td>
</tr>

<!-- Intro -->
<tr>
<td style="font-size:16px; line-height:26px; text-align:center; padding:0 20px 24px; color:#444;">
Don't miss it — the whole day of pickup soccer, patio watch party and community energy, all in one spot.
</td>
</tr>

<!-- EVENT HEADER STRIPE -->
<tr>
<td style="background:#0d1928; padding:16px 20px; text-align:center; border-radius:10px 10px 0 0;">
<span style="font-size:11px; letter-spacing:3px; text-transform:uppercase; color:#FFD700; font-weight:bold;">🏆 This Sunday · July 19</span>
</td>
</tr>

<!-- EVENT TITLE -->
<tr>
<td style="background:#0d1928; padding:4px 20px 16px; text-align:center;">
<div style="font-size:22px; line-height:30px; font-weight:bold; color:#fff;">World Cup Final Party</div>
<div style="font-size:14px; padding-top:4px;">📍 <b style="color:#fff;">Waldschänke Ciders · 4100 Jason St</b></div>
</td>
</tr>

<!-- EVENT DETAILS -->
<tr>
<td style="background:#111e3a; padding:20px 24px; text-align:center; font-size:16px; line-height:34px; color:rgba(255,255,255,0.85);">
⚽ <b style="color:#fff;">4v4 Parking Lot Pickup: 11AM - 3PM</b><br>
📺 <b style="color:#fff;">Watch Party — TVs on the Patio, Kickoff at 1 PM</b><br>
🆓 <b style="color:#FFD700;">Watch Party FREE</b> and open to everyone — no ticket needed<br>
💰 <b style="color:#fff;">Pickup is donation based</b><br>
🎁 <b style="color:#FFD700;">We'll have prizes!</b>
</td>
</tr>

<!-- CTA -->
<tr>
<td style="background:#0d1928; text-align:center; padding:20px 20px 32px; border-radius:0 0 10px 10px;">
<a href="https://barebonessoccer.com/events/" class="cta-rsvp" style="background-color:#FFD700; color:#0d1928; padding:16px 44px; text-decoration:none; font-size:17px; font-weight:bold; border-radius:6px; display:inline-block; box-shadow:0 0 22px 5px rgba(255,215,0,0.65), 0 6px 20px rgba(0,0,0,0.3);">🏆 RESERVE YOUR PLAYER SPOT →</a>
</td>
</tr>

<!-- SPACER -->
<tr><td style="height:28px;"></td></tr>

<!-- DONATE SECTION -->
<tr>
<td style="padding:0 20px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f8f8f8; border-radius:10px;">
<tr>
<td style="text-align:center; padding:20px 16px;">
<p style="font-size:18px; font-weight:bold; margin:0 0 18px 0; letter-spacing:1px; color:#111;">Support the Community — Donate What You Want</p>

<!-- Venmo -->
<p style="font-size:15px; font-weight:bold; color:#3D95CE; margin:0 0 8px 0; letter-spacing:1px;">VENMO</p>
<img src="https://bare-bones-soccer.s3.amazonaws.com/images/bbs_venmo.jpeg" alt="Venmo QR Code" width="180" height="180" style="display:block; margin:0 auto 8px; border-radius:8px;">
<p style="font-size:15px; font-weight:bold; color:#3D95CE; margin:0 0 20px 0;">@barebonessoccer</p>

<!-- Divider -->
<table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr><td style="height:1px; background:#ddd; font-size:0; line-height:0;">&nbsp;</td></tr></table>

<!-- Zelle -->
<p style="font-size:15px; font-weight:bold; color:#9b59f5; margin:16px 0 4px 0; letter-spacing:1px;">ZELLE</p>
<p style="font-size:14px; color:#444; margin:0;">soccerbarebones@gmail.com</p>
</td>
</tr>
</table>
</td>
</tr>

<!-- SPACER -->
<tr><td style="height:24px;"></td></tr>

<!-- BODY -->
<tr>
<td style="font-size:15px; line-height:26px; padding:0 28px; text-align:left; color:#555;">
If people are still going when the final whistle blows, don't be surprised if it runs a little longer 😉<br><br>
Grab a seat on the patio for the match, jump in on the parking lot games, or do both. Food &amp; drinks available all day.<br><br>
<i style="text-align:center; display:block;">No team needed. Come solo or bring the whole crew.</i>
</td>
</tr>

<!-- SPACER -->
<tr><td style="height:24px;"></td></tr>

<!-- CLOSING -->
<tr>
<td style="font-size:17px; line-height:30px; text-align:center; padding:0 20px 24px;">
<b>One match. One party. Let's fill that pitch and that patio.</b> 🏆<br><br>
See you Sunday 🙌<br>
<b>— The Bare Bones Crew</b>
</td>
</tr>

<!-- SPONSORS -->
<tr>
<td style="padding:0 20px 8px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0">
<tr>
<td style="border-top:1px solid #eee; padding-top:20px; text-align:center;">
<span style="font-size:10px; letter-spacing:2.5px; text-transform:uppercase; color:#111; font-weight:900;">This Event Is Proudly Sponsored By</span>
</td>
</tr>
</table>
</td>
</tr>
<tr>
<td style="font-size:14px; line-height:26px; text-align:center; padding:8px 20px 24px; color:#555;">
<a href="https://www.instagram.com/robin.gerlach/" style="color:#8B0000; font-weight:bold; text-decoration:none;">Robin Gerlach</a> — your local footy realtor<br>
<a href="https://coloradopersonalinjuryhelp.com/" style="color:#8B0000; font-weight:bold; text-decoration:none;">Bowman Law Personal Injury Firm</a>
</td>
</tr>

<!-- UNSUBSCRIBE -->
<tr>
<td>
<p style="font-size:11px; color:#777; border-top:1px solid #eee; padding:10px 20px 20px; margin:0; text-align:center;">
You are receiving this email as a Bare Bones Soccer member. If you have received this email in error and/or no longer wish to receive email reminders, <a href="https://barebonessoccer.com/unsubscribe/" style="color:#777;">Unsubscribe</a>.
</p>
</td>
</tr>

</table>
</td>
</tr>
</table>

</body>
</html>
```

---

## World Cup Play & Watch — Full Event Calendar Launch — 2026-06-22

File: `email_templates/waldy_series_launch.html`

Launch announcement for the recurring "World Cup Play & Watch" series at Waldschänke — weekly street pickup + watch party all summer, pay-what-you-want on site, 32 player spots, account required to play. Includes Robin Gerlach sponsor spot and a "Homebuying Tip of the Month" section.

```html
<!DOCTYPE html>
<html>
<head>
<style>
.cta-main:hover {
    background-color:#1a9e4a !important;
    box-shadow:0 0 18px 4px rgba(30,180,80,0.6), 0 6px 20px rgba(0,0,0,0.3) !important;
    transform:translateY(-2px);
}
.cta-main {
    transition:all 0.2s ease !important;
    display:inline-block;
}
</style>
</head>
<body>

<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
<tr>
<td align="center">
<table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto; font-family:Arial, Helvetica, sans-serif; color:#111;">

<!-- Header -->
<tr>
<td style="font-size:22px; line-height:32px; text-align:center; font-weight:bold; padding:32px 20px 10px;">
⚽ World Cup Play &amp; Watch — The Full Event Calendar at Waldschänke Ciders
</td>
</tr>

<!-- Intro -->
<tr>
<td style="font-size:16px; line-height:28px; text-align:center; padding:0 24px 32px; color:#444;">
World Cup summer doesn't stop and we're back for more. Weekly <b>street pickup soccer in the parking lot</b> followed by <b>watch party</b> — all at Waldschänke Ciders in Sunnyside. <b>Pay what you want on site (Venmo, Zelle, Cash).</b> No team needed. 32 player spots per pickup. *Must have a <a href="https://barebonessoccer.com/register/" style="color:#1e8c3a; font-weight:bold; text-decoration:none;">Bare Bones account</a> to play* — watch parties are FREE to attend!
</td>
</tr>

<!-- Graphic -->
<tr>
<td align="center" style="padding:0 16px 32px;">
    <img src="https://bare-bones-soccer.s3.amazonaws.com/images/waldyevents.jpeg"
         width="560"
         style="display:block; width:100%; max-width:560px; border-radius:12px; box-shadow:0 6px 24px rgba(0,0,0,0.15);"
         alt="World Cup Play & Watch Event Schedule at Waldschänke Ciders" />
</td>
</tr>

<!-- Details -->
<tr>
<td style="font-size:16px; line-height:30px; text-align:center; padding:0 24px 12px; color:#222;">
📍 <b>Waldschänke Ciders — 4100 Jason St, Denver</b>
</td>
</tr>
<tr>
<td style="font-size:15px; line-height:28px; text-align:center; padding:0 28px 32px; color:#555;">
Kick around before the game, then catch every match on the big screen. Come solo or bring the crew — there's a spot for everyone. <b>Pay what you can, play what you want.</b>
</td>
</tr>

<!-- Closing -->
<tr>
<td style="font-size:16px; line-height:28px; text-align:center; padding:0 20px 28px;">
See you out there,<br>
<b>— Bare Bones Soccer</b>
</td>
</tr>

<!-- Sponsors -->
<tr>
<td style="padding:0 20px 8px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0">
<tr>
<td style="border-top:1px solid #eee; padding-top:20px; text-align:center;">
<span style="font-size:10px; letter-spacing:2.5px; text-transform:uppercase; color:#111; font-weight:900;">These Events Are Proudly Sponsored By</span>
</td>
</tr>
</table>
</td>
</tr>
<tr>
<td style="font-size:14px; line-height:26px; text-align:center; padding:8px 20px 24px; color:#555;">
<a href="https://www.instagram.com/robin.gerlach/" style="color:#1e8c3a; font-weight:bold; text-decoration:none;">Robin Gerlach</a> — your local footy realtor
</td>
</tr>

<!-- Robin's Tip -->
<tr>
<td style="padding:0 20px 8px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0">
<tr>
<td style="border-top:1px solid #eee; padding-top:20px; text-align:center;">
<span style="font-size:10px; letter-spacing:2.5px; text-transform:uppercase; color:#111; font-weight:900;">🏡 Robin's Homebuying Tip of the Month</span>
</td>
</tr>
</table>
</td>
</tr>
<tr>
<td style="font-size:14px; line-height:24px; text-align:left; padding:10px 24px 28px; color:#555;">
<b style="color:#111;">Shop homeowners insurance early.</b> Colorado homeowners insurance has increased over 40% in the last 4 years and continues to rise — driven by the Louisville/Superior fires in 2021 and ongoing wind and hail claims. If the roof on a home you're considering is over 10 years old, your insurance premium could be as much as 50% higher. Know the insurance costs for your target area and home style before you fall in love with a listing.<br><br>
<a href="https://www.instagram.com/robin.gerlach/" style="color:#1e8c3a; font-weight:bold; text-decoration:none;">Follow Robin on Instagram →</a>
</td>
</tr>

<!-- Unsubscribe -->
<tr>
<td>
<p style="font-size:11px; color:#777; border-top:1px solid #eee; padding:10px 20px 20px; margin:0; text-align:center;">
You are receiving this email as a Bare Bones Soccer member. If you have received this email in error and/or no longer wish to receive email reminders, <a href="https://barebonessoccer.com/unsubscribe/" style="color:#777;">Unsubscribe</a>.
</p>
</td>
</tr>

</table>
</td>
</tr>
</table>

</body>
</html>
```

---

## World Cup Schedule Blast — 2026-06-21

File: `email_templates/waldyschedule_blast.html`

Weekly schedule update highlighting the next match (USA vs Turkey, June 25) plus a full round-by-round table through the Final (July 19). CTA links to the full events page.

```html
<!DOCTYPE html>
<html>
<head>
<style>
.cta-main:hover {
    background-color:#1a9e4a !important;
    box-shadow:0 0 18px 4px rgba(30,180,80,0.6), 0 6px 20px rgba(0,0,0,0.3) !important;
    transform:translateY(-2px);
}
.cta-main {
    transition:all 0.2s ease !important;
    display:inline-block;
}
</style>
</head>
<body>

<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
<tr>
<td align="center">
<table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto; font-family:Arial, Helvetica, sans-serif; color:#111;">

<!-- Header -->
<tr>
<td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold; padding:28px 10px 6px; white-space:nowrap;">
⚽🌍 World Cup Play &amp; Watch — We're Doing It All
</td>
</tr>

<!-- Intro -->
<tr>
<td style="font-size:16px; line-height:26px; text-align:center; padding:0 20px 24px; color:#444;">
The World Cup is here and we're running the full schedule at Waldschänke Ciders. Pickup soccer, watch parties, and the whole community — every round through the Final.
</td>
</tr>

<!-- Graphic -->
<tr>
<td align="center" style="padding:0 16px 28px;">
    <img src="https://bare-bones-soccer.s3.amazonaws.com/images/waldyevents.jpeg"
         width="560"
         style="display:block; width:100%; max-width:560px; border-radius:12px; box-shadow:0 6px 24px rgba(0,0,0,0.15);"
         alt="World Cup Event Schedule at Waldschänke Ciders" />
</td>
</tr>

<!-- Highlight — USA vs Turkey -->
<tr>
<td style="background:#0d1928; padding:20px 24px; text-align:center; border-radius:10px 10px 0 0;">
<span style="font-size:11px; letter-spacing:3px; text-transform:uppercase; color:#FFD700; font-weight:bold;">⚽ Up Next · This Wednesday</span>
</td>
</tr>
<tr>
<td style="background:#111e3a; padding:20px 24px; text-align:center; font-size:16px; line-height:34px; color:rgba(255,255,255,0.85);">
🇺🇸 <b style="color:#fff; font-size:18px;">USA vs Turkey — June 25</b><br>
⚽ <b style="color:#FFD700;">Pickup: 6:00 PM</b><br>
📺 <b style="color:#FFD700;">Watch Party: 8:00 PM</b><br>
📍 <b style="color:#fff;">Waldschänke Ciders — 4100 Jason St, Denver</b>
</td>
</tr>
<tr>
<td style="background:#0d1928; font-size:15px; line-height:26px; padding:16px 28px; color:rgba(255,255,255,0.75); text-align:left; border-radius:0 0 10px 10px;">
Come early for pickup and stay for the watch party. The US plays Turkey on Wednesday — don't miss it with the crew.<br><br>
<i style="display:block; text-align:center;">No team needed. Come solo or bring the squad.</i>
</td>
</tr>

<!-- Spacer -->
<tr><td style="height:32px;"></td></tr>

<!-- Divider -->
<tr>
<td style="padding:0 20px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0">
<tr>
<td style="border-top:2px solid #eee; text-align:center; padding-top:18px;">
<span style="font-size:11px; letter-spacing:3px; text-transform:uppercase; color:#111; font-weight:bold;">The Full Schedule</span>
</td>
</tr>
</table>
</td>
</tr>

<!-- Spacer -->
<tr><td style="height:20px;"></td></tr>

<!-- Schedule Table -->
<tr>
<td style="padding:0 20px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="font-family:Arial, Helvetica, sans-serif;">

    <tr style="border-bottom:1px solid #eee;">
        <td style="padding:12px 8px; font-weight:bold; font-size:15px; color:#111; width:40%;">6/24 &nbsp; MEX vs CZE</td>
        <td style="padding:12px 8px; font-size:14px; color:#555;">No Pickup &nbsp;·&nbsp; Watch Party 7PM</td>
    </tr>
    <tr style="background:#f0fff4; border-bottom:1px solid #eee;">
        <td style="padding:12px 8px; font-weight:bold; font-size:15px; color:#1a7a3a;">🇺🇸 6/25 &nbsp; USA vs TUR</td>
        <td style="padding:12px 8px; font-size:14px; color:#1a7a3a; font-weight:bold;">Pickup 6PM &nbsp;·&nbsp; Watch Party 8PM</td>
    </tr>
    <tr style="border-bottom:1px solid #eee;">
        <td style="padding:12px 8px; font-weight:bold; font-size:15px; color:#111;">6/28 &nbsp; Round 32</td>
        <td style="padding:12px 8px; font-size:14px; color:#555;">Pickup 10:30AM &nbsp;·&nbsp; Watch Party 1PM</td>
    </tr>
    <tr style="border-bottom:1px solid #eee;">
        <td style="padding:12px 8px; font-weight:bold; font-size:15px; color:#111;">🇺🇸 7/4 &nbsp; Round 16</td>
        <td style="padding:12px 8px; font-size:14px; color:#555;">Pickup TBD &nbsp;·&nbsp; Watch Party 11AM</td>
    </tr>
    <tr style="border-bottom:1px solid #eee;">
        <td style="padding:12px 8px; font-weight:bold; font-size:15px; color:#111;">7/11 &nbsp; Round 4</td>
        <td style="padding:12px 8px; font-size:14px; color:#555;">Pickup 1PM &nbsp;·&nbsp; Watch Party 3PM</td>
    </tr>
    <tr>
        <td style="padding:12px 8px; font-weight:bold; font-size:15px; color:#111;">7/19 &nbsp; The Final 🏆</td>
        <td style="padding:12px 8px; font-size:14px; color:#555;">Pickup 10:30AM &nbsp;·&nbsp; Watch Party 1PM</td>
    </tr>

</table>
</td>
</tr>

<!-- Spacer -->
<tr><td style="height:28px;"></td></tr>

<!-- CTA -->
<tr>
<td style="text-align:center; padding:0 20px 10px;">
<a href="https://barebonessoccer.com/events/" class="cta-main" style="background-color:#1e8c3a; color:#ffffff; padding:14px 44px; text-decoration:none; font-size:16px; font-weight:bold; border-radius:6px; display:inline-block; letter-spacing:1px;">VIEW FULL EVENT SCHEDULE</a>
</td>
</tr>

<!-- Spacer -->
<tr><td style="height:28px;"></td></tr>

<!-- Closing -->
<tr>
<td style="font-size:17px; line-height:30px; text-align:center; padding:0 20px 20px;">
<b>Every round. Every watch party. All summer at Waldschänke.</b> 🌍⚽<br><br>
See you on the pitch!<br>
<b>— The Bare Bones Crew</b>
</td>
</tr>

<!-- Sponsors -->
<tr>
<td style="padding:0 20px 8px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0">
<tr>
<td style="border-top:1px solid #eee; padding-top:20px; text-align:center;">
<span style="font-size:10px; letter-spacing:2.5px; text-transform:uppercase; color:#111; font-weight:900;">These Events Are Proudly Sponsored By</span>
</td>
</tr>
</table>
</td>
</tr>
<tr>
<td style="font-size:14px; line-height:26px; text-align:center; padding:8px 20px 24px; color:#555;">
<a href="https://www.instagram.com/robin.gerlach/" style="color:#1e8c3a; font-weight:bold; text-decoration:none;">Robin Gerlach</a> — your local footy realtor &amp;
<a href="https://coloradopersonalinjuryhelp.com/" style="color:#1e8c3a; font-weight:bold; text-decoration:none;">Bowman Law Personal Injury Firm</a>
</td>
</tr>

<!-- Unsubscribe -->
<tr>
<td>
<p style="font-size:11px; color:#777; border-top:1px solid #eee; padding:10px 20px 20px; margin:0; text-align:center;">
You are receiving this email as a Bare Bones Soccer member. If you have received this email in error and/or no longer wish to receive email reminders, <a href="https://barebonessoccer.com/unsubscribe/" style="color:#777;">Unsubscribe</a>.
</p>
</td>
</tr>

</table>
</td>
</tr>
</table>

</body>
</html>
```

---

## World Cup Weekend — Block Party + Watch Party — 2026-06-10

File: `email_templates/wcbp_blast.html`

Combined announcement for the World Cup Block Party (Saturday, June 13 — two street soccer sessions + free watch party) and a standalone USA vs Paraguay watch party (June 12) co-hosted with SweatPals. Two separate CTAs (street soccer tickets, prize comp registration).

```html
<!DOCTYPE html>
<html>
<head>
<style>
.cta-bp:hover {
    background-color:#ffe033 !important;
    box-shadow:0 0 18px 4px rgba(255,215,0,0.7), 0 6px 20px rgba(0,0,0,0.3) !important;
    transform:translateY(-2px);
}
.cta-wp:hover {
    background-color:#a31515 !important;
    box-shadow:0 0 18px 4px rgba(180,30,30,0.7), 0 6px 20px rgba(0,0,0,0.3) !important;
    transform:translateY(-2px);
}
.cta-bp, .cta-wp {
    transition:all 0.2s ease !important;
    display:inline-block;
}
</style>
</head>
<body>

<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#ffffff; margin:0; padding:0;">
<tr>
<td align="center">
<table role="presentation" width="600" cellspacing="0" cellpadding="0" style="width:100%; max-width:600px; margin:0 auto; font-family:Arial, Helvetica, sans-serif; color:#111;">

<!-- Header -->
<tr>
<td style="font-size:20px; line-height:28px; text-align:center; font-weight:bold; padding:24px 10px 6px; white-space:nowrap;">
⚽🌍 World Cup Weekend — Bare Bones Goes All Out
</td>
</tr>

<!-- Intro -->
<tr>
<td style="font-size:16px; line-height:26px; text-align:center; padding:0 20px 28px; color:#444;">
The biggest US soccer weekend since 94'
</td>
</tr>

<!-- BLOCK PARTY HEADER STRIPE -->
<tr>
<td style="background:#0d1928; padding:16px 20px; text-align:center; border-radius:10px 10px 0 0;">
<span style="font-size:11px; letter-spacing:3px; text-transform:uppercase; color:#FFD700; font-weight:bold;">⚽ This Saturday · June 13</span>
</td>
</tr>

<!-- BLOCK PARTY TITLE -->
<tr>
<td style="background:#0d1928; padding:4px 20px 16px; text-align:center;">
<div style="font-size:22px; line-height:30px; font-weight:bold; color:#fff;">🏟️ World Cup Block Party</div>
<div style="font-size:14px; color:rgba(255,255,255,0.55); padding-top:4px;">Waldschänke Ciders · Sunnyside, Denver</div>
</td>
</tr>

<!-- BLOCK PARTY DETAILS -->
<tr>
<td style="background:#111e3a; padding:20px 24px; text-align:center; font-size:16px; line-height:34px; color:rgba(255,255,255,0.85);">
⏰ <b style="color:#fff;">Session 1: 10:00AM – 12:30PM</b><br>
⏰ <b style="color:#fff;">Session 2: 1:30PM – 4:00PM</b><br>
📍 <b style="color:#fff;">4100 Jason St, Denver</b><br>
💵 <b style="color:#FFD700;">$15 / session · $20 for both</b><br>
🚨 <b style="color:#FFD700;">LIMITED SPOTS</b> for street soccer — don't sleep on it<br>
🆓 <b style="color:#fff;">Watch party FREE</b> and open to everyone — no ticket needed
</td>
</tr>

<!-- BLOCK PARTY BODY -->
<tr>
<td style="background:#0d1928; padding:20px 28px; font-size:15px; line-height:27px; color:rgba(255,255,255,0.75); text-align:left;">
Parking lot pickup soccer, World Cup watch party inside, DJ, food &amp; drinks!<br><br>
<i style="text-align:center; display:block;">No team needed. Come solo or with the homies.</i>
</td>
</tr>

<!-- BLOCK PARTY CTA -->
<tr>
<td style="background:#0d1928; text-align:center; padding:16px 20px 32px; border-radius:0 0 10px 10px;">
<a href="https://barebonessoccer.com/world-cup-block-party/" class="cta-bp" style="background-color:#FFD700; color:#0d1928; padding:14px 40px; text-decoration:none; font-size:16px; font-weight:bold; border-radius:6px; display:inline-block;">🎟️ STREET SOCCER TIX</a>
</td>
</tr>

<!-- SPACER -->
<tr><td style="height:36px;"></td></tr>

<!-- DIVIDER -->
<tr>
<td style="padding:0 20px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0">
<tr>
<td style="border-top:2px solid #eee; text-align:center; padding-top:18px;">
<span style="font-size:12px; letter-spacing:3px; text-transform:uppercase; color:#111; font-weight:bold;">The Weekend Starts Friday</span>
</td>
</tr>
</table>
</td>
</tr>

<!-- SPACER -->
<tr><td style="height:24px;"></td></tr>

<!-- WATCH PARTY HEADER -->
<tr>
<td style="font-size:22px; line-height:30px; text-align:center; font-weight:bold; padding:0 10px 12px;">
🍺 USA vs. Paraguay Watch Party — June 12
</td>
</tr>

<!-- SWEATPALS IMAGE — 2/3 badge cropped via negative margin -->
<tr>
<td align="center" style="padding:0 20px; overflow:hidden;">
<img src="https://bare-bones-soccer.s3.amazonaws.com/images/watch_party6%3A12.jpeg" width="560" style="display:block; width:100%; max-width:560px; border-radius:8px; margin-top:-30px;" alt="USA vs Paraguay Watch Party at Number 38 with Bare Bones Soccer" />
</td>
</tr>

<!-- SPACER -->
<tr><td style="height:20px;"></td></tr>

<!-- WATCH PARTY DETAILS -->
<tr>
<td style="font-size:16px; line-height:32px; text-align:center; padding:0 20px;">
📍 <b>Number Thirty Eight — 3560 Chestnut Place, Denver</b><br>
🆓 <b style="text-align:center; display:block;">FREE to attend</b>
</td>
</tr>

<!-- WATCH PARTY BODY -->
<tr>
<td style="font-size:16px; line-height:26px; padding:16px 24px 8px; text-align:left;">
<b>Bonus:</b> Register a spot for our prize comp for a chance to go home with free goodies!
</td>
</tr>

<!-- WATCH PARTY CTA -->
<tr>
<td style="text-align:center; padding:20px 20px 10px;">
<a href="https://sweatpals.com/event/match-day-watch-party-cohosted-with-bare-bones-soccer/2026-06-12" class="cta-wp" style="background-color:#8B0000; color:#ffffff; padding:14px 40px; text-decoration:none; font-size:16px; font-weight:bold; border-radius:6px; display:inline-block;">PRIZE COMP REGISTRATION</a>
</td>
</tr>

<!-- SPACER -->
<tr><td style="height:24px;"></td></tr>

<!-- CLOSING -->
<tr>
<td style="font-size:17px; line-height:30px; text-align:center; padding:16px 20px 20px;">
<b>Two days. Two events. One weekend for the books.</b> 🏆<br><br>
See you out there 🙌<br>
<b>— The Bare Bones Crew</b>
</td>
</tr>

<!-- SPONSORS -->
<tr>
<td style="padding:0 20px 8px;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0">
<tr>
<td style="border-top:1px solid #eee; padding-top:20px; text-align:center;">
<span style="font-size:10px; letter-spacing:2.5px; text-transform:uppercase; color:#111; font-weight:900;">These Events Are Proudly Sponsored By</span>
</td>
</tr>
</table>
</td>
</tr>
<tr>
<td style="font-size:14px; line-height:26px; text-align:center; padding:8px 20px 24px; color:#555;">
<a href="https://www.instagram.com/robin.gerlach/" style="color:#8B0000; font-weight:bold; text-decoration:none;">Robin Gerlach</a> — your local footy realtor<br>
<a href="https://coloradopersonalinjuryhelp.com/?utm_source=google&utm_medium=cpc&utm_campaign=Brand" style="color:#8B0000; font-weight:bold; text-decoration:none;">Bowman Law Personal Injury Firm</a>
</td>
</tr>

<!-- UNSUBSCRIBE -->
<tr>
<td>
<p style="font-size:11px; color:#777; border-top:1px solid #eee; padding:10px 20px 20px; margin:0; text-align:center;">
You are receiving this email as a Bare Bones Soccer member. If you have received this email in error and/or no longer wish to receive email reminders, <a href="https://barebonessoccer.com/unsubscribe/" style="color:#777;">Unsubscribe</a>.
</p>
</td>
</tr>

</table>
</td>
</tr>
</table>

</body>
</html>
```
