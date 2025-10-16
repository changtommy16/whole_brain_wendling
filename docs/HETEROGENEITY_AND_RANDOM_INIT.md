# Heterogeneity 和 Random_Init 参数说明

## 📌 heterogeneity 参数

### 作用
控制节点间参数的**随机变异程度**，用于模拟大脑不同区域的差异性。

### 实现机制
```python
# 在 loadDefaultParams.py 中：
if heterogeneity > 0 and params.N > 1:
    # 触发向量模式
    params.B = B_base * (1 + np.random.uniform(-heterogeneity, heterogeneity, params.N))
    params.G = G_base * (1 + np.random.uniform(-heterogeneity, heterogeneity, params.N))
    params.A = A_base * (1 + np.random.uniform(-heterogeneity, heterogeneity, params.N))
    params.p_mean = p_mean_base * (1 + np.random.uniform(-heterogeneity, heterogeneity, params.N))
else:
    # 标量模式（单节点或无异质性）
    params.B = B_base
    params.G = G_base
    params.A = A_base
    params.p_mean = p_mean_base
```

### 参数范围
- **heterogeneity = 0.0**: 无变异，所有节点参数相同（标量）
- **heterogeneity = 0.1**: 10% 变异范围，例如 B ∈ [B_base×0.9, B_base×1.1]
- **heterogeneity = 0.3**: 30% 变异范围（推荐用于全脑网络）
- **heterogeneity = 0.5**: 50% 变异范围（高多样性）

### 💡 关键发现：触发向量模式
**即使 heterogeneity = 0.01（1%），也会触发向量模式！**

这意味着可以：
1. 使用 `heterogeneity=0.01` 来触发 B, G, A, p_mean 的向量化
2. 然后手动覆盖参数为精确的 Wendling types 值

```python
# Hack: 使用微小 heterogeneity 触发向量模式
model = WendlingModel(Cmat=Cmat, Dmat=Dmat, heterogeneity=0.01, seed=42)

# 然后手动设置精确参数
model.params['B'] = np.array([50, 25, 15, 15, 50, 50])  # Type1, Type3, Type6...
model.params['G'] = np.array([15, 15, 0, 0, 15, 15])
```

---

## 📌 random_init 参数

### 作用
控制初始条件的类型，影响系统动力学的启动方式。

### 实现机制
```python
# 在 loadDefaultParams.py 中：
if random_init:
    # 随机初始条件（适合全脑网络）
    params.y0_init = np.random.uniform(-0.1, 0.1, (params.N, 1))
    params.y1_init = np.random.uniform(-0.1, 0.1, (params.N, 1))
    # ... 其他状态变量
else:
    # 零初始条件（适合经典波形复现）
    params.y0_init = np.zeros((params.N, 1))
    params.y1_init = np.zeros((params.N, 1))
    # ... 其他状态变量
```

### 影响

| random_init | 初始条件 | 适用场景 | 效果 |
|-------------|---------|---------|------|
| **False** | 零初始条件 | Single-node 经典波形 | ✅ Type3, Type6 正常<br>❌ Type1 (B=50) 衰减 |
| **True** | 随机初始条件 | Multi-node 网络 | ✅ 所有 types 都能振荡<br>✅ 更接近真实大脑 |

### 💡 关键发现：Multi-node 需要 random_init=True

**在 multi-node 中，high-B types (如 Type1: B=50) 需要随机初始条件才能启动振荡！**

测试结果：
```
Type1 (B=50, G=15, p_sigma=2.0):
- Single-node + random_init=False: std=0.0000 (衰减)
- Multi-node + random_init=False:  std=0.0001 (衰减)
- Multi-node + random_init=True:   std=0.01 (微弱振荡)
```

原因：零初始条件 → 系统陷入稳态吸引子 → 无法产生振荡

---

## ⚠️ 当前实现的问题

### 问题 1: p_sigma 未向量化
```python
# 当前实现（标量）
params.p_sigma = 2.0  # 所有节点共用
```

**影响**：
- ❌ 不能混用 Type1 (需要 p_sigma=30) 和 Type3 (需要 p_sigma=2)
- ✅ 可以混用相同 p_sigma 的 types

### 问题 2: Type1 需要高噪声
```python
# Type1 (Background) 的正确参数应该是：
Type1: B=50, G=15, p_sigma=30.0  # 高噪声产生不规则慢波

# 但现在所有 types 都用 p_sigma=2.0，导致：
Type1 with p_sigma=2.0: std=0.01 (几乎无振荡)
```

---

## ✅ 正确用法总结

### Single-node 测试
```python
# 用于复现 Wendling 2002 经典波形
model = WendlingModel(
    Cmat=np.array([[0]]), 
    Dmat=np.array([[0]]),
    heterogeneity=0.0,      # 标量模式
    random_init=False,      # 零初始条件
    seed=42
)
model.params['B'] = 25  # Type3 参数
model.params['G'] = 15
model.params['p_sigma'] = 2.0
```

### Multi-node 网络（Wendling types）
```python
# 用于测试特定 Wendling types 的网络行为
model = WendlingModel(
    Cmat=Cmat, 
    Dmat=Dmat,
    heterogeneity=0.01,     # 触发向量模式（hack）
    random_init=True,       # 随机初始条件
    seed=42
)
# 手动设置每个节点的参数
model.params['B'] = np.array([50, 25, 15, ...])
model.params['G'] = np.array([15, 15, 0, ...])
model.params['A'] = np.array([5, 5, 5, ...])
model.params['p_mean'] = np.array([90, 90, 90, ...])
model.params['p_sigma'] = 2.0  # 只能用单一值
```

### Multi-node 网络（Heterogeneity 模式）
```python
# 用于真实全脑网络建模
model = WendlingModel(
    Cmat=Cmat, 
    Dmat=Dmat,
    heterogeneity=0.30,     # 30% 参数变异
    random_init=True,       # 随机初始条件
    seed=42
)
# 参数自动随机生成，不需要手动设置
model.params['K_gl'] = 0.15  # 全局耦合强度
```

---

## 📊 推荐配置

| 用途 | heterogeneity | random_init | 说明 |
|------|---------------|-------------|------|
| Single-node 验证 | 0.0 | False | 复现经典波形 |
| Multi-node Wendling types | 0.01 | True | 测试特定 types |
| 全脑网络建模 | 0.30 | True | 真实大脑模拟 |

---

## 🔧 需要改进

1. **向量化 p_sigma**：允许每个节点有不同的 p_sigma
2. **改进初始化**：为 high-B types 提供更好的初始条件
3. **文档说明**：在 WendlingModel 的 docstring 中说明这些细节

---

**最后更新**: 2025-10-14
**验证状态**: ✅ 已通过 6-nodes 和 simple tests 验证
