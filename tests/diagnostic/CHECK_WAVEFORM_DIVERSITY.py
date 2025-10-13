"""
Check Waveform Diversity - Not just frequency, but pattern diversity

检查波形多样性：Type 1 背景慢波, Type 2 正常, Type 4 快速波动
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from neurolib.models.wendling import WendlingModel

print("="*80)
print("Waveform Diversity Check - Show Different Activity Types")
print("="*80)

# Create single node model to demonstrate different types
def create_activity_type(B, G, title):
    """Create specific activity type by parameter values"""
    model = WendlingModel(heterogeneity=0.0, seed=42)
    model.params['duration'] = 5000
    model.params['dt'] = 0.1
    model.params['B'] = B
    model.params['G'] = G
    model.params['A'] = 5.0
    model.params['p_mean'] = 90.0
    model.run()
    
    t = model.t
    signal = model.y1[0, :] - model.y2[0, :] - model.y3[0, :]
    
    # Discard transient
    discard_idx = int(1000 / 0.1)
    signal_clean = signal[discard_idx:]
    t_clean = t[discard_idx:]
    
    # Compute PSD
    freqs, psd = welch(signal_clean, fs=10000.0, nperseg=4096)
    freq_mask = (freqs >= 0.5) & (freqs <= 50)
    peak_freq = freqs[freq_mask][np.argmax(psd[freq_mask])]
    
    # Signal statistics
    amplitude = np.std(signal_clean)
    mean_val = np.mean(signal_clean)
    
    print(f"\n{title}")
    print(f"  B={B}, G={G}")
    print(f"  Peak freq: {peak_freq:.1f} Hz")
    print(f"  Amplitude (std): {amplitude:.2f} mV")
    print(f"  Mean: {mean_val:.2f} mV")
    
    return t_clean, signal_clean, freqs[freq_mask], psd[freq_mask], peak_freq, amplitude

# Test different parameter combinations
fig = plt.figure(figsize=(20, 14))

activity_types = [
    (12, 8, "Type 1: Background (慢波)"),
    (18, 12, "Type 1/2: Slow background"),
    (22, 18, "Type 2: Normal (alpha) - 我们现在的设置"),
    (26, 16, "Type 2/3: Borderline"),
    (30, 15, "Type 3: Epileptic SWD"),
    (40, 20, "Type 3+: Strong epileptic"),
    (60, 30, "Type 4: Low voltage fast"),
]

for idx, (B, G, title) in enumerate(activity_types):
    print(f"\n{'='*80}")
    
    t, signal, freqs, psd, peak_freq, amplitude = create_activity_type(B, G, title)
    
    # Time series
    ax1 = plt.subplot(len(activity_types), 3, idx*3 + 1)
    time_window = 2000
    time_idx = int(time_window / 0.1)
    ax1.plot(t[:time_idx], signal[:time_idx], linewidth=0.8, color='navy')
    ax1.set_ylabel('mV', fontsize=8)
    ax1.set_title(f'{title}\nB={B}, G={G}, f={peak_freq:.1f}Hz', fontsize=9, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(-30, 30)
    if idx == len(activity_types) - 1:
        ax1.set_xlabel('Time (ms)', fontsize=8)
    
    # PSD
    ax2 = plt.subplot(len(activity_types), 3, idx*3 + 2)
    psd_db = 10*np.log10(psd + 1e-12)
    ax2.plot(freqs, psd_db, linewidth=1.5, color='darkred')
    ax2.set_ylabel('Power (dB)', fontsize=8)
    ax2.set_title(f'PSD (peak={peak_freq:.1f}Hz)', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 40)
    if idx == len(activity_types) - 1:
        ax2.set_xlabel('Frequency (Hz)', fontsize=8)
    
    # Waveform characteristics
    ax3 = plt.subplot(len(activity_types), 3, idx*3 + 3)
    ax3.axis('off')
    
    # Calculate characteristics
    energy = np.mean(signal**2)
    low_freq_power = np.sum(psd[freqs < 5])
    high_freq_power = np.sum(psd[freqs > 15])
    
    # Detect spikes
    spike_threshold = np.mean(signal) + 3 * np.std(signal)
    n_spikes = np.sum(signal > spike_threshold)
    spike_rate = n_spikes / (len(signal) * 0.0001)
    
    char_text = f"""
Characteristics:

Amplitude: {amplitude:.2f} mV
Energy: {energy:.2f}
Peak freq: {peak_freq:.1f} Hz

Low freq (<5Hz): {low_freq_power:.1e}
High freq (>15Hz): {high_freq_power:.1e}

Spikes/sec: {spike_rate:.1f}

Pattern:
"""
    
    if B < 18:
        pattern = "Slow waves\nLow amplitude\nBackground"
    elif 18 <= B < 25:
        pattern = "Alpha rhythm\nModerate amp\nNormal"
    elif 25 <= B < 35:
        pattern = "Spike-wave\nHigh amplitude\nEpileptic"
    else:
        pattern = "Fast activity\nLow amplitude\nHigh freq"
    
    char_text += pattern
    
    ax3.text(0.1, 0.9, char_text, transform=ax3.transAxes,
            fontsize=8, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.suptitle('Wendling Model: Activity Type Diversity (Waveform Comparison)', 
             fontsize=14, fontweight='bold')
plt.tight_layout()

# Save
import os
save_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'waveform_diversity.png')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
plt.savefig(save_path, dpi=150, bbox_inches='tight')
print(f"\n\nSaved: {save_path}")
plt.close()

# ==================== Now check our 6-node network ====================
print("\n" + "="*80)
print("Checking OUR 6-node network diversity")
print("="*80)

N = 6
np.random.seed(42)

Cmat = np.array([
    [0, 1, 1, 0, 0, 1],
    [1, 0, 1, 1, 0, 0],
    [1, 1, 0, 1, 1, 0],
    [0, 1, 1, 0, 1, 1],
    [0, 0, 1, 1, 0, 1],
    [1, 0, 0, 1, 1, 0],
], dtype=float)

for i in range(N):
    for j in range(i+1, N):
        if Cmat[i, j] > 0:
            weight = np.random.uniform(0.5, 1.5)
            Cmat[i, j] = weight
            Cmat[j, i] = weight

Dmat = np.zeros((N, N))
for i in range(N):
    for j in range(i+1, N):
        if Cmat[i, j] > 0:
            dist = 10 + (1.0 - Cmat[i, j]) * 30
        else:
            dist = np.random.uniform(50, 80)
        Dmat[i, j] = dist
        Dmat[j, i] = dist

# Test with wider parameter range
print("\nTesting with WIDER parameter range for diversity:")
model = WendlingModel(Cmat=Cmat, Dmat=Dmat, heterogeneity=0.40, seed=42)
model.params['duration'] = 5000
model.params['dt'] = 0.1
model.params['K_gl'] = 0.10  # Lower coupling for independence
model.run()

t = model.t
signals = np.zeros((N, len(t)))
for i in range(N):
    signals[i, :] = model.y1[i, :] - model.y2[i, :] - model.y3[i, :]

discard_idx = int(1000 / 0.1)
signals_clean = signals[:, discard_idx:]
t_clean = t[discard_idx:]

print(f"\nParameter values:")
print(f"  B: {model.params['B']}")
print(f"  G: {model.params['G']}")
print(f"  B range: [{np.min(model.params['B']):.1f}, {np.max(model.params['B']):.1f}]")
print(f"  G range: [{np.min(model.params['G']):.1f}, {np.max(model.params['G']):.1f}]")

# Analyze each node
print(f"\nNode Analysis:")
print(f"{'Node':<6} {'B':<8} {'G':<8} {'Amplitude':<12} {'Peak Freq':<12} {'Activity Type'}")
print("-"*80)

for i in range(N):
    B_i = model.params['B'][i]
    G_i = model.params['G'][i]
    
    amplitude = np.std(signals_clean[i, :])
    
    freqs, psd = welch(signals_clean[i, :], fs=10000.0, nperseg=4096)
    freq_mask = (freqs >= 0.5) & (freqs <= 50)
    peak_freq = freqs[freq_mask][np.argmax(psd[freq_mask])]
    
    # Classify
    if B_i < 18:
        act_type = "Type 1 (Background)"
    elif B_i < 25:
        act_type = "Type 2 (Normal)"
    elif B_i < 35:
        act_type = "Type 2/3 (Borderline)"
    else:
        act_type = "Type 3+ (Epileptic)"
    
    print(f"{i:<6} {B_i:<8.2f} {G_i:<8.2f} {amplitude:<12.2f} {peak_freq:<12.1f} {act_type}")

# Waveform diversity metrics
amplitudes = [np.std(signals_clean[i, :]) for i in range(N)]
print(f"\nWaveform Diversity Metrics:")
print(f"  Amplitude range: [{np.min(amplitudes):.2f}, {np.max(amplitudes):.2f}] mV")
print(f"  Amplitude diversity (CV): {np.std(amplitudes)/np.mean(amplitudes):.2f}")

# Frequency diversity
peak_freqs = []
for i in range(N):
    freqs, psd = welch(signals_clean[i, :], fs=10000.0, nperseg=4096)
    freq_mask = (freqs >= 0.5) & (freqs <= 50)
    peak_freq = freqs[freq_mask][np.argmax(psd[freq_mask])]
    peak_freqs.append(peak_freq)

print(f"  Frequency range: [{np.min(peak_freqs):.1f}, {np.max(peak_freqs):.1f}] Hz")
print(f"  Frequency diversity (std): {np.std(peak_freqs):.2f} Hz")

# Energy distribution
energies = [np.mean(signals_clean[i, :]**2) for i in range(N)]
print(f"  Energy range: [{np.min(energies):.2f}, {np.max(energies):.2f}]")
print(f"  Energy diversity (CV): {np.std(energies)/np.mean(energies):.2f}")

print("\n" + "="*80)
print("RECOMMENDATION")
print("="*80)
print("""
问题诊断：你观察到的"太干净、缺乏 background/fluctuation"

原因：
1. 当前参数范围集中在 Type 2 (B=15-28)
2. 缺乏 Type 1 (B<18) 的低频背景活动
3. 缺乏 Type 4 (B>50) 的快速波动
4. 所有节点"能量"相似

解决方案：
1. **增加参数范围多样性**：
   - 允许一些节点 B<15 (Type 1 背景)
   - 允许一些节点 B>30 (少量 Type 3/4)
   
2. **降低耦合** (K_gl = 0.05-0.10)
   - 让节点更独立
   - 保留各自的 activity pattern
   
3. **更大异质性** (heterogeneity = 0.5-0.7)
   - 创建更广的参数分布
   - 自然产生多种 activity types

示例配置（获得最大多样性）：
  B_base = 25.0, heterogeneity = 0.6 → B range: 10-40
  K_gl = 0.05
  → 会产生 Type 1, 2, 3 的混合
""")
print("="*80)
