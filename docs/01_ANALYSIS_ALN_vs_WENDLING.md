# ALN vs Wendling 模型差异分析

**分析日期**: 2025-10-13  
**分析者**: AI Assistant  
**目的**: 了解如何为 Wendling 模型实现节点异质性

---

## 📋 摘要

本文档分析 neurolib 中 **ALN 模型**和 **Wendling 模型**的实现差异，特别关注**节点异质性**（node heterogeneity）的实现方式。

**核心发现**:
- ✅ ALN 模型支持每个节点不同的参数（向量化）
- ❌ Wendling 模型目前只支持全局单一参数（标量）
- 🎯 需要将 Wendling 的参数从标量改为向量

---

## 🔍 详细对比

### **1. 参数定义方式**

#### **ALN 模型** (`neurolib/models/aln/loadDefaultParams.py`)

```python
# 外部输入参数（向量形式）
params.mue_ext_mean = 0.4  # 基准值（标量）
params.mui_ext_mean = 0.3

# 转换为每个节点的值（向量）
params.mue_ou = params.mue_ext_mean * np.ones((params.N,))  # shape: (N,)
params.mui_ou = params.mui_ext_mean * np.ones((params.N,))  # shape: (N,)
```

**关键点**:
- 基准值是标量
- 通过 `np.ones((params.N,))` 扩展为向量
- 每个节点可以有不同的值

---

#### **Wendling 模型（当前）** (`neurolib/models/wendling/loadDefaultParams.py`)

```python
# 参数（标量形式）
params.A = 5.0        # 标量
params.B = 25.0       # 标量
params.G = 15.0       # 标量
params.p_mean = 90.0  # 标量
```

**问题**:
- 所有节点使用相同的参数
- 无法实现节点异质性
- 导致过度同步（FC ≈ 1.0）

---

### **2. 初始条件生成**

#### **ALN 模型** (`neurolib/models/aln/loadDefaultParams.py`)

```python
def generateRandomICs(N, seed=None):
    """生成随机初始条件"""
    np.random.seed(seed)
    
    mufe_init = 3 * np.random.uniform(0, 1, (N,))  # 每个节点不同
    mufi_init = 3 * np.random.uniform(0, 1, (N,))
    # ... 更多初始条件
    
    return (mufe_init, mufi_init, ...)
```

**关键点**:
- 每个节点有不同的初始条件
- 使用 `np.random.uniform(0, 1, (N,))` 生成向量

---

#### **Wendling 模型（当前）** (`neurolib/models/wendling/loadDefaultParams.py`)

```python
def generateRandomICs(N, seed=None):
    """生成随机初始条件"""
    np.random.seed(seed)
    
    y0_init = np.random.uniform(-0.5, 0.5, (N, 1))  # shape: (N, 1)
    y1_init = np.random.uniform(-0.5, 0.5, (N, 1))
    # ... 更多初始条件
    
    return (y0_init, y1_init, ...)
```

**现状**:
- ✅ 已经支持每个节点不同的初始条件
- ✅ 实现方式类似 ALN
- ✅ 这部分不需要修改

---

### **3. 时间积分函数**

#### **ALN 模型** (`neurolib/models/aln/timeIntegration.py`)

```python
# 参数提取（可以是向量）
sigmae_ext = params["sigmae_ext"]
sigmai_ext = params["sigmai_ext"]

# 在循环中使用
for no in range(N):
    # 使用节点特定的参数（如果是向量）
    # 或全局参数（如果是标量）
    mue = Jee_max * seem[no] + ...
```

**特点**:
- 参数可以是标量或向量
- 如果是向量，每个节点使用 `param[no]`
- 如果是标量，所有节点使用相同值

---

#### **Wendling 模型（当前）** (`neurolib/models/wendling/timeIntegration.py`)

```python
@njit(cache=True, fastmath=True)
def _integrate_wendling_unified(y0_arr, n_steps, dt, N,
                                 A, a, B, b, G, g,  # 参数（标量）
                                 ...):
    
    for node in range(N):
        # 所有节点使用相同的 A, B, G
        dy5 = A * a * (...) - 2.0 * a * y5 - a * a * y0_
        dy7 = B * b * (...) - 2.0 * b * y7 - b * b * y2
        dy8 = G * g * (...) - 2.0 * g * y8 - g * g * y3
```

**问题**:
- A, B, G 是标量（所有节点相同）
- 需要改为向量（每个节点不同）

---

## 🎯 实现节点异质性的方案

### **方案 1: 自动异质性（推荐）**

在 `loadDefaultParams.py` 中增加 `heterogeneity` 参数：

```python
def loadDefaultParams(Cmat=None, Dmat=None, seed=None, 
                     sigmoid_type="wendling2002", 
                     random_init=True,
                     heterogeneity=0.0):  # 新增参数
    """
    :param heterogeneity: 节点异质性程度（0.0-0.3）
                         0.0 = 无异质性（所有节点相同）
                         0.1 = 10% 变异
                         0.2 = 20% 变异
    """
    
    # 基础参数
    A_base = 5.0
    B_base = 25.0
    G_base = 15.0
    
    if heterogeneity > 0 and params.N > 1:
        # 为每个节点生成略微不同的参数
        np.random.seed(seed)
        params.A = A_base * (1 + np.random.uniform(-heterogeneity, heterogeneity, params.N))
        params.B = B_base * (1 + np.random.uniform(-heterogeneity, heterogeneity, params.N))
        params.G = G_base * (1 + np.random.uniform(-heterogeneity, heterogeneity, params.N))
        params.p_mean = 90.0 * (1 + np.random.uniform(-heterogeneity, heterogeneity, params.N))
    else:
        # 无异质性或单节点：使用标量
        params.A = A_base
        params.B = B_base
        params.G = G_base
        params.p_mean = 90.0
```

**使用方式**:
```python
# 创建具有 10% 异质性的 6 节点网络
model = WendlingModel(Cmat=Cmat, heterogeneity=0.1)
```

---

### **方案 2: 手动设置（灵活）**

允许用户手动设置每个节点的参数：

```python
model = WendlingModel(Cmat=Cmat)
model.params['B'] = np.array([50, 40, 30, 20, 25, 35])  # 手动指定
```

**实现**: 修改 `timeIntegration.py` 中的参数处理逻辑：

```python
# 参数标准化（确保都是向量）
def _ensure_vector(param, N):
    """确保参数是向量形式"""
    if np.isscalar(param):
        return np.full(N, param)
    elif len(param) == 1 and N > 1:
        return np.full(N, param[0])
    else:
        return param

# 在积分函数中使用
A_vec = _ensure_vector(A, N)
B_vec = _ensure_vector(B, N)
G_vec = _ensure_vector(G, N)
```

---

## 🔧 具体修改位置

### **修改 1: `loadDefaultParams.py`**

**位置**: 第 42-125 行

**修改内容**:
1. 函数签名增加 `heterogeneity=0.0`
2. 参数向量化逻辑（第 99-125 行）

**影响**:
- 向后兼容（默认 `heterogeneity=0.0`，保持原有行为）
- 支持自动异质性
- 支持手动设置向量参数

---

### **修改 2: `timeIntegration.py`**

**位置**: 第 186-276 行（`_integrate_wendling_unified` 函数）

**修改内容**:

1. **参数标准化**（函数开头）:
```python
@njit(cache=True, fastmath=True)
def _integrate_wendling_unified(y0_arr, n_steps, dt, N,
                                 A, a, B, b, G, g, C, C1, C2, C3, C4, C5, C6, C7,
                                 e0, v0, r, p_mean, p_sigma,
                                 Cmat, K_gl, Dmat_ndt, max_delay):
    
    # === 新增：参数向量化 ===
    # 将标量参数扩展为向量
    if np.ndim(A) == 0:  # 如果是标量
        A_vec = np.full(N, A, dtype=np.float64)
        B_vec = np.full(N, B, dtype=np.float64)
        G_vec = np.full(N, G, dtype=np.float64)
        p_mean_vec = np.full(N, p_mean, dtype=np.float64)
    else:  # 如果已经是向量
        A_vec = A.astype(np.float64)
        B_vec = B.astype(np.float64)
        G_vec = G.astype(np.float64)
        p_mean_vec = p_mean.astype(np.float64)
    # === 结束新增 ===
```

2. **在循环中使用节点特定参数**（第 221-273 行）:
```python
for node in range(N):
    # === 修改：使用节点特定的参数 ===
    A_node = A_vec[node]
    B_node = B_vec[node]
    G_node = G_vec[node]
    p_mean_node = p_mean_vec[node]
    # === 结束修改 ===
    
    # 噪声
    xi_t = np.random.normal(0.0, 1.0)
    p_t = p_mean_node + p_sigma * xi_t * np.sqrt(dt)  # 使用节点特定的 p_mean
    
    # 耦合输入
    coupling_input = 0.0
    for j in range(N):
        if Cmat[node, j] > 0:
            delay_idx = idx - 1 - Dmat_ndt[node, j]
            if delay_idx >= 0:
                v_j = ys[j, 1, delay_idx] - ys[j, 2, delay_idx] - ys[j, 3, delay_idx]
                coupling_input += K_gl * Cmat[node, j] * _sigm_fast(v_j, e0, v0, r)
    
    # === 修改：使用节点特定的参数 ===
    dy0 = y5
    dy5 = A_node * a * (_sigm_fast(y1 - y2 - y3, e0, v0, r) + coupling_input) - 2.0 * a * y5 - a * a * y0_
    
    dy1 = y6
    dy6 = A_node * a * (C2 * _sigm_fast(C1 * y0_, e0, v0, r) + p_t) - 2.0 * a * y6 - a * a * y1
    
    dy2 = y7
    dy7 = B_node * b * (C4 * _sigm_fast(C3 * y0_, e0, v0, r)) - 2.0 * b * y7 - b * b * y2
    
    dy3 = y8
    dy8 = G_node * g * (C7 * _sigm_fast((C5 * y0_ - C6 * y4), e0, v0, r)) - 2.0 * g * y8 - g * g * y3
    
    dy4 = y9
    dy9 = B_node * b * (_sigm_fast(C3 * y0_, e0, v0, r)) - 2.0 * b * y9 - b * b * y4
    # === 结束修改 ===
```

---

### **修改 3: `model.py`（可选）**

**位置**: 类定义

**新增方法**:
```python
def set_heterogeneous_params(self, param_name, values):
    """设置节点异质性参数的便利方法"""
    if len(values) != self.params['N']:
        raise ValueError(f"values 长度必须等于节点数 N={self.params['N']}")
    self.params[param_name] = np.array(values)

def get_heterogeneity_summary(self):
    """返回参数异质性的统计总结"""
    summary = {}
    for param in ['A', 'B', 'G', 'p_mean']:
        val = self.params.get(param)
        if isinstance(val, np.ndarray) and len(val) > 1:
            summary[param] = {
                'mean': np.mean(val),
                'std': np.std(val),
                'cv': np.std(val) / np.mean(val)
            }
    return summary
```

---

## ✅ 验证方法

### **单元测试**

创建测试脚本验证向量化参数功能：

```python
import numpy as np
from neurolib.models.wendling import WendlingModel

# 测试 1: 自动异质性
Cmat = np.ones((6, 6)) - np.eye(6)
model = WendlingModel(Cmat=Cmat, heterogeneity=0.1, seed=42)

# 检查参数是否为向量
assert isinstance(model.params['A'], np.ndarray)
assert len(model.params['A']) == 6

# 检查参数是否有变异
assert np.std(model.params['B']) > 0

print("✅ 测试 1 通过：自动异质性")

# 测试 2: 手动设置
model2 = WendlingModel(Cmat=Cmat)
model2.params['B'] = np.array([50, 40, 30, 20, 25, 35])

assert len(model2.params['B']) == 6
assert model2.params['B'][0] == 50

print("✅ 测试 2 通过：手动设置向量参数")

# 测试 3: 运行模拟
model.params['duration'] = 5000
model.run()

# 检查每个节点活动是否不同
signals = np.zeros((6, len(model.t)))
for i in range(6):
    signals[i, :] = model.y1[i, :] - model.y2[i, :] - model.y3[i, :]

# 计算节点间相关性
from scipy.stats import pearsonr
fc = np.zeros((6, 6))
for i in range(6):
    for j in range(6):
        fc[i, j], _ = pearsonr(signals[i, :], signals[j, :])

mean_fc = np.mean(np.abs(fc[~np.eye(6, dtype=bool)]))
print(f"Mean |FC| = {mean_fc:.3f}")

assert mean_fc < 0.9, "FC 过高，异质性不足"

print("✅ 测试 3 通过：节点异质性导致 FC 降低")
```

---

## 📊 预期效果

### **无异质性（当前）**
```
参数: A=5.0, B=25.0, G=15.0（所有节点相同）
结果: 
  - 所有节点峰值频率: ~3.5 Hz
  - Mean |FC| = 0.99
  - 节点活动几乎完全相同
```

### **有异质性（目标）**
```
参数: 
  Node 0: B=50
  Node 1: B=40
  Node 2: B=30
  Node 3: B=20
  Node 4: B=25
  Node 5: B=35

结果:
  - 峰值频率: 2.1, 2.5, 3.5, 5.2, 4.1, 3.0 Hz (std = 1.1 Hz)
  - Mean |FC| = 0.45
  - 节点活动明显不同
```

---

## 🔗 参考代码位置

### **ALN 模型**
- `neurolib/models/aln/loadDefaultParams.py`: 第 1-230 行
- `neurolib/models/aln/timeIntegration.py`: 第 1-880 行

### **Wendling 模型**
- `neurolib/models/wendling/loadDefaultParams.py`: 第 1-174 行
- `neurolib/models/wendling/timeIntegration.py`: 第 1-277 行

### **Examples**
- `examples/example-0-aln-minimal.ipynb`
- `examples/example-1.2-brain-network-exploration.ipynb`

---

## 📝 总结

### **关键差异**

| 特性 | ALN | Wendling (当前) | 需要修改 |
|------|-----|----------------|---------|
| 参数类型 | 向量 | 标量 | ✅ 是 |
| 初始条件 | 向量 | 向量 | ❌ 否 |
| 耦合机制 | E→E | Pyr→Pyr | ❌ 否 |
| 延迟支持 | ✅ | ✅ | ❌ 否 |

### **实施步骤**

1. ✅ 分析差异（已完成）
2. ⏳ 修改 `loadDefaultParams.py`
3. ⏳ 修改 `timeIntegration.py`
4. ⏳ 创建单元测试
5. ⏳ 验证功能

---

**分析完成日期**: 2025-10-13  
**下一步**: 开始阶段 1 实施
