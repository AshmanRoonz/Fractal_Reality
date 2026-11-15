"""Audit probes for "The Architecture of Wholeness" study and its archive of Experiments 1 to 11.

Created: 2026-11-06
Last updated: 2026-11-06
Version: 1.0
History: 2026-11-06 v1.0: initial. Ashman sent the study (Word file) and the archive Circumpunct_Experiments_1-11_and_Research_Study.zip. The study says a fresh rerun was not done and asks for a source-level audit; this is that audit's own code.

The archive is not in this repository. Unpack it into a folder of its own and pass that folder:
Run: python -I architecture_study_audit_v1.py ARCHIVE_DIR [numbers e3 e10 e7]
Needs numpy and pandas. It imports the archive's own modules for e3 and e10, and writes nothing.

WHAT THE CODE SHOWS, read before anything was rerun.
(a) Experiment 3. Each site keeps a slow memory m of its own activity and a confidence c. After 80 settled steps m is within .03 of the activity and c is near .73 to .85. The repair terms are gamma c (m - a) and beta c m max(0, sum_m - n), both scaled by the site's own c and m. The injury sets the activity of the removed sites to 0 and leaves their m and c as they were. So a removed site still holds a confident record that it was active, and the repair reads that record. The study and README say the correction is designed in. They do not say the damage spares the memory that carries it.
(b) Experiment 10. With mean contribution rate r the mean habitat moves by 0.012 - 0.070 + 0.115 r each step, since each contribution adds 0.115 / 5 to five sites. So the commons holds only above r = 0.058 / 0.115 = 0.504. The random control contributes at 0.50, just under that; the forecasting policy at 0.544, just over. The drift at 0.50 is -0.0005 a step, which over 280 steps and a shock of 0.32 takes a habitat of 0.70 to about 0.24. The shipped random control ends at 0.222. So that control's outcome is arithmetic, and no control contributes at the forecasting policy's own rate.
(c) Experiment 10 again. The agents value a contribution to themselves as benefit x effect x annuity, 0.45 x 0.023 x 19.4 = 0.201 at a horizon of 32, against a cost near 0.115. That treats a one-step gain in their own habitat as lasting. The habitat spreads to neighbours at 0.08 a step, so their own share should fall toward 0.115 / 36 = 0.0032.
(d) Experiment 7, from the shipped table. The long trace reaches 585 cells against 201 for the one-step learner. With its feedback shuffled among cells the long trace still reaches 511. A random gate reaches 306 and an always-open gate 189. The README gives these; the study gives only 585 and 201.
(e) Experiment 6. The reward is the cell's own energy change with no noise, so a single open step reveals the sign of the payoff exactly. A closed cell gains 0.001 a step and cannot die, which the README does say.
(f) Experiment 4. The evidence is (2a - 1) times the realized payoff, which equals the sign of the hidden target except for a 20% flip. So each site is sent a noisy copy of the right answer every step. The README says the inference is especially simple.

PREDICTIONS, frozen before these probes ran.
A1. Experiment 3, 30 held-out seeds, combined rule. If the memory of the removed sites is reset along with their activity (m = .5, c = 0, as at the start), the share restored after 25 steps is within 10 points of the rule with no repair terms, for each of the four injuries. The shipped values for that rule are 0, 100, 43.2 and 4.0.
A2. Experiment 10, seeds 44000 to 44029. A random policy contributing at 0.55 keeps all 36 alive with final habitat at least .85 in at least 28 of 30 worlds.
A3. The same at 0.52: all 36 alive in at least 25 of 30, mean final habitat between .5 and .95. At 0.50 the patched code reproduces the shipped random rows exactly.
A4. With everything else held fixed and the habitat's own spreading included, one contribution is worth less than 0.115 to the contributor over 32 steps at the agents' own discount of 0.965.

RESULTS.
Integrity: all 178 files match the archive's SHA-256 manifest. Of 61 headline figures in the study, 61 agree with the shipped result files; the numbers option here rechecks 52 of them.
Reruns: every script of Experiments 1 to 11 was rerun from a copy, and all 32 result tables (CSV) came out identical to the shipped ones, apart from one p-value differing by 2e-21. matplotlib is not installed here, so a stand-in absorbed the plotting calls and no figure was regenerated or checked. Experiments 2 to 4 ran with an array version of their per-cell update, checked first to give identical states.
A1 MISS. Restored after 25 steps, memory of the removed sites reset: edge 0.0%, core 100.0%, random 20% 58.5%, patch 5.6%. With no repair terms: 0.0, 100.0, 43.2, 4.0. Three of four were within 10 points; the random case was 15 above. After the fact: the sites that were not removed keep their own memory, which holds the surround steady, and more removed sites then meet the plain rule's threshold of 5 active neighbours. As shipped, with memory spared, all four are 100%. With the memory set to 0 and confidence kept: 0, 100, 43.0, 0.
A2 PASS. Random at 0.55: all 36 alive and habitat at least .85 in 30 of 30 worlds, mean habitat .971.
A3 PASS. Random at 0.52: all 36 alive in 30 of 30, mean habitat .837. At 0.50 the patched code gives the shipped rows exactly. Also: 0.51 keeps all 36 alive in 30 of 30 with habitat .566; 0.53 gives .943; at 0.544, the forecasting policy's own rate, .967 against the policy's .973.
A4 PASS. The agents' formula values one contribution at .201 to the contributor at a horizon of 32 and .073 at 8. With the habitat's spreading included it is .096 and .059. Costs run from .085 to .145, mean .115, so the true private return is below cost for about 4 agents in 5. Their own share of a contribution falls from .0230 to .0112 after 8 steps and .0040 after 31.
Seen while rerunning: experiment10_evaluate.py has its own stress block of 12 worlds and 5 conditions. The shipped stress table comes from experiment10_finish.py, 8 worlds and 3 conditions. The block that was not shipped includes higher productivity (0.122, break-even 0.475), where the random control at 0.50 keeps all 36 alive with habitat .946.
From the shipped tables: in Experiment 7 the long trace keeps .81 of its gain over the one-step learner when its feedback is shuffled. In Experiment 5 total energy is the same with sharing and without (1320.9, 1304.4); sharing gives 585.6 cells holding 2.26 each, no sharing 680.7 holding 1.92. In Experiment 11 under collusion the strict three-of-four rule keeps 34.0 alive with 1.1% of cooperative member-time restricted, and evidence-blind random soft restriction keeps 35.83 alive with 45%.
None of the eleven takes a framework input, as the study itself says. In all of them "center" names each unit; none has a center of the whole in any sense tested in the wholeness_*.py files.
"""
import json
import os
import sys
import types
from pathlib import Path

import numpy as np

OFFS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def verdict(ok):
    return "PASS" if ok else "MISS"


def stub_matplotlib():
    """The archive's modules import matplotlib when loaded. Nothing here plots, so a bare stand-in is enough."""
    try:
        import matplotlib  # noqa: F401
    except ImportError:
        mp = types.ModuleType("matplotlib")
        mp.use = lambda *a, **k: None
        pp = types.ModuleType("matplotlib.pyplot")
        mp.pyplot = pp
        sys.modules["matplotlib"] = mp
        sys.modules["matplotlib.pyplot"] = pp


# ---------- numbers: the study's headline figures against the shipped result files ----------
def numbers(root):
    import pandas as pd
    rows = []

    def say(exp, claim, study, got):
        rows.append((exp, claim, str(study), str(got)))

    e = root / "experiment_01"
    d = pd.read_csv(e / "circumpunct_experiment_30_seeds.csv")
    say(1, "stable blocks", 129, int(d.blocks_unchanged_4_steps.sum()))
    say(1, "period-two oscillators", 104, int(d.observed_blinkers_period2.sum()))
    say(1, "gliders", 11, int(d.verified_gliders_4step.sum()))
    e = root / "experiment_02"
    d = pd.read_csv(e / "experiment2_trials.csv")
    say(2, "grids unchanged 60 to 80", 30, int((d.changed_60_to_80 == 0).sum()))
    say(2, "edge over interior response", 10.4, round(d.interface_enrichment.mean(), 2))
    say(2, "interior cell recovered", "30/30", f"{int(d.core_restored_t1.sum())}/{int(d.core_available.sum())}")
    say(2, "edge cell recovered", "0/30", f"{int(d.edge_restored_t25.sum())}/{int(d.edge_available.sum())}")
    say(2, "restored, interface off", 60.1, round(100 * d.unprotected_restored_fraction.mean(), 1))
    say(2, "restored, default", 46.0, round(100 * d.default_restored_fraction.mean(), 1))
    e = root / "experiment_03"
    d = pd.read_csv(e / "experiment3_trials.csv")
    for typ in ("edge", "core", "random20", "patch"):
        say(3, f"combined restores {typ}", 100.0, round(100 * d[f"{typ}_adaptive_full_restored_fraction"].mean(), 1))
        say(3, f"combined exact match {typ}, of 30", 30, int((d[f"{typ}_adaptive_full_errors"] == 0).sum()))
    e = root / "experiment_04"
    d = pd.read_csv(e / "experiment4_trials.csv")
    ev = d[d["mode"] == "evidence"]
    for sc, v in (("injury", 100.0), ("helpful_change", 87.9), ("new_opportunity", 80.5), ("misleading_feedback", 14.3)):
        say(4, f"evidence + structure, {sc}", v, round(100 * ev[ev.scenario == sc].affected_accuracy.mean(), 1))
    say(4, "unaffected sites kept", 99.99, round(100 * ev[ev.scenario.isin(["injury", "helpful_change", "new_opportunity"])].unaffected_retention.mean(), 2))
    e = root / "experiment_05"
    g = pd.read_csv(e / "experiment5_trials.csv").groupby("mode").after_alive.mean()
    for m, v in (("evolving", 585.6), ("always_open", 353.9), ("nonheritable", 586.6), ("fixed_sensitive", 638.1), ("evolving_no_sharing", 680.7)):
        say(5, f"living cells, {m}", v, round(g[m], 1))
    e = root / "experiment_06"
    d = pd.read_csv(e / "experiment6_trials.csv")
    g = d.groupby("mode").alive_final.mean()
    for m, v in (("local_learning", 1373.9), ("frozen_memory", 125.7), ("always_open", 0.0), ("random_gate", 0.0)):
        say(6, f"surviving cells, {m}", v, round(g[m], 1))
    say(6, "learner correctness at the end", 92.4, round(100 * d[d["mode"] == "local_learning"].accuracy_final.mean(), 1))
    say(6, "delayed harm: surviving learners", 3.5, round(pd.read_csv(e / "experiment6_delayed_trials.csv").groupby("mode").alive_final.mean()["local_learning"], 1))
    e = root / "experiment_07"
    g = pd.read_csv(e / "experiment7_trials.csv").groupby("mode").alive_final.mean()
    say(7, "living cells, long trace", 585.2, round(g["trace_long"], 1))
    say(7, "living cells, one-step", 200.9, round(g["instant"], 1))
    s = json.loads((e / "experiment7_causal_diagnostic_summary.json").read_text())["stationary"]
    say(7, "diagnostic, delayed: long / one-step", "71.0 / 55.6", f"{100 * s['7']['trace_long']['decision_accuracy']:.1f} / {100 * s['7']['instant']['decision_accuracy']:.1f}")
    say(7, "diagnostic, immediate: long / one-step", "77.9 / 92.6", f"{100 * s['0']['trace_long']['decision_accuracy']:.1f} / {100 * s['0']['instant']['decision_accuracy']:.1f}")
    e = root / "experiment_08"
    d = pd.read_csv(e / "experiment8_trials.csv")
    r = d[d.strategy == "episodic_recall"]
    say(8, "switches detected", 90, int(r.detected_switches.sum()))
    say(8, "overall correct, recall", 89.1, round(100 * r.optimal_action_rate.mean(), 1))
    say(8, "first 30 after return: recall / no recall", "70.0 / 48.9", f"{100 * r.repeat_switch_30_accuracy.mean():.1f} / {100 * d[d.strategy == 'change_detect_no_recall'].repeat_switch_30_accuracy.mean():.1f}")
    e = root / "experiment_09"
    d = pd.read_csv(e / "experiment9_trials.csv")
    g = d.groupby("strategy").yield_per_agent_step.mean()
    for m, v in (("private_clean", 0.4746), ("mean_clean", 0.5465), ("mean_attack", 0.4785), ("trust_and_policy_attack", 0.5341)):
        say(9, f"yield, {m}", v, round(g[m], 4))
    t = d[d.strategy == "trust_and_policy_attack"]
    say(9, "weight to honest / misleading peers", "0.866 / 0.011", f"{t.accepted_honest_peers.mean():.3f} / {t.accepted_corrupt_peers.mean():.3f}")
    e = root / "experiment_10"
    g = pd.read_csv(e / "experiment10_trials.csv").groupby("method")[["living_cells", "habitat", "donation_fraction"]].mean()
    for m, v in (("model_long", "36.00 / 0.973 / 0.544"), ("random", "31.17 / 0.222 / 0.496"), ("cooperate", "36.00 / 1.000 / 1.000")):
        say(10, f"survivors / habitat / contribution, {m}", v, f"{g.loc[m, 'living_cells']:.2f} / {g.loc[m, 'habitat']:.3f} / {g.loc[m, 'donation_fraction']:.3f}")
    e = root / "experiment_11"
    d = pd.read_csv(e / "experiment11_trials.csv")
    c = d[d.scenario == "collusion"].groupby("policy")[["survivors", "mean_false_exclusion"]].mean()
    for m, v in (("open", "7.40, 0.0%"), ("soft_reciprocity", "35.97, 25.4%"), ("majority", "34.00, 1.1%"), ("universal_soft", "36.00, 100.0%")):
        say(11, f"collusion: survivors, cooperative members restricted, {m}", v, f"{c.loc[m, 'survivors']:.2f}, {100 * c.loc[m, 'mean_false_exclusion']:.1f}%")
    same = 0
    for exp, claim, study, got in rows:
        try:
            ok = abs(float(study) - float(got)) < 1e-9
        except ValueError:
            ok = study == got
        same += ok
        print(f"  E{exp:<2} {claim}: study {study}; data {got}" + ("" if ok else "   <-- differs"))
    print(f"numbers: {same} of {len(rows)} agree")
    return same == len(rows)


# ---------- e7 and e5: figures the study leaves out, read from the shipped files ----------
def e7(root):
    import pandas as pd
    g = pd.read_csv(root / "experiment_07" / "experiment7_trials.csv").groupby("mode").alive_final.mean()
    gain = g["trace_long"] - g["instant"]
    kept = g["trace_long_shuffled"] - g["instant"]
    print(f"  E7 living cells: long trace {g['trace_long']:.1f}; one-step {g['instant']:.1f}; long trace with shuffled feedback {g['trace_long_shuffled']:.1f}; random gate {g['random_gate']:.1f}; always open {g['always_open']:.1f}")
    print(f"  E7 share of the long trace's gain that remains with feedback shuffled: {kept / gain:.2f}")
    en = pd.read_csv(root / "experiment_05" / "experiment5_trials.csv").groupby("mode")[["after_alive", "after_energy"]].mean()
    a, b = en.loc["evolving"], en.loc["evolving_no_sharing"]
    print(f"  E5 sharing: {a.after_alive:.1f} cells, energy {a.after_energy:.1f}, {a.after_energy / a.after_alive:.2f} each. No sharing: {b.after_alive:.1f} cells, energy {b.after_energy:.1f}, {b.after_energy / b.after_alive:.2f} each")
    return True


# ---------- e3: does the repair survive damage to the memory that carries it? ----------
def nsum(x):
    s = np.zeros(x.shape, np.float64)
    for di, dj in OFFS:
        s = s + np.roll(x, (-di, -dj), axis=(0, 1))
    return s


def step3(u, b, f, m, c, gamma=3.5, memrate=0.035, conf_rate=0.055, feedback=0.8, local_support=1.0):
    """Experiment 3's update with the same operations in the same order as its per-cell loop."""
    uf = u.astype(np.float64)
    su, sb, sf, sm = nsum(uf), nsum(b), nsum(f), nsum(m)
    un, bn, fn = su / 8.0, sb / 8.0, sf / 8.0
    nb = np.minimum(1.0, np.maximum(0.0, 0.72 * b + 0.28 * np.abs(uf - un) + 0.1 * (bn - b)))
    nf = np.minimum(1.0, np.maximum(0.0, f + 0.18 * (fn - f) + 0.04 * (1 - f) - 0.08 * uf * f))
    shortfall = np.maximum(0.0, sm - su)
    score = (su + 0.65 * (2 * uf - 1) + feedback * b * (2 * uf - 1) + 0.5 * (f - 0.5) - 4.25
             + gamma * c * (m - uf) + local_support * c * m * shortfall)
    nm = (1 - memrate) * m + memrate * uf
    nc = (1 - conf_rate) * c + conf_rate * np.maximum(0.0, 1 - 4 * np.abs(uf - m))
    return (score >= 0).astype(u.dtype), nb, nf, nm, nc


def e3(root):
    stub_matplotlib()
    sys.path.append(str(root / "experiment_03"))
    import circumpunct_experiment3 as m
    s = m.init(7)
    for _ in range(30):
        s = step3(*s)
    s[0][40:60, 40:60] = 0
    same = all(np.array_equal(x, y) for x, y in zip(m.step(*s), step3(*s)))
    print("  array update identical to the shipped loop on a state with history:", same)
    m.step = step3
    kinds = ("activity only", "memory also reset", "memory also zeroed", "confidence also zeroed", "no repair terms")
    res = {}
    for seed in m.SEEDS:
        s80 = m.run(m.init(seed), 80)
        for typ in ("edge", "core", "random20", "patch"):
            sites = m.damage_sites(s80[0], seed, typ)
            if not len(sites):
                continue
            r, c = sites[:, 0], sites[:, 1]
            for kind in kinds:
                z = tuple(x.copy() for x in s80)
                z[0][r, c] = 0
                if kind == "memory also reset":
                    z[3][r, c] = 0.5
                    z[4][r, c] = 0.0
                elif kind == "memory also zeroed":
                    z[3][r, c] = 0.0
                elif kind == "confidence also zeroed":
                    z[4][r, c] = 0.0
                out = m.run(z, 25, 0.0, 0.0) if kind == "no repair terms" else m.run(z, 25)
                res.setdefault((typ, kind), []).append(float(out[0][r, c].mean()))
    ok = True
    for typ in ("edge", "core", "random20", "patch"):
        row = {k: 100 * float(np.mean(res[(typ, k)])) for k in kinds}
        ok &= abs(row["memory also reset"] - row["no repair terms"]) <= 10
        print(f"  {typ}: " + "; ".join(f"{k} {v:.1f}%" for k, v in row.items()))
    print("A1", verdict(ok))
    return ok


# ---------- e10: is it the forecasting, or the rate? ----------
def four(x):
    return np.roll(x, 1, 0) + np.roll(x, -1, 0) + np.roll(x, 1, 1) + np.roll(x, -1, 1)


def private_value(horizon=32, disc=0.965, n=6):
    """One contribution, everything else held fixed and no clipping: the contributor's own energy gain over the horizon."""
    h = np.zeros((n, n))
    a = np.zeros((n, n))
    a[0, 0] = 1
    h = h + 0.115 * (a + four(a)) / 5
    tot = 0.0
    own = []
    for k in range(horizon):
        own.append(h[0, 0])
        tot += disc ** k * 0.45 * h[0, 0]
        h = h + 0.08 * (four(h) - 4 * h)
    return tot, own


def e10(root):
    import pandas as pd
    stub_matplotlib()
    src = (root / "experiment_10" / "circumpunct_experiment10.py").read_text(encoding="utf-8")
    target = "a=(u[t]<.5).astype(float)"
    assert src.count(target) == 1
    ns = {"__name__": "e10_patched", "RANDOM_P": 0.5}
    exec(compile(src.replace(target, "a=(u[t]<RANDOM_P).astype(float)"), "circumpunct_experiment10_patched", "exec"), ns)
    run, T = ns["run"], ns["T"]
    ship = pd.read_csv(root / "experiment_10" / "experiment10_trials.csv")
    ship_r = ship[ship.method == "random"].set_index("seed")
    print(f"  break-even contribution rate (0.070 - 0.012) / 0.115 = {(0.07 - 0.012) / 0.115:.4f}")
    seeds = range(44000, 44030)
    ok = True
    for p in (0.5, 0.51, 0.52, 0.53, 0.544, 0.55, 0.6):
        ns["RANDOM_P"] = p
        out = [run(s, "random") for s in seeds]
        alive = np.array([o["final_alive"] for o in out])
        hab = np.array([o["final_habitat"] for o in out])
        rate = np.mean([o["total_actions"] / (T * 36) for o in out])
        line = f"  random at {p:g}: survivors {alive.mean():.2f}; all 36 in {int((alive == 36).sum())} of 30; habitat {hab.mean():.3f}; habitat at least .85 in {int((hab >= 0.85).sum())}; realized rate {rate:.3f}"
        if p == 0.5:
            exact = bool(np.array_equal(alive, ship_r.loc[list(seeds), "living_cells"].values) and np.allclose(hab, ship_r.loc[list(seeds), "habitat"].values, atol=1e-12))
            line += f"; identical to the shipped random rows: {exact}"
            ok &= exact
        if p == 0.55:
            a2 = int(((alive == 36) & (hab >= 0.85)).sum()) >= 28
            line += f"; A2 {verdict(a2)}"
            ok &= a2
        if p == 0.52:
            a3 = int((alive == 36).sum()) >= 25 and 0.5 <= hab.mean() <= 0.95
            line += f"; A3 {verdict(a3)}"
            ok &= a3
        print(line, flush=True)
    ml = ship[ship.method == "model_long"]
    print(f"  shipped forecasting policy: survivors {ml.living_cells.mean():.2f}; habitat {ml.habitat.mean():.3f}; rate {ml.donation_fraction.mean():.3f}")
    for hz in (8, 32):
        v, own = private_value(hz)
        formula = 0.45 * 0.023 * (1 - 0.965 ** hz) / (1 - 0.965)
        print(f"  horizon {hz}: the agents' formula values one contribution at {formula:.3f} to themselves; with the habitat's own spreading it is {v:.3f}; cost .085 to .145, mean .115")
    v, own = private_value(32)
    print("  own share of one contribution after 0, 1, 2, 4, 8, 16, 31 steps: " + ", ".join(f"{own[k]:.4f}" for k in (0, 1, 2, 4, 8, 16, 31)))
    a4 = v < 0.115
    print("A4", verdict(a4))
    return ok and a4


if __name__ == "__main__":
    root = Path(sys.argv[1]) / "experiments"
    which = sys.argv[2:] or ["numbers", "e7", "e3", "e10"]
    for w in which:
        print(w)
        {"numbers": numbers, "e7": e7, "e3": e3, "e10": e10}[w](root)
