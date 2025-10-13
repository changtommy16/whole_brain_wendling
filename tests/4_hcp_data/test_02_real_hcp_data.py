"""
Real HCP Data Test - Using Human Connectome Project Data

Load actual brain connectivity from HCP dataset and run Wendling model.
Compare simulated FC with empirical FC.
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from neurolib.models.wendling import WendlingModel
from neurolib.utils.loadData import Dataset
import time

print("="*80)
print("Real HCP Data Test - Wendling Whole-Brain Model")
print("="*80)

# Load HCP dataset
print("\nLoading HCP dataset...")
try:
    ds = Dataset("hcp")
    print(f"  Dataset loaded successfully!")
    print(f"  Number of subjects: {len(ds.data['subjects'])}")
    print(f"  Cmat shape: {ds.Cmat.shape}")
    print(f"  Dmat shape: {ds.Dmat.shape}")
    
    N = ds.Cmat.shape[0]
    print(f"  Number of brain regions: {N}")
    
    # Network statistics
    density = np.sum(ds.Cmat > 0) / (N * (N-1))
    print(f"  SC density: {density:.3f}")
    print(f"  SC range: [{np.min(ds.Cmat):.3f}, {np.max(ds.Cmat):.3f}]")
    print(f"  Distance range: [{np.min(ds.Dmat[ds.Dmat>0]):.1f}, {np.max(ds.Dmat):.1f}] mm")
    
except Exception as e:
    print(f"  ERROR: Could not load HCP dataset: {e}")
    print(f"\n  Possible reasons:")
    print(f"  1. HCP data not downloaded")
    print(f"  2. Data files not in correct location")
    print(f"  3. File format issues")
    print(f"\n  Falling back to synthetic data for demonstration...")
    
    # Create synthetic data as fallback
    N = 80
    np.random.seed(42)
    
    # Small-world network
    k = 10
    Cmat = np.zeros((N, N))
    for i in range(N):
        for offset in range(1, k+1):
            j = (i + offset) % N
            weight = np.random.uniform(0.6, 1.0)
            Cmat[i, j] = weight
            Cmat[j, i] = weight
    
    # Normalize to [0, 1]
    Cmat = Cmat / np.max(Cmat)
    
    # Distance matrix
    Dmat = np.zeros((N, N))
    for i in range(N):
        for j in range(i+1, N):
            if Cmat[i, j] > 0:
                dist = 20 + (1.0 - Cmat[i, j]) * 50
            else:
                dist = np.random.uniform(70, 120)
            Dmat[i, j] = dist
            Dmat[j, i] = dist
    
    density = np.sum(Cmat > 0) / (N * (N-1))
    print(f"\n  Using synthetic data:")
    print(f"  Nodes: {N}")
    print(f"  Density: {density:.3f}")
    
    # No empirical FC available
    empirical_fc = None
    ds = None

# If we have real data, get empirical FC
if ds is not None and hasattr(ds, 'FCs') and len(ds.FCs) > 0:
    empirical_fc = np.mean(ds.FCs, axis=0)  # Average across subjects
    print(f"\n  Empirical FC loaded!")
    print(f"  Mean |FC|: {np.mean(np.abs(empirical_fc[~np.eye(N, dtype=bool)])):.3f}")
    Cmat = ds.Cmat.copy()
    Dmat = ds.Dmat.copy()
else:
    empirical_fc = None
    print(f"\n  No empirical FC available (continuing without it)")

# Create Wendling model
print(f"\nCreating Wendling model...")
start_time = time.time()

# Threshold sparse connectivity (remove weak connections)
Cmat_thresh = Cmat.copy()
threshold = np.percentile(Cmat[Cmat > 0], 30)  # Keep top 70% connections
Cmat_thresh[Cmat_thresh < threshold] = 0
density_after = np.sum(Cmat_thresh > 0) / (N * (N-1))
print(f"  SC threshold: {threshold:.3f}")
print(f"  Density after threshold: {density_after:.3f}")

model = WendlingModel(Cmat=Cmat_thresh, Dmat=Dmat, heterogeneity=0.30, seed=42)
model.params['duration'] = 5000  # 5 seconds
model.params['dt'] = 0.1
model.params['K_gl'] = 0.15  # Increased for better FC (was 0.08)

init_time = time.time() - start_time
print(f"  Initialization: {init_time:.2f}s")
print(f"  Parameters:")
print(f"    heterogeneity = 0.30")
print(f"    K_gl = 0.15")
print(f"    N = {N}")
print(f"    SC density (thresholded) = {density_after:.3f}")

# Run simulation
print(f"\nRunning simulation...")
start_time = time.time()
model.run()
sim_time = time.time() - start_time
print(f"  Simulation completed in {sim_time:.2f}s")

# Extract signals
print(f"\nExtracting signals...")
t = model.t
signals = np.zeros((N, len(t)))
for i in range(N):
    signals[i, :] = model.y1[i, :] - model.y2[i, :] - model.y3[i, :]

# Discard transient
discard_idx = int(1000 / 0.1)
signals_clean = signals[:, discard_idx:]

# Compute simulated FC
print(f"\nComputing simulated FC...")
start_time = time.time()
sim_fc = np.zeros((N, N))
for i in range(N):
    for j in range(i, N):
        sim_fc[i, j], _ = pearsonr(signals_clean[i, :], signals_clean[j, :])
        sim_fc[j, i] = sim_fc[i, j]

fc_time = time.time() - start_time
print(f"  FC computation: {fc_time:.2f}s")

mean_sim_fc = np.mean(np.abs(sim_fc[~np.eye(N, dtype=bool)]))
std_sim_fc = np.std(sim_fc[~np.eye(N, dtype=bool)])

print(f"\nSimulated FC:")
print(f"  Mean |FC|: {mean_sim_fc:.3f}")
print(f"  Std FC: {std_sim_fc:.3f}")

# ==================== DIAGNOSTIC: Activity Type Classification ====================
print(f"\n" + "="*80)
print("DIAGNOSTIC VALIDATION")
print("="*80)

# Sample parameter values
print(f"\nSample Parameter Values (first 10 nodes):")
if isinstance(model.params['B'], np.ndarray):
    sample_nodes = min(10, N)
    print(f"  B: {model.params['B'][:sample_nodes]}")
    print(f"  G: {model.params['G'][:sample_nodes]}")
else:
    print(f"  B: {model.params['B']} (scalar)")
    print(f"  G: {model.params['G']} (scalar)")

# Classify activity types
def classify_activity_type(signal, B, G):
    amplitude = np.std(signal)
    spike_threshold = np.mean(signal) + 3 * np.std(signal)
    n_spikes = np.sum(signal > spike_threshold)
    spike_rate = n_spikes / (len(signal) * 0.0001)
    
    if B < 20:
        return "Type 1"
    elif 20 <= B < 28:
        return "Type 2" if 12 <= G <= 25 else "Type 2*"
    elif 28 <= B < 35:
        return "Type 3" if spike_rate > 2 else "Type 2/3"
    else:
        return "Type 3+"

activity_types = []
for i in range(N):
    B_i = model.params['B'][i] if isinstance(model.params['B'], np.ndarray) else model.params['B']
    G_i = model.params['G'][i] if isinstance(model.params['G'], np.ndarray) else model.params['G']
    activity_type = classify_activity_type(signals_clean[i, :], B_i, G_i)
    activity_types.append(activity_type)

from collections import Counter
type_counts = Counter(activity_types)
print(f"\nActivity Type Distribution:")
for atype in sorted(type_counts.keys()):
    count = type_counts[atype]
    print(f"  {atype}: {count}/{N} nodes ({count/N*100:.1f}%)")

if type_counts.get('Type 3', 0) + type_counts.get('Type 3+', 0) > N * 0.3:
    print(f"\n  ⚠️  WARNING: High proportion of epileptic activity!")
    print(f"  Consider: Reduce B_base or increase G_base")

print("="*80)

# Compare with empirical if available
if empirical_fc is not None:
    # FC-FC correlation
    sim_fc_flat = sim_fc[~np.eye(N, dtype=bool)]
    emp_fc_flat = empirical_fc[~np.eye(N, dtype=bool)]
    fc_fc_corr, _ = pearsonr(sim_fc_flat, emp_fc_flat)
    
    print(f"\nEmpirical FC:")
    print(f"  Mean |FC|: {np.mean(np.abs(emp_fc_flat)):.3f}")
    print(f"  Std FC: {np.std(emp_fc_flat):.3f}")
    print(f"\nFC-FC Correlation: {fc_fc_corr:.3f}")
else:
    fc_fc_corr = None
    print(f"\n  (No empirical FC to compare)")

# SC-FC correlation
sc_flat = Cmat[~np.eye(N, dtype=bool)]
sc_fc_corr, _ = pearsonr(sc_flat, np.abs(sim_fc[~np.eye(N, dtype=bool)]))
print(f"  SC-FC Correlation: {sc_fc_corr:.3f}")

# Signal statistics
signal_stats = {
    'mean': np.mean(signals_clean),
    'std': np.std(signals_clean),
    'min': np.min(signals_clean),
    'max': np.max(signals_clean)
}

print(f"\nSignal statistics:")
print(f"  Mean: {signal_stats['mean']:.3f} mV")
print(f"  Std: {signal_stats['std']:.3f} mV")
print(f"  Range: [{signal_stats['min']:.2f}, {signal_stats['max']:.2f}] mV")

# Validation
print(f"\nValidation:")
checks = []
checks.append(("Simulation completed", True))
checks.append(("FC in reasonable range", 0.2 <= mean_sim_fc <= 0.8))
checks.append(("Signals stable", np.abs(signal_stats['max']) < 50))
if empirical_fc is not None:
    checks.append(("FC-FC correlation > 0.2", fc_fc_corr > 0.2))
checks.append(("SC-FC correlation > 0.05", sc_fc_corr > 0.05))

for check_name, passed in checks:
    status = "PASS" if passed else "FAIL"
    print(f"  {status}: {check_name}")

all_pass = all(c[1] for c in checks)

# Plotting
print(f"\nGenerating plots...")
fig = plt.figure(figsize=(20, 12))

# 1. SC Matrix
ax1 = plt.subplot(2, 4, 1)
im1 = ax1.imshow(Cmat, cmap='hot', aspect='auto', interpolation='nearest')
ax1.set_xlabel('Region', fontsize=10)
ax1.set_ylabel('Region', fontsize=10)
ax1.set_title(f'Structural Connectivity\n({N} regions, density={density:.2f})', 
             fontsize=12, fontweight='bold')
plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)

# 2. Simulated FC Matrix
ax2 = plt.subplot(2, 4, 2)
im2 = ax2.imshow(sim_fc, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto', interpolation='nearest')
ax2.set_xlabel('Region', fontsize=10)
ax2.set_ylabel('Region', fontsize=10)
ax2.set_title(f'Simulated FC\n(mean={mean_sim_fc:.3f})', fontsize=12, fontweight='bold')
plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)

# 3. Empirical FC (if available)
if empirical_fc is not None:
    ax3 = plt.subplot(2, 4, 3)
    mean_emp_fc = np.mean(np.abs(empirical_fc[~np.eye(N, dtype=bool)]))
    im3 = ax3.imshow(empirical_fc, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto', interpolation='nearest')
    ax3.set_xlabel('Region', fontsize=10)
    ax3.set_ylabel('Region', fontsize=10)
    ax3.set_title(f'Empirical FC\n(mean={mean_emp_fc:.3f})', fontsize=12, fontweight='bold')
    plt.colorbar(im3, ax=ax3, fraction=0.046, pad=0.04)
else:
    ax3 = plt.subplot(2, 4, 3)
    ax3.axis('off')
    ax3.text(0.5, 0.5, 'No empirical\nFC available', 
            ha='center', va='center', fontsize=14, transform=ax3.transAxes)

# 4. FC-FC scatter (if empirical available)
ax4 = plt.subplot(2, 4, 4)
if empirical_fc is not None:
    sample_idx = np.random.choice(len(sim_fc_flat), min(2000, len(sim_fc_flat)), replace=False)
    ax4.scatter(emp_fc_flat[sample_idx], sim_fc_flat[sample_idx], s=5, alpha=0.3)
    ax4.plot([-1, 1], [-1, 1], 'r--', linewidth=2, label='Identity')
    ax4.set_xlabel('Empirical FC', fontsize=10)
    ax4.set_ylabel('Simulated FC', fontsize=10)
    ax4.set_title(f'FC-FC Comparison (r={fc_fc_corr:.3f})', fontsize=12, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(-1, 1)
    ax4.set_ylim(-1, 1)
else:
    ax4.axis('off')
    ax4.text(0.5, 0.5, 'No empirical\nFC to compare', 
            ha='center', va='center', fontsize=14, transform=ax4.transAxes)

# 5. Sample signals
ax5 = plt.subplot(2, 4, 5)
sample_nodes = np.linspace(0, N-1, min(10, N), dtype=int)
time_window = 2000
time_idx = int(time_window / 0.1)

for i, node_id in enumerate(sample_nodes):
    offset = i * 8
    ax5.plot(t[:time_idx], signals[node_id, :time_idx] + offset, 
            linewidth=0.6, alpha=0.7, label=f'R{node_id}')

ax5.set_xlabel('Time (ms)', fontsize=10)
ax5.set_ylabel('Activity (mV)', fontsize=10)
ax5.set_title(f'Sample Region Activities ({len(sample_nodes)}/{N})', fontsize=12, fontweight='bold')
ax5.legend(fontsize=7, ncol=2, loc='upper right')
ax5.grid(True, alpha=0.3)

# 6. SC vs simulated FC
ax6 = plt.subplot(2, 4, 6)
sample_idx = np.random.choice(len(sc_flat), min(2000, len(sc_flat)), replace=False)
ax6.scatter(sc_flat[sample_idx], np.abs(sim_fc[~np.eye(N, dtype=bool)])[sample_idx], 
           s=10, alpha=0.3)
ax6.set_xlabel('SC', fontsize=10)
ax6.set_ylabel('|Simulated FC|', fontsize=10)
ax6.set_title(f'SC vs FC (r={sc_fc_corr:.3f})', fontsize=12, fontweight='bold')
ax6.grid(True, alpha=0.3)

# 7. Performance summary
ax7 = plt.subplot(2, 4, 7)
ax7.axis('off')
perf_text = f"""
Performance:

Network:
  Regions: {N}
  SC density: {density:.3f}
  
Computation Time:
  Init: {init_time:.2f}s
  Simulation: {sim_time:.2f}s
  FC: {fc_time:.2f}s
  Total: {init_time+sim_time+fc_time:.2f}s
  
Time per sim-sec: {sim_time/5:.2f}s
"""
ax7.text(0.1, 0.9, perf_text, transform=ax7.transAxes, fontsize=10,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

# 8. Validation summary
ax8 = plt.subplot(2, 4, 8)
ax8.axis('off')
if empirical_fc is not None:
    validation_text = f"""
Validation:

{"PASS" if 0.2 <= mean_sim_fc <= 0.8 else "FAIL"}: FC in range
  Sim FC = {mean_sim_fc:.3f}

{"PASS" if fc_fc_corr > 0.2 else "FAIL"}: FC-FC corr > 0.2
  r = {fc_fc_corr:.3f}

{"PASS" if sc_fc_corr > 0.05 else "FAIL"}: SC-FC corr > 0.05
  r = {sc_fc_corr:.3f}

{"PASS" if np.abs(signal_stats['max']) < 50 else "FAIL"}: Signals stable
  Max = {signal_stats['max']:.2f} mV

Overall: {"PASS" if all_pass else "FAIL"}
"""
else:
    validation_text = f"""
Validation:

{"PASS" if 0.2 <= mean_sim_fc <= 0.8 else "FAIL"}: FC in range
  Sim FC = {mean_sim_fc:.3f}

{"PASS" if sc_fc_corr > 0.05 else "FAIL"}: SC-FC corr > 0.05
  r = {sc_fc_corr:.3f}

{"PASS" if np.abs(signal_stats['max']) < 50 else "FAIL"}: Signals stable
  Max = {signal_stats['max']:.2f} mV

(No empirical FC)

Overall: {"PASS" if all_pass else "FAIL"}
"""

ax8.text(0.1, 0.9, validation_text, transform=ax8.transAxes, fontsize=10,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', 
                  facecolor='lightgreen' if all_pass else 'lightyellow', 
                  alpha=0.8))

data_source = "HCP Data" if ds is not None else "Synthetic Data"
plt.suptitle(f'Wendling Whole-Brain Model - {data_source} (N={N}, het=0.30, K_gl=0.15)', 
             fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout()

# Save
import os
save_path = '../../results/hcp_data/real_hcp_test.png'
os.makedirs(os.path.dirname(save_path), exist_ok=True)
plt.savefig(save_path, dpi=150, bbox_inches='tight')
print(f"\nSaved: {save_path}")
plt.close('all')

print("\n" + "="*80)
print("Real HCP Data Test Complete")
print("="*80)
print(f"\n[{'SUCCESS' if all_pass else 'WARNING'}] Test {'passed' if all_pass else 'needs review'}!")
if empirical_fc is not None:
    print(f"FC-FC correlation: {fc_fc_corr:.3f}")
print(f"SC-FC correlation: {sc_fc_corr:.3f}")
print(f"Total time: {init_time+sim_time+fc_time:.1f}s")
print("="*80)
