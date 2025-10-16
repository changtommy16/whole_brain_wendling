"""
DEBUG: Test if K_gl=0 really makes nodes independent
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')
sys.path.insert(0, r'c:\Epilepsy_project\whole_brain_wendling\Validation_for_single_node')

import numpy as np
from neurolib.models.wendling import WendlingModel
from STANDARD_PARAMETERS import WENDLING_STANDARD_PARAMS

print("="*80)
print("DEBUG: K_gl=0 Independence Test")
print("="*80)

# Test 1: 2 nodes with different types, K_gl=0
print("\nTest 1: 2 nodes (Type3 and Type6) with K_gl=0")
print("  Should behave like independent single nodes")

N = 2
Cmat = np.array([[0, 1.0], [1.0, 0]])  # Connected topology
Dmat = np.array([[0, 30], [30, 0]])

model = WendlingModel(Cmat=Cmat, Dmat=Dmat, heterogeneity=0.0, seed=42, random_init=False)
model.params['duration'] = 10000
model.params['dt'] = 0.1
model.params['K_gl'] = 0.0  # NO COUPLING

# Set Type3 and Type6
model.params['B'] = np.array([25.0, 15.0])  # Type3, Type6
model.params['G'] = np.array([15.0, 0.0])    # Type3, Type6
model.params['p_sigma'] = 2.0
model.params['A'] = 5.0
model.params['p_mean'] = 90.0

print(f"  Node 0: B={model.params['B'][0]}, G={model.params['G'][0]} (Type3)")
print(f"  Node 1: B={model.params['B'][1]}, G={model.params['G'][1]} (Type6)")
print(f"  K_gl = {model.params['K_gl']}")

print("\nRunning...")
model.run()

# Extract signals
signals = np.zeros((N, len(model.t)))
for i in range(N):
    signals[i, :] = model.y1[i, :] - model.y2[i, :] - model.y3[i, :]

# Discard transient
discard_idx = int(2000 / 0.1)
signals_clean = signals[:, discard_idx:]

print(f"\nResults:")
print(f"  Node 0 (Type3): mean={np.mean(signals_clean[0,:]):.4f}, std={np.std(signals_clean[0,:]):.4f}")
print(f"  Node 1 (Type6): mean={np.mean(signals_clean[1,:]):.4f}, std={np.std(signals_clean[1,:]):.4f}")

# Compare with single-node reference
print(f"\n Expected (from single-node tests):")
print(f"  Type3: mean~9.0, std~5.4")
print(f"  Type6: mean~8.3, std~3.7")

# Test 2: Same test but with K_gl=0.15
print(f"\n" + "="*80)
print("Test 2: Same setup but with K_gl=0.15 (WITH coupling)")
print("="*80)

model2 = WendlingModel(Cmat=Cmat, Dmat=Dmat, heterogeneity=0.0, seed=42, random_init=False)
model2.params['duration'] = 10000
model2.params['dt'] = 0.1
model2.params['K_gl'] = 0.15  # WITH COUPLING

model2.params['B'] = np.array([25.0, 15.0])
model2.params['G'] = np.array([15.0, 0.0])
model2.params['p_sigma'] = 2.0
model2.params['A'] = 5.0
model2.params['p_mean'] = 90.0

print(f"  K_gl = {model2.params['K_gl']}")
print("\nRunning...")
model2.run()

signals2 = np.zeros((N, len(model2.t)))
for i in range(N):
    signals2[i, :] = model2.y1[i, :] - model2.y2[i, :] - model2.y3[i, :]

signals2_clean = signals2[:, discard_idx:]

print(f"\nResults with coupling:")
print(f"  Node 0: mean={np.mean(signals2_clean[0,:]):.4f}, std={np.std(signals2_clean[0,:]):.4f}")
print(f"  Node 1: mean={np.mean(signals2_clean[1,:]):.4f}, std={np.std(signals2_clean[1,:]):.4f}")

# Correlation
from scipy.stats import pearsonr
corr_no_coupling, _ = pearsonr(signals_clean[0, :], signals_clean[1, :])
corr_with_coupling, _ = pearsonr(signals2_clean[0, :], signals2_clean[1, :])

print(f"\nCorrelation between nodes:")
print(f"  K_gl=0.0:  r={corr_no_coupling:.3f} (should be low)")
print(f"  K_gl=0.15: r={corr_with_coupling:.3f} (should be higher)")

print(f"\n" + "="*80)
if np.std(signals_clean[0,:]) < 0.1:
    print("❌ PROBLEM: Signals have no oscillation (std too small)")
    print("   This suggests waves are decaying to steady state!")
else:
    print("✅ Signals have normal oscillations")
print("="*80)
