# 🚨 CRITICAL BUG REPORT - Activity Type Classification

**发现时间**: 2025-10-14 00:01  
**发现者**: User observation  
**严重程度**: 🔴 **CRITICAL** - 所有 activity type 诊断结果都是错误的

---

## 🐛 Bug 描述

### 用户观察
> "我懷疑你新的 six-node network 參數使用錯誤，現在變成全部看起來都是 background，
> 然後你的偵測activity 的結果也都是錯誤的"

### Root Cause

**在 `test_03_complete_analysis.py` 中使用了错误的分类标准**

#### ❌ 我使用的（错误）
```python
def classify_activity_type(signal, freq, B, G):
    """
    Type 1 (Background): B=10-20, G=5-10, ~2-4 Hz      ← 错！
    Type 2 (Normal): B=20-30, G=10-20, ~8-13 Hz        ← 错！
    Type 3 (Epileptic SWD): B=30-50, G=10-20, ~3-4 Hz  ← 错！
    Type 4 (Low voltage): B=50+, G=20+, high freq      ← 错！
    """
    if B < 20:
        return "Type 1 (Background)", "Low B parameter"
    elif 20 <= B < 28:
        return "Type 2 (Normal)", "Normal B,G range"
    elif 28 <= B < 35:
        return "Type 3 (Epileptic)", "High B + spikes"
    else:
        return "Type 3+ (Strong epileptic)", "Very high B"
```

#### ✅ 正确的 Wendling 2002 参数
```python
# From STANDARD_PARAMETERS.py (已验证)
Type 1 (Background):      B=50, G=15  ← 完全相反！
Type 2 (Sporadic spikes): B=40, G=15
Type 3 (SWD):             B=25, G=15
Type 4 (Alpha-like):      B=10, G=15
Type 5 (LVFA):            B=5,  G=25
Type 6 (Quasi-sinusoidal):B=15, G=0
```

---

## 💣 Impact Analysis

### 受影响的文件

1. **test_03_complete_analysis.py** ❌
   - `classify_activity_type()` 函数完全错误
   - 诊断输出误导性
   
2. **test_02_real_hcp_data.py** ❌
   - 同样使用错误分类
   
3. **所有诊断报告** ❌
   - `DIAGNOSTIC_REPORT.md`
   - `VERIFICATION_REPORT.md`
   - 显示的 "Type 1: 33%, Type 2: 67%" 都是基于错误分类

### 为什么会发生

**混淆了两套不同的参数系统**：

1. **Whole-brain heterogeneity 系统**（我自己推测的）
   ```python
   # 用于 heterogeneity 的参数范围
   B_base = 22.0
   heterogeneity = 0.30
   # → B range: 15-29
   # 我错误地认为：B<20是background, B>28是epileptic
   ```

2. **Wendling 2002 single-node 系统**（正确的）
   ```python
   # 验证通过的 6 种 activity types
   # B 的意义完全不同！
   # B=50 是 background (低频慢波)
   # B=25 是 epileptic (SWD)
   # B=10 是 alpha rhythm
   ```

**关键错误**：我没有意识到这两套系统中 **B 参数的意义是相反的**！

---

## 🔍 具体错误示例

### 示例 1: 6-node network 诊断

**错误输出**（基于我的分类）：
```
Node 0: B=17.22  → "Type 1 (Background)" ✅ 看似正确
Node 1: B=24.15  → "Type 2 (Normal)"     ✅ 看似正确
Node 5: B=25.04  → "Type 2 (Normal)"     ✅ 看似正确
```

**实际情况**（如果用 Wendling 2002 标准）：
```
Node 0: B=17.22  → 接近 Type 4/6 (Alpha/Quasi-sinusoidal)
Node 1: B=24.15  → 接近 Type 3 (SWD)
Node 5: B=25.04  → Type 3 (SWD) 范围
```

**结论**：分类完全不对应！

### 示例 2: test_04_six_types_network.py

**如果使用 heterogeneity 生成的参数** (B: 15-29):
```
所有节点的 B 都在 15-29 之间
→ 用我的错误分类：会显示 Type 1, 2, 3 混合 ✅
→ 用 Wendling 标准：这些都不是任何标准 type ❌
```

**如果使用 STANDARD_PARAMETERS 的参数** (B: 5, 10, 15, 25, 40, 50):
```
Type 1: B=50 → 用我的分类会显示 "Type 3+ Strong epileptic" ❌❌❌
Type 4: B=10 → 用我的分类会显示 "Type 1 Background" ❌❌❌
完全颠倒！
```

---

## 🎯 根本问题

### 两套参数系统是不兼容的！

| Aspect | Whole-Brain Heterogeneity | Wendling 2002 Types |
|--------|--------------------------|---------------------|
| **目的** | 创建多样性，避免过度同步 | 研究不同 activity patterns |
| **B 范围** | 15-29 (narrow) | 5-50 (wide) |
| **B=50** | 🔴 认为是 epileptic | ✅ 是 background |
| **B=10** | 🔴 认为是 background | ✅ 是 alpha rhythm |
| **B=25** | 🔴 认为是 normal | ✅ 是 SWD (epileptic) |
| **兼容性** | ❌ **完全不兼容** | - |

---

## 🛠️ 修复方案

### 选项 1: 分离两套系统 ⭐ 推荐

**A. Whole-Brain Network**
```python
# 使用 heterogeneity 的参数范围
B_base = 22.0
heterogeneity = 0.30
# → 不要分类为 "Type 1, 2, 3"
# → 只说 "diverse parameters" or "node-specific"
```

**B. Six Types Demo**
```python
# 使用 STANDARD_PARAMETERS 的参数
# 明确标注这是 single-node validated types
# 不要混用到 heterogeneity 系统
```

### 选项 2: 删除错误的分类函数

```python
# 删除 classify_activity_type() 
# 或者明确标注：
# "This classification is for heterogeneity-based networks ONLY"
# "NOT the same as Wendling 2002 activity types"
```

### 选项 3: 创建正确的分类

基于 **频率 + 波形特征** 而非 B 值：
```python
def classify_by_frequency(signal, freq):
    if freq < 7:
        return "Slow wave activity"
    elif 8 <= freq <= 13:
        return "Alpha/beta rhythm"
    elif freq > 15:
        return "Fast activity"
```

---

## ✅ 立即行动

### 必须修改的文件

1. **test_03_complete_analysis.py**
   - 删除或修复 `classify_activity_type()`
   - 或者改名为 `classify_by_heterogeneity_range()`
   - 添加警告：不是 Wendling 2002 types

2. **test_02_real_hcp_data.py**
   - 同样的修改

3. **所有诊断报告**
   - 添加澄清说明
   - 或者重新生成结果

### 文档更新

1. **STANDARD_PARAMETERS.py**
   - 添加警告：这些参数用于 single-node validation
   - 不要直接用于 heterogeneity 网络

2. **新文档：PARAMETER_SYSTEMS.md**
   - 解释两套系统的区别
   - 何时使用哪套参数
   - 为什么不兼容

---

## 📊 正确理解

### Wendling 2002 的 B 参数意义

**B = Slow inhibitory gain (GABA_B)**

- **高 B (50)**: 强慢抑制 → 压制快速振荡 → **慢波 background**
- **中 B (25)**: 适中抑制 → 可能出现 → **SWD (paradoxical)**
- **低 B (10)**: 弱慢抑制 → 允许快速振荡 → **Alpha rhythm**
- **很低 B (5)**: 几乎无慢抑制 → **LVFA**

### Whole-Brain Heterogeneity 的 B 参数

**B = Node diversity parameter**

- 目的：创建参数多样性
- 避免所有节点完全相同
- **不是为了复现特定 activity types**
- B 的值范围更窄 (15-29)

---

## 🎓 教训

1. ⚠️ **不要混淆两套参数系统**
2. ⚠️ **验证参数时要用正确的标准**
3. ⚠️ **参数的"意义"在不同上下文可能不同**
4. ⚠️ **single-node 参数 ≠ whole-brain 参数**

---

## 📝 Action Items

- [ ] 修复 test_03_complete_analysis.py 的分类函数
- [ ] 修复 test_02_real_hcp_data.py
- [ ] 重新运行所有测试
- [ ] 更新所有诊断报告
- [ ] 创建 PARAMETER_SYSTEMS.md 说明文档
- [ ] 在 STANDARD_PARAMETERS.py 添加使用警告

---

**报告日期**: 2025-10-14 00:01  
**状态**: 🔴 未修复  
**优先级**: P0 - CRITICAL
