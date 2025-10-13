# Two Parameter Systems - Critical Distinction

**Created**: 2025-10-14 00:01  
**Importance**: 🔴 CRITICAL - Must understand before using parameters

---

## ⚠️ WARNING: Two INCOMPATIBLE Parameter Systems

Wendling 模型中有**两套完全不同**的参数系统，**不可混用**！

---

## 📋 System 1: Wendling 2002 Activity Types

### Purpose
研究不同的神经活动模式（single-node validation）

### Parameter Range
**Wide range: B = 5-50, G = 0-25**

### Activity Types

| Type | B | G | 频率 | 描述 | 机制 |
|------|---|---|------|------|------|
| Type 1 | **50** | 15 | 1-7 Hz | Background slow | **高慢抑制** → 压制快振荡 |
| Type 2 | **40** | 15 | 1-5 Hz | Sporadic spikes | 强抑制 + 偶尔突破 |
| Type 3 | **25** | 15 | 3-6 Hz | SWD (epileptic) | **中等抑制** → 矛盾性SWD |
| Type 4 | **10** | 15 | 8-13 Hz | Alpha rhythm | **低慢抑制** → alpha振荡 |
| Type 5 | **5** | 25 | 10-20 Hz | LVFA | 极低慢抑制 + 高快抑制 |
| Type 6 | **15** | 0 | 9-13 Hz | Quasi-sinusoidal | 无快抑制 |

### Key Insight

**B参数的意义**: Slow inhibitory gain (GABA_B)

- **B ↑ (高)**: 强慢抑制 → 压制振荡 → **慢波**
- **B ↓ (低)**: 弱慢抑制 → 允许振荡 → **快波/alpha**

**这是counter-intuitive的！**

### Usage
```python
from STANDARD_PARAMETERS import WENDLING_STANDARD_PARAMS

# Single-node testing
params = WENDLING_STANDARD_PARAMS['Type4']
model.params['B'] = params['params']['B']  # 10
model.params['G'] = params['params']['G']  # 15
```

### 验证状态
✅ Single-node verified  
✅ Multi-node verified (het=0, K_gl=0)

---

## 📋 System 2: Whole-Brain Heterogeneity

### Purpose
创建节点间的参数多样性，避免过度同步

### Parameter Range
**Narrow range: B = 15-29 (with het=0.3)**

```python
B_base = 22.0
G_base = 18.0
heterogeneity = 0.30

# Result:
B_range = B_base * (1 ± heterogeneity)
        = 22.0 * (1 ± 0.30)
        = [15.4, 28.6]
```

### Purpose of Each Node
**Not specific activity types!** 只是增加多样性：
- 每个节点有不同的 B, G 值
- 目的：避免所有节点完全相同 → 避免 FC ≈ 1.0
- **不是为了复现 Type 1-6**

### Usage
```python
model = WendlingModel(Cmat=Cmat, Dmat=Dmat, 
                     heterogeneity=0.30)  # Diverse parameters
model.params['K_gl'] = 0.15  # Coupling
model.run()
```

### What You Get
- 节点参数在 15-29 范围内随机分布
- 创建 FC 多样性
- **不对应任何 Wendling activity type**

---

## 🚨 THE CRITICAL DIFFERENCE

### B=50 的意义

| System | B=50 的意义 | 为什么 |
|--------|------------|--------|
| **Wendling 2002** | ✅ Background (慢波) | 高慢抑制 → 压制快振荡 |
| **Heterogeneity** | ❌ Epileptic? | 错！不在 15-29 范围内 |

### B=10 的意义

| System | B=10 的意义 | 为什么 |
|--------|------------|--------|
| **Wendling 2002** | ✅ Alpha rhythm | 低慢抑制 → alpha振荡 |
| **Heterogeneity** | ❌ Background? | 错！这只是范围下限附近 |

### B=25 的意义

| System | B=25 的意义 | 为什么 |
|--------|------------|--------|
| **Wendling 2002** | ✅ SWD (epileptic) | 中等抑制的矛盾效应 |
| **Heterogeneity** | ❌ Normal? | 错！这是heterogeneity的上限 |

---

## ❌ WRONG: Mixing the Systems

### 错误示例 1

```python
# ❌ 错！试图在 heterogeneity 系统中分类 Wendling types
model = WendlingModel(heterogeneity=0.30)  # B range: 15-29
model.run()

# 然后用这样的逻辑：
if B < 20:
    print("Type 1 Background")  # ❌ 错！
elif B < 28:
    print("Type 2 Normal")      # ❌ 错！
```

**为什么错？**
- Heterogeneity 的 B 范围 (15-29) 不对应任何 Wendling type
- Type 1 是 B=50，不是 B<20
- Type 4 是 B=10，不是 B<20

### 错误示例 2

```python
# ❌ 错！在 whole-brain 网络中使用 Wendling types
model = WendlingModel(Cmat=Cmat, heterogeneity=0.0)
model.params['B'] = np.array([50, 40, 25, 10, 5, 15])  # Wendling types
model.params['K_gl'] = 0.15  # With coupling
model.run()
```

**为什么可能有问题？**
- Wendling types 是为 single-node validation 设计的
- 在网络中with coupling，行为可能不同
- B=50 (background) 可能因coupling变成其他pattern

---

## ✅ CORRECT Usage

### Use Case 1: Validate Multi-Node Implementation

**Goal**: Verify multi-node = single-node  
**System**: **Wendling 2002 types**

```python
# Use STANDARD_PARAMETERS
model = WendlingModel(heterogeneity=0.0)  # No diversity
model.params['B'] = 10  # Type 4
model.params['G'] = 15
model.params['K_gl'] = 0.0  # No coupling
model.run()

# Should match single-node result ✅
```

### Use Case 2: Whole-Brain Network with Diversity

**Goal**: Realistic FC, avoid over-synchronization  
**System**: **Heterogeneity**

```python
# Use heterogeneity system
model = WendlingModel(Cmat=Cmat, Dmat=Dmat,
                     heterogeneity=0.30)
model.params['K_gl'] = 0.15
model.run()

# DON'T classify as "Type 1, 2, 3" ❌
# Just say "diverse parameters" ✅
```

### Use Case 3: Six Types Demo (Educational)

**Goal**: Show different Wendling patterns  
**System**: **Wendling 2002 types**  
**Context**: Educational, not for realistic brain modeling

```python
# Manually assign types
model = WendlingModel(heterogeneity=0.0)
B_vals = [50, 40, 25, 10, 5, 15]  # Each node a type
model.params['B'] = B_vals
model.params['K_gl'] = 0.05  # Weak coupling to preserve patterns
model.run()

# This is OK for demonstration ✅
# But not a "realistic" brain network
```

---

## 📊 Summary Table

| Aspect | Wendling 2002 Types | Heterogeneity |
|--------|---------------------|---------------|
| **B range** | 5-50 (wide) | 15-29 (narrow) |
| **Purpose** | Study activity patterns | Create node diversity |
| **Context** | Single-node validation | Whole-brain networks |
| **B=50** | Background slow waves | Outside range |
| **B=10** | Alpha rhythm | Lower end of range |
| **B=25** | Epileptic SWD | Upper end of range |
| **Compatibility** | ❌ **NOT compatible** | ❌ **NOT compatible** |
| **Classification** | By B value | ❌ Cannot classify by B |

---

## 🎯 Recommendations

### For Single-Node Testing
✅ Use **Wendling 2002 parameters** from `STANDARD_PARAMETERS.py`  
✅ Can classify as Type 1-6  
✅ Reference: `Validation_for_single_node/test_six_types_strict.py`

### For Whole-Brain Networks
✅ Use **heterogeneity system**  
❌ **DO NOT classify as Type 1-6**  
✅ Describe as "diverse/heterogeneous parameters"  
✅ Focus on FC, SC-FC correlation, etc.

### For Network with Six Types (Demo)
⚠️ Use **Wendling parameters** but:
- Keep coupling low (K_gl < 0.10)
- Educational purpose only
- Not realistic brain modeling
- Clearly label as "demonstration"

---

## 🛠️ How to Fix Existing Code

### Problem: `classify_activity_type()` in test_03

```python
# ❌ WRONG - Uses heterogeneity ranges
def classify_activity_type(signal, freq, B, G):
    if B < 20:
        return "Type 1 (Background)"  # Wrong!
```

### Solution 1: Remove Classification
```python
# Just report parameters, don't classify
print(f"Node {i}: B={B:.2f}, G={G:.2f}, freq={freq:.1f}Hz")
```

### Solution 2: Classify by Frequency
```python
def classify_by_frequency(freq):
    if freq < 4:
        return "Slow wave activity"
    elif 4 <= freq < 8:
        return "Theta range"
    elif 8 <= freq <= 13:
        return "Alpha/beta range"
    else:
        return "Fast activity"
```

### Solution 3: Rename to Avoid Confusion
```python
def classify_heterogeneity_range(B):
    """
    NOTE: This is NOT Wendling activity types!
    Just describes position in heterogeneity range.
    """
    if B < B_base * 0.85:
        return "Lower heterogeneity range"
    elif B < B_base * 1.15:
        return "Near baseline"
    else:
        return "Upper heterogeneity range"
```

---

## 📚 References

1. **Wendling 2002 parameters**: `Validation_for_single_node/STANDARD_PARAMETERS.py`
2. **Heterogeneity implementation**: `neurolib/models/wendling/loadDefaultParams.py`
3. **Bug report**: `CRITICAL_BUG_REPORT.md`

---

**Key Takeaway**: 
# 两套系统完全不兼容！
# 使用前必须明确你在用哪一套！

---

**Created**: 2025-10-14 00:01  
**Status**: 🔴 CRITICAL DOCUMENTATION  
**Action**: Read before using any parameters!
