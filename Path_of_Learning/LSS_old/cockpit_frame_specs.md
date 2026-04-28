# Cockpit Frame Specs: Last Ship Sailing Titans

Created: 2026-04-26
Last updated: 2026-04-26
Version: 1.0

Per-titan specs for the cockpit-frame PNGs in `docs/LSS/frames/`. Pixel coordinates are the actual barrel-tip positions detected by the same alpha-channel scan the game uses at runtime (see `detectFrameMuzzlePoints()` in `last_ship_sailing_v6_7.html` line 9581); ported to Python and run against each PNG. Origin is image top-left, +x right, +y down.

All seven frames share one canvas size: **1536 x 1024 px** (3:2 landscape). Dual blaster barrels are mounted symmetrically left/right of center; the algorithm finds each tip in its half of the image.

The fleet falls into two cockpit archetypes:

**Archetype A: cockpit-arm guns** (VORTEX, PUNCTURE, SLAYER, TRACKER, SYPHON). Two arms reach in from the lower screen corners; barrels emerge from the wrists around y = 540 to 610 (53 to 60% down the frame), spread 760 to 820 px apart (50 to 53% of frame width); convergence varies from gentle (Vortex ~11°) to aggressive (Syphon ~50°).

**Archetype B: edge hardpoint guns** (PYRO, BLASTER). Massive barrels mounted on the outer hull, tips at y = 307 (30% down the frame, well above mid-screen), spread 1400 to 1473 px (91 to 96% of frame width, almost the whole image); barrels angle slightly outward from base to tip, indicating barrels that come up and out from the heavy chassis rather than converging on a single forward point.

---

## 1. VORTEX

- **Frame**: 1536 x 1024
- **Left barrel tip**: (383, 606)  [25% W, 59% H]
- **Right barrel tip**: (1153.5, 607)  [75% W, 59% H]
- **Spread**: 770.5 px tip-to-tip (50% of frame width)
- **Left base** (~8% H below tip, on barrel axis): (368, 687); direction (+0.182, -0.983); 10.5° inward of vertical
- **Right base**: (1170.5, 688); direction (-0.205, -0.979); 11.8° inward
- **Convergence**: gentle, ~11° each side; rays meet far above the frame (effectively parallel forward at engagement distance)
- **Layout**: classic two-armed corvette cockpit; symmetric arms reach in from the lower outer corners, wrist-mounted blasters; central canopy frame visible above the arms; HUD readout area between the wrists.

## 2. PYRO

- **Frame**: 1536 x 1024
- **Left barrel tip**: (30.5, 307)  [2% W, 30% H]
- **Right barrel tip**: (1503.5, 307)  [98% W, 30% H]
- **Spread**: 1473 px tip-to-tip (96% of frame width)
- **Left base**: (40, 388); direction (-0.117, -0.993); 6.7° outward of vertical
- **Right base**: (1498, 388); direction (+0.068, -0.998); 3.9° outward
- **Convergence**: none; barrels diverge slightly outward (mounted on shoulder hardpoints way out wide on the heavy chassis, not on cockpit arms)
- **Layout**: dreadnought-style; barrels enter the frame from the upper-left and upper-right edges, tips at upper third; the inside of the canopy frame is heavy armored ribbing; lower third is dashboard/HUD area; the painted barrels are stout thermite launchers, vented muzzles.

## 3. PUNCTURE

- **Frame**: 1536 x 1024
- **Left barrel tip**: (359.5, 540)  [23% W, 53% H]
- **Right barrel tip**: (1180.5, 540)  [77% W, 53% H]
- **Spread**: 821 px tip-to-tip (53% of frame width)
- **Left base**: (336, 621); direction (+0.279, -0.960); 16.2° inward
- **Right base**: (1207, 621); direction (-0.311, -0.950); 18.1° inward
- **Convergence**: moderate; lines meet roughly 1500 px ahead at screen-center axis (just past the painted nose tip, consistent with a long railgun spine)
- **Layout**: frigate cockpit; tighter, sleeker arms than the corvette set; tips sit slightly higher (~53% vs ~59% on corvettes), reflecting the smaller hull's more forward seating position; central spine should show the plasma-railgun barrel running forward between the two blasters.

## 4. SLAYER

- **Frame**: 1536 x 1024
- **Left barrel tip**: (358.5, 609)  [23% W, 59% H]
- **Right barrel tip**: (1178, 610)  [77% W, 60% H]
- **Spread**: 819.5 px tip-to-tip (53% of frame width)
- **Left base**: (287.5, 690); direction (+0.659, -0.752); 41.2° inward
- **Right base**: (1233.5, 691); direction (-0.565, -0.825); 34.4° inward
- **Convergence**: aggressive; barrels swing strongly inward, meeting roughly 600 to 800 px ahead at center, reflecting the close-range brawler doctrine (Leadwall + dual blasters firing into a tight kill cone)
- **Layout**: frigate cockpit, similar tip positions to Vortex but with the arms angled hard inward; the painted barrels are visibly tilted; central nose area between the two blasters should show the wide flared Leadwall mouths slightly lower in the frame.

## 5. TRACKER

- **Frame**: 1536 x 1024
- **Left barrel tip**: (388.5, 590)  [25% W, 58% H]
- **Right barrel tip**: (1152.5, 590)  [75% W, 58% H]
- **Spread**: 764 px tip-to-tip (50% of frame width)
- **Left base**: (363, 671); direction (+0.300, -0.954); 17.5° inward
- **Right base**: (1177.5, 671); direction (-0.295, -0.956); 17.2° inward
- **Convergence**: moderate; symmetric ~17° each side; meets ~1200 to 1500 px ahead at center
- **Layout**: corvette cockpit; geometry nearly identical to Vortex but with the arms toed in another 6° per side; the central HUD area should host sensor/radar readouts (Tracker's signature kit); the chin autocannon barrel should be visible below the dashboard line, between the two blasters.

## 6. BLASTER

- **Frame**: 1536 x 1024
- **Left barrel tip**: (68.5, 307)  [4% W, 30% H]
- **Right barrel tip**: (1469.5, 307)  [96% W, 30% H]
- **Spread**: 1401 px tip-to-tip (91% of frame width)
- **Left base**: (95.5, 388); direction (-0.316, -0.949); 18.4° outward
- **Right base**: (1440, 388); direction (+0.342, -0.940); 20.0° outward
- **Convergence**: none; strongly divergent; barrels mounted at the outer hull edges and angled outward as they rise
- **Layout**: dreadnought-style; barrels enter from upper-left and upper-right corners, tips deeper into the frame than Pyro's (Pyro at x = 30, Blaster at x = 68; Blaster's barrels are slightly more inboard); lower-center should show the chin-mounted six-barrel Predator Cannon between the two blasters; armored bulkheads visible around the edges.

## 7. SYPHON

- **Frame**: 1536 x 1024
- **Left barrel tip**: (388, 603)  [25% W, 59% H]
- **Right barrel tip**: (1151, 602)  [75% W, 59% H]
- **Spread**: 763 px tip-to-tip (50% of frame width)
- **Left base**: (292.5, 684); direction (+0.763, -0.647); 49.7° inward
- **Right base**: (1246, 683); direction (-0.761, -0.649); 49.6° inward
- **Convergence**: aggressive (sharpest in the fleet); barrels nearly horizontal, swinging hard inward; meets ~400 to 500 px ahead at center
- **Layout**: corvette cockpit; tip positions match Vortex/Tracker, but the arms are pulled in tight at the wrists; the painted barrels are visibly close to crossing; the nose between the blasters should show the chin-mounted XO-16 chaingun cluster, with siphon-emitter dishes on the upper canopy frame.

---

## Quick lookup table

| Ship | Left tip (x, y) | Right tip (x, y) | Spread px | Tip Y % | Per-side angle | Pattern |
|---|---|---|---|---|---|---|
| VORTEX | 383, 606 | 1153.5, 607 | 770.5 | 59% | 11° in | A |
| PYRO | 30.5, 307 | 1503.5, 307 | 1473 | 30% | 5° out | B |
| PUNCTURE | 359.5, 540 | 1180.5, 540 | 821 | 53% | 17° in | A |
| SLAYER | 358.5, 609 | 1178, 610 | 819.5 | 60% | 38° in | A |
| TRACKER | 388.5, 590 | 1152.5, 590 | 764 | 58% | 17° in | A |
| BLASTER | 68.5, 307 | 1469.5, 307 | 1401 | 30% | 19° out | B |
| SYPHON | 388, 603 | 1151, 602 | 763 | 59% | 50° in | A |

Pattern A: cockpit-arm guns, mid-screen, converging. Pattern B: edge hardpoint guns, upper screen, divergent.

---

## How the game uses these coordinates

`updateCockpitFrame()` (line 9680) loads each PNG, hands it to `detectFrameMuzzlePoints()`, and stores the result on `player.cockpitFrameMuzzle`. The HUD canvas reads this in the muzzle-flash render path (around line 13397) and spawns the flash at the detected tip in image coords, then translates to screen coords via `frameImgToScreen()` (line 9672), which compensates for `background-size: cover` cropping at the user's viewport aspect. So flashes track the painted barrel tips even if the frame art drifts a few percent between revisions; replacing a PNG with new art at the same overall layout works without code changes.

A `KEY1.png` companion (e.g. `VORTEX1.png`) is used as the firing-state swap (line 9711); the alpha-scan runs only on the base `KEY.png`, so the firing companion can show muzzle flashes painted in without affecting tip detection.

## Revision history

- 2026-04-26 v1.0: initial; coordinates extracted by porting `detectFrameMuzzlePoints()` to Python and running over the seven `frames/*.png` files; archetype split (cockpit-arm vs edge hardpoint) noted; quick-lookup table at the bottom.
