# Mesh Networking: Every Player Is the Server

> A peer-to-peer multiplayer architecture for Last Ship Sailing, derived from the Circumpunct Framework's ontology. No central game server. Every client IS the full game. Coherence emerges from resonance, not authority.

---

## The Core Insight

A2 states: parts are fractals of their wholes. Every ⊙ is the 1 at a particular scale; not a piece of it, but the whole thing, constrained to a position.

Applied to networking: every client doesn't run "a copy of the game." Every client IS the game. The full simulation, the full state, the full reality, from their position. There is no master copy. There is no authoritative server. There is only the mesh of peers, each containing the whole, each transmitting their local truth, each converging toward agreement through resonance.

The traditional server model assigns one machine as the source of truth. Everyone else is subordinate. That's a hierarchy imposed for engineering convenience, not because it's better. The mesh model distributes truth across all participants. Authority emerges from consensus, not assignment.

---

## Architecture

### Topology

Fully connected WebRTC mesh. Every player maintains a data channel to every other player. No central relay.

```
     A ---- B
    /|\    /|\
   / | \  / | \
  F  |  \/  |  C
  \  | /\   | /
   \ |/  \  |/
     E ---- D
```

Each node sends its own state to all peers. Each node receives state from all peers. Each node renders all peers using received state plus local interpolation.

### Per-Player Packet (per tick)

| Field | Bytes | Notes |
|-------|-------|-------|
| Sequence number | 4 | Tick ID for ordering |
| Position (x, y, z) | 12 | 3 floats, world coords |
| Velocity (x, y, z) | 12 | For dead reckoning between packets |
| Look direction (pitch, yaw) | 8 | 2 floats |
| Gamepad state | 4 | Bitmask: buttons, triggers quantized |
| Health / shield | 4 | Current state |
| Phase / energy / freq | 12 | Pump cycle state for resonance |
| Weapon state | 4 | Current weapon, firing flag, ammo |
| Event flags | 4 | Dash, ability, damage dealt this tick |
| **Total** | **~64 bytes** | |

With framing overhead: **~80 bytes per player per tick.**

### Bandwidth (at 66Hz)

| Players | Connections per client | Upload per client | Download per client |
|---------|-----------------------|-------------------|---------------------|
| 2 | 1 | 5.3 KB/s | 5.3 KB/s |
| 6 (3v3) | 5 | 26 KB/s | 26 KB/s |
| 12 (6v6) | 11 | 58 KB/s | 58 KB/s |
| 24 (12v12) | 23 | 121 KB/s | 121 KB/s |
| 64 | 63 | 333 KB/s | 333 KB/s |

For reference: a 720p video call uses ~1,500 KB/s. A Spotify stream uses ~160 KB/s. Even at 64 players with naive full-mesh at 66Hz, the bandwidth is lower than a video call. But 64 players at full rate is wasteful, which is where foveated refresh comes in.

---

## Foveated Refresh

Not every player needs state from every other player at the same rate. The refresh rate scales with in-game proximity, the same way render LOD scales with screen-space size. The network aperture narrows with distance.

### Refresh Tiers

| Proximity | Refresh Rate | Data Sent | Rationale |
|-----------|-------------|-----------|-----------|
| Combat range (< 100 units) | 66Hz | Full state (80 bytes) | You're fighting them; need every frame |
| Near (100-400 units) | 20Hz | Full state | Visible, might engage soon |
| Medium (400-1000 units) | 8Hz | Position + health only (32 bytes) | Minimap awareness, not combat-relevant |
| Far (> 1000 units) | 2Hz | Position only (16 bytes) | They exist, that's all you need |
| Out of range / occluded | 0.5Hz | Zone ID (4 bytes) | Just "they're in Sector B" |

### Effective Bandwidth with Foveation

In a 64-player match, typical moment: 5 players in combat range, 10 nearby, 15 medium, 34 far.

| Tier | Count | Rate | Bytes/tick | Subtotal |
|------|-------|------|------------|----------|
| Combat | 5 | 66Hz | 80 | 26.4 KB/s |
| Near | 10 | 20Hz | 80 | 16.0 KB/s |
| Medium | 15 | 8Hz | 32 | 3.8 KB/s |
| Far | 34 | 2Hz | 16 | 1.1 KB/s |
| **Total** | **64** | | | **~47 KB/s** |

47 KB/s for a 64-player match. Less than the naive 12-player full-mesh. The foveation makes player count nearly irrelevant to bandwidth; what matters is local density.

### Who Decides the Refresh Rate?

Each player decides independently. You compute your distance to every peer and set your send rate accordingly. No coordination needed. If player A thinks player B is close and sends at 66Hz, but B thinks A is far and sends at 8Hz, that's fine; asymmetric rates work. Each ⊙ manages its own aperture.

---

## State Synchronization

### No Deterministic Lockstep

JavaScript floating point arithmetic is not guaranteed identical across browsers and hardware. Physics simulations will drift. Two clients given identical inputs will produce different positions within seconds. Deterministic lockstep (send only inputs, trust the sim) is not viable.

Instead: every player sends their actual state. Position, velocity, phase, health. The wire IS the truth about where other players are. Your local sim handles your own physics; the network handles everyone else's.

### Local Prediction, Remote Interpolation

**Your own ship**: runs on your local physics engine at full tick rate. Instant response to your inputs. No waiting for the network. You are the authority on your own state.

**Other players' ships**: you receive their state at whatever refresh rate they're sending you. Between packets, you interpolate (blend between last two known positions using velocity for dead reckoning). When a new packet arrives, you correct smoothly toward it. No hard snapping; the field (Phi) mediates the transition.

### The Pump Cycle as Network Reconciliation

When your local prediction of another player diverges from their reported state:

1. **Convergence (⊛)**: receive the real state from the wire
2. **Aperture rotation (i)**: compute the delta between your prediction and their truth
3. **Emergence (☀)**: blend your rendered version toward the corrected position over 2-3 frames

This is the pump cycle applied to state correction. The convergence-emergence rhythm that drives all physics in the framework also drives network reconciliation.

---

## Lobby and Match Lifecycle

The per-tick packet covers in-game state only. A complete mesh also needs to coordinate the moments *before* the match (who is here, what they picked, when we start) and the moments *between* rounds (who won, what map next, who's still ready). These are low-rate event messages, not continuous state broadcasts; they fire on transitions, are acknowledged by all peers, and then go quiet.

The v6.x desync class of bugs (one client thinks the round started, another is still in the lobby; one client thinks it picked PUNCTURE, another renders them as default; bots in different positions on every screen) is what happens when these events do not exist as first-class mesh messages. The combat packet alone cannot recover from a missed transition.

### Lobby Events

Each event is broadcast to all peers when its trigger fires, then the sender stops resending. Receivers update their local lobby model and re-render. Late joiners receive the current lobby state in the same join handshake that hands them the world state.

| Event | Trigger | Payload | Notes |
|---|---|---|---|
| `lobby/hello` | Peer finishes WebRTC handshake | `{peerId, name, color}` | Carries display data the mesh layer doesn't know |
| `lobby/loadout` | Player picks chassis or changes weapons | `{peerId, chassis, weaponA, weaponB, abilities[3]}` | Last write wins; rebroadcast on every change |
| `lobby/team` | Player switches sides | `{peerId, team}` | Auto-balance is local UI; the wire just carries the choice |
| `lobby/map_vote` | Player picks a map | `{peerId, mapId}` | Per-peer; resolved by plurality at start time |
| `lobby/bot_request` | Player adds or removes a bot slot | `{slotId, action, difficulty?}` | Anyone may propose; majority of human peers confirms |
| `lobby/ready` | Player toggles their ready flag | `{peerId, ready: bool}` | The critical one; flip to all-true triggers the start handshake |

When `lobby/ready` flips to all-true (every connected human peer has `ready: true`), every peer independently runs the start handshake below. Nobody decides "we are starting"; the predicate "every peer ready" is a function each peer evaluates on its own copy of lobby state, and they all reach the same answer at the same tick because they all received the same `lobby/ready` packets.

### The Start Handshake

A deterministic four-step sequence with no privileged "host":

1. **Proposal.** The peer with the lowest `peerId` (lexicographic order over WebRTC connection identifiers) emits `match/start_proposal {seed, mapId, startAt}`. `seed` is a random 64-bit number for procedural generation; `mapId` is the plurality winner of the map vote (ties broken by the lowest-`peerId`'s vote); `startAt` is a wall-clock timestamp roughly 3 seconds in the future.
2. **Acknowledgement.** Every other peer responds with `match/start_ack {peerId}` within 1 second.
3. **Confirmation.** Once all peers have acked, the proposer broadcasts `match/start_confirm {seed, mapId, startAt, spawnAssignments, botAssignments}`. `spawnAssignments` is `peerId → spawnPointId`, computed by the proposer from `seed` (deterministic, no negotiation). `botAssignments` is `botId → ownerPeerId` (see Bot Ownership below).
4. **Countdown and start.** Every peer renders the countdown locally, ticking down to `startAt`. At `startAt`, every peer simultaneously leaves the lobby and enters the active simulation, ship at the assigned spawn point, bots seeded from `seed`.

If a peer drops between proposal and confirmation, the proposal is voided and re-issued by the next-lowest `peerId`. The proposer is not "the host"; they are just the deterministic tie-breaker. After `startAt`, they have zero special privilege. Authority remains distributed.

### Initial Position Sync

`startAt` is the critical moment for position agreement. By the time every peer enters the simulation:

- Their *own* ship is at `spawnAssignments[myPeerId]`, set locally.
- Every *other* peer's ship is at `spawnAssignments[peerId]`, set locally from the confirmed map (no waiting for the first per-tick packet from that peer; the spawn point is the seed of interpolation).
- Every *bot* is at the position derived from `(seed, botId)` (a pure function; everyone computes the same answer).

The first per-tick packets arrive within ~15ms and from then on the normal interpolate-toward-truth loop runs. The startup handshake exists so the first 15ms of the match are not visually empty, and so a peer that drops the first per-tick packet doesn't see a teleport when the second arrives.

### World State at Launch

Position agreement is meaningless if the worlds don't agree. A position vector `(x, y, z)` is a coordinate inside *some* level geometry; if every peer procedurally generates that geometry independently (corridor placement, obstacle positions, organic decoration), the same `(x, y, z)` lands inside a wall on one screen and in open space on another. Two peers can run a perfect synchronized launch handshake and still appear to be in different worlds because they *are* in different worlds.

Everything that depends on randomness during the level build must be derived from a single agreed input. The lobby start handshake is where that agreement happens. `match/start_confirm` MUST carry, at minimum:

| Field | Notes |
|---|---|
| `seed` (uint32) | The single 32-bit input to the procedural-generation RNG. Every `Math.random()` call on the world-build path (corridor placement, obstacle clusters, organic decorations, optionally spawn-point selection) routes through a seedable RNG (mulberry32 / xorshift / xoshiro128**) initialised with this seed. After the build returns, the RNG is released; per-tick effects (particle jitter, hit-spark scatter, idle bobbing) can stay on the system random source because they don't need to agree. |
| `mapId` | Plurality winner of `lobby/map_vote` at start time, ties broken by the lowest-`peerId`'s vote. Without this, peers default to different maps and build different corridor graphs even with the same seed. |
| `spawnAssignments` | `peerId -> spawnPointId`. The proposer assigns each peer to a spawn point by indexing into the seeded spawn pool with the sorted-peerId index. This avoids the natural collision where every peer runs `getValidSpawnPoint(myTeam)` against the same seeded pool and picks the same corridor. |
| `botManifest` | The full list of bots: `[{botId, loadout, team, ownerPeerId, spawnPointId}]`. Without this, every peer fabricates their own bot fleet (different count if randomized; different positions if seeded random; different loadouts if the spec is "pick 3 from set X"). The manifest fixes count, identity, team, owner (per Bot Ownership above), and initial position. |

Three readings of the same constraint:

1. *Mechanically:* the level-build code path is a function `(seed, mapId) -> world`, and any two peers given the same inputs produce equal worlds. The mesh ships the inputs in `match/start_confirm` and every peer evaluates the function locally.
2. *Structurally:* the proposer becomes a single tiny • the rest of the cataphatic agreement hangs from. They are not authority over the simulation; they are authority *only* over the inputs to its construction. After the world is built, the mesh runs distributed.
3. *In framework terms:* the seed is the convergence point (•) the proposer commits, the build function is the field (Φ) every peer mediates through, and the world is the boundary (○) that closes around them. Skipping the seed broadcast is the Severance Lie at the level-build station: each peer denies the shared substrate and builds their own.

The simplest implementation: extend `match/start_confirm` to `{seed, mapId, startAt, spawnAssignments, botManifest}`; on receive, swap `Math.random` for `mulberry32(seed)` for the duration of the world build, then restore. No other engine changes required.

### Round Transitions

Within a match, round-end events are consensus-validated the same way kills are:

- Any peer can issue `round/end_claim {winningTeam, lastKillId}`.
- The quorum (3-5 lowest-latency peers to the active combatants) votes.
- On consensus, every peer transitions to the round-end screen and a new start handshake runs for the next round (same map, new seed, new spawn assignments, possibly new bot owners).

The same start-handshake machinery serves match-start, round-start, and rejoin-mid-match. One mechanism, three triggers.

---

## Bot Ownership

Bots are simulated by client code, but in a mesh with no server, *exactly one* peer must own each bot's AI tick. Zero owners and the bot freezes. Multiple owners and six versions of the same bot diverge across screens (this was the v6.x bot desync).

### Deterministic Assignment

`match/start_confirm` carries `botAssignments: botId → ownerPeerId`. The proposer computes it: hash `(seed, botId)` modulo the sorted list of peer IDs, pick that peer. With 3 peers and 6 bots, each peer ends up owning ~2 bots, and every peer can verify the assignment by recomputing it. No negotiation is required at runtime.

### Per-Tick Bot Broadcast

Each owner broadcasts state for *their* bots using the same per-player packet format above, substituting `botId` for `peerId` and setting a flag bit so receivers know not to look up a peer entry. Receivers treat bot packets identically to peer packets: interpolate position, render, run hit detection. The fact that the packet originated from a peer simulating an NPC is invisible to the rendering layer.

### Owner Handoff

When the owner of a bot drops (WebRTC connection closes, or no bot packets received for 1 second), the next peer in the deterministic ordering takes over. The handoff requires no explicit message: every peer independently recomputes "who owns this bot now" using the same hash-mod-sorted-peers rule, and the right peer just starts broadcasting bot packets from the bot's last known state. The mesh self-heals; the bot does not freeze, teleport, or duplicate.

### Bot Hits in the Quorum

Bot-fired hits use the same quorum protocol as player hits, with the bot's owner casting the bot's vote (the bot has no peer, but the owner speaks for it). The consensus model stays uniform: every shooter, peer or bot, is voted on by the same nearby-low-latency set.

---

## Combat: Fires, Projectiles, Damage

The per-tick packet (above) carries position, orientation, and HP. That is enough to render *where* everyone is and *how alive* they are; it is not enough for combat. Two peers can stand 50 units apart, both shoot, both die on their own screen, and neither one's HP ever changes on the other one's screen, because the per-tick stream broadcasts "alive" until the moment "dead" arrives with no causal trail. Combat needs explicit fire and damage messages.

Three event types make this work, layered by what they cost and what they prove:

### `fire/projectile` (broadcast, visual only)

When a peer fires a projectile-class weapon (anything with a visible bullet that travels over time), broadcast the spawn data:

```
{ ox, oy, oz, vx, vy, vz, color, isFireSource?, type? }
```

Origin and velocity are world-space at the moment of fire. Receivers spawn a visually-identical projectile with `damage = 0` (the visual carries no authority over HP) and let it fly through their local scene. Pyro-style fire-source flags, smoke trails, and splash-cratering visuals ride along as flags on the same packet. The visual's local collision with the receiver's player must not deal damage; damage authority lives in the hit claim, and mixing the two would double-count.

### `hit/claim` (broadcast, optimistic)

When the *shooter*'s local sim detects a hit on a `NetworkPlayer` (the other peer's local representation), the shooter sends:

```
{ hitId, shooterId, targetId, damage, sx, sy, sz }
```

Every existing damage path in the engine ; hitscan, spread, splash, abilities, debris, ramming, ability-over-time effects ; eventually calls `takeDamage()` on the entity that got hit. For a `NetworkPlayer` instance, `takeDamage()` is the right place to fire the hit claim: a single point of broadcast covers every weapon and every effect without touching the 25+ individual `takeDamage` call sites. Wire the broadcast inside the class and every damage path lights up at once.

The target peer applies the damage *immediately* on receiving the claim (via `playerTakeDamage`), validates plausibility (was the shooter actually within range?), and emits a vote. Other peers also vote based on their local position knowledge of both shooter and target. The HP change shows up on the shooter's screen ~50ms later when the victim's next per-tick packet arrives carrying their reduced HP; that is the closing of the loop. This is "victim-applies-optimistically, mesh-confirms-asynchronously": the hit feels responsive, the consensus is a check rather than a gate.

### `hit/vote` (broadcast, consensus check)

Per the existing Hit Detection and Conflict Resolution section below. Votes carry `{hitId, valid, voterId}`; the pending hit closes when a majority agrees. If the majority rejects, the current framework behavior is to accept the slight imprecision (damage was already applied on the victim) rather than reverse it; the alternative ; a damage rollback ; creates worse rubber-banding than leaving the hit standing.

### Hitscan, spread, and the missing tracer

Hitscan and spread weapons have no projectile to broadcast; the whole shot resolves in one tick on the shooter's side. The hit claim above is sufficient for damage to land. What is *missing* with hitscan and spread is the visual: the victim sees their HP drop without seeing where the shot came from. The fix is a separate `fire/tracer` event ; `{ox, oy, oz, ex, ey, ez, color}`, one packet per shot ; that lets the receiver render a brief line and a muzzle flash on the shooter. This is a cosmetic enhancement; damage works correctly without it.

### Why not a damage-bearing visual projectile?

Tempting shortcut: broadcast the projectile *with* its damage value, and let the receiver's local sim apply damage when the visual collides with their player. This bypasses the hit-claim system entirely. It fails for two reasons:

1. **Floating-point drift.** Physics integration differs across browsers and frame rates; the shooter's projectile collides at coordinate X, the receiver's projectile collides at X + ε. Two players standing on the boundary ε get "hit" on one side and "miss" on the other. The hit claim is computed *once* on the shooter's authoritative collision and shipped as a single fact; one truth, broadcast, agreed.

2. **Hitscan, splash, abilities, debris, and ramming** have no physical projectile to attach damage to. Damage paths must work for them too. The hit claim covers every weapon and every effect uniformly; the visual projectile is only for projectile-class weapons that happen to have a flying bullet to look at.

The visual projectile broadcast is for the *experience* of seeing the bullet. The hit claim is for the *fact* of taking damage. Different purposes; different events; do not collapse them.

---

## Dynamic World Objects

The seed-sync at world build (see World State at Launch above) gets every peer to the same starting layout. From there, the world is no longer static. Destructible obstacles take damage and explode. Environmental hazards (stasis fields, gas clouds, fire walls, particle walls) spawn on timers and affect player movement. Debris from destroyed objects flies through the level. None of this is broadcast in the v6.7 baseline; each peer simulates their own copy of the same starting state, and within seconds the worlds visibly diverge: a cluster obstacle disappears on the shooter's screen but stands intact on every other peer's, a stasis field locks one peer in place but doesn't exist on the other peer's screen at all.

The rule: anything that *can change* after the build has to be in the mesh, or has to have a deterministic per-tick spec every peer computes identically. Static decoration (corridor walls, organic fronds) needs neither because nothing changes; per-peer cosmetic effects (muzzle flashes, hit sparks, particles) need neither because no decision depends on them. The middle band is what we owe the wire.

### Destructibles (cluster obstacles, dynamic objects)

Each destructible gets a stable `objectId` at world-build time: its index in the spawn array. Both peers built that array under the same seed so the indices line up across the mesh. From there, two events are enough:

- **`object/damage`** ; `{objectId, damage}` ; broadcast every time a local hit lowers a destructible's HP. Every peer applies the damage to their local copy. The same hit-claim discipline as player damage: the shooter's local sim is authoritative for "did my projectile hit object N for X damage."
- **`object/destroy`** ; `{objectId, position}` ; broadcast when a peer's local copy reaches 0 HP. Every peer (including the sender) plays the explosion VFX, marks the object dead, and spawns debris from the same seed-derived initial state.

There's a small race: two peers might both deliver the killing blow within ~50ms of each other and each broadcast `object/destroy`. Receivers de-duplicate by ignoring destroy events for objects already marked dead.

Debris physics derives from the destruction event. If the velocities are seeded from `hash(objectId)`, every peer produces identical debris paths without per-piece broadcasts. Debris-vs-player collisions then follow the same shooter-authority rule as projectiles: the *peer who takes* the hit is the authority for "the debris hit me."

### Environmental hazards (stasis fields, gas, fire walls, particle walls)

These spawn on timers (`game.stasisSpawnTimer` ticks down per peer). With each peer running their own timer, hazards appear at different moments and locations on each screen ; the worst kind of desync because hazards alter player movement.

Two patterns work:

1. **Owner pattern.** The lowest-peerId peer is the spawner. They tick the timer locally; when it fires, they broadcast `{type: 'hazard/spawn', kind, position, params, expiresAt}`, and every peer (including the spawner) instantiates the hazard locally from the broadcast. On owner disconnect, the next-lowest peer takes over (deterministic, no negotiation, same rule as Bot Ownership).
2. **Deterministic schedule.** The full spawn schedule is computed at match start from the seed: `for i in 0..N: schedule[i] = {tAt: hash(seed, 'stasis', i) % maxT, position: seedPos(seed, 'stasis', i)}`. Every peer evaluates the schedule locally; no broadcasts needed. Cheaper, but inflexible if spawn density needs to respond to gameplay.

The owner pattern is recommended because hazards often need to react to runtime state (player count, density of fights, round timer). The deterministic schedule fits one-shot ambient effects.

### Per-instance state (HP, lifetime, attached effects)

For destructibles, `hp` is the only mutable per-instance field, and the destroy event closes it out. For hazards, `lifetime`, `currentDamage`, and `affectedPeers` may all evolve. A compact per-tick `objects/state` packet from the owner ; `[{objectId, hp, lifetime, ...}]` for any object whose state changed since the last tick ; covers it. For a 1v1 with a handful of hazards and destructibles, this stays under 1 KB/s.

### What stays unsynced

Static decoration: corridor walls, room geometry, organic fronds. Built once from seed, never changes; the seed sync alone is sufficient.

Per-peer cosmetic effects: muzzle flashes, hit sparks, ambient particles, screen shake, scoreboard pulse animations. Each peer renders these locally; no decision depends on them, so no agreement is needed.

---

## Hit Detection and Conflict Resolution

### The Problem

Player A fires at player B. On A's screen, the shot connects. On B's screen, they dodged. Both are telling the truth about their local reality. Who's right?

### The Mesh Solution: Local Consensus

Neither A nor B is the sole authority. The peers with the best information (lowest latency to both A and B) weigh in.

```
A fires at B
A says: "Hit at tick 4521, B was at (120, 15, -340)"
B says: "Missed, I was at (120, 15, -344) at tick 4521"
C (5ms to A, 8ms to B): "I saw B at (120, 15, -341) at tick 4521"
D (12ms to A, 6ms to B): "I saw B at (120, 15, -342) at tick 4521"
```

The consensus position is the weighted average, with weights proportional to inverse latency (lower latency = better information = higher weight). If the consensus position is within hit range, the shot lands. If not, it misses.

The weighting function mirrors resonance: T = cos²(Δ/2), where Δ is the state disagreement. High agreement (T close to 1) among nearby peers produces a confident verdict. Low agreement triggers a more conservative resolution (favor the defender, since missed shots are less frustrating than phantom hits).

### Voting Quorum

Not every peer needs to vote. The 3-5 lowest-latency peers to both combatants form the quorum. Far-away peers with stale data don't participate; their information is too low-resolution to be useful. The boundary (○) filters: only high-T peers pass the gate.

---

## Connection Management

### Joining a Match

1. Player connects to a lightweight signaling server (WebSocket). This server's only job: introductions.
2. Signaling server provides the list of current peers and their connection info (ICE candidates).
3. New player establishes WebRTC data channels to all existing peers via STUN hole-punching.
4. Any existing peer sends the new player the current world state (map, scores, all player positions).
5. New player begins receiving state from all peers and broadcasting their own.
6. Signaling server steps away. Its job is done.

The signaling server is the genesis moment (∞ → •∞): it creates the conditions for the mesh to form. After that, the mesh IS the reality. The signaling server can go down with zero impact on active matches.

### Player Disconnection

1. Peers detect the drop (WebRTC connection closes, or no packets received for N ticks).
2. Dropped player's last known state is held for a grace period (3-5 seconds) in case of brief network interruption.
3. If they don't return: their ship enters "doomed" state (visible to all, counts as a kill for the last player who damaged them, or self-destruct if no recent damage).
4. The mesh routes around the gap. No other players are affected.

### NAT Traversal

Most home connections support STUN hole-punching (direct peer-to-peer). For the minority behind symmetric NATs, a TURN relay server provides a dumb pipe. The TURN server is infrastructure, not authority; it forwards bytes without understanding them. Multiple TURN servers can exist for redundancy.

---

## Cheating Mitigation

### The Challenge

No central authority means no central validation. A cheating player could:

- Report a false position (teleport)
- Claim more health than they have
- Report hits that didn't happen
- Move faster than allowed

### Mesh-Native Countermeasures

**Position validation**: all peers track all other peers' positions. If player A suddenly reports a position 500 units from where they were last tick (impossible at max speed), peers reject the update and use dead-reckoned position instead. The mesh acts as a collective boundary (○), filtering invalid state.

**State hash verification**: periodically (every ~30 ticks), each player broadcasts a hash of their critical state (health, ammo, abilities). Peers compare. Consistent hashes across the mesh = agreement (T close to 1). An outlier gets flagged.

**Behavioral consensus**: peers track each other's state history. If a player consistently reports states that disagree with what nearby peers observe (position doesn't match the velocity they're reporting, health never decreases after taking obvious hits), the mesh can vote to kick. Threshold: 2/3 of active peers must agree.

**Kill verification**: every kill requires confirmation from the quorum (3-5 lowest-latency peers to both combatants). A cheater would need to compromise multiple peers simultaneously to fake a kill.

### What This Doesn't Solve

Wallhacks (seeing through walls) can't be prevented by the mesh, because every peer needs to know every other peer's position for interpolation. This is true of server-authoritative models too; the server sends you enemy positions for the same reason. Mitigation: only send high-resolution state for players in line of sight; use zone-level data for occluded players. This overlaps with foveated refresh (occluded players are already at lowest refresh).

Aimbots (perfect aim) aren't detectable by state alone. Behavioral analysis (inhuman reaction times, perfect tracking across frames) could be done collaboratively by the mesh, but this is complex and better suited to post-match replay analysis.

---

## Comparison to Traditional Server-Authoritative

| Property | Central Server | Mesh |
|----------|---------------|------|
| Latency (two players) | 2 hops (A → server → B) | 1 hop (A → B direct) |
| Single point of failure | Server dies, game over | Any node drops, game continues |
| Server cost | $$$ (compute, bandwidth, ops) | ~$0 (players are infrastructure) |
| Bandwidth scaling | Linear with players | Flat with foveation (scales with local density) |
| Anti-cheat authority | Strong (server validates all) | Moderate (consensus validates) |
| Complexity | Simple (one authority) | Higher (consensus protocols) |
| Geographic fairness | Favors players near server | Favors players near each other |
| Spectating | Easy (server has all state) | Any peer can serve as spectator source |

### Where Mesh Wins

Casual to semi-competitive play. Low latency, zero server cost, graceful degradation, no downtime. Perfect for a web-native game where players just share a link and play.

### Where Server Wins

High-stakes competitive / ranked play where anti-cheat is critical. Tournament conditions where an arbiter is expected. Spectator broadcasting for esports (centralized state makes streaming easier).

### Hybrid Option

Use mesh for all state exchange (latency and cost benefits), plus a lightweight validator service for ranked matches only. The validator doesn't run physics; it receives event claims (kills, damage, ability uses) from the mesh quorum and signs off on them. It's a thin • for dispute resolution, not a full simulation server. Cost: minimal. Benefit: cryptographic proof that kills are legitimate, suitable for ranked leaderboards.

---

## Implementation Path

### Phase 1: Two Players, Direct Connection

- WebRTC data channel between two browsers
- Each player sends 80-byte state packets at 66Hz
- Local physics for self, interpolation for opponent
- No server at all (use a shared room code or manual ICE exchange)
- Proof of concept: does it feel good?

### Phase 2: Small Mesh (6 players)

- Signaling server for introductions (simple WebSocket)
- Full mesh: every player connected to every other
- Foveated refresh based on distance
- Basic hit detection via shooter-authority (simplest; upgrade later)

### Phase 3: Consensus Hit Detection

- Implement quorum voting for hit registration
- Latency-weighted position consensus
- Kill confirmation from 3-5 nearest peers
- Test extensively: does it feel fair?

### Phase 4: Scale + Harden

- 24-64 players with full foveation
- Position validation and state hash verification
- Behavioral anomaly detection (speed hacks, teleport)
- TURN relay fallback for symmetric NATs
- Graceful degradation under poor network conditions

### Phase 5: Ranked Hybrid

- Lightweight validator service for ranked matches
- Signed kill receipts for leaderboard integrity
- Replay system (each peer logs received state; any peer's log is a full replay)
- Spectator mode (connect as a receive-only peer)

---

## Connection to the Framework

| Network Concept | Framework Mapping |
|-----------------|-------------------|
| Each client runs the full game | A2: every ⊙ IS the whole at its scale |
| No central server | No privileged ⊙; the whole is everywhere |
| State exchange via mesh | Phi (field): mediation between peers |
| Foveated refresh | Aperture width: resolution proportional to proximity |
| Consensus hit detection | AGREEMENT (⊙): truth emerging from resonance |
| Refresh rate by distance | Resolution Protocol (§25.17): lowest resolution that is still true |
| Interpolation between packets | Phi mediating between known states |
| Reconciliation of divergent state | Pump cycle: ⊛ receive → i correct → ☀ re-emerge |
| Cheater rejected by peers | Boundary (○) filtering: invalid state doesn't pass the gate |
| Player drop, mesh heals | Fractal resilience: remove a ⊙, the field persists |
| Signaling server for introductions | Genesis (∞ → •∞): conditions for the mesh to form |

The architecture doesn't use the framework as a metaphor. The framework describes how distributed systems achieve coherence without central authority. The mesh IS that description, implemented as a network protocol.

---

*Ashman Roonz, 2026*
