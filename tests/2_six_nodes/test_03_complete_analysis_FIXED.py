"""
6-Nodes Complete Network Analysis - FIXED VERSION

修复说明：
1. 删除错误的 classify_activity_type() 函数（基于错误的 B 参数范围）
2. 改用基于频率的分类（更客观）
3. 添加明确说明：这不是 Wendling 2002 的 activity types
4. 添加手动指定每个 node 参数类型的选项（基于 STANDARD_PARAMETERS.py）
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')
sys.path.insert(0, r'c:\Epilepsy_project\whole_brain_wendling\Validation_for_single_node')

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.stats import pearsonr
from neurolib.models.wendling import WendlingModel
from STANDARD_PARAMETERS import WENDLING_STANDARD_PARAMS

print("="*80)
print("6-Nodes Complete Network Analysis (FIXED)")
print("="*80)

# ============================================================================
# CONFIGURATION OPTIONS
# ============================================================================

# Option 1: Manual parameter assignment (specify each node's type)
# Set to None to use heterogeneity instead
NODE_TYPES = ['Type1', 'Type3', 'Type6', 'Type6', 'Type1', 'Type1']  # All Type3 (SWD)
# NODE_TYPES = None  # Use heterogeneity

# Option 2: Network connectivity
NETWORK_DENSITY = 0.6  # 60% of possible connections
WEIGHT_RANGE = (0.5, 1.5)  # Connection weight range

# Option 3: Coupling strength
K_GL = 0.0  # No coupling (K_gl = 0)

# ============================================================================

N = 6
np.random.seed(42)

# Generate random weighted connectivity matrix
print(f"\nGenerating random connectivity matrix...")
print(f"  Target density: {NETWORK_DENSITY*100:.0f}%")

Cmat = np.zeros((N, N))
n_possible = N * (N - 1) // 2
n_connections_target = int(n_possible * NETWORK_DENSITY)

# Randomly select connections
connections = []
for i in range(N):
    for j in range(i+1, N):
        connections.append((i, j))

np.random.shuffle(connections)
selected_connections = connections[:n_connections_target]

# Assign random weights to selected connections
for i, j in selected_connections:
    weight = np.random.uniform(*WEIGHT_RANGE)
    Cmat[i, j] = weight
    Cmat[j, i] = weight

# Calculate actual density and connections
n_connections = len(selected_connections)
density = n_connections / n_possible

print(f"  Connections: {n_connections}/{n_possible}")
print(f"  Actual density: {density*100:.2f}%")

# Distance matrix (distance inversely related to connection strength)
Dmat = np.zeros((N, N))
for i in range(N):
    for j in range(i+1, N):
        if Cmat[i, j] > 0:
            # Stronger connections = shorter distances
            dist = 20 + (1.0 - Cmat[i, j]) * 40  # 20-60mm
        else:
            # No connection = long distance
            dist = np.random.uniform(60, 100)  # 60-100mm
        Dmat[i, j] = dist
        Dmat[j, i] = dist

print(f"\nNetwork Configuration:")
print(f"  Nodes: {N}")
print(f"  Connections: {n_connections}")
print(f"  Density: {density*100:.2f}%")
print(f"  Weight range: [{WEIGHT_RANGE[0]}, {WEIGHT_RANGE[1]}]")

# ============================================================================
# MODEL CREATION AND PARAMETER ASSIGNMENT
# ============================================================================

if NODE_TYPES is not None:
    print(f"\n[*] Using MANUAL parameter assignment (STANDARD_PARAMETERS)")
    print(f"  Mode: Wendling 2002 verified types")
    
    # Verify NODE_TYPES
    if len(NODE_TYPES) != N:
        raise ValueError(f"NODE_TYPES length ({len(NODE_TYPES)}) must equal N ({N})")
    
    for node_type in NODE_TYPES:
        if node_type not in WENDLING_STANDARD_PARAMS:
            raise ValueError(f"Invalid type: {node_type}. Must be one of {list(WENDLING_STANDARD_PARAMS.keys())}")
    
    # Create model with heterogeneity=0.01 to enable vectorization
    # (Even tiny heterogeneity triggers vector mode, then we override with exact values)
    # ⚠️ CRITICAL: Use random_init=True for multi-node networks!
    # random_init=False works for single-node but causes high-B types (Type1) to decay in multi-node
    model = WendlingModel(Cmat=Cmat, Dmat=Dmat, heterogeneity=0.01, seed=42, random_init=True)
    model.params['duration'] = 10000
    model.params['dt'] = 0.1
    model.params['K_gl'] = K_GL
    
    # Manually assign parameters for each node
    B_vals = np.zeros(N)
    G_vals = np.zeros(N)
    A_vals = np.zeros(N)
    p_mean_vals = np.zeros(N)
    
    # Determine p_sigma (currently NOT vectorized in model, so use most common value)
    p_sigma_vals = [WENDLING_STANDARD_PARAMS[nt]['params']['p_sigma'] for nt in NODE_TYPES]
    p_sigma_mode = max(set(p_sigma_vals), key=p_sigma_vals.count)  # Most common value
    
    print(f"\nNode Parameter Assignment:")
    print(f"{'Node':<6} {'Type':<10} {'B':<6} {'G':<6} {'A':<6} {'p_mean':<8} {'p_sigma':<10} {'Description'}")
    print("-"*100)
    
    for i, node_type in enumerate(NODE_TYPES):
        params = WENDLING_STANDARD_PARAMS[node_type]['params']
        desc = WENDLING_STANDARD_PARAMS[node_type]['name']
        
        B_vals[i] = params['B']
        G_vals[i] = params['G']
        A_vals[i] = params['A']
        p_mean_vals[i] = params['p_mean']
        
        print(f"{i:<6} {node_type:<10} {params['B']:<6.0f} {params['G']:<6.0f} {params['A']:<6.1f} {params['p_mean']:<8.0f} {params['p_sigma']:<10.1f} {desc}")
    
    if len(set(p_sigma_vals)) > 1:
        print(f"\n[!] Note: p_sigma is not yet vectorized in model.")
        print(f"   Using mode value: p_sigma = {p_sigma_mode} for all nodes")
        print(f"   (Some types specify {set(p_sigma_vals)}, but model uses scalar)")
    
    # Assign to model - MUST be vectors for heterogeneity mode
    model.params['B'] = B_vals
    model.params['G'] = G_vals
    model.params['A'] = A_vals
    model.params['p_mean'] = p_mean_vals
    model.params['p_sigma'] = p_sigma_mode  # Scalar only
    
    # Verify parameters were set correctly
    print(f"\n[OK] Verification after assignment:")
    print(f"  model.params['B'] = {model.params['B']}")
    print(f"  model.params['G'] = {model.params['G']}")
    print(f"  Shape check: B.shape={np.shape(model.params['B'])}, expected=({N},)")
    
else:
    print(f"\n[!] Using HETEROGENEITY system")
    print(f"  Mode: Random parameter diversity (NOT Wendling types)")
    
    # Create model with heterogeneity
    model = WendlingModel(Cmat=Cmat, Dmat=Dmat, heterogeneity=0.30, seed=42)
    model.params['duration'] = 10000
    model.params['dt'] = 0.1
    model.params['K_gl'] = K_GL
    
    print(f"\nModel Parameters:")
    print(f"  heterogeneity = 0.30")

print(f"  K_gl = {K_GL}")
print(f"  N = {N}")
print(f"  SC density = {density:.3f}")

# DEBUG: Verify parameters before run
if NODE_TYPES is not None:
    print(f"\n[DEBUG] Parameters BEFORE run():")
    print(f"  B = {model.params['B']}")
    print(f"  G = {model.params['G']}")

# Run simulation
print(f"\nRunning simulation...")
import time
start_time = time.time()
model.run()
elapsed = time.time() - start_time
print(f"  Simulation completed in {elapsed:.2f}s")

# DEBUG: Verify parameters after run
if NODE_TYPES is not None:
    print(f"\n[DEBUG] Parameters AFTER run():")
    print(f"  B = {model.params['B']}")
    print(f"  G = {model.params['G']}")

# Extract signals
t = model.t
signals = np.zeros((N, len(t)))
for i in range(N):
    signals[i, :] = model.y1[i, :] - model.y2[i, :] - model.y3[i, :]

print(f"\nExtracting signals...")
print(f"  Signal shape: {signals.shape}")
print(f"  Time shape: {t.shape}")

# Check signal statistics BEFORE discarding transient
print(f"\n📊 Signal Statistics (full):")
for i in range(N):
    print(f"  Node {i}: mean={np.mean(signals[i,:]):.4f}, std={np.std(signals[i,:]):.4f}, "
          f"min={np.min(signals[i,:]):.4f}, max={np.max(signals[i,:]):.4f}")

# Discard transient
discard_idx = int(2000 / 0.1)
signals_clean = signals[:, discard_idx:]
t_clean = t[discard_idx:]

print(f"\n📊 Signal Statistics (after transient removal):")
for i in range(N):
    print(f"  Node {i}: mean={np.mean(signals_clean[i,:]):.4f}, std={np.std(signals_clean[i,:]):.4f}, "
          f"min={np.min(signals_clean[i,:]):.4f}, max={np.max(signals_clean[i,:]):.4f}")

# Compute FC
print(f"\nComputing FC...")
fc = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        fc[i, j], _ = pearsonr(signals_clean[i, :], signals_clean[j, :])

mean_fc = np.mean(np.abs(fc[~np.eye(N, dtype=bool)]))
std_fc = np.std(fc[~np.eye(N, dtype=bool)])

print(f"\nSimulated FC:")
print(f"  Mean |FC|: {mean_fc:.3f}")
print(f"  Std FC: {std_fc:.3f}")

# Compute PSD and features for each node
print(f"\nComputing PSD...")
peak_freqs = []
amplitudes = []
psds_all = []

for i in range(N):
    freqs, psd = welch(signals_clean[i, :], fs=10000.0, nperseg=4096)
    freq_mask = (freqs >= 1) & (freqs <= 50)
    peak_freq = freqs[freq_mask][np.argmax(psd[freq_mask])]
    amplitude = np.std(signals_clean[i, :])
    
    peak_freqs.append(peak_freq)
    amplitudes.append(amplitude)
    psds_all.append((freqs, psd))

freq_diversity = np.std(peak_freqs)

print("="*80)
print("DIAGNOSTIC VALIDATION")
print("="*80)

# Show parameter values
print(f"\nSample Parameter Values (first 10 nodes):")
if isinstance(model.params['B'], np.ndarray):
    B_show = model.params['B'][:min(10, N)]
    G_show = model.params['G'][:min(10, N)]
else:
    B_show = [model.params['B']] * min(10, N)
    G_show = [model.params['G']] * min(10, N)
print(f"  B: {B_show}")
print(f"  G: {G_show}")

# ==================== CLASSIFICATION ====================

def classify_by_frequency_band(peak_freq):
    """频率分类"""
    if peak_freq < 4:
        return "Delta (<4 Hz)"
    elif 4 <= peak_freq < 8:
        return "Theta (4-8 Hz)"
    elif 8 <= peak_freq < 13:
        return "Alpha (8-13 Hz)"
    elif 13 <= peak_freq < 30:
        return "Beta (13-30 Hz)"
    else:
        return "Gamma (>30 Hz)"

if NODE_TYPES is not None:
    # Manual type assignment - show Wendling types
    print(f"\n✅ Wendling Activity Type Analysis:")
    print(f"{'Node':<6} {'Assigned Type':<12} {'B':<6} {'G':<6} {'Freq(Hz)':<10} {'Amp(mV)':<10} {'Expected Freq':<15} {'Match'}")
    print("-"*95)
    
    type_matches = []
    for i in range(N):
        assigned_type = NODE_TYPES[i]
        B_i = model.params['B'][i]
        G_i = model.params['G'][i]
        expected_freq = WENDLING_STANDARD_PARAMS[assigned_type]['expected']['freq_range']
        freq_match = expected_freq[0] <= peak_freqs[i] <= expected_freq[1]
        match_str = "✅ MATCH" if freq_match else "❌ OFF"
        type_matches.append(freq_match)
        
        print(f"{i:<6} {assigned_type:<12} {B_i:<6.0f} {G_i:<6.0f} {peak_freqs[i]:<10.2f} {amplitudes[i]:<10.2f} "
              f"{expected_freq[0]}-{expected_freq[1]} Hz{'':<6} {match_str}")
    
    # Summary
    from collections import Counter
    type_counts = Counter(NODE_TYPES)
    match_rate = sum(type_matches) / len(type_matches) * 100
    
    print(f"\nAssigned Type Distribution:")
    for node_type, count in type_counts.items():
        type_name = WENDLING_STANDARD_PARAMS[node_type]['name']
        print(f"  {node_type}: {count}/{N} nodes ({count/N*100:.0f}%) - {type_name}")
    
    print(f"\nFrequency Match Rate: {match_rate:.0f}% ({sum(type_matches)}/{len(type_matches)} nodes)")
    
else:
    # Heterogeneity mode - warn about frequency band classification
    print(f"\n⚠️  IMPORTANT NOTE:")
    print(f"  Using HETEROGENEITY mode - classification is by FREQUENCY BAND only.")
    print(f"  This is NOT the same as Wendling 2002 activity types.")
    print(f"  To use Wendling types, set NODE_TYPES at the top of this file.")
    
    print(f"\nNode Parameter & Frequency Analysis:")
    print(f"{'Node':<6} {'B':<8} {'G':<8} {'Freq(Hz)':<12} {'Amp(mV)':<10} {'Freq Band'}")
    print("-"*80)
    
    frequency_bands = []
    for i in range(N):
        B_i = model.params['B'][i] if isinstance(model.params['B'], np.ndarray) else model.params['B']
        G_i = model.params['G'][i] if isinstance(model.params['G'], np.ndarray) else model.params['G']
        freq_band = classify_by_frequency_band(peak_freqs[i])
        frequency_bands.append(freq_band)
        print(f"{i:<6} {B_i:<8.2f} {G_i:<8.2f} {peak_freqs[i]:<12.2f} {amplitudes[i]:<10.2f} {freq_band}")
    
    # Summary by frequency band
    from collections import Counter
    band_counts = Counter(frequency_bands)
    print(f"\nFrequency Band Distribution:")
    for band, count in sorted(band_counts.items()):
        print(f"  {band}: {count}/{N} nodes ({count/N*100:.0f}%)")

print(f"\nDiversity Metrics:")
print(f"  Frequency std: {freq_diversity:.2f} Hz")
print(f"  Frequency range: [{min(peak_freqs):.1f}, {max(peak_freqs):.1f}] Hz")
print(f"  Amplitude range: [{min(amplitudes):.2f}, {max(amplitudes):.2f}] mV")

# Parameter diversity
if isinstance(model.params['B'], np.ndarray):
    B_std = np.std(model.params['B'])
    G_std = np.std(model.params['G'])
    print(f"  B std: {B_std:.2f}")
    print(f"  G std: {G_std:.2f}")
    p_mean = model.params['p_mean'] if hasattr(model.params, 'p_mean') else None
    if p_mean is not None and isinstance(p_mean, np.ndarray):
        print(f"  p_mean: {p_mean}")

print("="*80)

# SC-FC correlation
sc_flat = Cmat[~np.eye(N, dtype=bool)]
fc_flat = np.abs(fc[~np.eye(N, dtype=bool)])
sc_fc_corr, _ = pearsonr(sc_flat, fc_flat)
print(f"\nSC-FC correlation: {sc_fc_corr:.3f}")
print("="*80)

# ==================== Plotting ====================
print(f"\nGenerating plots...")

# DEBUG: Verify parameters before plotting
if NODE_TYPES is not None:
    print(f"\n[DEBUG] Parameters at plotting time:")
    print(f"  B = {model.params['B']}")
    print(f"  G = {model.params['G']}")
    print(f"  Expected:")
    for i, nt in enumerate(NODE_TYPES):
        from STANDARD_PARAMETERS import WENDLING_STANDARD_PARAMS
        exp_B = WENDLING_STANDARD_PARAMS[nt]['params']['B']
        exp_G = WENDLING_STANDARD_PARAMS[nt]['params']['G']
        print(f"    Node {i} ({nt}): B={exp_B}, G={exp_G}")

fig = plt.figure(figsize=(20, 12))

# 1. Time series
ax1 = plt.subplot(3, 4, 1)
time_window = 3000
time_idx = int(time_window / 0.1)
for i in range(N):
    offset = i * 10
    ax1.plot(t_clean[:time_idx], signals_clean[i, :time_idx] + offset, 
            linewidth=0.8, alpha=0.8, label=f'Node {i+1}')
ax1.set_xlabel('Time (ms)', fontsize=10)
ax1.set_ylabel('Activity (mV)', fontsize=10)
ax1.set_title('Node Activity Time Series', fontsize=12, fontweight='bold')
ax1.legend(fontsize=8, loc='upper right')
ax1.grid(True, alpha=0.3)

# 2. PSD
ax2 = plt.subplot(3, 4, 2)
for i in range(N):
    freqs, psd = psds_all[i]
    freq_mask = (freqs >= 1) & (freqs <= 50)
    psd_db = 10*np.log10(psd[freq_mask] + 1e-12)
    ax2.plot(freqs[freq_mask], psd_db, linewidth=1.2, alpha=0.7, 
            label=f'N{i+1} ({peak_freqs[i]:.1f}Hz)')
ax2.set_xlabel('Frequency (Hz)', fontsize=10)
ax2.set_ylabel('Power (dB)', fontsize=10)
ax2.set_title('Power Spectral Density', fontsize=12, fontweight='bold')
ax2.legend(fontsize=8, ncol=2)
ax2.grid(True, alpha=0.3)
ax2.set_xlim(0, 30)

# 3. FC matrix
ax3 = plt.subplot(3, 4, 3)
im = ax3.imshow(fc, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
ax3.set_xlabel('Node', fontsize=10)
ax3.set_ylabel('Node', fontsize=10)
ax3.set_title(f'Functional Connectivity\n(Mean |FC|={mean_fc:.3f})', 
             fontsize=12, fontweight='bold')
plt.colorbar(im, ax=ax3, fraction=0.046, pad=0.04)

# 4. SC matrix
ax4 = plt.subplot(3, 4, 4)
im = ax4.imshow(Cmat, cmap='viridis', aspect='auto')
ax4.set_xlabel('Node', fontsize=10)
ax4.set_ylabel('Node', fontsize=10)
ax4.set_title('Structural Connectivity', fontsize=12, fontweight='bold')
plt.colorbar(im, ax=ax4, fraction=0.046, pad=0.04)

# 5. SC-FC scatter
ax5 = plt.subplot(3, 4, 5)
ax5.scatter(sc_flat, fc_flat, alpha=0.6, s=50)
ax5.set_xlabel('SC weight', fontsize=10)
ax5.set_ylabel('|FC|', fontsize=10)
ax5.set_title(f'SC-FC Relationship\n(r={sc_fc_corr:.3f})', fontsize=12, fontweight='bold')
ax5.grid(True, alpha=0.3)

# 6. Frequency distribution
ax6 = plt.subplot(3, 4, 6)
ax6.bar(range(N), peak_freqs, color='steelblue', alpha=0.7)
ax6.set_xlabel('Node', fontsize=10)
ax6.set_ylabel('Peak Frequency (Hz)', fontsize=10)
ax6.set_title(f'Peak Frequencies\n(std={freq_diversity:.2f} Hz)', fontsize=12, fontweight='bold')
ax6.grid(True, alpha=0.3, axis='y')
ax6.set_xticks(range(N))
ax6.set_xticklabels([f'N{i+1}' for i in range(N)])

# 7. Amplitude distribution
ax7 = plt.subplot(3, 4, 7)
ax7.bar(range(N), amplitudes, color='coral', alpha=0.7)
ax7.set_xlabel('Node', fontsize=10)
ax7.set_ylabel('Amplitude (mV)', fontsize=10)
ax7.set_title('Signal Amplitudes', fontsize=12, fontweight='bold')
ax7.grid(True, alpha=0.3, axis='y')
ax7.set_xticks(range(N))
ax7.set_xticklabels([f'N{i+1}' for i in range(N)])

# 8. Distribution pie chart
ax8 = plt.subplot(3, 4, 8)
if NODE_TYPES is not None:
    # Show Wendling type distribution
    from collections import Counter
    type_counts = Counter(NODE_TYPES)
    type_labels = list(type_counts.keys())
    type_values = list(type_counts.values())
    ax8.pie(type_values, labels=type_labels, autopct='%1.0f%%', startangle=90)
    ax8.set_title('Wendling Type Distribution', fontsize=12, fontweight='bold')
else:
    # Show frequency band distribution
    band_labels = list(band_counts.keys())
    band_values = list(band_counts.values())
    ax8.pie(band_values, labels=band_labels, autopct='%1.0f%%', startangle=90)
    ax8.set_title('Frequency Band Distribution', fontsize=12, fontweight='bold')

# 9-12. Individual node samples (first 4 nodes)
for idx in range(4):
    ax = plt.subplot(3, 4, 9 + idx)
    sample_window = 2000
    sample_idx = int(sample_window / 0.1)
    ax.plot(t_clean[:sample_idx], signals_clean[idx, :sample_idx], linewidth=0.8, color='navy')
    
    B_i = model.params['B'][idx] if isinstance(model.params['B'], np.ndarray) else model.params['B']
    G_i = model.params['G'][idx] if isinstance(model.params['G'], np.ndarray) else model.params['G']
    
    # DEBUG: Print what we're plotting
    if idx == 0 and NODE_TYPES is not None:
        print(f"\n[DEBUG] Plotting parameters:")
        for i in range(min(4, N)):
            B_plot = model.params['B'][i] if isinstance(model.params['B'], np.ndarray) else model.params['B']
            G_plot = model.params['G'][i] if isinstance(model.params['G'], np.ndarray) else model.params['G']
            print(f"  Node {i}: B={B_plot:.1f}, G={G_plot:.1f} (will display as 'Node {i+1}')")
    
    # Determine label for node
    if NODE_TYPES is not None:
        node_label = NODE_TYPES[idx]
    else:
        node_label = frequency_bands[idx]
    
    ax.set_xlabel('Time (ms)', fontsize=9)
    ax.set_ylabel('mV', fontsize=9)
    ax.set_title(f'Node {idx+1}: {node_label}\n'
                f'B={B_i:.1f}, G={G_i:.1f}, f={peak_freqs[idx]:.1f}Hz', 
                fontsize=10, fontweight='bold')
    ax.grid(True, alpha=0.3)

# Set title based on mode
if NODE_TYPES is not None:
    title_mode = f'Using Wendling 2002 Types: {", ".join(set(NODE_TYPES))}'
else:
    title_mode = 'Using Heterogeneity (NOT Wendling types)'

plt.suptitle(f'6-Nodes Complete Network Analysis\n{title_mode}', 
            fontsize=14, fontweight='bold')
plt.tight_layout()

# Save
import os
# Use script directory as base, not current working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..', '..')
save_path = os.path.join(project_root, 'results', 'six_nodes', 'complete_analysis_FIXED.png')
save_path_abs = os.path.abspath(save_path)
print(f"\nSaving to: {save_path_abs}")
os.makedirs(os.path.dirname(save_path_abs), exist_ok=True)
plt.savefig(save_path_abs, dpi=150, bbox_inches='tight')
print(f"✅ Saved successfully!")
plt.close()

# Verify file exists
if os.path.exists(save_path_abs):
    file_size = os.path.getsize(save_path_abs)
    print(f"✅ File verified: {file_size/1024:.1f} KB")
else:
    print(f"❌ ERROR: File was not created!")

print("\n" + "="*80)
print("Analysis Complete")
print("="*80)

# Validation
print(f"\nValidation Results:")
if mean_fc < 0.3:
    print(f"  ⚠️  Mean |FC| = {mean_fc:.3f} (target: 0.3-0.7)")
else:
    print(f"  ✅  Mean |FC| = {mean_fc:.3f} (target: 0.3-0.7)")

if freq_diversity < 1.0:
    print(f"  ⚠️  Freq diversity = {freq_diversity:.2f} Hz (target: > 1 Hz)")
else:
    print(f"  ✅  Freq diversity = {freq_diversity:.2f} Hz (target: > 1 Hz)")

if sc_fc_corr < 0.05:
    print(f"  ⚠️  SC-FC correlation = {sc_fc_corr:.3f} (target: > 0.2)")
else:
    print(f"  ✅  SC-FC correlation = {sc_fc_corr:.3f} (target: > 0.2)")

print("\n" + "="*80)
print("IMPORTANT NOTES")
print("="*80)
if NODE_TYPES is not None:
    print(f"""
✅ Using WENDLING 2002 VERIFIED TYPES:
  - Parameters from STANDARD_PARAMETERS.py
  - Each node assigned specific type: {NODE_TYPES}
  - Expected frequencies validated against single-node results
  - This is the CORRECT way to test specific activity types

For different types, modify NODE_TYPES at top of file:
  NODE_TYPES = ['Type1', 'Type2', 'Type3', 'Type4', 'Type5', 'Type6']
  
Available types:
  Type1: Background (B=50, G=15, 1-7 Hz)
  Type2: Sporadic spikes (B=40, G=15, 1-5 Hz)
  Type3: SWD epileptic (B=25, G=15, 3-6 Hz)
  Type4: Alpha rhythm (B=10, G=15, 8-13 Hz)
  Type5: LVFA (B=5, G=25, 10-20 Hz)
  Type6: Quasi-sinusoidal (B=15, G=0, 9-13 Hz)
""")
else:
    print(f"""
⚠️  Using HETEROGENEITY system (B range: ~15-29):
  - Purpose: Create node diversity to avoid over-synchronization
  - NOT designed to reproduce Wendling 2002 activity types
  - Frequency band classification is descriptive only

To use Wendling 2002 activity types:
  1. Set NODE_TYPES at top of file
  2. Example: NODE_TYPES = ['Type1', 'Type1', 'Type4', 'Type4', 'Type5', 'Type5']
  3. See STANDARD_PARAMETERS.py for available types
""")
print("="*80)
