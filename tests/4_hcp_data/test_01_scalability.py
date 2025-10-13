"""
Scalability Test: 80-nodes Network

Test if the model scales to larger networks.
Since we don't have actual HCP data loaded yet, we'll test with a synthetic 80-node network.

Validation:
- Model runs without errors
- FC in reasonable range
- Computation time acceptable
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from neurolib.models.wendling import WendlingModel
import time

print("="*80)
print("80-Nodes Scalability Test")
print("="*80)

# Network configuration
N = 80
np.random.seed(42)

# Create synthetic connectivity (small-world like)
print(f"\nCreating {N}-node network...")

# Start with ring lattice (increased k for better density)
k = 10  # Increased from 4 to get density ~0.35
Cmat = np.zeros((N, N))

for i in range(N):
    for offset in range(1, k+1):
        j = (i + offset) % N
        weight = np.random.uniform(0.6, 1.0)
        Cmat[i, j] = weight
        Cmat[j, i] = weight

# Add random long-range connections (small-world)
p_rewire = 0.15  # Increased for more connectivity
for i in range(N):
    for j in range(i+1, N):
        if Cmat[i, j] == 0 and np.random.rand() < p_rewire:
            weight = np.random.uniform(0.3, 0.6)
            Cmat[i, j] = weight
            Cmat[j, i] = weight

# Distance matrix (based on connection strength: stronger = closer)
Dmat = np.zeros((N, N))
for i in range(N):
    for j in range(i+1, N):
        if Cmat[i, j] > 0:
            # Stronger connections = shorter distances
            dist = 20 + (1.0 - Cmat[i, j]) * 40  # 20-60mm range
        else:
            # No connection = longer distances
            dist = np.random.uniform(60, 100)
        Dmat[i, j] = dist
        Dmat[j, i] = dist

n_edges = int(np.sum(Cmat > 0) / 2)
density = n_edges / (N * (N-1) / 2)

print(f"  Nodes: {N}")
print(f"  Edges: {n_edges}")
print(f"  Density: {density:.3f}")

# Create model
print(f"\nCreating model...")
start_time = time.time()

model = WendlingModel(Cmat=Cmat, Dmat=Dmat, heterogeneity=0.30, seed=42)
model.params['duration'] = 5000  # 5 seconds (shorter for speed)
model.params['dt'] = 0.1
model.params['K_gl'] = 0.08  # Reduced from 0.12 for lower FC (larger network needs weaker coupling)

init_time = time.time() - start_time
print(f"  Initialization time: {init_time:.2f}s")
print(f"  heterogeneity = 0.30")
print(f"  K_gl = 0.08")

# Run simulation
print(f"\nRunning simulation...")
start_time = time.time()
model.run()
sim_time = time.time() - start_time

print(f"  Simulation time: {sim_time:.2f}s")
print(f"  Time per second: {sim_time/5:.2f}s")

# Extract signals
print(f"\nExtracting signals...")
t = model.t
signals = np.zeros((N, len(t)))
for i in range(N):
    signals[i, :] = model.y1[i, :] - model.y2[i, :] - model.y3[i, :]

# Discard transient
discard_idx = int(1000 / 0.1)
signals_clean = signals[:, discard_idx:]

# Compute FC (sample subset for speed)
print(f"\nComputing FC...")
start_time = time.time()

fc = np.zeros((N, N))
for i in range(N):
    for j in range(i, N):
        fc[i, j], _ = pearsonr(signals_clean[i, :], signals_clean[j, :])
        fc[j, i] = fc[i, j]

fc_time = time.time() - start_time
print(f"  FC computation time: {fc_time:.2f}s")

# Statistics
mean_fc = np.mean(np.abs(fc[~np.eye(N, dtype=bool)]))
std_fc = np.std(fc[~np.eye(N, dtype=bool)])

# SC-FC correlation
sc_flat = Cmat[~np.eye(N, dtype=bool)]
fc_flat = np.abs(fc[~np.eye(N, dtype=bool)])
sc_fc_corr, _ = pearsonr(sc_flat, fc_flat)

print(f"\nResults:")
print(f"  Mean |FC|: {mean_fc:.3f}")
print(f"  Std FC: {std_fc:.3f}")
print(f"  SC-FC correlation: {sc_fc_corr:.3f}")

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
checks.append(("FC in reasonable range", 0.2 <= mean_fc <= 0.8))
checks.append(("Signals stable (< 50 mV)", np.abs(signal_stats['max']) < 50))
checks.append(("SC-FC correlation > 0.1", sc_fc_corr > 0.1))
checks.append(("Total time < 60s", (init_time + sim_time + fc_time) < 60))

for check_name, passed in checks:
    status = "PASS" if passed else "FAIL"
    print(f"  {status}: {check_name}")

all_pass = all(c[1] for c in checks)

# Plotting
print(f"\nGenerating plots...")
fig = plt.figure(figsize=(20, 10))

# 1. SC Matrix (downsampled for visualization)
ax1 = plt.subplot(2, 4, 1)
im1 = ax1.imshow(Cmat, cmap='hot', aspect='auto', interpolation='nearest')
ax1.set_xlabel('Node', fontsize=10)
ax1.set_ylabel('Node', fontsize=10)
ax1.set_title(f'Structural Connectivity ({N} nodes)', fontsize=12, fontweight='bold')
plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)

# 2. FC Matrix
ax2 = plt.subplot(2, 4, 2)
im2 = ax2.imshow(fc, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto', interpolation='nearest')
ax2.set_xlabel('Node', fontsize=10)
ax2.set_ylabel('Node', fontsize=10)
ax2.set_title(f'Functional Connectivity (mean={mean_fc:.3f})', fontsize=12, fontweight='bold')
plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)

# 3. SC vs FC
ax3 = plt.subplot(2, 4, 3)
# Sample for visualization
sample_idx = np.random.choice(len(sc_flat), min(2000, len(sc_flat)), replace=False)
ax3.scatter(sc_flat[sample_idx], fc_flat[sample_idx], s=10, alpha=0.3)
ax3.set_xlabel('SC', fontsize=10)
ax3.set_ylabel('|FC|', fontsize=10)
ax3.set_title(f'SC vs FC (r={sc_fc_corr:.3f})', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3)

# 4. FC Distribution
ax4 = plt.subplot(2, 4, 4)
fc_vals = fc[~np.eye(N, dtype=bool)]
ax4.hist(fc_vals, bins=30, alpha=0.7, edgecolor='black')
ax4.axvline(mean_fc, color='red', linestyle='--', linewidth=2, label=f'Mean={mean_fc:.3f}')
ax4.set_xlabel('FC Value', fontsize=10)
ax4.set_ylabel('Count', fontsize=10)
ax4.set_title('FC Distribution', fontsize=12, fontweight='bold')
ax4.legend()
ax4.grid(True, alpha=0.3)

# 5. Sample time series (10 nodes)
ax5 = plt.subplot(2, 4, 5)
sample_nodes = np.linspace(0, N-1, 10, dtype=int)
time_window = 2000
time_idx = int(time_window / 0.1)

for i, node_id in enumerate(sample_nodes):
    offset = i * 8
    ax5.plot(t[:time_idx], signals[node_id, :time_idx] + offset, 
            linewidth=0.6, alpha=0.7, label=f'N{node_id}')

ax5.set_xlabel('Time (ms)', fontsize=10)
ax5.set_ylabel('Activity (mV)', fontsize=10)
ax5.set_title('Sample Node Activities (10/{})'.format(N), fontsize=12, fontweight='bold')
ax5.legend(fontsize=7, ncol=2, loc='upper right')
ax5.grid(True, alpha=0.3)

# 6. Degree distribution
ax6 = plt.subplot(2, 4, 6)
degrees = np.sum(Cmat > 0, axis=1)
ax6.hist(degrees, bins=15, alpha=0.7, edgecolor='black', color='steelblue')
ax6.set_xlabel('Degree', fontsize=10)
ax6.set_ylabel('Count', fontsize=10)
ax6.set_title(f'Degree Distribution (mean={np.mean(degrees):.1f})', fontsize=12, fontweight='bold')
ax6.grid(True, alpha=0.3, axis='y')

# 7. Performance summary
ax7 = plt.subplot(2, 4, 7)
ax7.axis('off')
perf_text = f"""
Performance Summary:

Network Size:
  Nodes: {N}
  Edges: {n_edges}
  Density: {density:.3f}

Computation Time:
  Initialization: {init_time:.2f}s
  Simulation: {sim_time:.2f}s
  FC computation: {fc_time:.2f}s
  Total: {init_time+sim_time+fc_time:.2f}s

Time per sim second: {sim_time/5:.2f}s
"""
ax7.text(0.1, 0.9, perf_text, transform=ax7.transAxes, fontsize=10,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

# 8. Validation summary
ax8 = plt.subplot(2, 4, 8)
ax8.axis('off')
validation_text = f"""
Validation Results:

{"PASS" if 0.2 <= mean_fc <= 0.8 else "FAIL"}: FC in range
  Mean |FC| = {mean_fc:.3f}

{"PASS" if np.abs(signal_stats['max']) < 50 else "FAIL"}: Signals stable
  Max = {signal_stats['max']:.2f} mV

{"PASS" if sc_fc_corr > 0.1 else "FAIL"}: SC-FC corr
  r = {sc_fc_corr:.3f}

{"PASS" if (init_time + sim_time + fc_time) < 60 else "FAIL"}: Time < 60s
  Total = {init_time+sim_time+fc_time:.1f}s

Overall: {"PASS" if all_pass else "FAIL"}
"""
ax8.text(0.1, 0.9, validation_text, transform=ax8.transAxes, fontsize=10,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', 
                  facecolor='lightgreen' if all_pass else 'lightyellow', 
                  alpha=0.8))

plt.suptitle('80-Nodes Scalability Test (het=0.30, K_gl=0.08)', 
             fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout()

# Save
import os
save_path = '../../results/hcp_data/scalability_test.png'
os.makedirs(os.path.dirname(save_path), exist_ok=True)
plt.savefig(save_path, dpi=150, bbox_inches='tight')
print(f"\nSaved: {save_path}")
plt.close('all')  # Close figure instead of showing

print("\n" + "="*80)
print("Scalability Test Complete")
print("="*80)
print(f"\n[{'SUCCESS' if all_pass else 'WARNING'}] 80-nodes network {'passed' if all_pass else 'needs review'}!")
print(f"Total time: {init_time+sim_time+fc_time:.1f}s")
print("="*80)
