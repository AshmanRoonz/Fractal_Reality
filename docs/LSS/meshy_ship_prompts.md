# Meshy AI Prompts: Last Ship Sailing Titans

Created: 2026-04-26
Last updated: 2026-04-26
Version: 1.0

Seven prompts, one per titan, sourced from `last_ship_sailing_v6_7.html` (LOADOUTS table at line 1132, CHASSIS table at line 1097, procedural silhouettes from `createShipMesh()` at line 5021). Every ship carries a pair of forward-firing blaster cannons mounted under the cockpit (the same dual-barrel arrangement the player sees painted into every cockpit frame PNG); this is repeated in each prompt so Meshy treats it as required, not optional.

Use one prompt per generation. Each is written for a single-shot text-to-3D pass; orientation is nose-forward (-Z), engines back (+Z).

---

## 1. VORTEX (Corvette MkII)

A balanced military space gunship; boxy purposeful hull with an angled forward prow, a raised armored command bridge, thick shoulder armor plates, and a single large rear thruster bell flanked by four small corner maneuvering thrusters. Two stubby barrel hardpoints sit on the shoulders. Underneath the cockpit canopy, a pair of long forward-firing blaster cannons protrudes side by side (these dual under-cockpit blasters are mandatory and visible from the front). Mounted in a small nose-recess between the dual blasters, an oversized lens-emitter for the Splitter Rifle / Laser Core. Color palette: gunmetal grey hull plating with cyan-blue emissive trim along seams, blue-tinted glass canopy, hot-cyan engine glow. Sleek tactical military style; sci-fi PBR; clean panel lines.

## 2. PYRO (Dreadnought Incinerator)

A heavy slow siege titan; wide imposing hull with a layered armor deck on top and a keel plate underneath, an angled ram prow at the front, a raised armored bridge tower set back behind the prow, and chunky weapons nacelles bulging from each flank. Three large engine bells sit in a row across the rear with four smaller dorsal thrusters above them. Two heavy thermite-launcher barrels (squat, vented, blackened muzzles) extend forward from the side nacelles, plus one dorsal turret barrel on top. Underneath the cockpit canopy, a pair of forward-firing blaster cannons protrudes side by side (these dual under-cockpit blasters are mandatory and visible from the front). Color palette: charred dark steel and orange-rust armor, glowing molten-orange vent slits along the flanks, soot-black weapon barrels, deep amber engine glow. Brutalist war-machine style; heat-stained; industrial.

## 3. PUNCTURE (Frigate Starcaster)

A sleek fast precision interceptor; tapered wedge fuselage with a sharp pointed four-sided cone nose, swept-back delta wings angled slightly downward, vertical stabilizer fins on each wingtip, and twin cylindrical engine pods slung underneath the rear hull. A small angular cockpit canopy sits centered on top of the mid-fuselage. A long heavy plasma railgun barrel runs along the spine of the ship, muzzle extending past the nose tip. Underneath the cockpit canopy, a pair of forward-firing blaster cannons protrudes side by side (these dual under-cockpit blasters are mandatory and visible from the front). Color palette: white and arctic-blue panels, dark navy underside, electric-blue emissive accents along wing leading edges and engine intakes, violet-white plasma glow at the railgun muzzle. Aerodynamic stealth-strike aesthetic; razor-sharp lines.

## 4. SLAYER (Frigate Blade)

A sleek aggressive close-range fighter; tapered wedge fuselage with a pointed cone nose, swept wings, vertical stabilizer tips, and twin underslung engine pods. The cockpit canopy is angular and tilted forward; the overall silhouette is shorter and stockier than other frigates, built for boarding. Two enormous wide-mouthed shotgun-style barrels (the Leadwall) sit centered under the nose, muzzles flared like blunderbusses. Two energized blade-style projection vanes fold along the wing roots (collapsible electric melee weapons). Underneath the cockpit canopy, a pair of forward-firing blaster cannons protrudes side by side, distinct from the larger leadwall mouths and positioned slightly higher on the chin (these dual under-cockpit blasters are mandatory and visible from the front). Color palette: matte black and deep crimson armor, electric-purple arc emissive along the blade vanes, red-hot engine glow. Predatory melee-fighter style; menacing; close-quarters brawler.

## 5. TRACKER (Corvette Tracker)

A balanced sensor-pursuit corvette; boxy purposeful hull with an angled prow, raised armored command bridge, shoulder armor plates, and a single large rear thruster bell with four corner maneuvering jets. The defining feature is a cluster of missile-pod hardpoints: two box-shaped multi-tube rocket racks mounted on the shoulders (clearly showing rows of small circular missile-tube openings), plus a forward-mounted radar/sonar dish or angular sensor array on top of the bridge. A single autocannon barrel runs along the chin. Underneath the cockpit canopy, a pair of forward-firing blaster cannons protrudes side by side (these dual under-cockpit blasters are mandatory and visible from the front). Color palette: olive-drab and tan military hull plating, amber and red sensor lights, warm orange engine glow, exposed missile tubes with grey interior. Hunter-killer aesthetic; lots of antennas and sensor detail; utilitarian.

## 6. BLASTER (Dreadnought Siege)

A heavy long-range siege titan; wide massive hull with layered upper and lower armor decks, a long armored ram prow at the front, a raised reinforced bridge tower set back, and bulky weapons nacelles on each flank. Three large rear engine bells in a row with four smaller dorsal thrusters above. The signature weapon is a single enormous multi-barrel rotary cannon (the Predator Cannon) extending from the chin of the ship, comprising six rotating barrels in a circular cluster, vented and finned; the barrels can telescope for the close/long mode switch. A frontal deployable shield panel folds back along the chin around the cannon. Underneath the cockpit canopy and flanking the rotary cannon, a pair of forward-firing blaster cannons protrudes side by side (these dual under-cockpit blasters are mandatory and visible from the front). Color palette: heavy industrial steel grey and yellow safety chevrons on the armor, hazard-stripe accents, glowing red emissive along the cannon vents, hot-white muzzle interior. Battleship-grade firepower aesthetic; mechanical bulk; oversized.

## 7. SYPHON (Corvette Sovereign)

A balanced veteran-officer corvette; boxy purposeful hull with an angled regal prow, a tall raised command bridge with extra greebles and antennas, ornate shoulder armor plates, and a single large rear thruster bell with four corner maneuvering jets. Twin chaingun barrels (the XO-16) project forward from the chin, multi-barrel rotary, slightly smaller than Blaster's Predator. Two side-mounted rocket salvo pods are visible on the shoulders, square multi-cell missile blocks. A pair of energy-siphon emitter dishes (concave glowing collectors) are mounted on the upper hull behind the bridge. Underneath the cockpit canopy, a pair of forward-firing blaster cannons protrudes side by side (these dual under-cockpit blasters are mandatory and visible from the front). Color palette: royal navy blue and gold-trim armor plating, bright cyan emissive on the siphon dishes, warm white engine glow, polished accents at panel seams. Flagship-officer aesthetic; ornamented; commanding presence.

---

## Shared notes for Meshy

These constants apply to every prompt above, in case a regeneration loses them:

- Orientation: nose toward -Z, engines toward +Z, dorsal toward +Y; ship is symmetric across the YZ plane.
- The dual under-cockpit blasters: two parallel cylindrical cannon barrels mounted on the chin directly below the cockpit canopy, muzzles pointing forward, spaced roughly one barrel-diameter apart, slightly recessed into a chin housing. The barrels are shorter than the ship's primary weapon. They are present on every titan and visible from the front view.
- Approximate hull proportions: Frigate (Puncture, Slayer) is the smallest and most slender (60w x 25h x 80l units); Corvette (Vortex, Tracker, Syphon) is medium and chunky (80 x 30 x 100); Dreadnought (Pyro, Blaster) is the largest and widest (110 x 45 x 140).
- Style across the fleet: PBR sci-fi, plated hull with panel lines, faction-colored emissive trim along seams, glowing engine plumes, glass-like canopy with internal pilot glow.

## Revision history

- 2026-04-26 v1.0: initial; seven prompts derived from LOADOUTS / CHASSIS / createShipMesh in last_ship_sailing_v6_7.html, dual under-cockpit blasters required on every ship per the cockpit frame PNGs.
