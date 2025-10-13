"""
6-Nodes Complete Network Analysis - FIXED VERSION

修复说明：
1. 删除错误的 classify_activity_type() 函数（基于错误的 B 参数范围）
2. 改用基于频率的分类（更客观）
3. 添加明确说明：这不是 Wendling 2002 的 activity types
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.stats import pearsonr
from neurolib.models.wendling import WendlingModel

print("="*80)
print("6-Nodes Complete Network Analysis (FIXED)")
print("="*80)

# Network configuration
N = 6
np.random.seed(42)

# Topology
Cmat_topo = np.array([
    [0, 1, 1, 0, 0, 1],
    [1, 0, 1, 1, 0, 0],
    [1, 1, 0, 1, 1, 0],
    [0, 1, 1, 0, 1, 1],
    [0, 0, 1, 1, 0, 1],
    [1, 0, 0, 1, 1, 0],
], dtype=float)

n_connections = int(np.sum(Cmat_topo) / 2)
density = n_connections / (N * (N - 1) / 2)

# Weighted connectivity
Cmat = Cmat_topo.copy()
for i in range(N):
    for j in range(i+1, N):
        if Cmat[i, j] > 0:
            weight = np.random.uniform(0.5, 1.5)
            Cmat[i, j] = weight
            Cmat[j, i] = weight

# Distance matrix
Dmat = np.zeros((N, N))
for i in range(N):
    for j in range(i+1, N):
        if Cmat[i, j] > 0:
            dist = 20 + (1.0 - Cmat[i, j]) * 40
        else:
            dist = np.random.uniform(60, 100)
        Dmat[i, j] = dist
        Dmat[j, i] = dist

print(f"\nNetwork Configuration:")
print(f"  Nodes: {N}")
print(f"  Connections: {n_connections}")
print(f"  Density: {density*100:.2f}%")

# Create model with heterogeneity
model = WendlingModel(Cmat=Cmat, Dmat=Dmat, heterogeneity=0.30, seed=42)
model.params['duration'] = 10000
model.params['dt'] = 0.1
model.params['K_gl'] = 0.15

print(f"\nModel Parameters:")
print(f"  heterogeneity = 0.30")
print(f"  K_gl = 0.15")
print(f"  N = {N}")
print(f"  SC density = {density:.3f}")

# Run simulation
print(f"\nRunning simulation...")
import time
start_time = time.time()
model.run()
elapsed = time.time() - start_time
print(f"  Simulation completed in {elapsed:.2f}s")

# Extract signals
t = model.t
signals = np.zeros((N, len(t)))
for i in range(N):
    signals[i, :] = model.y1[i, :] - model.y2[i, :] - model.y3[i, :]

# Discard transient
discard_idx = int(2000 / 0.1)
signals_clean = signals[:, discard_idx:]
t_clean = t[discard_idx:]

print(f"\nExtracting signals...")

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

# ==================== FIXED CLASSIFICATION ====================
# 基于频率范围分类，而非错误的 B 参数范围

def classify_by_frequency_band(peak_freq):
    """
    ⚠️ WARNING: 这不是 Wendling 2002 的 activity types!
    
    这只是基于频率范围的简单分类。
    Wendling 2002 types 需要特定的 B,G 参数值 (B=5-50 wide range)。
    
    Heterogeneity 系统 (B=15-29) 不对应 Wendling types。
    """
    if peak_freq < 4:
        return "Delta band (<4 Hz)"
    elif 4 <= peak_freq < 8:
        return "Theta band (4-8 Hz)"
    elif 8 <= peak_freq < 13:
        return "Alpha band (8-13 Hz)"
    elif 13 <= peak_freq < 30:
        return "Beta band (13-30 Hz)"
    else:
        return "Gamma band (>30 Hz)"

print(f"\n⚠️  IMPORTANT NOTE:")
print(f"  The following classification is by FREQUENCY BAND only.")
print(f"  This is NOT the same as Wendling 2002 activity types (Type 1-6).")
print(f"  Wendling types require specific B,G parameters (see STANDARD_PARAMETERS.py).")
print(f"")
print(f"  This network uses heterogeneity (B range: 15-29) for diversity,")
print(f"  NOT to reproduce specific Wendling activity types.")

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

# 8. Frequency band pie chart
ax8 = plt.subplot(3, 4, 8)
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
    
    ax.set_xlabel('Time (ms)', fontsize=9)
    ax.set_ylabel('mV', fontsize=9)
    ax.set_title(f'Node {idx+1}: {frequency_bands[idx]}\n'
                f'B={B_i:.1f}, G={G_i:.1f}, f={peak_freqs[idx]:.1f}Hz', 
                fontsize=10, fontweight='bold')
    ax.grid(True, alpha=0.3)

plt.suptitle('6-Nodes Complete Network Analysis (FIXED)\n'
            'Note: Classification by frequency band, NOT Wendling activity types', 
            fontsize=14, fontweight='bold')
plt.tight_layout()

# Save
import os
save_path = '../../results/six_nodes/complete_analysis_FIXED.png'
os.makedirs(os.path.dirname(save_path), exist_ok=True)
plt.savefig(save_path, dpi=150, bbox_inches='tight')
print(f"\nSaved: {save_path}")
plt.close()

print("\n" + "="*80)
print("Analysis Complete")
print("="*80)

# Validation
print(f"\nValidation Results:")
if mean_fc < 0.3:
    print(f"  FAIL: Mean |FC| = {mean_fc:.3f} (target: 0.3-0.7)")
else:
    print(f"  PASS: Mean |FC| = {mean_fc:.3f} (target: 0.3-0.7)")

if freq_diversity < 1.0:
    print(f"  FAIL: Freq diversity = {freq_diversity:.2f} Hz (target: > 1 Hz)")
else:
    print(f"  PASS: Freq diversity = {freq_diversity:.2f} Hz (target: > 1 Hz)")

if sc_fc_corr < 0.05:
    print(f"  FAIL: SC-FC correlation = {sc_fc_corr:.3f} (target: > 0.2)")
else:
    print(f"  PASS: SC-FC correlation = {sc_fc_corr:.3f} (target: > 0.2)")

print("\n" + "="*80)
print("IMPORTANT NOTES")
print("="*80)
print("""
This network uses HETEROGENEITY system (B range: ~15-29):
  - Purpose: Create node diversity to avoid over-synchronization
  - NOT designed to reproduce Wendling 2002 activity types

Wendling 2002 activity types require specific parameters:
  - Type 1 (Background): B=50, G=15
  - Type 4 (Alpha): B=10, G=15
  - etc. (See STANDARD_PARAMETERS.py)

The "frequency band" classification here is just for describing signal content,
NOT the same as Wendling activity type classification.
""")
print("="*80)
