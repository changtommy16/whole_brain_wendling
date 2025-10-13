"""
快速测试：不同 heterogeneity 级别对 FC 的影响

找出最佳的 heterogeneity 参数范围
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')

import numpy as np
from scipy.stats import pearsonr
from neurolib.models.wendling import WendlingModel

print("="*80)
print("Heterogeneity 参数扫描测试")
print("="*80)

# 创建网络
N = 6
Cmat = np.ones((N, N)) - np.eye(N)

# 测试不同 heterogeneity 级别
heterogeneity_levels = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
results = []

for het in heterogeneity_levels:
    print(f"\n测试 heterogeneity = {het:.2f}...")
    
    model = WendlingModel(Cmat=Cmat, heterogeneity=het, seed=42)
    model.params['duration'] = 5000
    model.params['dt'] = 0.1
    model.params['K_gl'] = 0.3
    model.run()
    
    signals = np.zeros((N, len(model.t)))
    for i in range(N):
        signals[i, :] = model.y1[i, :] - model.y2[i, :] - model.y3[i, :]
    
    discard = int(2000 / 0.1)
    fc = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            fc[i, j], _ = pearsonr(signals[i, discard:], signals[j, discard:])
    
    mean_fc = np.mean(np.abs(fc[~np.eye(N, dtype=bool)]))
    
    # 计算峰值频率多样性
    from scipy.signal import welch
    peak_freqs = []
    fs = 10000.0
    for i in range(N):
        freqs, psd = welch(signals[i, discard:], fs=fs, nperseg=4096)
        freq_mask = (freqs >= 1) & (freqs <= 50)
        peak_freq = freqs[freq_mask][np.argmax(psd[freq_mask])]
        peak_freqs.append(peak_freq)
    
    freq_std = np.std(peak_freqs)
    
    print(f"  Mean |FC| = {mean_fc:.3f}")
    print(f"  Freq std  = {freq_std:.2f} Hz")
    
    results.append({
        'heterogeneity': het,
        'mean_fc': mean_fc,
        'freq_std': freq_std
    })

print("\n" + "="*80)
print("扫描结果总结")
print("="*80)
print(f"{'Heterogeneity':<15} {'Mean |FC|':<12} {'Freq std (Hz)':<15} {'评估'}")
print("-"*80)

for r in results:
    het = r['heterogeneity']
    fc = r['mean_fc']
    fstd = r['freq_std']
    
    # 评估
    if 0.3 <= fc <= 0.7:
        assessment = "✅ 理想范围"
    elif 0.7 < fc < 0.85:
        assessment = "⚠️  接近目标"
    elif fc >= 0.85:
        assessment = "❌ FC太高"
    else:
        assessment = "⚠️  FC可能太低"
    
    print(f"{het:<15.2f} {fc:<12.3f} {fstd:<15.2f} {assessment}")

print("\n建议:")
best_het = None
for r in results:
    if 0.3 <= r['mean_fc'] <= 0.7:
        best_het = r['heterogeneity']
        print(f"  推荐 heterogeneity = {best_het:.2f} (FC = {r['mean_fc']:.3f})")
        break

if best_het is None:
    # 找最接近的
    closest = min(results, key=lambda x: abs(x['mean_fc'] - 0.5))
    print(f"  建议 heterogeneity = {closest['heterogeneity']:.2f} (FC = {closest['mean_fc']:.3f})")
    if closest['mean_fc'] > 0.7:
        print(f"  提示：可能需要降低 K_gl 全局耦合")

print("="*80)
