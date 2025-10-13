# Wendling Whole-Brain Network Implementation Plan

**项目**: 从单节点到全脑网络的 Wendling 模型实现  
**主要工作目录**: `c:\Epilepsy_project\whole_brain_wendling\`  
**核心修改目录**: `c:\Epilepsy_project\Neurolib_desktop\Neurolib_package\neurolib\models\wendling\`  
**创建日期**: 2025-10-13  
**状态**: 阶段 0 进行中

---

## 📋 项目目标

从**已验证的单节点 Wendling 模型**逐步构建到**全脑多节点网络**，确保：

1. ✅ **节点异质性** (Node Heterogeneity)
   - 每个节点可以有不同的参数（A, B, G, p_mean 等）
   - 参考 ALN 模型的实现方式
   - 避免所有节点完全同步

2. ✅ **合理的功能连接** (Functional Connectivity)
   - Mean |FC| 应在 0.3-0.7 范围（不是 0.99）
   - 有结构连接的节点对应有较高 FC
   - 无结构连接的节点对应有较低 FC

3. ✅ **频率多样性** (Frequency Diversity)
   - 不同节点可以有不同的峰值频率
   - 频率分布标准差 > 1 Hz

4. ✅ **逐步验证** (Incremental Validation)
   - 2 nodes → 6 nodes → 20 nodes → 80 nodes
   - 每个阶段都要验证正确性再继续

---

## 📁 档案管理架构（超详细版）

### **1. 主工作目录：whole_brain_wendling/**

```
whole_brain_wendling/
│
├── README.md                          # 项目快速导览（精简版，指向 PLAN.md）
├── PLAN.md                           # 本档案：完整计划
├── PROGRESS.md                       # 实时进度追踪（每天更新）
│
├── Validation_for_single_node/       # ✅ 已完成的单节点验证
│   ├── test_six_types_strict.py     # 6种活动类型测试
│   ├── Guideline.txt                # 验证指南
│   └── waveforms.txt                # 波形说明
│
├── tests/                            # 所有测试脚本（按阶段组织）
│   │
│   ├── 1_single_node/               # 阶段1：单节点（已完成）
│   │   └── COMPLETED.md             # 标记为已完成
│   │
│   ├── 2_six_nodes/                 # 阶段2：6节点网络
│   │   ├── README.md                # 本阶段说明
│   │   ├── test_01_basic_coupling.py       # 测试1：基础耦合
│   │   ├── test_02_delay_effect.py         # 测试2：延迟效应
│   │   ├── test_03_heterogeneity.py        # 测试3：异质性参数
│   │   └── test_04_complete_analysis.py    # 测试4：完整分析
│   │
│   ├── 3_twenty_nodes/              # 阶段3：20节点模块化网络
│   │   ├── README.md
│   │   ├── test_01_modular_structure.py    # 测试1：模块化结构
│   │   └── test_02_community_detection.py  # 测试2：社区检测
│   │
│   ├── 4_hcp_data/                  # 阶段4：HCP真实数据
│   │   ├── README.md
│   │   ├── data/                    # 数据档案（SC, Dmat）
│   │   │   ├── hcp_80_Cmat.npy
│   │   │   └── hcp_80_Dmat.npy
│   │   └── test_01_hcp_validation.py
│   │
│   └── utils/                       # 共用工具函数
│       ├── __init__.py
│       ├── analysis_tools.py        # FC, PSD 计算等
│       ├── plotting_tools.py        # 绘图函数
│       └── network_generators.py    # 网络生成器
│
├── results/                          # 所有结果图片（按阶段+日期）
│   │
│   ├── single_node/                 
│   │   └── six_types_validated_2025-10-13.png  # 已完成
│   │
│   ├── six_nodes/                   
│   │   ├── 01_basic_coupling_2025-10-XX.png
│   │   ├── 02_delay_effect_2025-10-XX.png
│   │   ├── 03_heterogeneity_2025-10-XX.png
│   │   └── 04_complete_analysis_2025-10-XX.png
│   │
│   ├── twenty_nodes/
│   │   └── 01_modular_structure_2025-10-XX.png
│   │
│   └── hcp_data/
│       └── 01_hcp_validation_2025-10-XX.png
│
├── docs/                             # 文档与分析报告
│   │
│   ├── 01_ANALYSIS_ALN_vs_WENDLING.md      # ALN vs Wendling 差异分析
│   ├── 02_IMPLEMENTATION_DETAILS.md        # 实现细节
│   ├── 03_VALIDATION_RESULTS.md            # 各阶段验证结果
│   ├── 04_KEY_FINDINGS.md                  # 关键发现与问题
│   └── 05_REFERENCES.md                    # 参考文献与链接
│
├── original_papers/                  # ✅ 参考论文（已有）
│   └── (保持原样)
│
└── archive/                          # 归档（仅保留重要的失败案例）
    └── failed_attempts/             # 记录失败的尝试（供参考）
        └── README.md                # 说明为什么失败
```

---

### **2. 核心代码修改目录：neurolib/models/wendling/**

```
Neurolib_package/neurolib/models/wendling/
│
├── __init__.py                      # 模型导出
├── model.py                         # ✏️ 需要小幅修改
├── loadDefaultParams.py             # ✏️ 需要大幅修改（核心）
├── timeIntegration.py               # ✏️ 需要大幅修改（核心）
│
└── __pycache__/                     # 自动生成（忽略）
```

**修改计划**：
- `loadDefaultParams.py`: 支持向量化参数（每个节点不同）
- `timeIntegration.py`: 修改 `_integrate_wendling_unified()` 支持节点异质性
- `model.py`: 增加便利方法（如 `set_heterogeneous_params()`）

---

### **3. 参考目录：neurolib/examples/**

```
examples/
├── example-0-aln-minimal.ipynb              # ⭐ ALN 基础用法
├── example-1.2-brain-network-exploration.ipynb  # ⭐ 全脑网络探索
└── example-2.2-evolution-brain-network-aln-resting-state-fit.ipynb  # ⭐ FC 拟合
```

**用途**：
- 遇到问题时参考这些范例
- 了解如何设置多节点网络
- 学习 FC 分析方法

---

## 📝 档案命名规范

### **测试脚本命名**
格式：`test_{序号}_{功能描述}.py`

例子：
- `test_01_basic_coupling.py`
- `test_02_delay_effect.py`
- `test_03_heterogeneity.py`

### **结果图片命名**
格式：`{序号}_{描述}_{日期}.png`

例子：
- `01_basic_coupling_2025-10-13.png`
- `02_delay_effect_2025-10-14.png`

### **文档命名**
格式：`{序号}_{全大写标题}.md`

例子：
- `01_ANALYSIS_ALN_vs_WENDLING.md`
- `02_IMPLEMENTATION_DETAILS.md`

---

## 🗑️ 档案清理规则

### **要删除的档案**
1. ❌ 重复的测试脚本（保留最新版本）
2. ❌ 过时的结果图片（超过3天且已被新版本取代）
3. ❌ 临时测试档案（`temp_*.py`, `test_*.py` 如果已完成）
4. ❌ 无用的 `.md` 档案（内容已合并到主文档）

### **要保留的档案**
1. ✅ 所有 `README.md` 和 `PLAN.md`
2. ✅ 最终验证结果图片
3. ✅ 关键发现的文档
4. ✅ 失败案例（如果有学习价值）

### **清理时机**
- 每完成一个阶段后，清理该阶段的临时档案
- 每天工作结束前，删除明显的临时档案

---

## 🔧 技术实现计划

### **阶段 0: 架构规划与档案整理** ⏳ 进行中

#### **任务清单**
- [x] 分析 ALN vs Wendling 差异
- [x] 制定详细档案架构
- [ ] 创建所有必要的资料夹
- [ ] 编写 README.md
- [ ] 编写 PLAN.md（本档案）
- [ ] 编写 PROGRESS.md

#### **输出档案**
- `whole_brain_wendling/README.md`
- `whole_brain_wendling/PLAN.md` ⭐
- `whole_brain_wendling/PROGRESS.md`
- `whole_brain_wendling/docs/01_ANALYSIS_ALN_vs_WENDLING.md`

#### **验收标准**
- ✅ 档案结构清晰
- ✅ 每个资料夹有 README 说明用途
- ✅ 计划档案详细且可执行

---

### **阶段 1: 实现节点异质性参数** 🎯 核心

#### **问题分析**

当前 Wendling 模型的参数是**标量**（单一值），所有节点使用相同参数：
```python
# 当前实现（问题）
params.A = 5.0        # 标量
params.B = 25.0       # 标量
params.G = 15.0       # 标量
```

ALN 模型的参数是**向量**（每个节点一个值）：
```python
# ALN 实现（目标）
params.mue_ou = params.mue_ext_mean * np.ones((params.N,))  # 形状 (N,)
```

**目标**：让 Wendling 支持向量化参数。

---

#### **修改 1: loadDefaultParams.py**

**位置**: `neurolib/models/wendling/loadDefaultParams.py`

**修改内容**：

1. **增加 `heterogeneity` 参数**：
```python
def loadDefaultParams(Cmat=None, Dmat=None, seed=None, 
                     sigmoid_type="wendling2002", 
                     random_init=True,
                     heterogeneity=0.0):  # 新增参数
    """
    :param heterogeneity: 节点异质性程度（0.0 = 无异质性，0.1 = 10%变异）
    """
```

2. **参数向量化**：
```python
# 基础参数（保持标量作为基准值）
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
    # 单节点或无异质性：使用标量（向后兼容）
    params.A = A_base
    params.B = B_base
    params.G = G_base
    params.p_mean = 90.0
```

3. **同时支持手动设置**：
```python
# 用户可以在创建模型后手动设置
model = WendlingModel(Cmat=Cmat)
model.params['B'] = np.array([50, 40, 30, 20, 25, 35])  # 手动指定
```

---

#### **修改 2: timeIntegration.py**

**位置**: `neurolib/models/wendling/timeIntegration.py`

**函数**: `_integrate_wendling_unified()`

**修改内容**：

1. **接受向量化参数**：
```python
@njit(cache=True, fastmath=True)
def _integrate_wendling_unified(y0_arr, n_steps, dt, N,
                                 A, a, B, b, G, g,  # 这些可能是标量或向量
                                 C, C1, C2, C3, C4, C5, C6, C7,
                                 e0, v0, r, p_mean, p_sigma,
                                 Cmat, K_gl, Dmat_ndt, max_delay):
    
    # 参数标准化（确保都是向量）
    A_vec = np.atleast_1d(A) if np.ndim(A) == 0 else A
    B_vec = np.atleast_1d(B) if np.ndim(B) == 0 else B
    G_vec = np.atleast_1d(G) if np.ndim(G) == 0 else G
    p_mean_vec = np.atleast_1d(p_mean) if np.ndim(p_mean) == 0 else p_mean
    
    # 如果是标量，扩展到所有节点
    if len(A_vec) == 1 and N > 1:
        A_vec = np.full(N, A_vec[0])
        B_vec = np.full(N, B_vec[0])
        G_vec = np.full(N, G_vec[0])
        p_mean_vec = np.full(N, p_mean_vec[0])
```

2. **在循环中使用节点特定参数**：
```python
for node in range(N):
    # 使用该节点的参数
    A_node = A_vec[node]
    B_node = B_vec[node]
    G_node = G_vec[node]
    p_mean_node = p_mean_vec[node]
    
    # 噪声
    xi_t = np.random.normal(0.0, 1.0)
    p_t = p_mean_node + p_sigma * xi_t * np.sqrt(dt)  # 使用节点特定的 p_mean
    
    # ... 其余代码使用 A_node, B_node, G_node ...
    dy0 = y5
    dy5 = A_node * a * (...) - 2.0 * a * y5 - a * a * y0_
    # ...
```

---

#### **修改 3: model.py（可选，增加便利方法）**

**位置**: `neurolib/models/wendling/model.py`

**新增方法**：
```python
def set_heterogeneous_params(self, param_name, values):
    """
    设置节点异质性参数的便利方法。
    
    :param param_name: 参数名称（'A', 'B', 'G', 'p_mean'）
    :param values: 数组或列表，长度必须等于节点数 N
    """
    if len(values) != self.params['N']:
        raise ValueError(f"values 长度 ({len(values)}) 必须等于节点数 ({self.params['N']})")
    self.params[param_name] = np.array(values)

def get_heterogeneity_summary(self):
    """
    返回参数异质性的总结。
    """
    summary = {}
    for param in ['A', 'B', 'G', 'p_mean']:
        val = self.params.get(param)
        if isinstance(val, np.ndarray) and len(val) > 1:
            summary[param] = {
                'mean': np.mean(val),
                'std': np.std(val),
                'min': np.min(val),
                'max': np.max(val),
                'cv': np.std(val) / np.mean(val)  # 变异系数
            }
        else:
            summary[param] = {'value': val, 'type': 'scalar'}
    return summary
```

---

#### **验证测试**

**测试档案**: `tests/2_six_nodes/test_03_heterogeneity.py`

**测试内容**：
1. 创建 6 节点网络，每个节点不同 B 参数
2. 运行模拟
3. 验证：
   - 每个节点的峰值频率不同
   - Mean |FC| < 0.9
   - 节点活动有明显差异

**成功标准**：
- ✅ 峰值频率标准差 > 1 Hz
- ✅ Mean |FC| 在 0.3-0.7 范围
- ✅ 视觉检查：时间序列明显不同

---

#### **输出档案**
- `neurolib/models/wendling/loadDefaultParams.py` (修改)
- `neurolib/models/wendling/timeIntegration.py` (修改)
- `neurolib/models/wendling/model.py` (修改)
- `tests/2_six_nodes/test_03_heterogeneity.py` (新建)
- `docs/02_IMPLEMENTATION_DETAILS.md` (新建)

---

### **阶段 2: 6-nodes 网络验证**

#### **测试 2.1: 基础耦合**
**档案**: `tests/2_six_nodes/test_01_basic_coupling.py`

**内容**：
- 2 个节点
- 测试 K_gl = 0 vs K_gl = 0.5
- 验证耦合确实影响活动

**验证**：
- K_gl = 0 时，两个节点完全独立
- K_gl > 0 时，两个节点有相关性

---

#### **测试 2.2: 延迟效应**
**档案**: `tests/2_six_nodes/test_02_delay_effect.py`

**内容**：
- 2 个节点
- 测试不同距离（Dmat）的影响

**验证**：
- 距离远 → 延迟大 → 相位差明显

---

#### **测试 2.3: 异质性参数**
**档案**: `tests/2_six_nodes/test_03_heterogeneity.py`

**内容**：
- 6 个节点
- 每个节点不同 B 参数

**验证**：
- 频率多样性
- FC 合理

---

#### **测试 2.4: 完整分析**
**档案**: `tests/2_six_nodes/test_04_complete_analysis.py`

**内容**：
- Activity + PSD + FC + SC 对比

**输出**：
- 4x3 网格图片

---

### **阶段 3: 20-nodes 模块化网络**

#### **网络设计**
- 4 个模块，每个 5 个节点
- 模块内密度: 0.8
- 模块间密度: 0.2

#### **测试内容**
- 验证模块化结构
- 社区检测

---

### **阶段 4: 80-nodes HCP 数据**

#### **数据来源**
- 使用 neurolib 提供的数据集
- 或从 HCP 下载

#### **测试内容**
- 真实 SC/Dmat
- FC 拟合

---

## 📊 验证标准总结

### **全局标准（所有阶段）**

| 指标 | 合格标准 | 优秀标准 |
|------|---------|---------|
| Mean \|FC\| | 0.3 - 0.8 | 0.4 - 0.6 |
| FC 标准差 | > 0.1 | > 0.15 |
| 峰值频率 std | > 1 Hz | > 2 Hz |
| SC-FC 相关性 | > 0.2 | > 0.4 |

### **节点活动标准**

| 特性 | 合格标准 |
|------|---------|
| 振幅范围 | -10 to +10 mV |
| 主导频率 | 1-20 Hz |
| 无发散 | 振幅不超过 ±50 mV |

---

## 🚨 调试与问题解决

### **遇到问题时的检查清单**

1. **模型不收敛/发散**
   - [ ] 检查 dt 是否太大（建议 dt = 0.1）
   - [ ] 检查参数是否在合理范围
   - [ ] 检查初始条件是否合理

2. **FC 过高（> 0.9）**
   - [ ] 增加节点异质性（heterogeneity = 0.1 - 0.2）
   - [ ] 检查是否所有节点参数相同
   - [ ] 降低全局耦合 K_gl

3. **FC 过低（< 0.1）**
   - [ ] 增加全局耦合 K_gl
   - [ ] 检查 Cmat 是否正确
   - [ ] 检查模拟时间是否够长

4. **节点活动完全相同**
   - [ ] 检查参数是否为向量（不是标量）
   - [ ] 检查初始条件是否有差异
   - [ ] 检查 random seed 是否正确设置

### **参考资源**

1. **Neurolib Examples**
   - `example-0-aln-minimal.ipynb`
   - `example-1.2-brain-network-exploration.ipynb`

2. **文献搜寻关键词**
   - "whole brain modeling heterogeneity"
   - "neural mass model network synchronization"
   - "functional connectivity structural connectivity"

3. **在线资源**
   - Neurolib 文档: https://github.com/neurolib-dev/neurolib
   - 神经动力学论坛

---

## 📅 时间表与里程碑

### **预估时间**

| 阶段 | 任务 | 预估时间 | 累计时间 |
|------|------|---------|----------|
| 0 | 架构与文档 | 1小时 | 1h |
| 1 | 实现异质性 | 3小时 | 4h |
| 2 | 6-nodes 验证 | 2小时 | 6h |
| 3 | 20-nodes 验证 | 1.5小时 | 7.5h |
| 4 | 80-nodes HCP | 2小时 | 9.5h |
| - | 缓冲时间 | 2.5小时 | 12h |

**总计**: 约 12 小时（1.5 天）

### **里程碑**

- **M1** (阶段0完成): 档案结构建立，文档完成
- **M2** (阶段1完成): 节点异质性实现，单元测试通过
- **M3** (阶段2完成): 6-nodes 所有测试通过
- **M4** (阶段3完成): 20-nodes 模块化验证通过
- **M5** (阶段4完成): HCP 数据验证完成

---

## ✅ 下一步行动

**立即执行**（阶段 0）：

1. [ ] 创建所有必要的资料夹结构
2. [ ] 编写 `README.md`
3. [ ] 编写 `PROGRESS.md`
4. [ ] 编写 `docs/01_ANALYSIS_ALN_vs_WENDLING.md`
5. [ ] 清理不必要的档案

**等待确认后执行**（阶段 1）：

- 修改 `loadDefaultParams.py`
- 修改 `timeIntegration.py`
- 创建测试脚本

---

## 📝 备注

- **修改原则**: 最小化修改，保持向后兼容
- **测试原则**: 先简单后复杂，逐步验证
- **文档原则**: 记录所有关键决策和发现

---

**计划版本**: v1.0  
**最后更新**: 2025-10-13 22:06  
**下次更新**: 完成阶段 0 后
