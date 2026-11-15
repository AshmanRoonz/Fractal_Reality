"""Audit probes for the "Circumpunct Life" series (v0.1 to v1.9) shipped in
Circumpunct_Complete_Research_Project_Experiments_01-11_Life_v0.1-v1.9.zip.

Created: 2026-11-07
Last updated: 2026-11-07
Version: 1.0
History:
  - 2026-11-07 v1.0: manifest check, byte comparison of the eleven foundation
    experiments against the 2026-11-06 archive, and recomputation of every
    version's primary outcome table from the shipped CSVs (no archive code is run).

Usage (the unpacked archive folder is passed in; nothing inside it is executed):
  python -I circumpunct_life_series_audit_v1.py <archive_root> [--versions v0.5,v0.9]
  python -I circumpunct_life_series_audit_v1.py <archive_root> --verify
  python -I circumpunct_life_series_audit_v1.py <archive_root> --old <2026-11-06 archive root>
"""
import argparse
import csv
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

pd.set_option('display.width', 200)
pd.set_option('display.max_columns', 30)
pd.set_option('display.float_format', lambda v: f'{v:.4g}')


def verify_manifest(root: Path):
    rows = list(csv.DictReader((root / 'MANIFEST_SHA256.csv').open(newline='', encoding='utf-8')))
    bad = []
    for r in rows:
        p = root / r['relative_path']
        if not p.is_file():
            bad.append(('missing', r['relative_path']))
            continue
        if hashlib.sha256(p.read_bytes()).hexdigest() != r['sha256'] or p.stat().st_size != int(r['size_bytes']):
            bad.append(('mismatch', r['relative_path']))
    disk = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} - {'MANIFEST_SHA256.csv'}
    extra = sorted(disk - {r['relative_path'] for r in rows})
    print(f'manifest rows {len(rows)}, files on disk {len(disk) + 1}, errors {len(bad)}, unlisted {len(extra)}')
    for k, p in bad[:20]:
        print(' ', k, p)
    for p in extra[:20]:
        print('  unlisted', p)


def compare_foundation(old: Path, new: Path):
    """Byte comparison of experiment_01..11 folders between two unpacked archives."""
    def index(r):
        out = {}
        for p in r.rglob('*'):
            if not p.is_file():
                continue
            parts = p.relative_to(r).parts
            hit = [i for i, c in enumerate(parts) if c.startswith('experiment_') and c[11:].isdigit()]
            if hit:
                out['/'.join(parts[hit[0]:])] = hashlib.sha256(p.read_bytes()).hexdigest()
        return out
    a, b = index(old), index(new)
    same = sum(1 for k in a if k in b and a[k] == b[k])
    changed = sum(1 for k in a if k in b and a[k] != b[k])
    print(f'foundation files: old {len(a)}, new {len(b)}, identical {same}, changed {changed}, '
          f'only old {len(set(a) - set(b))}, only new {len(set(b) - set(a))}')


def table(df, group, metrics, sums=(), title=''):
    cols = [c for c in metrics if c in df.columns]
    g = df.groupby(group, sort=False)
    out = g[cols].mean()
    for s in sums:
        if s in df.columns:
            out[f'{s}(sum)'] = g[s].sum()
    out['n'] = g.size()
    print(f'-- {title}')
    print(out.to_string())
    print()


def paired(df, group, a, b, metric, key='seed'):
    """Mean of (a - b) across matched seeds with a 95% t interval and win count."""
    x = df[df[group] == a].set_index(key)[metric]
    y = df[df[group] == b].set_index(key)[metric]
    d = (x - y.reindex(x.index)).dropna()
    n = len(d)
    if n < 2:
        return None
    h = stats.t.ppf(.975, n - 1) * d.std(ddof=1) / np.sqrt(n)
    return dict(mean=d.mean(), lo=d.mean() - h, hi=d.mean() + h, wins=int((d > 0).sum()), ties=int((d == 0).sum()), n=n)


def show_pairs(df, group, pairs, metric, key='seed'):
    for a, b in pairs:
        r = paired(df, group, a, b, metric, key)
        if r:
            print(f'   {a} minus {b} [{metric}]: {r["mean"]:+.4g} (95% t {r["lo"]:+.4g} to {r["hi"]:+.4g}), '
                  f'wins {r["wins"]}/{r["n"]}, ties {r["ties"]}')
        else:
            print(f'   {a} minus {b}: labels not found')
    print()


def audit(root: Path, versions):
    L = root / 'life'

    def rd(*p):
        return pd.read_csv(L.joinpath(*p))

    if 'v0.1' in versions:
        d = rd('v0.1', 'trials.csv')
        table(d, 'method', ['survivors', 'habitat', 'contribution_rate', 'gate_accuracy'], title='v0.1 trials.csv (30 seeds)')
        d['alive'] = d.survivors > 0
        table(d, 'method', [], sums=['alive'], title='v0.1 worlds with a survivor')
    if 'v0.2' in versions:
        d = rd('v0.2', 'trials.csv')
        table(d, 'strategy', ['population', 'mean_habitat', 'contribution_rate', 'mean_contribution_bias'], sums=['extinct'], title='v0.2 trials.csv (30 seeds)')
        show_pairs(d, 'strategy', [('evolving', 'clonal'), ('evolving', 'fresh_genomes')], 'population')
        table(rd('v0.2', 'main_trials_bias_guard.csv'), 'strategy', ['population', 'mean_contribution_bias'], title='v0.2 bias guard')
        r = rd('v0.2', 'robustness_trials.csv')
        table(r, ['environment', 'strategy'], ['population'], title='v0.2 robustness (12 seeds)')
    if 'v0.3' in versions:
        d = rd('v0.3', 'trials.csv')
        d['viable'] = (d.population >= 32) & (d.mean_habitat >= .40)
        table(d, 'strategy', ['population', 'mean_habitat', 'contribution_rate'], sums=['extinct', 'viable'], title='v0.3 trials.csv (30 seeds)')
        r = rd('v0.3', 'robustness_trials.csv')
        table(r, ['scenario', 'strategy'], ['population'], title='v0.3 robustness (12 seeds)')
    if 'v0.4' in versions:
        d = rd('v0.4', 'heldout_all_24_worlds.csv')
        table(d, 'strategy', ['link_accuracy', 'mean_link_reward', 'population', 'contribution_rate', 'phase1_late_accuracy', 'phase2_late_accuracy'], sums=['viable'], title='v0.4 heldout (24 seeds)')
        show_pairs(d, 'strategy', [('social_learn', 'social_frozen'), ('social_learn', 'social_scrambled'), ('social_learn', 'social_random'), ('social_learn', 'social_noculture')], 'link_accuracy')
        show_pairs(d, 'strategy', [('social_learn', 'social_always_open')], 'population')
        r = rd('v0.4', 'robustness_all_8_worlds.csv')
        grp = [c for c in ('scenario', 'condition', 'stress') if c in r.columns]
        table(r, grp + ['strategy'], ['population', 'link_accuracy'], sums=['viable'], title='v0.4 robustness (8 seeds)')
    if 'v0.5' in versions:
        d = rd('v0.5', 'main_trials.csv')
        table(d, 'strategy', ['population', 'mean_population_last40', 'habitat', 'unique_centers', 'center_reliability_sigma', 'contribution_rate', 'network_agreement'], sums=['viable'], title='v0.5 main_trials.csv (30 seeds)')
        show_pairs(d, 'strategy', [('emergent', 'local'), ('emergent', 'random'), ('emergent', 'fixed'), ('emergent', 'emergent_no_feedback')], 'population')
        k = rd('v0.5', 'knockout_trials.csv')
        table(k, 'strategy', ['population', 'post_knockout_population', 'contribution_rate'], sums=['center_removed', 'viable'], title='v0.5 knockout (12 seeds)')
        s = rd('v0.5', 'stress_trials.csv')
        table(s, 'strategy', ['population', 'habitat', 'contribution_rate'], sums=['viable'], title='v0.5 stress (10 seeds)')
    if 'v0.6' in versions:
        d = rd('v0.6', 'main_30_worlds.csv')
        d['frac_above'] = d.tail_population_above_threshold / 144
        table(d, 'strategy', ['energy_per_site_tail', 'frac_above', 'flow_concentration_tail', 'distinct_loci', 'locus_changes'], title='v0.6 main (30 seeds)')
        show_pairs(d, 'strategy', [('adaptive', 'uniform'), ('adaptive', 'adaptive_shuffled'), ('adaptive', 'random_fixed')], 'energy_per_site_tail')
        f = rd('v0.6', 'frozen_after_change_30.csv')
        table(f, 'strategy', ['energy_per_site_tail'], title='v0.6 frozen after change')
        k = rd('v0.6', 'knockout_30_worlds.csv')
        table(k, 'intervention', ['mean_energy_damage', 'mean_energy_recovery', 'tail_energy'], title='v0.6 knockout (30 seeds)')
    if 'v0.7' in versions:
        d = rd('v0.7', 'main_0_30.csv')
        table(d, 'strategy', ['population', 'final_population', 'habitat', 'contribution_mean', 'concentration', 'distinct_loci'], sums=['viable'], title='v0.7 main_0_30.csv (30 seeds)')
        show_pairs(d, 'strategy', [('distributed', 'local_only'), ('distributed', 'fixed_links'), ('distributed', 'shifted'), ('distributed', 'high_fixed')], 'population')
        i = rd('v0.7', 'injury_0_24.csv')
        table(i, ['strategy', 'injury'], ['population', 'habitat', 'reformed_locus', 'injured_count'], sums=['viable'], title='v0.7 injury (24 seeds)')
    if 'v0.8' in versions:
        d = rd('v0.8', 'main_trials_1000_1030.csv')
        table(d, 'strategy', ['population', 'habitat', 'contribution', 'effect_mae', 'mean_trust', 'warning_prediction_lift'], sums=['viable'], title='v0.8 main (30 seeds)')
        show_pairs(d, 'strategy', [('causal_field', 'causal_local'), ('causal_field', 'no_action_model'), ('causal_field', 'frozen'), ('causal_field', 'fixed'), ('causal_field', 'shuffled_field')], 'population')
        w = rd('v0.8', 'wave_trials_2000_2012.csv')
        table(w, 'strategy', ['population', 'habitat'], sums=['viable'], title='v0.8 wave (12 seeds)')
        k = rd('v0.8', 'knockout_trials_3000_3012.csv')
        table(k, 'strategy', ['population', 'reform_after_knockout'], title='v0.8 knockout (12 seeds)')
    if 'v0.9' in versions:
        d = rd('v0.9', 'main_all_30_worlds.csv')
        table(d, 'strategy', ['population', 'habitat', 'mean_maintenance', 'center_turnover', 'mean_regulator'], sums=['viability'], title='v0.9 main (30 seeds)')
        show_pairs(d, 'strategy', [('field', 'local_equal_effort'), ('field', 'scrambled'), ('field', 'fixed'), ('field', 'adaptive')], 'population')
        i = rd('v0.9', 'interventions_all_16_worlds.csv')
        table(i, ['strategy', 'intervention'], ['population', 'habitat', 'post_injury_pop'], title='v0.9 interventions (16 seeds)')
        show_pairs(i[i.strategy == 'field'], 'intervention', [('relay_top', 'relay_random'), ('none', 'relay_silence'), ('top', 'random')], 'population')
        p = rd('v0.9', 'dependency_all_12_worlds.csv')
        table(p, 'condition', ['population', 'habitat'], sums=['viability'], title='v0.9 dependency (12 seeds)')
    if 'v1.0' in versions:
        d = rd('v1.0', 'main_all_30_worlds.csv')
        table(d, ['environment', 'mode'], ['population', 'habitat', 'investment', 'message_future_correlation'], sums=['viability'], title='v1.0 main (30 seeds x 2 environments)')
        for env in d.environment.unique():
            print(f'   environment {env}:')
            show_pairs(d[d.environment == env], 'mode', [('learned', 'no_relay'), ('learned', 'frozen'), ('learned', 'random'), ('learned', 'shuffled'), ('learned', 'uniform_sham')], 'population')
        i = rd('v1.0', 'interventions_all_30_worlds.csv')
        table(i, 'condition', ['population', 'habitat', 'viability'], title='v1.0 interventions (30 seeds)')
    if 'v1.1' in versions:
        d = rd('v1.1', 'v11_main_30_seeds.csv')
        table(d, 'mode', ['population', 'habitat', 'funding_phase1', 'funding_phase2', 'funding_phase3', 'births', 'deaths'], sums=['viable'], title='v1.1 main (30 seeds)')
        show_pairs(d, 'mode', [('contextual_temporal', 'contextual_onestep'), ('contextual_temporal', 'scrambled'), ('contextual_temporal', 'risk_reactive')], 'population')
        i = rd('v1.1', 'v11_interventions_30_seeds.csv')
        table(i, 'condition', ['population', 'habitat'], title='v1.1 interventions (30 seeds)')
    if 'v1.2' in versions:
        d = rd('v1.2', 'heldout_trials.csv')
        table(d, 'policy', ['final_population', 'phase2_buffer', 'phase5_buffer', 'phase3_buffer', 'phase3_sharing', 'phase6_sharing'], title='v1.2 heldout (30 seeds)')
        show_pairs(d, 'policy', [('learner', 'private'), ('learner', 'scrambled'), ('learner', 'frozen'), ('learner', 'random'), ('learner', 'reactive')], 'final_population')
        i = rd('v1.2', 'intervention_trials.csv')
        table(i, 'intervention', ['final_population'], title='v1.2 interventions (30 seeds)')
    if 'v1.3' in versions:
        d = rd('v1.3', 'main_24_seeds.csv')
        table(d, 'strategy', ['final_population', 'mean_groups', 'mean_largest', 'grouped_fraction', 'edge_retention', 'protect_storm', 'protect_mild', 'share_scarcity'], title='v1.3 main (24 seeds)')
        show_pairs(d, 'strategy', [('adaptive', 'random'), ('adaptive', 'no_links'), ('adaptive', 'no_memory'), ('adaptive', 'shuffled_credit')], 'final_population')
        i = rd('v1.3', 'interventions_24_seeds.csv')
        table(i, 'intervention', ['final_population', 'mean_groups'], title='v1.3 interventions (24 seeds)')
        show_pairs(i, 'intervention', [('none', 'blackout'), ('none', 'sever_hubs'), ('none', 'sever_random'), ('none', 'sever_matched_edges')], 'final_population')
    if 'v1.4' in versions:
        d = rd('v1.4', 'main_24_worlds.csv')
        table(d, 'policy', ['final_population', 'mean_links', 'mean_groups', 'grouped_fraction', 'bond_retention', 'protect_storm', 'protect_mild'], title='v1.4 main (24 seeds)')
        show_pairs(d, 'policy', [('causal_probe', 'random'), ('causal_probe', 'no_probe'), ('causal_probe', 'shuffled_feedback'), ('causal_probe', 'frozen_learning')], 'final_population')
        i = rd('v1.4', 'interventions_24_worlds.csv')
        table(i, 'intervention', ['final_population'], title='v1.4 interventions (24 seeds)')
        table(rd('v1.4', 'v13_matched_reference.csv'), 'strategy', ['final_population'], title='v1.4 matched v1.3 reference')
    if 'v1.5' in versions:
        d = rd('v1.5', 'heldout_32_worlds.csv')
        table(d, 'strategy', ['final_population', 'links', 'protect_storm', 'protect_mild', 'trial_edges', 'trial_mae', 'trial_sign_accuracy', 'attributed_sign_accuracy'], title='v1.5 heldout (32 seeds)')
        show_pairs(d, 'strategy', [('crossover', 'random'), ('crossover', 'always_protect'), ('crossover', 'frozen'), ('crossover', 'reactive_rule')], 'final_population')
        i = rd('v1.5', 'interventions_32_worlds.csv')
        table(i, 'intervention', ['final_population'], title='v1.5 interventions (32 seeds)')
    if 'v1.6' in versions:
        d = rd('v1.6', 'all_48_worlds.csv')
        d['cohort'] = np.where(d.seed < 161700, '161600', '161700')
        table(d, 'strategy', ['final_population', 'trial_edges', 'trial_cost', 'attributed_sign_accuracy', 'probe_risk', 'unprobed_risk', 'probe_uncertainty', 'unprobed_uncertainty'], title='v1.6 all 48 worlds')
        table(d, ['cohort', 'strategy'], ['final_population'], title='v1.6 by cohort')
        show_pairs(d, 'strategy', [('self_initiated', 'random'), ('self_initiated', 'scheduled'), ('self_initiated', 'risk_only'), ('self_initiated', 'no_trials'), ('self_initiated', 'frozen')], 'final_population')
    if 'v1.7' in versions:
        d = rd('v1.7', 'heldout_00_30.csv')
        table(d, 'strategy', ['final_population', 'trial_edges', 'final_energy', 'trial_sign_accuracy', 'trial_cost', 'mean_groups'], title='v1.7 heldout (30 seeds)')
        show_pairs(d, 'strategy', [('voi_budget', 'uncertainty_budget'), ('voi_budget', 'risk_budget'), ('voi_budget', 'random_budget'), ('voi_budget', 'no_probes'), ('voi_budget', 'reactive_rule')], 'final_population')
    if 'v1.8' in versions:
        for fam in ('standard', 'high_cost', 'noisy', 'reversed'):
            d = rd('v1.8', f'heldout_{fam}.csv')
            table(d, 'strategy', ['cumulative_net', 'trials', 'mean_test_cost', 'mean_cost_mae', 'fixed_cost_mae', 'observation_sign_accuracy'], title=f'v1.8 {fam}')
            if fam == 'standard':
                show_pairs(d, 'strategy', [('learned_cost', 'information_only'), ('learned_cost', 'random'), ('learned_cost', 'frozen_value'), ('learned_cost', 'scrambled_cost')], 'cumulative_net')
    if 'v1.9' in versions:
        for fam in ('standard', 'volatile', 'noisy', 'low_stability_signal'):
            d = rd('v1.9', f'heldout_{fam}.csv')
            table(d, 'strategy', ['cumulative_net', 'trials', 'explicit_test_cost', 'mean_future_knowledge_gain', 'stability_selected', 'viable_agents'], title=f'v1.9 {fam}')
            if fam == 'standard':
                show_pairs(d, 'strategy', [('future_value', 'information_only'), ('future_value', 'scrambled_future'), ('future_value', 'uncertainty'), ('future_value', 'stable_cue'), ('future_value', 'random')], 'cumulative_net')
                a = d[d.strategy == 'frozen_future'].set_index('seed').cumulative_net
                b = d[d.strategy == 'information_only'].set_index('seed').cumulative_net
                if len(a) and len(b):
                    print('   frozen_future identical to information_only:', bool(np.allclose(a, b.reindex(a.index))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root')
    ap.add_argument('--versions', default=None)
    ap.add_argument('--old', default=None)
    ap.add_argument('--verify', action='store_true')
    a = ap.parse_args()
    root = Path(a.root)
    if a.verify:
        verify_manifest(root)
        return
    if a.old:
        compare_foundation(Path(a.old), root / 'experiments')
        return
    vs = a.versions.split(',') if a.versions else [p.name for p in (root / 'life').glob('v*')]
    audit(root, vs)


if __name__ == '__main__':
    main()
