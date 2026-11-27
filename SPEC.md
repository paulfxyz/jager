# Jager (jager.social) — Build Spec

Working name: **Jager** (pronounced "Ya-guerr"). Tagline: **Post drunk. Wake up clean.**
Price: **$2/month, billed $24/year.** Built on **Zernio** (white-label, multi-tenant).
Status of this document: v1, written 26 Nov 2026 from the Zernio docs. Items marked **[VERIFY]** need a short spike against a real Zernio account before we commit.

---

## 0. TL;DR and decisions needed

1. **The product** is a switch with a timer. While Jager is on, anything the user posts on a connected account is deleted. Posts the user liked themselves are protected. Users can set one-off windows (hours, a night, a day, a week or more) or recurring auto-hours (for example Fri/Sat 21:00 to 09:00).
2. **Zernio covers the hard part** (OAuth, tokens, per-platform APIs, webhooks, a white-label connect flow). We build: auth, billing, the sweep engine, the dashboard.
3. **Three issues that change the plan** (details in sections 2 and 10):
   - **Instagram and TikTok posts cannot be deleted through Zernio.** Only comments and replies can. Facebook, X, LinkedIn, Threads, Bluesky and YouTube posts can be deleted.
   - **Unit economics break at $2 with several accounts.** Zernio bills per connected account (marginal $1/account/month at scale, $6 for accounts 3 to 10, plus X API usage at cost). A user with 3 accounts costs about $3.20 per month at 3,000 accounts, more than the $2 they pay. We need an account cap, a paid add-on per extra account, or a negotiated Zernio rate.
   - **Self-like detection is not offered by Zernio.** "Ignore posts I liked myself" needs a per-platform check or a Jager-native keep mechanism (section 5.3).
4. **Decisions for Paul:**
   - Account policy: 2 accounts included, then +$1/month each? (recommended)
   - Delete timing default: at end of window ("morning-after sweep") or a short delay after each post? (recommended: 15 minutes after posting, with a per-user choice)
   - Trademark check on "Jager" and the green/orange palette before spending on launch (section 11).
   - Where the app runs. The landing page lives on SiteGround (static + one PHP script). The app needs always-on workers, so run it on **Fly.io** at `app.jager.social` (recommended).

---

## 1. Product definition

### 1.1 Core concepts
| Term | Meaning |
|---|---|
| **Jager mode** | The master switch. On = the sweep engine watches the user's connected accounts and deletes new content. |
| **Window** | A time range during which Jager mode is on. Created manually ("stay on for 3h / tonight / 1 day / 1 week / 1 month / custom") or from a schedule. |
| **Auto-hours** | Recurring windows: days of the week + start/end time + the user's timezone. Overnight ranges (21:00 to 09:00) cross midnight. |
| **Sweep** | One engine run that finds in-scope content and deletes it. |
| **Self-like shield** | If the user liked their own post, Jager keeps it. Toggle, default on. |
| **Keep** | A post exempted from deletion (by self-like or by a manual keep in Jager). |
| **Kill switch** | One tap to turn everything off immediately and cancel pending deletes. |

### 1.2 What gets deleted
In scope: content **created while a window is open** on any connected account: posts, replies, comments the user makes on their own posts, videos (see section 2 for platform limits).
Out of scope: anything created before the window opened. Jager never touches history. (A separate "wipe my history" tool is a different product; do not mix it in.)

### 1.3 When it gets deleted (user setting)
1. **After a short delay** (default 15 minutes): gives a safety margin and lets the user self-like in time.
2. **At the end of the window** ("morning-after sweep").
3. **As fast as possible** (next poll or webhook).
The grace period doubles as an **undo window**: during it the app shows "Will be deleted at 03:15 — Keep".

### 1.4 Safety rails (build these in v1)
- **Dry-run first.** First time a user turns Jager on, show "Jager would have deleted these N items" for the last 24h, with no deletions. Builds trust.
- **Connect confirmation:** explicit consent screen: "Jager will permanently delete content you post while it's on."
- **Per-platform opt-out** inside a window (for example skip LinkedIn).
- **Hard stop** on repeated platform errors: pause that account, tell the user.
- **Deletions are permanent.** YouTube deletion is permanent per Zernio; assume all are. Say so in the UI.

---

## 2. Platform matrix

Source: Zernio docs (Comments API, Compare platforms, Unpublish post). "Posts" means the user's own posts; "Comments" means comments/replies the user makes or receives on their own posts.

### 2.1 Available at launch (green on the landing page)
| Platform | Delete own posts | Delete comments/replies | Notes |
|---|---|---|---|
| X | Yes (unpublish) | Yes (own) | X API usage billed per call at X's rate; budget for it (section 10). |
| Facebook | Yes | Yes (any comment on your Page posts) | Pages. |
| LinkedIn | Yes | Yes | **Zernio notes organization accounts only for some features; personal profiles can read/reply to comments only on posts published through Zernio.** [VERIFY personal profile coverage] |
| Threads | Yes | Yes (own) | |
| Bluesky | Yes | Yes (own) | Connects with an app password. |
| YouTube | Yes (permanent) | Yes | Comment moderation uses approve/reject/hold. |
| Instagram | **No** | Yes (any comment on your posts) | Zernio: unpublish not supported on Instagram. Landing page says "Comments & replies". |
| TikTok | **No** | Yes (own) | Needs the TikTok Business app connection. Landing page says "Comments & replies". |

### 2.2 Coming soon (grey on the landing page)
| Platform | Status | Why not at launch |
|---|---|---|
| Reddit | In Zernio, but **temporarily unavailable** (Reddit blocked third-party apps) | Re-enable when Zernio does. |
| Pinterest | In Zernio, unpublish supported | No comments API; low priority for "drunk posting". |
| Discord, Telegram, Slack | In Zernio (bot-based) | Message deletion semantics differ; needs a design pass. |
| Snapchat | Zernio closed beta; unpublish not supported | Blocked. |
| Google reviews (Business Profile) | In Zernio, unpublish supported | Different use case. |
| Mastodon, Tumblr, Twitch chat, Letterboxd, Strava, Substack Notes | **Not in Zernio** | Needs custom integrations ("we'll try to add more custom API and sources"). |

### 2.3 The honest gap
"Anything you post anywhere" is not achievable with Zernio alone:
- Instagram and TikTok posts: platform limitation, not ours. Comments only.
- **Comments the user writes on other people's posts** are not covered by Zernio's Comments API, which reads comments on the user's own posts. On X, Threads and Bluesky a reply is itself a post by the user, so it is covered if we can list the user's recent posts. On Instagram, Facebook, YouTube, LinkedIn and TikTok, comments on others' content are **not** reachable. [VERIFY]
- **Posts created outside Zernio** (all of them, in our case): Zernio says reading comments and analytics works on posts published outside Zernio, and mentions a post import/sync for X. Whether `POST /v1/posts/{id}/unpublish` works on imported posts is the single most important spike. [VERIFY]

Marketing must match reality: the landing page already says "comments & replies" for Instagram/TikTok and has a footnote. Keep that wording.

---

## 3. Architecture

```
jager.social (SiteGround, static)       app.jager.social (Fly.io)               Zernio
┌────────────────────┐                  ┌───────────────────────────┐          ┌──────────────────┐
│ landing + login UI │  fetch /api  ──▶ │ API (Node/TS, Hono/Fastify)│  REST ─▶ │ profiles         │
│ api/notify.php     │                  │ Auth (email OTP)           │          │ connect (white-  │
└────────────────────┘                  │ Billing (Stripe webhooks)  │ ◀─ webhooks │ label)         │
                                        │ Worker (sweep engine)      │          │ posts / comments │
                                        │ Scheduler (windows)        │          └──────────────────┘
                                        │ Postgres (Fly) + Redis/queue│
                                        └───────────────────────────┘
connect.jager.social  → Zernio hosted connect screens on our domain
```

- **Landing:** keep static on SiteGround. Replace `api/notify.php` with the real API once the app exists (or keep it for the waitlist).
- **App + API:** one service in TypeScript. Frontend: React or plain SPA served from `app.jager.social`. Mobile-first PWA (users flip it on from a taxi).
- **Worker:** same codebase, separate process. Queue: Postgres-based (pg-boss) is enough; Redis only if we outgrow it.
- **Database:** Postgres. All timestamps UTC; store the user's IANA timezone.
- **Email:** transactional provider (Resend, Postmark or SES) for OTP codes and morning-after receipts. SPF, DKIM and DMARC on `jager.social`. Do not use PHP `mail()` for OTP.
- **Observability:** structured logs, error tracking, an admin page listing failed deletions.

---

## 4. Zernio white-label integration

Zernio's own model for this is "Build a platform": one **profile per customer**, accounts connected inside it, webhooks that carry your own `externalId`.

### 4.1 Setup (one time)
1. Create the Zernio workspace and API key for Jager. Add a card; note the **prepaid balance model starting 1 Dec 2026** (pay-per-use from a prepaid balance, so enable auto top-up).
2. `PUT /v1/connect/welcome-screen` with `brandName: "Jager"`, logo, `primaryColor: "#ff7a00"`, `showByDefault: true`, so each connect flow shows "Jager wants to connect to your Instagram".
3. **Custom domain for connect** (`connect.jager.social`) per the "Use your own domain for connect" guide.
4. **Own platform apps** (optional, later): connect through Jager-owned developer apps on each platform so the consent screen shows Jager and rate limits are ours. Requires app review per platform; plan for weeks. Not needed for v1.
5. Register webhooks (up to 50 endpoints per team): `account.connected`, `account.disconnected`, `comment.received`, plus post-lifecycle events. [VERIFY which event fires for content published outside Zernio; if none, poll.]
6. Consider **Zero content retention** (team or profile setting): Zernio stores identifiers and metadata only, never content. Good for privacy and matches Jager's promise.

### 4.2 Per-user flow
| Step | Zernio call |
|---|---|
| Sign-up | `POST /v1/profiles` with `externalId = jager_user_id` (idempotent: unique per owner). Store `profile._id`. |
| Connect account | `GET /v1/connect/{platform}?profileId=…&redirect_url=https://app.jager.social/connected&welcome=true` → redirect user to `authUrl`. |
| Account connected | Webhook `account.connected` (carries `profiles[0].externalId` and `account.accountId`). |
| List accounts | `GET /v1/accounts?profileId=…` |
| Account died | Webhook `account.disconnected` → email the user, show "Reconnect" in the app. |
| Detect new content | Poll (see 5.2): `GET /v1/posts`, `GET /v1/inbox/comments?profileId=…`, `GET /v1/inbox/comments/{postId}?accountId=…` |
| Delete post | `POST /v1/posts/{postId}/unpublish` with `{platform, accountId}` (not on Instagram, TikTok, Snapchat). |
| Delete comment | Comments API delete endpoint with `accountId`. |
| User deletes Jager account | Disconnect accounts, `DELETE` the profile, purge our data. |

Security rule from Zernio's docs: `POST /v1/posts` accepts any `accountId` in the workspace, so **always scope calls to the user's own `profileId` / `accountId`s that we stored**. Never accept an account id from the client.

### 4.3 Rate limits and retries
- Use `Idempotency-Key` on writes. Branch on the error `type`/`code` envelope. Back off on 429.
- Zernio rate limits scale with connected-account count; X has its own per-call costs.
- Comment lists can lag up to 10 minutes (cached). Your own deletes refresh that post's thread at once.

---

## 5. Sweep engine

### 5.1 State machine
```
User toggles ON / window opens ──▶ create window row (starts_at, ends_at, policy)
                                   └─▶ record baseline per account: last_seen_post_time = now

Every tick (only for users with an open window):
  for each active account:
     new_items = fetch items created after window.starts_at
     for item in new_items not yet tracked:
         insert tracked_item(status = 'pending', delete_at = per policy)
  for tracked_item where status='pending' and delete_at <= now:
     if shield on and is_self_liked(item): status='kept'
     elif not in_open_window_or_grace(item): status='kept'  # never delete outside scope
     else call Zernio delete → status='deleted' | 'failed'(retry with backoff, max 5)

Window ends (or kill switch): flush policy "at end of window", cancel the rest, send receipt.
```

### 5.2 Detection strategy
- **Webhooks first** where available (Instagram, Facebook, Threads, TikTok deliver `comment.received` in real time; YouTube, LinkedIn, Bluesky, Reddit and X are polled by Zernio, so minutes of lag).
- **Polling second**, only while a window is open: every 2 minutes for posts, every 5 minutes for comments, with `since` cursors to keep reads tiny. X reads cost $0.005 per resource, so always use a cursor.
- **Idle accounts cost nothing**: no windows, no polling.
- **Timezone and DST:** schedules are stored as local wall-clock + IANA zone; compute UTC per occurrence (Zernio has a Timezones guide with the same model).

### 5.3 Self-like shield (hard part)
Zernio does not expose "did I like my own post". Options per platform:

| Platform | Approach | Confidence |
|---|---|---|
| X | `GET /2/tweets/:id/liking_users` or the user's liked-tweets timeline via Zernio if exposed; check if `me ∈ likers` | [VERIFY, costs X read credits] |
| Instagram, Facebook, Threads, YouTube, TikTok, LinkedIn, Bluesky | Not exposed through Zernio. Likers lists are limited or unavailable | Low |

**Fallback that always works: Jager Keep.** Every pending item appears in the app (and in a push/email digest) with a one-tap **Keep** button during the grace period. A browser/extension or Telegram bot shortcut can come later. The landing page promise "like your own post and Jager leaves it alone" should be validated per platform before launch; if a platform can't support it, say "Tap Keep in Jager" for that platform.

### 5.4 Receipts
After each window: "Jager erased 12 items, kept 2, failed 0" with per-platform counts. Store only IDs, platform, timestamps and a short hash of the text. **Do not store post content** (privacy and GDPR).

---

## 6. Data model (Postgres)

```sql
users(id, email unique, tz, created_at, deleted_at)
otp_codes(id, email, code_hash, expires_at, attempts, consumed_at, ip)
sessions(id, user_id, token_hash, expires_at, ua, ip)
subscriptions(user_id, stripe_customer_id, stripe_sub_id, status, plan, current_period_end, account_limit)
zernio_profiles(user_id, profile_id, created_at)
accounts(id, user_id, zernio_account_id, platform, handle, status, connected_at, last_error)
settings(user_id, shield bool default true, delete_policy enum('fast','delay','end'), delay_minutes int default 15,
         skip_platforms text[] , master_on bool)
schedules(id, user_id, days smallint[], start_local time, end_local time, active bool)
windows(id, user_id, source enum('manual','schedule'), starts_at, ends_at, ended_reason, created_at)
tracked_items(id, window_id, account_id, kind enum('post','comment'), platform_item_id, content_hash,
              seen_at, delete_at, status enum('pending','kept','deleted','failed'), kept_reason, error)
events(id, user_id, type, payload jsonb, created_at)   -- audit log
waitlist(email unique, created_at, source)             -- pre-launch
```

---

## 7. Auth: email OTP only

- `POST /auth/request` `{email}` → always respond 200 (do not reveal whether the user exists). Create a 6-digit code, **hash it**, TTL 10 minutes, send via email provider.
- `POST /auth/verify` `{email, code}` → on success create the user if new, issue a session (httpOnly, Secure, SameSite=Lax cookie; 30-day rolling).
- Limits: 5 attempts per code, 5 requests per email per hour, 20 per IP per hour, 60-second resend cooldown. Constant-time compare. Invalidate older codes on a new request.
- Optional magic link in the same email (same token, one-click).
- Sign-up and login are the same flow.
- The landing-page login UI (`login.html`) already matches this: email screen → 6-digit screen. Today it is a **placeholder**: it sends a notification to hello@paulfleury.com and shows the "coming soon" modal, with no real code.

---

## 8. Billing

- **Stripe Checkout + Customer Portal.** One price: **$24/year** (`price_jager_yearly`). Marketing says "$2/month".
- Options: 7-day free trial (card up front) or a 14-day money-back guarantee. A trial is usually better here because users need to see a dry run.
- **Stripe Tax** for EU VAT (Paul is in Portugal; most users will be consumers).
- Webhooks: `checkout.session.completed`, `invoice.paid`, `customer.subscription.updated/deleted`. When the subscription lapses: turn master switch off, disconnect accounts after a grace period, delete data after 30 days.
- Gate the app on `subscriptions.status in ('trialing','active')`.
- Fees: roughly 1.5% + €0.25 on EU cards, 2.9% + $0.30 on others, so about $0.60 to $1.00 per $24 charge.

---

## 9. App screens (v1)

1. **Login / sign-up** (done as placeholder) → email → 6-digit code.
2. **Onboarding:** connect first account (Zernio flow, branded) → consent screen → **dry run** of last 24h → pick default delete policy → done.
3. **Home (the switch):** big On/Off, "On until tomorrow, 09:00", duration chips (3h, Tonight, 1 day, 1 week, 1 month, custom), live feed of pending/erased/kept items, **Kill switch**.
4. **Auto-hours:** day pills + start/end time + timezone (the landing page panel is a faithful preview).
5. **Accounts:** list, connection health, connect/disconnect, per-account skip toggle, account-limit meter.
6. **Settings:** self-like shield, delete policy, notifications (email/push), timezone, delete my data.
7. **History:** windows and receipts.
8. **Billing:** Stripe portal link.

Design: reuse the landing tokens (bottle green `#08170f`, paper `#f4ecdc`, amber `#ff7a00` for actions, lime `#c6ff3d` for "clean/on" states; Bricolage Grotesque, Instrument Serif italic, JetBrains Mono). Same voice: dry, a bit chaotic, never preachy.

---

## 10. Economics and risks

### 10.1 Zernio cost model
Zernio bills per **connected account** across the whole team, graduated, prorated daily:
- Accounts 1 to 2: free. 3 to 10: **$6**. 11 to 100: **$3**. 101 and up: **$1** each per month.
- **X API calls at X's published rate, no markup:** read $0.005 per resource, create $0.015 per post (URL posts $0.20). Connecting X requires a card on monthly billing; on prepaid balance connecting X is free. Delete calls are not listed; [VERIFY].
- Profiles are free and unlimited. Comment replies and deletes do not count as outbound messages.

| Users | Avg accounts/user | Connected accounts | Zernio monthly cost | Per user | Revenue per user ($2) |
|---|---|---|---|---|---|
| 100 | 3 | 300 | $48 + $270 + $200 = **$518** | $5.18 | $2.00 |
| 1,000 | 3 | 3,000 | $48 + $270 + $2,900 = **$3,218** | $3.22 | $2.00 |
| 1,000 | 2 | 2,000 | $48 + $270 + $1,900 = **$2,218** | $2.22 | $2.00 |
| 10,000 | 2 | 20,000 | about $20,200 | $2.02 | $2.00 |

Before payment fees, X API usage, email, hosting. **At $2/month, Jager loses money at every size unless users average about one account.** Options (pick one before launch):
1. **Include 2 accounts, +$1/month per extra account** (matches Zernio's marginal rate at scale). Still thin: negotiate.
2. **Raise the price** to $3 to $4/month or $36 to $48/year. $2 is great marketing; consider "from $2".
3. **Negotiate a white-label/volume rate with Zernio.** Their pricing page says every account includes every feature; ask sales for platform pricing before building.
4. **Only keep accounts connected while a window is open** (daily proration makes this cheaper) at a UX cost. Probably not worth it.
5. **Cap X** (most expensive per call) or make X an add-on.

Do this math with Zernio's calculator and real numbers before shipping pricing publicly. Until then the landing page says $2/month, which Paul asked for; it does not promise a number of accounts, so there is room to introduce a limit.

### 10.2 Other risks
| Risk | Severity | Mitigation |
|---|---|---|
| Unpublish not working for posts made outside Zernio | **High** | Spike first (section 13). If it fails, v1 is comments-only + posts we can see. |
| Detection latency (X/YouTube/LinkedIn are polled; lists lag up to 10 min) | Medium | Delay policy default 15 min; set expectations ("within minutes"). |
| Self-like shield unavailable on most platforms | Medium | Jager Keep button; honest copy. |
| False deletions (clock skew, timezone bugs, window edges) | **High** (irreversible) | Only items with `created_at >= window.starts_at`; dry run; unit tests for DST/overnight; kill switch; delete delay. |
| Platform account blocked for bulk deletes | Medium | Throttle, jitter, per-platform concurrency. |
| Brand/trademark: "Jager" is a pun on Jägermeister, and the green + orange palette echoes its branding | **Medium** | Do a trademark search (classes 9, 42, 45) before launch; consider a non-orange accent or a different name; never use a stag or bottle imagery. The landing footer says "Not affiliated with Jägermeister". |
| Zernio dependency (single supplier) | Medium | Keep an abstraction layer (`PlatformProvider`) so a direct integration (X, Bluesky first) can replace Zernio per platform. |
| Reddit blocked, Snapchat in beta | Low | Marked coming soon. |

---

## 11. Legal, privacy, security

- **GDPR:** controller is Paul's entity; processors: Zernio, Stripe, email provider, Fly. Sign DPAs. Privacy policy and Terms pages required before launch (footer links currently open the coming-soon modal).
- **Data minimisation:** store IDs and hashes, never post text. Turn on Zernio zero content retention.
- **Tokens:** Zernio holds the platform OAuth tokens; Jager stores only Zernio ids. Encrypt the Zernio API key (secret manager), rotate on schedule.
- **Terms must say:** deletions are permanent; Jager is not responsible for content missed by platform lag or API limits; users must be adults; not affiliated with any platform or Jägermeister.
- **Abuse:** a user could use Jager to wipe evidence. Log deletions (IDs + timestamps) for 90 days and respond to lawful requests; say so in the Terms.
- **Platform terms:** deleting your own content via official APIs is within normal use. Review Meta, TikTok, X, Google (YouTube) and LinkedIn app review needs only if we move to our own apps.
- **Security basics:** hashed OTPs, rate limits, CSRF protection, strict CSP, audit log, per-user scoping on every Zernio call.

---

## 12. Roadmap

| Milestone | Scope | Notes |
|---|---|---|
| **M0 — Spikes (2 to 3 days)** | Zernio account; connect one X, Bluesky, Facebook, YouTube account; test: list own posts (incl. externally published), unpublish, delete comment, webhooks, lag | Kills or confirms section 2.3 |
| **M1 — Waitlist (now)** | Landing + placeholder login (done); real email delivery for notifications; SPF/DKIM; Terms/Privacy | Landing live on jager.social |
| **M2 — Core (3 to 4 weeks)** | OTP auth, Zernio profile + connect, dashboard switch, manual windows, sweep engine for X, Bluesky, Facebook, Threads, YouTube, dry run, kill switch, receipts | Private beta, free |
| **M3 — Money** | Stripe, trial, account limits, receipts email | Public beta |
| **M4 — Schedules + Keep** | Auto-hours, Keep button/digest, self-like shield where supported | |
| **M5 — Coverage** | Instagram/TikTok comments, LinkedIn, per-platform polish | |
| **M6 — Beyond Zernio** | Custom sources (Mastodon, Tumblr, Substack Notes, Letterboxd, Strava…), browser extension for "Keep" | "Coming soon" tiles become real |

Later ideas: morning-after summary email ("Jager saved you from 7 posts"), friend-lock (a trusted person can enable your Jager), geofenced auto-on (near a bar), shared "sober pact", rescue bin that holds encrypted content for 24h so a mistaken delete can be re-posted.

---

## 13. Spikes and open questions

1. Does `POST /v1/posts/{id}/unpublish` work for posts **not created through Zernio** (imported)? What does `GET /v1/posts` return for them? How are they imported, and how often?
2. Which webhook fires when a user publishes natively on each platform? Otherwise define polling cadence per platform.
3. Real detection latency on X, LinkedIn, YouTube, Bluesky.
4. X: exact API cost of a delete and of polling a user's timeline; does Zernio's X pass-through apply to deletes?
5. LinkedIn personal profiles: can we list and delete own posts, or only org pages?
6. Can the user's own like on their post be read on any platform through Zernio? (Check Likers/engagement endpoints in the Analytics API.)
7. Zernio volume/white-label pricing and any reseller terms. Does their terms of service allow reselling under our brand with their per-account billing?
8. Instagram: only accounts connected via Facebook Login support some comment features; confirm onboarding path for creators and personal accounts.

---

## 14. Landing page: what is delivered

Folder `jager/` (static, relative paths, works at the root of jager.social):

```
index.html        landing page
login.html        log in / sign up (email → 6-digit code) → "Thank you, coming soon" modal
styles.css  fonts.css  app.js
assets/fonts/     Bricolage Grotesque, Instrument Serif, JetBrains Mono (self-hosted woff2)
assets/icons/     Simple Icons platform logos (used to show supported platforms)
api/notify.php    emails hello@paulfleury.com and appends to api/data/leads.csv (blocked from web access)
.htaccess  robots.txt  sitemap.xml  favicon.svg  og.png
```

Behaviour:
- Every call to action goes to `login.html`. Email entry sends a notification email to hello@paulfleury.com and shows a code screen; entering any 6 digits sends a second notification and shows the **Thank you, coming soon** modal. Footer Terms and Privacy and the "Your platform missing?" tile open the same modal and also notify.
- Email notifications use PHP `mail()` from `noreply@jager.social`. Every submission is also written to `api/data/leads.csv`, so nothing is lost if mail lands in spam. Create the mailbox/SPF/DKIM in SiteGround for reliable delivery.
- Spam protection: honeypot field, 20 requests per 10 minutes per IP, payload size cap.
- Accessibility: keyboard focus styles, reduced-motion support, semantic headings, labelled controls.

Deploy: upload the contents of `jager/` into `public_html/` of jager.social over FTP/SFTP (SiteGround: SFTP port 18765 or FTP port 21). Make sure `api/` is writable by PHP so `api/data/` can be created. Then test the full login flow once and check hello@paulfleury.com.

---

## 15. Sources

- Zernio docs index: https://docs.zernio.com/llms.txt
- Build a platform (profiles, connect, white-label connect window, webhooks): https://docs.zernio.com/multi-tenant.mdx
- Comments API (platform delete/hide matrix): https://docs.zernio.com/products/comments.mdx
- Compare platforms (incl. Reddit unavailable): https://docs.zernio.com/platforms/compare.mdx
- Unpublish post (not supported on Instagram, TikTok, Snapchat): https://docs.zernio.com/posts/unpublish-post.mdx
- Posts API index: https://docs.zernio.com/llms/api/posts.txt
- Social pricing (per connected account, X pass-through): https://docs.zernio.com/pricing/social.mdx
- Prepaid balance (from 1 Dec 2026): https://docs.zernio.com/pricing/balance.mdx

## 0c. v4 changes (Telegram, how-it-works demo, footer)

- Channels are now WhatsApp, Telegram and email (Signal, iMessage/SMS, Slack remain "coming soon"). Zernio supports Telegram (bot-based): https://docs.zernio.com/llms/platforms/telegram.txt. Telegram needs a bot (BotFather token), a /start deep link to link the Jager account, inline-keyboard quick replies and slash commands (/recap, /rules, /stop). Telegram bots can message proactively once the user has pressed Start, so no template approval is needed (unlike WhatsApp business-initiated messages).
- New pages: channels.html (per-channel cards with live chat skins), terms/privacy/cookies/gdpr stubs (noindex, to be written before launch), 404.html.
- how.html rebuilt: scroll-driven 5-step story (connect, say hi, set rule, overnight cleanup, recap and reply), a full "drunk weekend" demo (virtual clock, feed that deletes posts on the rule's timer, user can post and watch Jager delete it) and the interactive command sandbox. Channel tabs sync across every chat on the page. Quick-reply buttons are rendered per channel (chips on WhatsApp, inline keyboard on Telegram, "Quick reply" links in email).
- Footer follows iris.online and digital.spot: waitlist pitch, link columns, giant wordmark, bottom bar with Enki Ltd, company number 2067348138, 14 Antim I Street, fl. 1 & 2, Sofia, Bulgaria, ask@jager.social (mailbox or forwarder to create), sister-product note.
- Login: channel picker now has WhatsApp, Telegram, Email; notify.php stores the channel value.

## 0d. v5: free, open-source (MIT) pivot

- Jager is now a free, MIT-licensed project. No login, signup, pricing, payments or coming-soon labels. Every CTA points to https://github.com/paulfxyz (placeholder until the repository is published; update to the repo URL when it exists).
- User brings keys: Zernio API key (accounts plus a WhatsApp number or Telegram bot), OpenRouter key (language model) and optionally Runware (image jobs). Runs anywhere via docker compose; config via .env (ZERNIO_API_KEY, OPENROUTER_API_KEY, RUNWARE_API_KEY, JAGER_CHANNEL, JAGER_MODEL, JAGER_TIMEZONE, JAGER_RECAP). The repo layout and variable names on the site are illustrative and must match the real repo.
- Three jobs: comment master (triage, drafted replies, send/hide/delete after approval), weekly reminder (recap, reply-to-delete), sprints (night sprint delete-after-X, comment sprint, launch sprint, cleanup sprint).
- Honest limits kept in copy: platform APIs decide what can be deleted (Instagram and TikTok are comments only through Zernio).
- Pages: index, how (animated story, weekend demo, sandbox), setup, faq, 404. Removed: login, pricing, platforms, channels, legal stubs, api/notify.php (old URLs redirect to home). Footer keeps Enki Ltd details and MIT notice.

## 0e. v6: full visual redesign ("The Night Shift")
- New identity: midnight, hot pink and acid yellow on cream, neo-brutalist stickers and hard shadows, giant uppercase Bricolage plus italic Instrument Serif. Replaces the bottle-green/amber look.
- One long scroll that is a night: a fixed HUD clock (21:00 to 09:00) and moon/sun follow scroll progress. Five chapters (21:00 plug in, 23:30 night sprint, 02:00 posts erased, 03:30 comment sprint, 09:00 weekly reminder) drive one sticky phone plus a floating feed card. Then sprint cards, try-it sandbox, three-keys stack, MIT/terminal, FAQ, closer, Enki footer.
- Pages: index.html and setup.html (+404). Old pages redirect to home via .htaccess. Source: build_night.py, night.css, night.js, chat.js.

## v7
- EN/FR (fr/ subfolder), 30-language selector (only EN/FR enabled), Product Hunt launch 1 Jan 2027 countdown, "What is Jager" explainer, comparison table, setup checklist.
