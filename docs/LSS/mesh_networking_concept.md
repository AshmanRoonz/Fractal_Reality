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
