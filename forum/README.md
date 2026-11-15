# The Fractal Reality Forum

```
Created: 2026-11-14
Last updated: 2026-11-14
Version: 1.0
```

A small, dependency-free forum for fractalreality.ca, running on Cloudflare Workers with a D1 (SQLite) database. Server-rendered HTML in the site's house style; no frontend framework, no build step. Sign in with Google, Discord, Facebook, or Apple.

The doorway on the main site is `docs/forum.html` (the What Exists? poster); the forum itself is meant to live at **https://forum.fractalreality.ca**.

## What is in here

| Path | What it is |
| --- | --- |
| `src/index.js` | Router: pages, posting, moderation, OAuth endpoints |
| `src/oauth.js` | Google, Discord, Facebook, Apple providers (Apple mints its ES256 client-secret JWT in the Worker) |
| `src/auth.js` | HMAC-signed session cookie, OAuth state cookie, CSRF origin check |
| `src/db.js` | All D1 queries (prepared statements only) |
| `src/html.js` | Page templates, house palette, escaping |
| `migrations/0001_init.sql` | Schema plus the five seeded places (Ideas, The Steelman Arena, Corrigibility Practice, New Perspectives, Open Questions) |
| `wrangler.jsonc` | Worker config; D1 auto-provisions on first deploy |

Sign-in buttons appear automatically for whichever providers have secrets set; none are required to run the forum locally.

## Run it locally

```bash
cd forum
npm install
copy .dev.vars.example .dev.vars
npm run migrate:local
npm run dev
```

Open http://127.0.0.1:8787. With `DEV_LOGIN=1` (set in `.dev.vars`), the sign-in page has a "Continue as test user" button, so the whole forum works with no OAuth configured. Local data lives in `forum/.wrangler/` and is throwaway.

## Deploy to Cloudflare

One-time, from `forum/`:

```bash
npx wrangler login
npm run deploy            # creates the Worker and auto-provisions the D1 database
npm run migrate:remote    # creates the tables and seed categories in production
```

Then set the required secrets:

```bash
npx wrangler secret put SESSION_SECRET   # paste a long random string (40+ chars)
npx wrangler secret put ADMIN_EMAILS     # your email; grants admin role on first sign-in
```

`ADMIN_EMAILS` is a comma-separated list, matched against the email the sign-in provider reports. Set it BEFORE your own first sign-in; if you signed in first, promote yourself by hand:

```bash
npx wrangler d1 execute fractal-forum-db --remote --command "UPDATE users SET role='admin' WHERE email='you@example.com'"
```

### Custom domain

Dashboard: Workers & Pages -> fractal-forum -> Settings -> Domains & Routes -> Add -> Custom domain -> `forum.fractalreality.ca`. Because the zone is already on Cloudflare, DNS and TLS are handled for you. (Equivalently, uncomment the `routes` line in `wrangler.jsonc` and redeploy.)

The Worker derives all URLs from the request, so it works unchanged on the `workers.dev` URL and the custom domain.

## Sign-in providers

Each provider needs an app registered in that provider's console, and two secrets set via `npx wrangler secret put NAME`. Buttons only appear for configured providers, so you can add them one at a time: Google and Discord are free and take minutes; Facebook is free but needs Live mode for the public; Apple requires a paid developer account.

The redirect / callback URL to register is always:

```
https://forum.fractalreality.ca/auth/<provider>/callback
```

(plus `http://127.0.0.1:8787/auth/<provider>/callback` if you want to test a real provider locally via `.dev.vars`).

### Google (free)

1. https://console.cloud.google.com -> create a project -> "APIs & Services" -> "OAuth consent screen": External, app name, your email; add no extra scopes (the defaults cover openid/email/profile). Publish the app.
2. "Credentials" -> "Create credentials" -> "OAuth client ID" -> Web application. Authorized redirect URI: `https://forum.fractalreality.ca/auth/google/callback`.
3. `npx wrangler secret put GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.

### Discord (free)

1. https://discord.com/developers/applications -> New Application.
2. OAuth2 -> add redirect `https://forum.fractalreality.ca/auth/discord/callback`.
3. Secrets: `DISCORD_CLIENT_ID` (the Application ID) and `DISCORD_CLIENT_SECRET` (OAuth2 client secret).

### Facebook (free; needs Live mode for the public)

1. https://developers.facebook.com -> Create app (type: Consumer) -> add the "Facebook Login" product.
2. Facebook Login -> Settings -> Valid OAuth Redirect URIs: `https://forum.fractalreality.ca/auth/facebook/callback`.
3. App Settings -> Basic, field by field:
   - **App domains**: `fractalreality.ca` (covers the forum subdomain).
   - **Namespace**: leave blank (optional; only used by legacy Canvas apps).
   - **Privacy policy URL**: `https://fractalreality.ca/privacy.html`
   - **Terms of Service URL**: optional; leave blank.
   - **User data deletion**: switch the dropdown from "Data deletion callback URL" to **"Data deletion instructions URL"** and enter `https://fractalreality.ca/privacy.html#delete` (the policy's deletion section; the forum has a matching self-serve "Delete my account and data" button on the profile page).
   - **Category**: anything close ("Social networks & dating" or "Education").
   - **App icon**: 1024 x 1024; `forum/app_icon_1024.png` in this repo is a ready-made circumpunct icon.
   - Note App ID and App Secret -> secrets `FACEBOOK_CLIENT_ID`, `FACEBOOK_CLIENT_SECRET`.
4. Switch the app from Development to Live or only app admins/testers can sign in. `public_profile` and `email` need no review.

### Apple (requires the $99/year Apple Developer Program)

1. https://developer.apple.com -> Certificates, Identifiers & Profiles.
2. Identifiers -> create an App ID with "Sign in with Apple" enabled.
3. Identifiers -> create a **Services ID** (this is `APPLE_CLIENT_ID`), enable Sign in with Apple, configure it with domain `forum.fractalreality.ca` and return URL `https://forum.fractalreality.ca/auth/apple/callback`.
4. Keys -> create a key with "Sign in with Apple" -> download the `.p8` file (one chance), note the Key ID.
5. Secrets: `APPLE_CLIENT_ID` (the Services ID string), `APPLE_TEAM_ID` (top right of the developer portal), `APPLE_KEY_ID`, and `APPLE_PRIVATE_KEY` (paste the whole `.p8` file contents including the BEGIN/END lines).

Notes: Apple posts the callback (form_post) rather than redirecting with a GET; the Worker handles both. Apple sends the user's name only on the very first authorization, and users may choose to hide their email (you get a private relay address).

## Design notes

- Sessions are stateless HMAC-signed cookies (30 days); sign-out clears the cookie. No session table.
- id_tokens are accepted directly from the provider's token endpoint over TLS (code exchange), with iss/aud/exp checked; signatures are not re-verified against JWKS because the channel itself authenticates the issuer.
- Every state-changing POST requires a same-origin Origin/Referer header (CSRF).
- All HTML is escaped; post bodies render as plain text with preserved line breaks (no markdown yet).
- Rate limit: one post per 20 seconds per user. Deletes are soft (rows keep their place; bodies are hidden).
- Moderation: admins and mods can lock/unlock threads, delete threads, and delete posts, from the thread page.
- Costs: the Workers free tier (100k requests/day) and D1 free tier (500 MB) are far beyond what a young forum needs.

## Revision history

- 2026-11-14 v1.0: initial build. Worker + D1 forum, four OAuth providers, five seeded places, guidelines page, moderation, local dev login; verified locally end to end (sign-in, thread, rate limit, reply).
