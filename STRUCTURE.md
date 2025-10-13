# 完整档案结构总览

**最后更新**: 2025-10-13 22:10  
**状态**: ✅ 阶段 0 完成

---

## 📁 完整目录树

```
whole_brain_wendling/
│
├── 📄 README.md                              # 项目快速导览 (133 行)
├── 📄 PLAN.md                                # 完整实施计划 (800+ 行) ⭐
├── 📄 PROGRESS.md                            # 实时进度追踪 (200+ 行)
├── 📄 STRUCTURE.md                           # 本档案：完整结构总览
│
├── 📂 Validation_for_single_node/           # ✅ 已完成的单节点验证
│   ├── test_six_types_strict.py            # 6种活动类型测试 (302 行)
│   ├── Guideline.txt                       # 验证指南
│   └── waveforms.txt                       # 波形说明
│
├── 📂 tests/                                # 所有测试脚本（按阶段组织）
│   │
│   ├── 📂 2_six_nodes/                      # 阶段2：6节点网络
│   │   ├── README.md                       # 阶段说明 (200+ 行)
│   │   ├── test_01_basic_coupling.py       # 测试1：基础耦合 (待创建)
│   │   ├── test_02_delay_effect.py         # 测试2：延迟效应 (待创建)
│   │   ├── test_03_heterogeneity.py        # 测试3：异质性参数 (待创建)
│   │   └── test_04_complete_analysis.py    # 测试4：完整分析 (待创建)
│   │
│   ├── 📂 3_twenty_nodes/                   # 阶段3：20节点模块化网络
│   │   ├── README.md                       # 阶段说明
│   │   ├── test_01_modular_structure.py    # 测试1：模块化结构 (待创建)
│   │   └── test_02_community_detection.py  # 测试2：社区检测 (待创建)
│   │
│   ├── 📂 4_hcp_data/                       # 阶段4：HCP真实数据
│   │   ├── README.md                       # 阶段说明
│   │   ├── 📂 data/                        # 数据档案 (待下载)
│   │   │   ├── hcp_80_Cmat.npy            # SC 矩阵
│   │   │   └── hcp_80_Dmat.npy            # 距离矩阵
│   │   └── test_01_hcp_validation.py       # HCP验证 (待创建)
│   │
│   └── 📂 utils/                            # ✅ 共用工具函数
│       ├── __init__.py                     # 模块初始化 (37 行)
│       ├── analysis_tools.py               # FC, PSD, 模块性计算 (140 行)
│       ├── plotting_tools.py               # 标准化绘图函数 (130 行)
│       └── network_generators.py           # 网络生成器 (160 行)
│
├── 📂 results/                              # 所有结果图片（按阶段+日期）
│   ├── 📂 single_node/                     
│   │   └── (单节点验证结果)
│   ├── 📂 six_nodes/                       
│   │   └── (6节点测试结果，待生成)
│   ├── 📂 twenty_nodes/
│   │   └── (20节点测试结果，待生成)
│   └── 📂 hcp_data/
│       └── (HCP数据结果，待生成)
│
├── 📂 docs/                                 # 文档与分析报告
│   ├── 01_ANALYSIS_ALN_vs_WENDLING.md      # ✅ ALN vs Wendling 差异分析 (300+ 行)
│   ├── 02_IMPLEMENTATION_DETAILS.md        # 实现细节 (待创建)
│   ├── 03_VALIDATION_RESULTS.md            # 验证结果 (待创建)
│   ├── 04_KEY_FINDINGS.md                  # 关键发现 (待创建)
│   └── 05_REFERENCES.md                    # 参考文献 (待创建)
│
└── 📂 original_papers/                      # ✅ 参考论文
    └── (5篇 PDF 文档)
```

---

## 📊 档案统计

### **已创建的档案**

| 类型 | 数量 | 详情 |
|------|------|------|
| Markdown 文档 | 10 | README, PLAN, PROGRESS, STRUCTURE + 各阶段 README + 技术分析 |
| Python 模块 | 4 | utils 下的 4 个工具模块 |
| 资料夹 | 11 | tests (4个) + results (4个) + docs + utils + data |
| 代码行数 | ~500 | utils 工具函数 |
| 文档行数 | ~2000 | 所有 Markdown 文档 |

### **待创建的档案**

| 阶段 | 测试脚本数 | 文档数 |
|------|----------|--------|
| 阶段 1 | 1 (单元测试) | 1 (实现细节) |
| 阶段 2 | 4 (6-nodes) | 1 (验证报告) |
| 阶段 3 | 2 (20-nodes) | 0 |
| 阶段 4 | 1 (HCP) | 2 (发现+参考) |

---

## 🎯 核心档案说明

### **必读档案** ⭐

1. **PLAN.md** (800+ 行)
   - 完整的实施计划
   - 详细的档案架构说明
   - 每个阶段的任务清单
   - 验证标准和成功指标
   - 修改代码的具体位置和方法

2. **README.md** (133 行)
   - 项目快速导览
   - 目录结构概览
   - 进度总览
   - 常见问题

3. **docs/01_ANALYSIS_ALN_vs_WENDLING.md** (300+ 行)
   - ALN 和 Wendling 模型的详细对比
   - 参数向量化的实现方法
   - 具体的代码修改示例
   - 验证测试方法

### **工具函数** 🔧

4. **tests/utils/analysis_tools.py**
   - `compute_fc()`: 计算功能连接矩阵
   - `compute_psd()`: 计算功率谱密度
   - `extract_peak_frequency()`: 提取峰值频率
   - `compute_modularity()`: 计算模块性指数
   - `compute_fc_statistics()`: FC 统计指标

5. **tests/utils/plotting_tools.py**
   - `plot_timeseries()`: 绘制多节点时间序列
   - `plot_psd()`: 绘制功率谱密度
   - `plot_fc_matrix()`: 绘制 FC 矩阵
   - `plot_sc_fc_comparison()`: SC vs FC 对比

6. **tests/utils/network_generators.py**
   - `create_modular_network()`: 创建模块化网络
   - `create_random_network()`: 创建随机网络
   - `create_ring_network()`: 创建环形网络
   - `create_small_world_network()`: 创建小世界网络
   - `create_distance_matrix()`: 创建距离矩阵

---

## 📝 档案命名规范

### **测试脚本**
```
格式: test_{序号}_{功能描述}.py
例子: test_01_basic_coupling.py
      test_02_delay_effect.py
```

### **结果图片**
```
格式: {序号}_{描述}_{日期}.png
例子: 01_basic_coupling_2025-10-13.png
      02_delay_effect_2025-10-14.png
```

### **文档**
```
格式: {序号}_{全大写标题}.md
例子: 01_ANALYSIS_ALN_vs_WENDLING.md
      02_IMPLEMENTATION_DETAILS.md
```

---

## 🗂️ 档案用途速查

### **我想了解...**

| 问题 | 查看档案 |
|------|---------|
| 项目总体规划 | `PLAN.md` |
| 当前进度 | `PROGRESS.md` |
| 快速开始 | `README.md` |
| 档案结构 | `STRUCTURE.md` (本档案) |
| ALN vs Wendling 差异 | `docs/01_ANALYSIS_ALN_vs_WENDLING.md` |
| 阶段 2 测试内容 | `tests/2_six_nodes/README.md` |
| 如何计算 FC | `tests/utils/analysis_tools.py` |
| 如何绘制图片 | `tests/utils/plotting_tools.py` |
| 如何生成网络 | `tests/utils/network_generators.py` |

---

## 🔄 档案更新流程

### **每完成一个阶段**

1. 更新 `PROGRESS.md`:
   - 标记任务完成
   - 更新进度条
   - 记录完成日期

2. 更新 `README.md`:
   - 更新进度表
   - 更新下一步行动

3. 创建结果档案:
   - 保存图片到 `results/{阶段}/`
   - 命名包含日期

4. 编写总结文档（如需要）:
   - 保存到 `docs/`

### **每天工作结束**

1. 更新 `PROGRESS.md`:
   - 添加每日记录
   - 更新时间统计

2. 检查档案:
   - 删除临时档案
   - 整理结果图片

---

## 🗑️ 档案清理规则

### **可以删除的档案**

- ❌ `temp_*.py` (临时测试档案)
- ❌ `test_*.py` (已完成且不再需要的测试)
- ❌ `*_old.md` (旧版本文档)
- ❌ 重复的结果图片（保留最新版本）

### **必须保留的档案**

- ✅ 所有 `README.md` 和 `PLAN.md`
- ✅ `PROGRESS.md` (唯一进度追踪)
- ✅ 最终验证结果图片
- ✅ `docs/` 下的技术文档
- ✅ `utils/` 下的工具函数

---

## 📊 当前状态总结

### **阶段 0: 架构规划** ✅ 已完成

**已创建**:
- ✅ 10 个 Markdown 文档
- ✅ 4 个 Python 工具模块
- ✅ 11 个资料夹
- ✅ 完整的档案架构

**验收**:
- ✅ 档案结构清晰
- ✅ 每个资料夹有说明
- ✅ 计划详细可执行
- ✅ 工具函数可复用

### **下一步: 阶段 1** ⏳

**任务**:
- 修改 `loadDefaultParams.py`
- 修改 `timeIntegration.py`
- 创建单元测试

**预估时间**: 3 小时

---

## 🎓 使用指南

### **新手入门**

1. 先读 `README.md` 了解项目概况
2. 再读 `PLAN.md` 了解详细计划
3. 查看 `docs/01_ANALYSIS_ALN_vs_WENDLING.md` 了解技术细节
4. 开始执行阶段 1

### **日常工作**

1. 查看 `PROGRESS.md` 确认当前进度
2. 查看对应阶段的 `README.md` 了解任务
3. 使用 `utils/` 下的工具函数
4. 完成后更新 `PROGRESS.md`

### **遇到问题**

1. 查看 `PLAN.md` 的"调试与问题解决"章节
2. 查看对应阶段 `README.md` 的"常见问题"
3. 参考 `neurolib/examples/` 的范例
4. 搜寻相关文献

---

**本档案版本**: v1.0  
**最后更新**: 2025-10-13 22:10  
**下次更新**: 阶段 1 开始时
