"""
寻找最佳参数组合：heterogeneity + K_gl

目标：Mean |FC| 在 0.4-0.6 范围
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')

import numpy as np
from scipy.stats import pearsonr
from neurolib.models.wendling import WendlingModel

print("="*80)
print("最佳参数组合搜索")
print("="*80)

N = 6
Cmat = np.ones((N, N)) - np.eye(N)

# 测试组合
test_cases = [
    {'het': 0.30, 'K_gl': 0.3},
    {'het': 0.30, 'K_gl': 0.2},
    {'het': 0.30, 'K_gl': 0.15},
    {'het': 0.35, 'K_gl': 0.2},
]

results = []

for case in test_cases:
    het = case['het']
    K_gl = case['K_gl']
    
    print(f"\n测试: heterogeneity={het:.2f}, K_gl={K_gl:.2f}")
    
    model = WendlingModel(Cmat=Cmat, heterogeneity=het, seed=42)
    model.params['duration'] = 5000
    model.params['dt'] = 0.1
    model.params['K_gl'] = K_gl
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
    
    print(f"  Mean |FC| = {mean_fc:.3f}")
    
    if 0.4 <= mean_fc <= 0.6:
        print(f"  ✅ 理想范围！")
        results.append((het, K_gl, mean_fc, '✅'))
    elif 0.3 <= mean_fc < 0.4 or 0.6 < mean_fc <= 0.7:
        print(f"  ⚠️  可接受")
        results.append((het, K_gl, mean_fc, '⚠️'))
    else:
        print(f"  ❌ 需调整")
        results.append((het, K_gl, mean_fc, '❌'))

print("\n" + "="*80)
print("推荐参数")
print("="*80)

# 找最佳
best = min(results, key=lambda x: abs(x[2] - 0.5))
print(f"\n最佳组合:")
print(f"  heterogeneity = {best[0]:.2f}")
print(f"  K_gl = {best[1]:.2f}")
print(f"  Mean |FC| = {best[2]:.3f}")
print(f"\n这将用于后续的 6-nodes 完整测试。")
print("="*80)
