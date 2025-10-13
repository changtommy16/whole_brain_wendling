"""
单元测试：节点异质性参数

验证 Wendling 模型的节点异质性功能是否正确实现。

测试内容：
1. 向量化参数：检查参数是否正确转换为向量
2. 手动设置：检查能否手动设置不同节点的参数
3. 模拟运行：检查异质性是否降低同步性
4. 向后兼容：检查单节点模拟是否仍然正常工作
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')

import numpy as np
from scipy.stats import pearsonr
from neurolib.models.wendling import WendlingModel

print("="*80)
print("单元测试：节点异质性参数")
print("="*80)

# ==================== 测试 1: 自动异质性 ====================
print("\n" + "-"*80)
print("测试 1: 自动异质性（heterogeneity=0.1）")
print("-"*80)

Cmat = np.ones((6, 6)) - np.eye(6)
model = WendlingModel(Cmat=Cmat, heterogeneity=0.1, seed=42)

# 检查参数是否为向量
print("\n检查参数类型:")
print(f"  A 类型: {type(model.params['A'])}, 形状: {np.shape(model.params['A'])}")
print(f"  B 类型: {type(model.params['B'])}, 形状: {np.shape(model.params['B'])}")
print(f"  G 类型: {type(model.params['G'])}, 形状: {np.shape(model.params['G'])}")

assert isinstance(model.params['A'], np.ndarray), "A 应该是 numpy array"
assert len(model.params['A']) == 6, "A 长度应该是 6"
assert len(model.params['B']) == 6, "B 长度应该是 6"
assert len(model.params['G']) == 6, "G 长度应该是 6"

print("  ✅ 参数类型检查通过")

# 检查参数是否有变异
print("\n检查参数变异:")
print(f"  A 值: {model.params['A']}")
print(f"  B 值: {model.params['B']}")
print(f"  G 值: {model.params['G']}")
print(f"  B 标准差: {np.std(model.params['B']):.3f}")

assert np.std(model.params['B']) > 0, "B 应该有变异"
print("  ✅ 参数变异检查通过")

# ==================== 测试 2: 手动设置参数 ====================
print("\n" + "-"*80)
print("测试 2: 手动设置向量参数")
print("-"*80)

model2 = WendlingModel(Cmat=Cmat, seed=42)
B_manual = np.array([50, 40, 30, 20, 25, 35], dtype=float)
model2.params['B'] = B_manual

print(f"\n设置的 B 值: {model2.params['B']}")
assert len(model2.params['B']) == 6, "B 长度应该是 6"
assert model2.params['B'][0] == 50, "B[0] 应该是 50"
assert model2.params['B'][5] == 35, "B[5] 应该是 35"
print("  ✅ 手动设置检查通过")

# ==================== 测试 3: 运行模拟（异质性降低同步性） ====================
print("\n" + "-"*80)
print("测试 3: 模拟运行 - 异质性降低同步性")
print("-"*80)

# 无异质性
print("\n运行无异质性模拟...")
model_homo = WendlingModel(Cmat=Cmat, heterogeneity=0.0, seed=42)
model_homo.params['duration'] = 5000  # 5秒
model_homo.params['dt'] = 0.1
model_homo.params['K_gl'] = 0.3
model_homo.run()

signals_homo = np.zeros((6, len(model_homo.t)))
for i in range(6):
    signals_homo[i, :] = model_homo.y1[i, :] - model_homo.y2[i, :] - model_homo.y3[i, :]

# 计算 FC
discard = int(2000 / 0.1)
fc_homo = np.zeros((6, 6))
for i in range(6):
    for j in range(6):
        fc_homo[i, j], _ = pearsonr(signals_homo[i, discard:], signals_homo[j, discard:])

mean_fc_homo = np.mean(np.abs(fc_homo[~np.eye(6, dtype=bool)]))
print(f"  无异质性 Mean |FC| = {mean_fc_homo:.3f}")

# 有异质性
print("\n运行有异质性模拟...")
model_hetero = WendlingModel(Cmat=Cmat, heterogeneity=0.15, seed=42)
model_hetero.params['duration'] = 5000
model_hetero.params['dt'] = 0.1
model_hetero.params['K_gl'] = 0.3
model_hetero.run()

signals_hetero = np.zeros((6, len(model_hetero.t)))
for i in range(6):
    signals_hetero[i, :] = model_hetero.y1[i, :] - model_hetero.y2[i, :] - model_hetero.y3[i, :]

fc_hetero = np.zeros((6, 6))
for i in range(6):
    for j in range(6):
        fc_hetero[i, j], _ = pearsonr(signals_hetero[i, discard:], signals_hetero[j, discard:])

mean_fc_hetero = np.mean(np.abs(fc_hetero[~np.eye(6, dtype=bool)]))
print(f"  有异质性 Mean |FC| = {mean_fc_hetero:.3f}")

# 验证：异质性应该降低 FC
print(f"\n对比:")
print(f"  FC 降低: {mean_fc_homo - mean_fc_hetero:.3f}")
assert mean_fc_hetero < mean_fc_homo, "异质性应该降低 FC"
print("  ✅ 异质性降低同步性 - 检查通过")

# ==================== 测试 4: 向后兼容（单节点） ====================
print("\n" + "-"*80)
print("测试 4: 向后兼容性 - 单节点模拟")
print("-"*80)

print("\n运行单节点模拟...")
model_single = WendlingModel(seed=100)
model_single.params['duration'] = 5000
model_single.params['dt'] = 0.1
model_single.params['B'] = 30.0  # 标量
model_single.run()

signal_single = model_single.y1[0, :] - model_single.y2[0, :] - model_single.y3[0, :]
print(f"  信号长度: {len(signal_single)}")
print(f"  信号范围: [{np.min(signal_single):.2f}, {np.max(signal_single):.2f}] mV")
print(f"  RMS: {np.sqrt(np.mean(signal_single**2)):.3f} mV")

assert len(signal_single) > 0, "单节点模拟应该产生信号"
assert np.abs(np.max(signal_single)) < 50, "信号幅度应该在合理范围内"
print("  ✅ 单节点模拟正常 - 向后兼容性检查通过")

# ==================== 总结 ====================
print("\n" + "="*80)
print("测试总结")
print("="*80)
print("✅ 测试 1: 自动异质性参数 - 通过")
print("✅ 测试 2: 手动设置参数 - 通过")
print("✅ 测试 3: 异质性降低同步性 - 通过")
print("✅ 测试 4: 向后兼容性 - 通过")
print("\n[ALL PASS] ✅ 所有单元测试通过！")
print("="*80)
print("\n节点异质性功能已成功实现并验证。")
print("下一步：创建 6-nodes 网络的完整测试。")
print("="*80)
