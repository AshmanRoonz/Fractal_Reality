# Meshy AI Prompts: Last Ship Sailing Titans

Created: 2026-04-26
Last updated: 2026-04-26
Version: 1.3

Seven prompts, one per titan, sourced from `last_ship_sailing_v6_7.html` (LOADOUTS line 1132, CHASSIS line 1097, `createShipMesh()` line 5021). Every titan is a single-pilot space starfighter with two parallel cannon barrels under the cockpit (matching the cockpit frame PNGs); each prompt opens with that framing so generators do not default to naval/sailing ships, and repeats the dual-cannon clause so it is treated as required. Trimmed to fit a ~800-char prompt limit.

Use one prompt per generation. Orientation (folded into each): nose toward -Z, thrusters toward +Z.

---

## 1. VORTEX (Corvette MkII)

A single-pilot space starfighter (medium strike-fighter class); armored spacecraft, angled forward chin plate, raised glass bubble cockpit canopy, twin shoulder pylons mounting stub-barrel hardpoints, single large rear thruster cone flanked by four small corner attitude jets. Beneath the cockpit canopy, two parallel cannon barrels protrude forward side by side (mandatory dual under-cockpit cannons; visible from the front view). An oversized Splitter Rifle laser-emitter lens sits in a nose recess between the dual cannons. Gunmetal grey plating, cyan-blue emissive trim along seams, blue-tinted glass canopy, hot-cyan thruster glow. Sleek tactical sci-fi PBR; clean panel lines; nose toward -Z, thrusters toward +Z.

## 2. PYRO (Dreadnought Incinerator)

A single-pilot space starfighter (heavy assault class); bulky armored spacecraft with layered upper and lower armor plates running the fuselage, pointed forward chin wedge, raised armored cockpit pod set back, chunky weapon nacelles bulging from each side. Three large rear thruster cones with four smaller dorsal attitude jets above. Two heavy thermite-launcher barrels (vented, blackened muzzles) on the side nacelles, plus one dorsal turret barrel on top. Beneath the cockpit, two parallel cannon barrels protrude forward side by side (mandatory dual under-cockpit cannons; visible from front). Charred dark steel and orange-rust armor, glowing molten-orange vent slits, soot-black barrels, deep amber thruster glow. Brutalist heat-stained sci-fi war-machine.

## 3. PUNCTURE (Frigate Starcaster)

A single-pilot space starfighter (fast precision interceptor); tapered wedge spacecraft, sharp four-sided cone nose, swept-back delta wings angled slightly downward, vertical stabilizer fins on each wingtip, twin cylindrical thruster pods slung beneath the rear fuselage. Angular bubble cockpit canopy on the fuselage. A long heavy plasma-railgun barrel runs along the spine, muzzle extending past the nose. Beneath the cockpit, two parallel cannon barrels protrude forward side by side (mandatory dual under-cockpit cannons; visible from front). White and arctic-blue panels, dark navy underside, electric-blue emissive along wing leading edges, violet-white plasma glow at the railgun muzzle. Aerodynamic stealth-strike sci-fi starfighter; razor-sharp lines.

## 4. SLAYER (Frigate Blade)

A single-pilot space starfighter (aggressive close-range interceptor); tapered wedge spacecraft, pointed cone nose, swept wings, vertical stabilizer tips, twin underslung thruster pods. Angular bubble cockpit canopy tilted forward; stockier than other interceptors, for boarding actions. Two enormous flared shotgun barrels (Leadwall) under the nose, blunderbuss muzzles. Two energized blade-projection vanes along the wing roots. Beneath the cockpit, two parallel cannon barrels protrude forward side by side, above the leadwall mouths (mandatory dual under-cockpit cannons; visible from front). Matte black and deep crimson armor plating, electric-purple arc emissive on the blade vanes, red-hot thruster glow. Predatory close-quarters space brawler.

## 5. TRACKER (Corvette Tracker)

A single-pilot space starfighter (medium sensor-pursuit class); armored spacecraft, angled forward chin plate, raised armored cockpit pod, shoulder armor plates, single large rear thruster cone with four corner attitude jets. Two box-shaped multi-tube rocket pods on the shoulders (circular missile-tube openings visible), plus an angular radar/sonar dish atop the cockpit pod. A single autocannon barrel along the chin. Beneath the cockpit, two parallel cannon barrels protrude forward side by side (mandatory dual under-cockpit cannons; visible from front). Olive-drab and tan military plating, amber and red sensor lights, warm orange thruster glow, exposed missile tubes with grey interiors. Hunter-killer sci-fi aesthetic; antennas and sensor detail.

## 6. BLASTER (Dreadnought Siege)

A single-pilot space starfighter (heavy long-range siege class); wide bulky spacecraft with layered armor plates, pointed chin wedge, raised armored cockpit pod set back, bulky weapon nacelles on each side. Three large rear thruster cones, four smaller dorsal attitude jets above. Six-barrel rotary cannon (Predator) on the chin, vented and finned, telescopes for close/long mode. Frontal shield panel folds back along the chin. Beneath the cockpit, flanking the rotary cannon, two parallel cannon barrels protrude forward side by side (mandatory dual under-cockpit cannons; visible from front). Industrial steel grey with yellow safety chevrons, hazard stripes, glowing red cannon vents, hot-white muzzle interior. Battleship-grade sci-fi bulk.

## 7. SYPHON (Corvette Sovereign)

A single-pilot space starfighter (medium veteran-officer class); armored spacecraft, angled regal chin plate, tall raised cockpit pod with greebles and antennas, ornate shoulder armor plates, single rear thruster cone with four attitude jets. Twin XO-16 chainguns (multi-barrel rotary) on the chin, smaller than Blaster's Predator. Two square missile-pod blocks on the shoulders. Two concave glowing siphon-emitter dishes on the upper fuselage behind the cockpit. Beneath the cockpit, two parallel cannon barrels protrude forward side by side (mandatory dual under-cockpit cannons; visible from front). Royal navy blue and gold-trim plating, bright cyan emissive on the siphon dishes, warm white thruster glow, polished panel-seam accents. Flagship-officer sci-fi.

---

## Shared notes (in case a generator drops them)

- Every titan is a single-pilot space starfighter (a flying spacecraft, NOT a sailing ship, NOT a boat, NOT a naval vessel). Style cues: Star Wars X-wing / TIE Fighter scale, Star Citizen / Elite Dangerous detailing, Battlestar Galactica viper.
- Dual under-cockpit cannons: two parallel cylindrical cannon barrels on the chin directly below the cockpit canopy, forward-pointing, spaced roughly one barrel-diameter apart, recessed into a chin housing, shorter than the primary weapon. Present on every titan.
- Hull proportions: small interceptors (Puncture, Slayer) ~60w x 25h x 80l; medium fighters (Vortex, Tracker, Syphon) ~80 x 30 x 100; heavy fighters (Pyro, Blaster) ~110 x 45 x 140.
- Fleet style: PBR sci-fi, plated armored fuselage with panel lines, team-colored emissive trim, glowing thruster plume at the rear, glass-like bubble canopy with internal pilot glow.

## Revision history

- 2026-04-26 v1.3: trimmed each prompt back under 800 chars after v1.2 spacecraft framing pushed them over; dropped redundant trailing "not a sailing ship; flying spacecraft" anchors (the opener already establishes spacecraft framing) and tightened descriptive phrases; the strong "single-pilot space starfighter" lead is preserved on every prompt.
- 2026-04-26 v1.2: recast every prompt as "single-pilot space starfighter" because v1.1 naval terminology (frigate/corvette/dreadnought/prow/keel/bridge) was triggering Meshy to generate sailing ships; led each prompt with the spacecraft framing, swapped naval words for spacecraft equivalents (cockpit pod, thruster cone, attitude jets, fuselage).
- 2026-04-26 v1.1: trimmed each prompt to fit ~800-char limit; folded orientation into each.
- 2026-04-26 v1.0: initial; seven prompts derived from LOADOUTS / CHASSIS / createShipMesh in last_ship_sailing_v6_7.html.
