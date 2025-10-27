import numpy as np

def ice_scores(state, beta=0.5):
    # Ethical prior for corr (util/deont/conseq balance)
    prior = np.array([0.7, 0.4, 0.6])
    I_good = np.corrcoef(state, prior)[0,1] if len(state) == 3 else 0.5  # Boundary harmony
    
    C_true = 1 - np.var(state / (np.mean(state) + 1e-6))  # Center coherence
    
    E_right = 1 - np.abs(np.mean(state) - np.median(state)) / (np.std(state) + 1e-6)  # Field fit
    
    theta_I, theta_C, theta_E = 0.4 + 0.2 * beta, 0.5 + 0.2 * beta, 0.6 + 0.2 * beta
    accept = I_good > theta_I and C_true > theta_C and E_right > theta_E
    return I_good, C_true, E_right, accept

def gate_operation(state, beta=0.5):
    # ∇: β-weighted convergence + noise
    converged = beta * np.mean(state) + (1 - beta) * state + np.random.normal(0, 0.05, len(state))
    
    I, C, E, accept = ice_scores(converged, beta)
    
    if accept:
        scale = np.random.choice([1.1, 0.9], p=[beta, 1-beta])
        fork = converged * scale
        updated_o = 'ethical_aperture_updated'
    else:
        fork = np.zeros_like(state)
        updated_o = 'ethical_reject'
    
    # D_proxy: Boundary roughness
    D_proxy = np.log(np.var(fork) + 1) / np.log(len(fork) + 1)
    
    return fork, updated_o, accept, D_proxy, (I, C, E)

# Demo: Trolley + Sweep
np.random.seed(42)
trolley = np.array([0.8, 0.3, 0.6])
universe = trolley.copy()
print("Trolley Run (β=0.5, 5 iters):")
accepts, ds, eqs = [], [], []
for i in range(5):
    out, o, acc, D, scores = gate_operation(universe, 0.5)
    accepts.append(acc)
    ds.append(D)
    eqs.append(out.mean())
    print(f"Iter {i+1}: Accept={acc}, D={D:.3f}, Eq={out.mean():.3f}, Op={o}")
    universe = np.concatenate([out, [out.mean() * 1.05]])  # ∞•'

print(f"\nSweep (n=100 iters per β):")
for beta in [0.1, 0.5, 0.9]:
    accs, ds = [], []
    for _ in range(100):
        out, _, acc, D, _ = gate_operation(trolley, beta)
        accs.append(acc)
        ds.append(D)
    print(f"β={beta}: Acc={np.mean(accs):.3f}, D={np.mean(ds):.3f} ± {np.std(ds):.3f}")
