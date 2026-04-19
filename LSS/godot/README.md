# Last Ship Sailing Godot

This is the start of a real Godot 4 migration, not a throwaway mockup.

What is already here:

- A standalone Godot 4 project in [godot/project.godot](/C:/Users/ashro/LSS/godot/project.godot)
- Ported chassis/loadout data from the web version in [godot/scripts/game_data.gd](/C:/Users/ashro/LSS/godot/scripts/game_data.gd)
- A round-based combat slice with warmup, round end, score tracking, and ship switching in [godot/scripts/player_ship.gd](/C:/Users/ashro/LSS/godot/scripts/player_ship.gd), [godot/scripts/enemy_ship.gd](/C:/Users/ashro/LSS/godot/scripts/enemy_ship.gd), and [godot/scripts/main.gd](/C:/Users/ashro/LSS/godot/scripts/main.gd)
- The Nexus map port with chamber/tunnel arena geometry, spawn points, navigation points, and map wall queries in [godot/scripts/arena_map.gd](/C:/Users/ashro/LSS/godot/scripts/arena_map.gd)
- Real GLB ship model imports with procedural fallback, engine plumes, shields, and muzzle flashes in [godot/scripts/ship_visuals.gd](/C:/Users/ashro/LSS/godot/scripts/ship_visuals.gd) and [godot/assets/ships](/C:/Users/ashro/LSS/godot/assets/ships)
- GPU-instanced tracers through `MultiMeshInstance3D` in [godot/scripts/tracer_pool.gd](/C:/Users/ashro/LSS/godot/scripts/tracer_pool.gd)
- Ported ship abilities and cores for player and enemies, plus a presentation-heavy HUD pass with a circumpunct reticle, enemy markers, round banner, cockpit gun flashes, and minimap in [godot/scripts/hud.gd](/C:/Users/ashro/LSS/godot/scripts/hud.gd) and [godot/scripts/hud_overlay.gd](/C:/Users/ashro/LSS/godot/scripts/hud_overlay.gd)

Current controls:

- `WASD` move
- `Space` / `Ctrl` vertical thrust
- `Shift` dash
- `Left Mouse` fire
- `R` reload
- `1` / `2` / `3` abilities
- `F` core
- `Q` / `E` cycle ships
- `Esc` release or recapture the cursor

What this prototype is for:

- Validate how the ships feel under Godot movement/input
- Start using GPU-native rendering paths for repeated effects
- Exercise a real player-vs-enemy round loop instead of a static target range
- Validate chamber/tunnel combat flow instead of an open-box placeholder arena
- Separate data, visuals, and gameplay systems early so the port stays maintainable
- Push the Godot version closer to the web build's readibility and combat presentation instead of only porting backend systems

What is not ported yet:

- Real maps and collision from the web build
- Executions, netcode, lobbies, and multiplayer sync
- The web game's audio systems
- Scoreboard overlays, kill feed, and the rest of the broader presentation stack from the web version
- Dynamic map dressing, destructibles, and the richer environmental presentation from the web version

Recommended next Godot steps:

1. Build one real combat map scene and move the port off soft arena bounds.
2. Split abilities, projectiles, and world effects into dedicated Godot nodes/resources.
3. Port audio buses plus ship-specific weapon/engine/core sound design.
4. Add scoreboard, kill feed, and post-round presentation on top of the new HUD layer.
5. Decide whether multiplayer lands in ENet/WebRTC first, then port the network model deliberately.

This project has been validated in the workspace with both headless Godot runs and a real Vulkan render launch.
