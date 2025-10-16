"""
Single-Node Wendling Model - Interactive Testing

可以轻松调整参数或选择不同的 Wendling types 进行测试
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')
sys.path.insert(0, r'c:\Epilepsy_project\whole_brain_wendling\Validation_for_single_node')

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from neurolib.models.wendling import WendlingModel
from STANDARD_PARAMETERS import WENDLING_STANDARD_PARAMS

print("="*80)
print("Single-Node Wendling Model - Interactive Testing")
print("="*80)

# ============================================================================
# CONFIGURATION - 在这里修改配置
# ============================================================================

# 选项 1: 使用预定义的 Wendling type
USE_STANDARD_TYPE = 'Type2'  # 'Type1', 'Type2', 'Type3', 'Type4', 'Type5', 'Type6' 或 None
# USE_STANDARD_TYPE = None  # 设为 None 使用下面的手动参数

# 选项 2: 手动设置参数 (当 USE_STANDARD_TYPE = None 时使用)
MANUAL_PARAMS = {
    'A': 5.0,
    'B': 50,
    'G': 15,
    'p_mean': 90,
    'p_sigma': 2.0
}

# 仿真参数
DURATION = 10000  # ms (10 seconds)
DT = 0.1  # ms
SEED = 42

# ============================================================================

# 选择参数
if USE_STANDARD_TYPE is not None:
    if USE_STANDARD_TYPE not in WENDLING_STANDARD_PARAMS:
        raise ValueError(f"Invalid type: {USE_STANDARD_TYPE}. Choose from {list(WENDLING_STANDARD_PARAMS.keys())}")
    
    params_dict = WENDLING_STANDARD_PARAMS[USE_STANDARD_TYPE]
    params = params_dict['params']
    type_name = params_dict['name']
    expected_freq = params_dict['expected']['freq_range']
    
    print(f"\n✅ Using Standard Type: {USE_STANDARD_TYPE}")
    print(f"   {type_name}")
    print(f"   Expected frequency: {expected_freq[0]}-{expected_freq[1]} Hz")
else:
    params = MANUAL_PARAMS
    type_name = "Manual Parameters"
    expected_freq = None
    print(f"\n⚙️  Using Manual Parameters")

print(f"\nParameters:")
print(f"  A = {params['A']}")
print(f"  B = {params['B']}")
print(f"  G = {params['G']}")
print(f"  p_mean = {params['p_mean']}")
print(f"  p_sigma = {params['p_sigma']}")

# ============================================================================
# 创建并运行模型
# ============================================================================

print(f"\nCreating single-node model...")
model = WendlingModel(
    Cmat=np.array([[0]]), 
    Dmat=np.array([[0]]), 
    heterogeneity=0.0, 
    seed=SEED,
    random_init=False  # 使用零初始条件以获得经典波形
)

model.params['duration'] = DURATION
model.params['dt'] = DT
model.params['K_gl'] = 0.0  # No coupling for single node
model.params['A'] = params['A']
model.params['B'] = params['B']
model.params['G'] = params['G']
model.params['p_mean'] = params['p_mean']
model.params['p_sigma'] = params['p_sigma']

print(f"\nRunning simulation ({DURATION} ms)...")
import time
start_time = time.time()
model.run()
elapsed = time.time() - start_time
print(f"  Completed in {elapsed:.2f}s")

# ============================================================================
# 提取和分析信号
# ============================================================================

t = model.t
signal = model.y1[0, :] - model.y2[0, :] - model.y3[0, :]

# 去除瞬态
discard_idx = int(2000 / DT)
signal_clean = signal[discard_idx:]
t_clean = t[discard_idx:]

# 计算统计量
mean_val = np.mean(signal_clean)
std_val = np.std(signal_clean)
min_val = np.min(signal_clean)
max_val = np.max(signal_clean)

print(f"\nSignal Statistics:")
print(f"  Mean: {mean_val:.4f} mV")
print(f"  Std:  {std_val:.4f} mV")
print(f"  Min:  {min_val:.4f} mV")
print(f"  Max:  {max_val:.4f} mV")

# 计算频谱
freqs, psd = welch(signal_clean, fs=1000.0/DT, nperseg=4096)
freq_mask = (freqs >= 0.5) & (freqs <= 50)
peak_freq = freqs[freq_mask][np.argmax(psd[freq_mask])]

print(f"\nFrequency Analysis:")
print(f"  Peak frequency: {peak_freq:.2f} Hz")
if expected_freq is not None:
    if expected_freq[0] <= peak_freq <= expected_freq[1]:
        print(f"  ✅ MATCH (expected {expected_freq[0]}-{expected_freq[1]} Hz)")
    else:
        print(f"  ❌ OFF (expected {expected_freq[0]}-{expected_freq[1]} Hz)")

# ============================================================================
# 绘图
# ============================================================================

print(f"\nGenerating plots...")

fig = plt.figure(figsize=(16, 10))

# 1. 完整时间序列 (前5秒)
ax1 = plt.subplot(3, 2, 1)
window_idx = int(5000 / DT)
ax1.plot(t_clean[:window_idx], signal_clean[:window_idx], linewidth=0.8, color='navy')
ax1.set_xlabel('Time (ms)', fontsize=11)
ax1.set_ylabel('Amplitude (mV)', fontsize=11)
ax1.set_title(f'Time Series - Full View (5s)\n{type_name}', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)

# 2. 放大视图 (2秒)
ax2 = plt.subplot(3, 2, 2)
zoom_idx = int(2000 / DT)
ax2.plot(t_clean[:zoom_idx], signal_clean[:zoom_idx], linewidth=1.0, color='darkgreen')
ax2.set_xlabel('Time (ms)', fontsize=11)
ax2.set_ylabel('Amplitude (mV)', fontsize=11)
ax2.set_title('Time Series - Zoom (2s)', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)

# 3. 功率谱密度
ax3 = plt.subplot(3, 2, 3)
psd_db = 10*np.log10(psd[freq_mask] + 1e-12)
ax3.plot(freqs[freq_mask], psd_db, linewidth=1.5, color='darkred')
ax3.axvline(peak_freq, color='red', linestyle='--', alpha=0.7, label=f'Peak: {peak_freq:.1f} Hz')
if expected_freq is not None:
    ax3.axvspan(expected_freq[0], expected_freq[1], alpha=0.2, color='green', label='Expected range')
ax3.set_xlabel('Frequency (Hz)', fontsize=11)
ax3.set_ylabel('Power (dB)', fontsize=11)
ax3.set_title('Power Spectral Density', fontsize=12, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.set_xlim(0, 30)

# 4. 信号直方图
ax4 = plt.subplot(3, 2, 4)
ax4.hist(signal_clean, bins=50, color='steelblue', alpha=0.7, edgecolor='black')
ax4.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
ax4.set_xlabel('Amplitude (mV)', fontsize=11)
ax4.set_ylabel('Count', fontsize=11)
ax4.set_title('Signal Distribution', fontsize=12, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3, axis='y')

# 5. 相位空间 (y1 vs dy1/dt)
ax5 = plt.subplot(3, 2, 5)
y1_vals = model.y1[0, discard_idx:]
y5_vals = model.y5[0, discard_idx:]  # dy1/dt
# Subsample for clarity
subsample = slice(0, len(y1_vals), 10)
ax5.plot(y1_vals[subsample], y5_vals[subsample], linewidth=0.5, alpha=0.6, color='purple')
ax5.set_xlabel('y1 (Pyramidal PSP)', fontsize=11)
ax5.set_ylabel('dy1/dt', fontsize=11)
ax5.set_title('Phase Space (y1 vs dy1/dt)', fontsize=12, fontweight='bold')
ax5.grid(True, alpha=0.3)

# 6. 参数摘要
ax6 = plt.subplot(3, 2, 6)
ax6.axis('off')

summary_text = f"""
Parameter Summary
{'='*40}

Type: {type_name if USE_STANDARD_TYPE else 'Manual'}
{f'Standard Type: {USE_STANDARD_TYPE}' if USE_STANDARD_TYPE else ''}

Model Parameters:
  A (Excitatory gain):      {params['A']:.1f} mV
  B (Slow inhib. gain):     {params['B']:.1f} mV
  G (Fast inhib. gain):     {params['G']:.1f} mV
  p_mean (Input mean):      {params['p_mean']:.1f} Hz
  p_sigma (Input noise):    {params['p_sigma']:.1f} Hz

Results:
  Peak Frequency:           {peak_freq:.2f} Hz
{f'  Expected Frequency:       {expected_freq[0]}-{expected_freq[1]} Hz' if expected_freq else ''}
{f'  Match: {"✅ YES" if expected_freq and expected_freq[0] <= peak_freq <= expected_freq[1] else "❌ NO"}' if expected_freq else ''}
  
  Signal Mean:              {mean_val:.4f} mV
  Signal Std:               {std_val:.4f} mV
  Signal Range:             [{min_val:.2f}, {max_val:.2f}] mV

Simulation:
  Duration:                 {DURATION} ms
  Time step:                {DT} ms
  Random seed:              {SEED}
"""

ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes,
        fontsize=10, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.tight_layout()

# 保存
import os
if USE_STANDARD_TYPE:
    filename = f'single_node_{USE_STANDARD_TYPE}_result.png'
else:
    filename = f'single_node_B{params["B"]}_G{params["G"]}_result.png'

save_path = os.path.join(os.path.dirname(__file__), 'results', filename)
os.makedirs(os.path.dirname(save_path), exist_ok=True)
plt.savefig(save_path, dpi=150, bbox_inches='tight')
print(f"\n✅ Saved: {save_path}")

plt.show()

print("\n" + "="*80)
print("Analysis Complete!")
print("="*80)
print(f"""
To test different configurations:

1. Change USE_STANDARD_TYPE:
   USE_STANDARD_TYPE = 'Type3'  # For SWD
   USE_STANDARD_TYPE = 'Type6'  # For quasi-sinusoidal
   
2. Use manual parameters:
   USE_STANDARD_TYPE = None
   MANUAL_PARAMS = {{'A': 5.0, 'B': 25, 'G': 15, 'p_mean': 90, 'p_sigma': 2.0}}

3. Adjust simulation duration:
   DURATION = 20000  # 20 seconds for longer observation
""")
print("="*80)
