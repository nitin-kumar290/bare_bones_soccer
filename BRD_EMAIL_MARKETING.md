# Business Requirements Document
## Email Marketing System — Bare Bones Soccer
**Prepared for:** Nate (Developer)
**Requested by:** Ian Marcus
**Date:** May 2026

---

## Priority Goals

Two things matter above everything else:

1. **Analytics** — We need deep, accurate campaign analytics. Open rate, click tracking (who clicked which link), unsubscribe rate, bounce rate, audience growth, and best send time are the core outputs. These must be reliable, per-campaign, and viewable in a clean admin dashboard. This is the primary reason we're building this instead of using a simpler tool.

2. **Zero spam issues** — Every campaign must land in the inbox. Proper authentication (SPF, DKIM, DMARC), mandatory unsubscribe links, bounce suppression, and complaint handling are non-negotiable. A spam flag damages the entire sending domain permanently.

Everything else in this document supports those two goals.

---

## Overview

Bare Bones Soccer needs a custom email marketing system to send mass marketing campaigns and automated newsletters to a growing subscriber base of 500–1,000+ users. And one day thousands. The system must handle high-volume sends without spam issues, track core engagement analytics, and run entirely within our existing AWS infrastructure.

### Current Infrastructure
- Django app deployed on **AWS Lambda** via Zappa
- Database: **PostgreSQL on Neon**
- Existing email: **Gmail / Google Workspace SMTP** — used for transactional emails only (registration confirmations, payment receipts)
- ~500+ registered users and growing

### Critical Infrastructure Constraint
**Gmail / Google Workspace SMTP cannot be used for marketing blasts.** Google Workspace enforces daily sending limits and bulk outbound mail will be flagged as spam, damaging sender reputation and preventing delivery at scale. Note we still want to be able to send manual marketing emails too.

**Sending split:**
- Transactional emails (confirmations, receipts) → Gmail / Google Workspace SMTP — unchanged
- Marketing emails (campaigns, newsletters) → **AWS SES** — new requirement

All campaign logic is coded and triggered from **AWS Lambda**. AWS SES handles delivery. This keeps marketing volume off Gmail entirely. - not true, gmail handles delivery***

---

## Functional Requirements

### 1. Campaign Management
- Compose and send a marketing email campaign to the full subscriber list or a filtered segment
- Campaign types:
  - One-time blast (send immediately)
  - Scheduled send (set future date and time)
  - Recurring monthly newsletter (fires automatically on a set schedule)
- Email composer: HTML editor and/or simple template builder
- Save campaigns as drafts
- Preview email before sending
- Test send to a single address before full blast

### 2. Mass Send Capability
- Must support sending to **500–1,000+ recipients in a single campaign** reliably
- Sends route through **AWS SES** using verified sender domain (`soccerbarebones@gmail.com`)
- All emails must include proper authentication headers (SPF, DKIM, DMARC) and a functioning unsubscribe link to avoid spam classification
- System must respect SES sending rate limits and queue/batch sends if needed

### 3. Subscriber Management
- Subscriber list auto-populated from existing registered Django `User` accounts
- No subscriber cap — must scale beyond 1,000 without architectural changes
- **Unsubscribe handling:** One-click unsubscribe link in every email. Unsubscribed users are flagged in the database and permanently excluded from all future sends
- **Bounce handling:** SES bounce and complaint notifications routed back via AWS SNS webhook. Hard bounces and spam complaints automatically suppress the address
- Manual ability to add or remove individual subscribers

### 4. Analytics & Tracking *(Primary Goal)*

All metrics must be tracked per campaign and viewable in an admin dashboard. The metrics below are ordered by priority.

**Core — must have:**

| Metric | Description |
|---|---|
| **Open Rate** | % of recipients who opened the email, tracked via a 1×1 invisible tracking pixel |
| **Click Rate** | % of recipients who clicked at least one link |
| **Link-Level Click Tracking** | Which specific links were clicked and by how many unique recipients — this is the most important click metric |
| **Top Links Ranking** | Ranked list of most-clicked links per campaign |
| **Unsubscribe Rate** | % of recipients who unsubscribed after a given campaign |
| **Bounce Rate** | % of emails that bounced (hard and soft), sourced from SES/SNS callbacks |

**Also required:**

| Metric | Description |
|---|---|
| **Audience Growth Over Time** | Chart of subscriber count by week/month over time |
| **Best Send Time** | Based on historical open timestamps, surface the time of day and day of week that generates highest open rates |

### 5. Automation
- **Monthly newsletter:** Set a recurring send schedule (e.g. first Tuesday of every month) that fires automatically without manual intervention
- **Scheduled campaigns:** Compose now, auto-send at a specified future date/time
- v1 does not require drip sequences or behavioral triggers

### 6. Admin Interface
- Accessible only to Django staff/admin users
- Dashboard must show:
  - All campaigns (sent, scheduled, draft) with status
  - Per-campaign analytics (opens, clicks, link breakdown, unsubscribes, bounces)
  - Subscriber count and growth chart
  - Unsubscribe and bounce logs
- Accessible as a section within existing Django admin or a protected custom internal page

---

## Non-Functional Requirements

### Spam & Deliverability *(Non-negotiable)*
Getting flagged as spam is a permanent reputation hit on the sending domain — it breaks both marketing AND transactional emails. These requirements are not optional:

- SPF, DKIM, and DMARC must be configured and verified on `barebonessoccer.com` before any campaign sends
- Every marketing email must include a functioning one-click unsubscribe link
- Hard bounces and spam complaints must be automatically suppressed — never mail a bad address twice
- SES sending reputation must be actively monitored
- Marketing sends must **never** go through Gmail/Workspace SMTP — that path is reserved for transactional emails only (confirmations, receipts). Mixing them risks getting the entire domain flagged

### Volume & Reliability
- A single campaign must reliably deliver to 1,000+ addresses without partial failure
- No third-party SaaS fees. SES costs ~$0.10 per 1,000 emails
- Failed or dropped recipients must be logged — the system must not silently skip addresses

---

## Out of Scope (v1)
- Geographic open tracking
- Revenue attribution per email / Stripe integration
- Device or email client breakdown (iPhone vs Android, Gmail vs Outlook)
- A/B testing
- Advanced drip / behavioral automation
- SMS marketing
- Landing page builder

---

## Technical Implementation Notes for Nate

| Component | Implementation |
|---|---|
| **Sending** | AWS SES via boto3 from Lambda — same pattern as existing `send_email_ses()` function in views.py |
| **Tracking pixel** | 1×1 transparent PNG endpoint in Django — on load, logs a `CampaignOpen` record (campaign ID + recipient user ID + timestamp) |
| **Click tracking** | All links in campaign HTML rewritten to a Django redirect URL (e.g. `/t/click/?c=123&l=456&u=789`) — logs the click event then redirects to the real destination URL |
| **Unsubscribe** | Unique signed unsubscribe link per recipient — hits Django endpoint, sets flag on user record. `EmailUnsubscribe` model already exists in the codebase. |
| **Bounce/complaint handling** | AWS SNS topic → Django webhook endpoint → suppress address in DB |
| **Scheduling/recurring sends** | AWS EventBridge cron rule → Lambda trigger. EventBridge client already instantiated in views.py (`EVENTBRIDGE`). |
| **Best send time** | Aggregate `CampaignOpen.timestamp` by hour and day of week across all historical campaigns — surface top performing windows in dashboard |
