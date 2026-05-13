# LSS Companion Hub: Architecture Sketch

Created: 2026-05-01
Last updated: 2026-05-01
Version: 0.1

> A web hub that lives next to the game, hosts the social and creative loops the game itself can't carry (leaderboards, events, forum, custom content gallery), and links bidirectionally back into LSS so a custom map made on the hub opens in-game with one click.

## 1. Goal: three retention loops, one hub

The game is HTML; players already have the runtime (their browser). The hub adds nothing they have to install. What it adds is the loops the round-based game alone can't carry:

- **Competitive loop**: leaderboards (per chassis, per loadout, per map, weekly + all-time). Brings players back to defend a position.
- **Social loop**: scheduled events (tournaments, themed nights, "all-Phi-chassis" gimmick rounds), forum threads. Brings players back at specific times, with specific people.
- **Creative loop**: a gallery of player-made maps, walls, sounds, frames, and ships, with one-click "play this in-game" buttons. Brings players back to publish, browse, and remix.

The hub doesn't replace the game; it surrounds it. The game ships round-based combat; the hub ships everything else that gives the rounds context.

## 2. System diagram

```
   Player browser
   ┌────────────────────────────────────────┐
   │  LSS game (lss.html)                   │
   │   - localStorage: player_id, settings  │
   │   - in-game UI: "Share to Hub"         │
   │   - import endpoint: ?map=<hub_id>     │
   └─────────┬──────────────────────────────┘
             │ deep links + REST
             ▼
   ┌────────────────────────────────────────┐
   │  Hub (hub.html, single-page)           │
   │   - Leaderboards / Events / Forum /    │
   │     Content Gallery / Profile          │
   │   - vanilla JS + supabase-js           │
   └─────────┬──────────────────────────────┘
             │ supabase-js
             ▼
   ┌────────────────────────────────────────┐
   │  Supabase                              │
   │   - Postgres (tables below)            │
   │   - Storage bucket (sounds, ship art)  │
   │   - Auth (anonymous + email claim)     │
   │   - Row-level security policies        │
   │   - Realtime channels (forum, events)  │
   └────────────────────────────────────────┘
```

Both `lss.html` and `hub.html` are static; everything dynamic lives in Supabase. No build step, no framework, no rendering library; consistent with the `feedback_no_threejs` rule.

## 3. Player identity model: anonymous-first, claimable

Friction is the enemy. A player should be able to post a leaderboard score, browse content, and even upload a custom map without ever creating an account. They should be able to *claim* their handle later if they want to protect it across devices or recover it if localStorage clears.

- **First visit (game or hub)**: generate a UUID v4; store as `player_id` in localStorage. Create a row in `players` with this UUID, a randomly-suggested handle (e.g., `nimble-titan-3417`), and `claimed = false`.
- **Anonymous play**: scores, posts, and uploads are signed with `player_id`. Row-level security says: a row can only be edited/deleted by its `player_id` owner (verified via Supabase JWT containing the UUID).
- **Claim flow** (optional): player enters an email, gets a magic link, the link binds the `player_id` to an auth user. After claim, `claimed = true`; player can sign in on a new device and recover their handle.
- **Cross-device without claim**: an "export ID" button generates a one-time recovery code the player can paste on another device. No email needed.

This is the lowest-friction model that still keeps the leaderboard honest enough to be worth posting on. Trade-off: a determined cheater can spawn fresh UUIDs forever; we mitigate via per-IP rate limits on score submissions and (later) a server-side replay validator for top-100 scores.

## 4. Database schema (Supabase / Postgres)

Eleven tables; all timestamps `created_at timestamptz default now()`.

```
players
  id              uuid pk
  handle          text unique
  claimed         boolean
  email           text null
  created_at      timestamptz

scores
  id              uuid pk
  player_id       uuid fk -> players
  map_id          uuid fk -> content_items (nullable; null = official map)
  official_map    text null         (e.g., "downtown_a", null if custom)
  chassis         text              (• / Φ / ○)
  loadout         text              (one of seven loadout codes)
  metric          text              (kills, time, score, ...)
  value           numeric
  replay_url      text null         (Storage path)
  verified        boolean default false
  created_at      timestamptz

events
  id              uuid pk
  host_id         uuid fk -> players
  title           text
  description     text
  starts_at       timestamptz
  ends_at         timestamptz
  rules           jsonb             (chassis lock, map list, etc.)
  cover_url       text null
  created_at      timestamptz

event_signups
  event_id        uuid fk
  player_id       uuid fk
  status          text              (going / interested / declined)
  primary key     (event_id, player_id)

forum_threads
  id              uuid pk
  author_id       uuid fk -> players
  title           text
  category        text              (general / strategy / showcase / bugs)
  pinned          boolean default false
  locked          boolean default false
  created_at      timestamptz

forum_posts
  id              uuid pk
  thread_id       uuid fk -> forum_threads
  author_id       uuid fk -> players
  body_md         text              (markdown; sanitized on render)
  created_at      timestamptz

content_items
  id              uuid pk
  author_id       uuid fk -> players
  type            text              (map / wall / sound / frame / ship)
  schema_version  text              (e.g., "lss-map-v1")
  title           text
  description     text
  payload         jsonb             (the content, schema below)
  asset_url       text null         (Storage path; sounds, ship art)
  tags            text[]
  download_count  int default 0
  play_count      int default 0
  created_at      timestamptz

content_likes
  content_id      uuid fk
  player_id       uuid fk
  primary key     (content_id, player_id)

reports
  id              uuid pk
  reporter_id     uuid fk -> players
  target_type     text              (content / forum_post / score)
  target_id       uuid
  reason          text              (offensive / spam / cheating / broken / other)
  detail          text
  status          text              (open / reviewed / actioned / dismissed)
  created_at      timestamptz
  reviewed_at     timestamptz null

admin_actions
  id              uuid pk
  admin_id        uuid fk -> players
  target_type     text
  target_id       uuid
  action          text              (hide / delete / warn / unban / etc.)
  note            text
  created_at      timestamptz

leaderboard_views (materialized view, refreshed every 5 min)
  category        text              (chassis × loadout × map × window)
  player_id       uuid
  handle          text
  best_value      numeric
  rank            int
```

**Row-level security** (sketched, not exhaustive):

- `players`: read-public on (id, handle, claimed); write-self only.
- `scores`, `forum_posts`, `forum_threads`, `content_items`: insert by any authenticated player; update/delete by author only; read-public.
- `reports`: insert by any player; read by admins only.
- `admin_actions`: insert + read by admins only.

## 5. Content schemas (versioned JSON)

Five content types, each with a v1 schema we commit to before launch. All payloads carry `schema_version` so we can migrate cleanly later.

### `lss-map-v1`

```json
{
  "schema_version": "lss-map-v1",
  "name": "string",
  "size": [width, height, depth],
  "spawn_points": [{ "team": "a|b", "pos": [x, y, z], "rot": [yaw, pitch] }],
  "geometry": [
    { "type": "wall", "bounds": [...], "wall_id": "uuid|builtin" },
    { "type": "floor", "bounds": [...], "material": "string" }
  ],
  "props": [{ "kind": "string", "pos": [...], "params": {} }],
  "lighting": { "ambient": [r, g, b], "sources": [...] },
  "round_rules": { "time_limit": int, "score_limit": int, "respawn": "wave|instant" }
}
```

### `lss-wall-v1`

```json
{
  "schema_version": "lss-wall-v1",
  "name": "string",
  "shader": "string",
  "uniforms": { "color": [r, g, b], "pattern": "string" },
  "collision_profile": "solid|passthrough|bounce"
}
```

### `lss-sound-v1`

```json
{
  "schema_version": "lss-sound-v1",
  "name": "string",
  "category": "footstep|weapon|ambient|voice|ui",
  "asset_url": "supabase://...",
  "duration_ms": int,
  "loop": boolean,
  "volume_default": float
}
```

### `lss-frame-v1`

```json
{
  "schema_version": "lss-frame-v1",
  "name": "string",
  "chassis_class": "•|Φ|○",
  "stats": { "hp": int, "speed": float, "shield_cap": float },
  "art_url": "supabase://...",
  "hitbox": { "type": "string", "params": {} }
}
```

### `lss-ship-v1`

```json
{
  "schema_version": "lss-ship-v1",
  "name": "string",
  "frame_id": "uuid",
  "loadout": ["weapon_id", "weapon_id", "ability_id"],
  "cosmetics": { "decals": [...], "trail": "string" }
}
```

Validation lives in a single `validate(content_type, payload)` function shared by hub upload and in-game import; either both accept it or both reject it.

## 6. Game ↔ Hub integration points

This is the unlock. Five touchpoints, all bidirectional where possible:

1. **Deep link in**: `lss.html?map=<hub_id>` loads a custom map directly into a play session. Same pattern for `?ship=<hub_id>`, `?wall_pack=<hub_id>`, etc. The game fetches `content_items` row, validates, applies.
2. **Share-to-hub button** (in-game): on round end, button posts the run to `scores` (with optional replay blob to Storage). On the map editor, button publishes to `content_items` as a draft.
3. **Hub "Open in game" button**: every content item card has a button that opens `lss.html?map=<id>` in the game tab.
4. **Profile sync**: hub profile page reads from `players` + `scores`; in-game profile widget reads same data via the supabase-js client.
5. **Event hooks**: when an event is live (current time between `starts_at` and `ends_at`), the in-game lobby shows a banner with rules and a one-click "Join event playlist" button.

The pattern: the game and the hub talk to the same Supabase project; neither needs to know the other exists at the protocol level. They share schemas and a player ID.

## 7. Moderation: auto-publish + report flow

Per your decision; this is the right call for early growth, with safeguards:

- **All content auto-publishes** on upload. Forum posts, custom maps, ship art, sounds: live immediately.
- **Report button** on every public-facing item. Reports go into `reports` with reason + detail.
- **Per-player rate limit** on uploads (e.g., 10 content items per day, 50 forum posts per day) to slow spam without blocking real activity.
- **Report queue**: admin page (`hub.html#admin`, gated by admin role) lists open reports, sortable by report count. One-click "hide" (sets `hidden = true`, item stops appearing publicly but isn't deleted) or "delete" (hard delete; logged to `admin_actions`).
- **Auto-hide threshold**: if an item gets N reports from N distinct players in M minutes (start with N=3, M=60), auto-hide pending review. Conservative; biased toward visibility, not censorship.
- **No-edit window**: forum posts can be edited by author within 1 hour of posting; after that, they're frozen (prevents bait-and-switch).
- **Banned content categories**: real-name impersonation, doxxing, illegal content. Spelled out in a short ToS modal on first visit.

Sounds are the riskiest content type because audio uploads can be anything; consider a transcoding step (Supabase Edge Function calling ffmpeg) that re-encodes uploads to a fixed format and length cap, which strips embedded metadata and limits damage.

## 8. Tech stack: zero rendering libs

Per `feedback_no_threejs`: vanilla HTML/CSS/JS only.

- **Hub front-end**: one `hub.html` file with sectioned views (`#leaderboards`, `#events`, `#forum`, `#content`, `#profile`, `#admin`). Hash-routed; no router library. Plain `<table>` for leaderboards, plain `<form>` for posting.
- **Realtime**: Supabase Realtime over WebSocket for live forum updates and event chat; supabase-js handles it.
- **Markdown**: lightweight inline parser (under 5KB) for forum post bodies; or, simpler, allow only a curated subset (bold, italic, code, links). I lean toward the latter for v1.
- **Images and audio**: served straight from Supabase Storage with presigned URLs. No CDN layer in v1.
- **Auth**: Supabase Auth, anonymous-first; email magic links for claim flow.

## 9. Free-tier sizing

Supabase free tier (as of mid-2026, verify before launch):

- 500 MB Postgres: enough for ~500K forum posts or ~50K content items with small JSON payloads. Plenty for v1.
- 1 GB Storage: ~500 average-size sounds + ~2K ship art images. Tight if community grows; budget the `pro` tier ($25/mo) once Storage starts filling.
- 2 GB egress/month: generous for v1; a custom-map JSON payload is small.
- 50K monthly active auth users: not a concern at this stage.

Cost ceiling for the first six months should be $0 to $25.

## 10. MVP scope (rollout order)

Five-stage rollout; each stage shippable on its own:

**Stage 1 (week 1): Identity + leaderboards.** `players` table, anonymous-first ID, score posting from in-game, one global leaderboard view on hub. No claims, no events, no forum. Proves the game ↔ hub data path.

**Stage 2 (week 2): Content gallery (read-only).** `content_items` table, all five schemas defined and frozen, gallery page on hub showing items. Upload disabled; you seed it with 3-5 example maps yourself. Proves the schema works end-to-end.

**Stage 3 (week 3): Content uploads + in-game import.** Upload form on hub; in-game `?map=<id>` deep link; "Share to Hub" button in the map editor. The creative loop starts working.

**Stage 4 (week 4): Forum + reports + moderation queue.** `forum_threads`, `forum_posts`, `reports`, admin page. The social loop starts working.

**Stage 5 (week 5): Events + claim flow.** `events`, `event_signups`, in-game event banner; magic-link claim for handles. The competitive cadence starts working.

After stage 5: iterate based on what the community actually does. Don't pre-build features for behaviors you haven't seen yet.

## 11. Open questions and decisions still owed

These don't block stage 1, but they need answers before stage 3:

1. **Replay format and storage.** Does the game have a deterministic replay format yet, or do we capture video? Replay JSON is cheap; video is expensive on egress.
2. **Map editor in-game vs hub-side.** Is the map editor part of `lss.html` already, or is it a separate `lss-editor.html`? Affects where the "Share to Hub" button lives.
3. **Admin role bootstrap.** How does the first admin (you) get the role flag? Probably a one-time SQL update; document it.
4. **Search.** Postgres full-text on `content_items.description` and `forum_posts.body_md` is free and good enough; commit to it now to avoid bolting search on later.
5. **i18n.** English-only for v1; what's the policy if a non-English community forms?
6. **Discord parity.** Many web games have a Discord that does most of what the forum does. Do we cede the social loop to Discord and use the hub forum as a long-form archive only, or compete?

## 12. Falsification handle

We'll know this architecture is wrong if:

- Stage 1 ships and nobody posts a score voluntarily; the in-game "Share to Hub" button has < 5% click rate. Means the social motivation isn't there yet, and a hub won't fix it; need to rethink the game's win-state framing first.
- Stage 3 ships and uploads come in but the "Open in game" button has < 20% click-through from the gallery. Means the content discovery loop is broken, not the upload pipeline.
- Stage 4 ships and the report queue floods with false positives. Means the moderation tooling needs a "downvote a report" mechanism before it's usable.

If any of these triggers, stop adding stages and fix the loop that broke.

---

## Revision history

- 2026-05-01 v0.1: initial sketch; backend = Supabase, moderation = auto-publish + report flow, identity = anonymous-first claimable, five-stage rollout, schemas v1 frozen at draft level
