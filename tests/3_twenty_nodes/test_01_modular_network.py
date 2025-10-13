"""
20-nodes Modular Network Analysis

Network design:
- 4 modules, 5 nodes each
- High intra-module connectivity (density=0.8)
- Low inter-module connectivity (density=0.2)

Validation:
- Modularity Q > 0.3
- Intra-module FC > inter-module FC
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.stats import pearsonr
from neurolib.models.wendling import WendlingModel

print("="*80)
print("20-Nodes Modular Network Analysis")
print("="*80)

# Network configuration
N = 20
n_modules = 4
nodes_per_module = 5

# Create modular connectivity matrix
np.random.seed(42)

# Initialize
Cmat = np.zeros((N, N))

# Module assignments
modules = np.zeros(N, dtype=int)
for i in range(n_modules):
    modules[i*nodes_per_module:(i+1)*nodes_per_module] = i

print(f"\nNetwork configuration:")
print(f"  Total nodes: {N}")
print(f"  Modules: {n_modules}")
print(f"  Nodes per module: {nodes_per_module}")

# Build connectivity
intra_density = 0.8
inter_density = 0.2

for i in range(N):
    for j in range(i+1, N):
        if modules[i] == modules[j]:
            # Intra-module connection
            if np.random.rand() < intra_density:
                weight = np.random.uniform(0.8, 1.2)
                Cmat[i, j] = weight
                Cmat[j, i] = weight
        else:
            # Inter-module connection
            if np.random.rand() < inter_density:
                weight = np.random.uniform(0.3, 0.7)
                Cmat[i, j] = weight
                Cmat[j, i] = weight

# Count connections
intra_edges = np.sum((Cmat > 0) & (modules[:, None] == modules[None, :]))
inter_edges = np.sum((Cmat > 0) & (modules[:, None] != modules[None, :]))

print(f"\nConnectivity:")
print(f"  Intra-module edges: {intra_edges//2}")
print(f"  Inter-module edges: {inter_edges//2}")
print(f"  Total edges: {(intra_edges+inter_edges)//2}")

# Distance matrix (based on connection strength and modules)
Dmat = np.zeros((N, N))
for i in range(N):
    for j in range(i+1, N):
        if Cmat[i, j] > 0:
            # Stronger connections = shorter distances
            # Same module = shorter baseline distance
            if modules[i] == modules[j]:
                dist = 10 + (1.0 - Cmat[i, j]) * 20  # 10-30mm for intra-module
            else:
                dist = 30 + (1.0 - Cmat[i, j]) * 40  # 30-70mm for inter-module
        else:
            # No connection = longer distances
            dist = np.random.uniform(70, 100)
        Dmat[i, j] = dist
        Dmat[j, i] = dist

# Create model with optimal parameters
print(f"\nCreating model...")
model = WendlingModel(Cmat=Cmat, Dmat=Dmat, heterogeneity=0.30, seed=42)
model.params['duration'] = 10000  # 10 seconds
model.params['dt'] = 0.1
model.params['K_gl'] = 0.15
print(f"  heterogeneity = 0.30")
print(f"  K_gl = 0.15")

# Run simulation
print(f"\nRunning simulation...")
model.run()
print(f"  Done!")

# Extract signals
t = model.t
signals = np.zeros((N, len(t)))
for i in range(N):
    signals[i, :] = model.y1[i, :] - model.y2[i, :] - model.y3[i, :]

# Discard transient
discard_idx = int(2000 / 0.1)
signals_clean = signals[:, discard_idx:]

# Compute FC
print(f"\nComputing FC...")
fc = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        fc[i, j], _ = pearsonr(signals_clean[i, :], signals_clean[j, :])

# Analyze modularity
intra_fc = []
inter_fc = []

for i in range(N):
    for j in range(i+1, N):
        if modules[i] == modules[j]:
            intra_fc.append(np.abs(fc[i, j]))
        else:
            inter_fc.append(np.abs(fc[i, j]))

mean_intra_fc = np.mean(intra_fc)
mean_inter_fc = np.mean(inter_fc)
mean_fc_all = np.mean(np.abs(fc[~np.eye(N, dtype=bool)]))

print(f"\nFunctional Connectivity:")
print(f"  Intra-module FC: {mean_intra_fc:.3f}")
print(f"  Inter-module FC: {mean_inter_fc:.3f}")
print(f"  Overall FC: {mean_fc_all:.3f}")
print(f"  Ratio (intra/inter): {mean_intra_fc/mean_inter_fc:.2f}")

# Compute modularity Q
def compute_modularity(fc_matrix, module_labels):
    N = len(fc_matrix)
    m = np.sum(np.abs(fc_matrix)) / 2
    Q = 0
    for i in range(N):
        for j in range(N):
            if module_labels[i] == module_labels[j]:
                k_i = np.sum(np.abs(fc_matrix[i, :]))
                k_j = np.sum(np.abs(fc_matrix[:, j]))
                Q += np.abs(fc_matrix[i, j]) - (k_i * k_j) / (2 * m)
    Q = Q / (2 * m)
    return Q

Q = compute_modularity(fc, modules)
print(f"  Modularity Q: {Q:.3f}")

# Validation
print(f"\nValidation:")
checks = []
checks.append(("Intra-FC > Inter-FC", mean_intra_fc > mean_inter_fc))
checks.append(("Modularity Q > 0.3", Q > 0.3))
checks.append(("Overall FC in [0.3, 0.7]", 0.3 <= mean_fc_all <= 0.7))

for check_name, passed in checks:
    status = "PASS" if passed else "FAIL"
    print(f"  {status}: {check_name}")

all_pass = all(c[1] for c in checks)

# Plotting
print(f"\nGenerating plots...")
fig = plt.figure(figsize=(20, 12))

# 1. SC Matrix with module boundaries
ax1 = plt.subplot(3, 4, 1)
im1 = ax1.imshow(Cmat, cmap='hot', aspect='auto', interpolation='nearest')
ax1.set_xlabel('Node', fontsize=10)
ax1.set_ylabel('Node', fontsize=10)
ax1.set_title('Structural Connectivity (weighted)', fontsize=12, fontweight='bold')
# Draw module boundaries
for i in range(1, n_modules):
    pos = i * nodes_per_module - 0.5
    ax1.axhline(pos, color='cyan', linewidth=2, linestyle='--')
    ax1.axvline(pos, color='cyan', linewidth=2, linestyle='--')
plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)

# 2. FC Matrix with module boundaries
ax2 = plt.subplot(3, 4, 2)
im2 = ax2.imshow(fc, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto', interpolation='nearest')
ax2.set_xlabel('Node', fontsize=10)
ax2.set_ylabel('Node', fontsize=10)
ax2.set_title(f'Functional Connectivity (Q={Q:.3f})', fontsize=12, fontweight='bold')
for i in range(1, n_modules):
    pos = i * nodes_per_module - 0.5
    ax2.axhline(pos, color='yellow', linewidth=2, linestyle='--')
    ax2.axvline(pos, color='yellow', linewidth=2, linestyle='--')
plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)

# 3. FC by module
ax3 = plt.subplot(3, 4, 3)
positions = [1, 2]
bp = ax3.boxplot([intra_fc, inter_fc], positions=positions, widths=0.6,
                  patch_artist=True, labels=['Intra-module', 'Inter-module'])
bp['boxes'][0].set_facecolor('lightblue')
bp['boxes'][1].set_facecolor('lightcoral')
ax3.set_ylabel('|FC|', fontsize=10)
ax3.set_title('FC Distribution by Connection Type', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')
ax3.axhline(mean_intra_fc, color='blue', linestyle='--', linewidth=1.5, alpha=0.7)
ax3.axhline(mean_inter_fc, color='red', linestyle='--', linewidth=1.5, alpha=0.7)

# 4. Module-averaged FC matrix
ax4 = plt.subplot(3, 4, 4)
module_fc = np.zeros((n_modules, n_modules))
for m1 in range(n_modules):
    for m2 in range(n_modules):
        nodes_m1 = np.where(modules == m1)[0]
        nodes_m2 = np.where(modules == m2)[0]
        fc_block = fc[np.ix_(nodes_m1, nodes_m2)]
        module_fc[m1, m2] = np.mean(np.abs(fc_block))

im4 = ax4.imshow(module_fc, cmap='YlOrRd', aspect='auto', interpolation='nearest')
ax4.set_xlabel('Module', fontsize=10)
ax4.set_ylabel('Module', fontsize=10)
ax4.set_title('Module-Averaged FC', fontsize=12, fontweight='bold')
for i in range(n_modules):
    for j in range(n_modules):
        ax4.text(j, i, f'{module_fc[i, j]:.2f}', ha="center", va="center", 
                color="black", fontsize=10)
plt.colorbar(im4, ax=ax4, fraction=0.046, pad=0.04)

# 5-8. Time series for each module
for mod_idx in range(n_modules):
    ax = plt.subplot(3, 4, 5+mod_idx)
    mod_nodes = np.where(modules == mod_idx)[0]
    time_window = 2000
    time_idx = int(time_window / 0.1)
    
    for i, node_id in enumerate(mod_nodes):
        offset = i * 8
        ax.plot(t[:time_idx], signals[node_id, :time_idx] + offset, 
               linewidth=0.8, alpha=0.7, label=f'N{node_id}')
    
    ax.set_xlabel('Time (ms)', fontsize=9)
    ax.set_ylabel('Activity (mV)', fontsize=9)
    ax.set_title(f'Module {mod_idx+1} Activity', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)
    if mod_idx == 0:
        ax.legend(fontsize=7, loc='upper right')

# 9. Network topology
ax9 = plt.subplot(3, 4, 9)
ax9.axis('off')
ax9.set_xlim(0, 10)
ax9.set_ylim(0, 10)
ax9.set_title('Network Topology', fontsize=12, fontweight='bold')

# Draw modules as circles
module_colors = ['C0', 'C1', 'C2', 'C3']
module_positions = [(2.5, 7.5), (7.5, 7.5), (2.5, 2.5), (7.5, 2.5)]

for mod_idx, (x, y) in enumerate(module_positions):
    circle = plt.Circle((x, y), 1.2, color=module_colors[mod_idx], alpha=0.3, ec='black', linewidth=2)
    ax9.add_patch(circle)
    ax9.text(x, y, f'M{mod_idx+1}\n({nodes_per_module} nodes)', 
            ha='center', va='center', fontsize=10, fontweight='bold')

# Draw inter-module connections
for i in range(n_modules):
    for j in range(i+1, n_modules):
        x1, y1 = module_positions[i]
        x2, y2 = module_positions[j]
        ax9.plot([x1, x2], [y1, y2], 'gray', linewidth=1, alpha=0.3, linestyle='--')

# 10. Validation summary
ax10 = plt.subplot(3, 4, 10)
ax10.axis('off')
summary_text = f"""
Network Structure:
  Total nodes: {N}
  Modules: {n_modules}
  Nodes/module: {nodes_per_module}

Connectivity:
  Intra edges: {intra_edges//2}
  Inter edges: {inter_edges//2}
  
Functional Connectivity:
  Intra-module: {mean_intra_fc:.3f}
  Inter-module: {mean_inter_fc:.3f}
  Ratio: {mean_intra_fc/mean_inter_fc:.2f}x
  Modularity Q: {Q:.3f}

Overall FC: {mean_fc_all:.3f}
"""
ax10.text(0.1, 0.9, summary_text, transform=ax10.transAxes, fontsize=10,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

# 11. Validation results
ax11 = plt.subplot(3, 4, 11)
ax11.axis('off')
validation_text = f"""
Validation Results:

{"PASS" if mean_intra_fc > mean_inter_fc else "FAIL"}: Intra > Inter FC
  {mean_intra_fc:.3f} > {mean_inter_fc:.3f}

{"PASS" if Q > 0.3 else "FAIL"}: Modularity Q > 0.3
  Q = {Q:.3f}

{"PASS" if 0.3 <= mean_fc_all <= 0.7 else "WARN"}: Overall FC OK
  FC = {mean_fc_all:.3f}

Overall: {"PASS" if all_pass else "FAIL"}
"""
ax11.text(0.1, 0.9, validation_text, transform=ax11.transAxes, fontsize=10,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', 
                  facecolor='lightgreen' if all_pass else 'lightyellow', 
                  alpha=0.8))

# 12. FC histogram
ax12 = plt.subplot(3, 4, 12)
ax12.hist(intra_fc, bins=15, alpha=0.5, color='blue', label='Intra-module', edgecolor='black')
ax12.hist(inter_fc, bins=15, alpha=0.5, color='red', label='Inter-module', edgecolor='black')
ax12.axvline(mean_intra_fc, color='blue', linestyle='--', linewidth=2)
ax12.axvline(mean_inter_fc, color='red', linestyle='--', linewidth=2)
ax12.set_xlabel('|FC|', fontsize=10)
ax12.set_ylabel('Count', fontsize=10)
ax12.set_title('FC Distribution', fontsize=12, fontweight='bold')
ax12.legend(fontsize=9)
ax12.grid(True, alpha=0.3)

plt.suptitle('20-Nodes Modular Network Analysis (het=0.30, K_gl=0.15)', 
             fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout()

# Save
import os
save_path = '../../results/twenty_nodes/modular_analysis.png'
os.makedirs(os.path.dirname(save_path), exist_ok=True)
plt.savefig(save_path, dpi=150, bbox_inches='tight')
print(f"\nSaved: {save_path}")
plt.close('all')  # Close figure instead of showing

print("\n" + "="*80)
print("Analysis Complete")
print("="*80)
print(f"\nResults:")
print(f"  Modularity Q = {Q:.3f} (target: > 0.3)")
print(f"  Intra/Inter ratio = {mean_intra_fc/mean_inter_fc:.2f}x (target: > 1)")
print(f"  Overall FC = {mean_fc_all:.3f} (target: 0.3-0.7)")
print(f"\n[{'SUCCESS' if all_pass else 'WARNING'}] 20-nodes modular network validation {'complete' if all_pass else 'needs review'}!")
print("="*80)
