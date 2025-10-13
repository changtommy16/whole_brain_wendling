"""
CRITICAL VALIDATION: Verify Multi-Node Implementation is Correct

Compare single-node vs multi-node with SAME parameters
使用正确的 Wendling 2002 参数
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from neurolib.models.wendling import WendlingModel

print("="*80)
print("CRITICAL VALIDATION: Single-Node vs Multi-Node")
print("="*80)

# Use CORRECT Wendling 2002 parameters
CORRECT_PARAMS = {
    'Type1': {'B': 50, 'G': 15, 'name': 'Background'},
    'Type2': {'B': 40, 'G': 15, 'name': 'Sporadic spikes'},
    'Type3': {'B': 25, 'G': 15, 'name': 'SWD'},
    'Type4': {'B': 10, 'G': 15, 'name': 'Alpha-like'},
    'Type5': {'B': 5,  'G': 25, 'name': 'LVFA'},
    'Type6': {'B': 15, 'G': 0,  'name': 'Quasi-sinusoidal'},
}

fig, axes = plt.subplots(len(CORRECT_PARAMS), 4, figsize=(20, len(CORRECT_PARAMS)*2.5))

for idx, (type_name, params) in enumerate(CORRECT_PARAMS.items()):
    B = params['B']
    G = params['G']
    name = params['name']
    
    print(f"\n{'='*80}")
    print(f"Testing {type_name}: {name} (B={B}, G={G})")
    print(f"{'='*80}")
    
    # ========== TEST 1: Single Node (Ground Truth) ==========
    print("\n  [1/2] Single-node test...")
    model_single = WendlingModel(heterogeneity=0.0, seed=42)
    model_single.params['duration'] = 5000
    model_single.params['dt'] = 0.1
    model_single.params['B'] = B
    model_single.params['G'] = G
    model_single.params['A'] = 5.0
    model_single.params['p_mean'] = 90.0
    model_single.run()
    
    t = model_single.t
    signal_single = model_single.y1[0, :] - model_single.y2[0, :] - model_single.y3[0, :]
    
    # Discard transient
    discard_idx = int(1000 / 0.1)
    signal_single_clean = signal_single[discard_idx:]
    t_clean = t[discard_idx:]
    
    # PSD
    freqs, psd_single = welch(signal_single_clean, fs=10000.0, nperseg=4096)
    freq_mask = (freqs >= 0.5) & (freqs <= 50)
    peak_freq_single = freqs[freq_mask][np.argmax(psd_single[freq_mask])]
    amp_single = np.std(signal_single_clean)
    
    print(f"    Single-node: Peak freq = {peak_freq_single:.2f} Hz, Amp = {amp_single:.2f} mV")
    
    # ========== TEST 2: Multi-Node with NO heterogeneity (should be identical) ==========
    print("  [2/2] Multi-node test (NO heterogeneity)...")
    
    # Create 3-node network with NO heterogeneity
    N = 3
    Cmat = np.zeros((N, N))  # No coupling
    Dmat = np.zeros((N, N))
    
    model_multi = WendlingModel(Cmat=Cmat, Dmat=Dmat, heterogeneity=0.0, seed=42)
    model_multi.params['duration'] = 5000
    model_multi.params['dt'] = 0.1
    model_multi.params['B'] = B  # Should broadcast to all nodes
    model_multi.params['G'] = G
    model_multi.params['A'] = 5.0
    model_multi.params['p_mean'] = 90.0
    model_multi.params['K_gl'] = 0.0  # No coupling
    model_multi.run()
    
    # Extract node 0 signal
    signal_multi = model_multi.y1[0, :] - model_multi.y2[0, :] - model_multi.y3[0, :]
    signal_multi_clean = signal_multi[discard_idx:]
    
    # PSD
    freqs, psd_multi = welch(signal_multi_clean, fs=10000.0, nperseg=4096)
    peak_freq_multi = freqs[freq_mask][np.argmax(psd_multi[freq_mask])]
    amp_multi = np.std(signal_multi_clean)
    
    print(f"    Multi-node:  Peak freq = {peak_freq_multi:.2f} Hz, Amp = {amp_multi:.2f} mV")
    
    # ========== COMPARISON ==========
    freq_diff = abs(peak_freq_single - peak_freq_multi)
    amp_diff = abs(amp_single - amp_multi) / amp_single * 100
    
    if freq_diff < 0.5 and amp_diff < 5:
        status = "✅ PASS"
        print(f"    Status: {status} (freq diff={freq_diff:.2f}Hz, amp diff={amp_diff:.1f}%)")
    else:
        status = "❌ FAIL"
        print(f"    Status: {status} (freq diff={freq_diff:.2f}Hz, amp diff={amp_diff:.1f}%)")
        print(f"    ⚠️  WARNING: Single-node and multi-node produce different results!")
    
    # ========== PLOTTING ==========
    
    # Plot 1: Single-node time series
    ax1 = axes[idx, 0]
    time_window = 2000
    time_idx = int(time_window / 0.1)
    ax1.plot(t_clean[:time_idx], signal_single_clean[:time_idx], linewidth=0.8, color='navy', label='Single')
    ax1.set_ylabel('mV', fontsize=8)
    ax1.set_title(f'{type_name}: {name}\nSingle-node (B={B}, G={G})', fontsize=9, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=7)
    if idx == len(CORRECT_PARAMS) - 1:
        ax1.set_xlabel('Time (ms)', fontsize=8)
    
    # Plot 2: Multi-node time series
    ax2 = axes[idx, 1]
    ax2.plot(t_clean[:time_idx], signal_multi_clean[:time_idx], linewidth=0.8, color='darkred', label='Multi')
    ax2.set_ylabel('mV', fontsize=8)
    ax2.set_title(f'Multi-node (het=0, no coupling)\n{status}', fontsize=9, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=7)
    if idx == len(CORRECT_PARAMS) - 1:
        ax2.set_xlabel('Time (ms)', fontsize=8)
    
    # Plot 3: PSD comparison
    ax3 = axes[idx, 2]
    psd_single_db = 10*np.log10(psd_single[freq_mask] + 1e-12)
    psd_multi_db = 10*np.log10(psd_multi[freq_mask] + 1e-12)
    ax3.plot(freqs[freq_mask], psd_single_db, linewidth=1.5, color='navy', alpha=0.7, label='Single')
    ax3.plot(freqs[freq_mask], psd_multi_db, linewidth=1.5, color='darkred', alpha=0.7, label='Multi', linestyle='--')
    ax3.set_ylabel('Power (dB)', fontsize=8)
    ax3.set_title(f'PSD Comparison', fontsize=9)
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=7)
    ax3.set_xlim(0, 30)
    if idx == len(CORRECT_PARAMS) - 1:
        ax3.set_xlabel('Frequency (Hz)', fontsize=8)
    
    # Plot 4: Validation summary
    ax4 = axes[idx, 3]
    ax4.axis('off')
    
    summary_text = f"""
Validation Results:

Single-node:
  Peak freq: {peak_freq_single:.2f} Hz
  Amplitude: {amp_single:.2f} mV

Multi-node (het=0):
  Peak freq: {peak_freq_multi:.2f} Hz
  Amplitude: {amp_multi:.2f} mV

Difference:
  Freq: {freq_diff:.2f} Hz
  Amp: {amp_diff:.1f}%

Status: {status}
"""
    
    box_color = 'lightgreen' if 'PASS' in status else 'lightcoral'
    ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes,
            fontsize=8, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor=box_color, alpha=0.8))

plt.suptitle('CRITICAL VALIDATION: Single-Node vs Multi-Node\n(Using Correct Wendling 2002 Parameters)', 
             fontsize=14, fontweight='bold')
plt.tight_layout()

# Save
import os
save_path = os.path.join(os.path.dirname(__file__), '..', '..', 'results', 'validation', 'single_vs_multi_verification.png')
os.makedirs(os.path.dirname(save_path), exist_ok=True)
plt.savefig(save_path, dpi=150, bbox_inches='tight')
print(f"\n\nSaved: {save_path}")
plt.close()

print("\n" + "="*80)
print("VALIDATION COMPLETE")
print("="*80)
print("""
If all tests PASS:
  ✅ Multi-node implementation is CORRECT
  ✅ Can confidently use for whole-brain modeling

If any test FAILS:
  ❌ There is a BUG in multi-node implementation
  ❌ Need to fix before proceeding
""")
print("="*80)
