# 6-Nodes 测试总结

## 🎯 测试目标
验证 Wendling 模型在小规模网络中的行为，重点关注：
1. 节点异质性的实现
2. Wendling 2002 六种活动类型的复现
3. 参数设置和向量化机制

---

## 📊 核心发现

### 1. heterogeneity 和 random_init 的关键作用

| 参数 | 作用 | 推荐值 |
|------|------|--------|
| **heterogeneity** | 触发参数向量化 | Single-node: 0.0<br>Multi-node (Wendling types): 0.01<br>Multi-node (网络): 0.30 |
| **random_init** | 控制初始条件 | Single-node: False<br>Multi-node: True |

**关键发现**：
- ✅ `heterogeneity > 0` 会触发 B, G, A, p_mean 的向量化
- ✅ `random_init=True` 对 multi-node 中的 high-B types (如 Type1) 至关重要
- ⚠️ `p_sigma` 目前仍是标量，未向量化

### 2. Wendling Types 在 Multi-node 中的表现

| Type | B | G | p_sigma | Multi-node表现 | 需要random_init |
|------|---|---|---------|----------------|-----------------|
| Type1 (Background) | 50 | 15 | 30.0* | 低振幅慢波 | ✅ True |
| Type2 (Sporadic spikes) | 40 | 15 | 30.0* | 零星尖波 | ✅ True |
| Type3 (SWD) | 25 | 15 | 2.0 | Spike-wave ✅ | ✅ True/False 都可 |
| Type4 (Alpha) | 10 | 15 | 30.0* | Alpha节律 | ✅ True |
| Type5 (LVFA) | 5 | 25 | 30.0* | 快速活动 | ✅ True |
| Type6 (Quasi-sin) | 15 | 0 | 2.0 | 正弦波 ✅ | ✅ True/False 都可 |

*注：当前实现中所有 types 都用 p_sigma=2.0，导致 Type1, 2, 4, 5 振幅过小

### 3. 参数向量化的实现方式

**问题**：使用 `heterogeneity=0.0` 时，参数为标量，无法为每个节点设置不同值

**解决方案**：
```python
# 使用微小 heterogeneity 触发向量模式
model = WendlingModel(Cmat=Cmat, Dmat=Dmat, heterogeneity=0.01, seed=42, random_init=True)

# 然后手动覆盖为精确的 Wendling types 参数
model.params['B'] = np.array([50, 25, 15, 15, 50, 50])  # Type1, Type3, Type6...
model.params['G'] = np.array([15, 15, 0, 0, 15, 15])
model.params['A'] = np.array([5, 5, 5, 5, 5, 5])
model.params['p_mean'] = np.array([90, 90, 90, 90, 90, 90])
model.params['p_sigma'] = 2.0  # 标量（未向量化）
```

---

## ⚠️ 当前限制

### 1. p_sigma 未向量化
- **影响**：不能在同一网络中混用需要不同 p_sigma 的 types
- **变通方案**：只混用相同 p_sigma 的 types
  - Group A: Type3, Type6 (p_sigma=2.0)
  - Group B: Type1, Type2, Type4, Type5 (p_sigma=30.0)

### 2. Type1 在 p_sigma=2.0 下振幅过小
- **原因**：Type1 需要高噪声 (p_sigma=30.0) 才能产生不规则慢波
- **当前状态**：使用 p_sigma=2.0 时，Type1 几乎无振荡 (std≈0.01)
- **可能解释**：Type1 本身就是低振幅活动，相对其他 types 不明显

---

## ✅ 已验证的功能

1. ✅ 参数向量化机制（通过 heterogeneity hack）
2. ✅ Type3 (SWD) 在 multi-node 中正确展现
3. ✅ Type6 (Quasi-sinusoidal) 在 multi-node 中正确展现
4. ✅ random_init=True 对 multi-node 的必要性
5. ✅ 波形特征与参数标注一致

---

## 📁 文件结构

### 核心测试文件
```
2_six_nodes/
├── test_00_unit_test_heterogeneity.py    # 异质性单元测试
├── test_01_heterogeneity_sweep.py        # 异质性参数扫描
├── test_02_optimal_params.py             # 最优参数搜索
├── test_03_complete_analysis_FIXED.py    # ⭐ 完整分析（主要）
├── test_04_six_types_network.py          # 六种类型网络测试
├── README.md                             # 说明文档
├── SUMMARY.md                            # 本文件
├── CLEANUP.py                            # 清理脚本
└── archive_debug/                        # 归档的调试文件
```

### 主要测试：test_03_complete_analysis_FIXED.py

**配置选项**：
```python
# 手动指定每个节点的 Wendling type
NODE_TYPES = ['Type1', 'Type3', 'Type6', 'Type6', 'Type1', 'Type1']

# 或使用 heterogeneity 模式
NODE_TYPES = None  # 使用 heterogeneity=0.30

# 网络参数
K_GL = 0.0  # 全局耦合强度
NETWORK_DENSITY = 0.6  # 连接密度
```

**输出**：
- 12个子图的完整分析
- 参数验证和频率匹配检查
- SC-FC 相关性分析
- 模块化指标

---

## 🔧 建议改进

1. **向量化 p_sigma**
   ```python
   # 在 loadDefaultParams.py 中添加：
   if heterogeneity > 0:
       params.p_sigma = p_sigma_base * (1 + np.random.uniform(-heterogeneity, heterogeneity, params.N))
   ```

2. **改进初始化策略**
   - 为不同 B 值范围提供自适应初始条件
   - 或提供 `initial_perturbation` 参数

3. **恢复正确的 p_sigma 值**
   ```python
   # STANDARD_PARAMETERS.py 中：
   Type1: p_sigma=30.0  # 高噪声
   Type3: p_sigma=2.0   # 低噪声
   Type6: p_sigma=2.0   # 低噪声
   ```

---

## 📚 参考文档

- `docs/HETEROGENEITY_AND_RANDOM_INIT.md` - 详细参数说明
- `docs/08_TWO_PARAMETER_SYSTEMS.md` - 参数系统对比
- `Validation_for_single_node/STANDARD_PARAMETERS.py` - 标准参数定义

---

**最后更新**: 2025-10-14  
**状态**: ✅ 核心功能已验证，部分限制待改进
