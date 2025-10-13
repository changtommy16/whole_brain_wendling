# Waveform Diversity 问题 - 缺乏 Background & Fluctuation

**用户观察**: 波形太"干净"，都很像，缺乏：
1. Type 1 那种 background slow waves
2. Type 4/5 那种 fluctuation/fast activity
3. 怀疑整体能量太高或太单一

**诊断结果**: ✅ 观察正确！

---

## 🔍 问题分析

### 当前状态（heterogeneity=0.30）

```
Parameter Range:
  B: 15.4 - 28.6  ← 主要集中在 Type 2
  G: 12.6 - 23.4
  
Activity Type Distribution:
  Type 1 (Background, B<18):  ~10-20%  ← 太少！
  Type 2 (Normal, B=18-28):   ~70-80%  ← 占主导
  Type 3 (SWD, B>28):         ~0-10%   ← 几乎没有
  Type 4 (Fast, B>50):        0%       ← 完全没有
```

### 为什么会这样？

我们为了**避免 Type 3 癫痫活动**：
1. 限制了 B < 30
2. 保守的 heterogeneity (0.30)
3. 结果：**大部分节点都在 Type 2 范围**

**但真实大脑应该有多样性**：
- 有些区域是 background (慢波，低能量)
- 有些区域是 active (正常振荡)
- 甚至少量高频 fast activity

---

## 📊 Wendling Activity Types 详解

### Type 1: Background (慢波)
```
Parameters: B = 10-18, G = 5-10
Waveform:
  - 2-4 Hz slow waves
  - Low amplitude (~3-5 mV)
  - Smooth, regular
  - Low energy
  
在大脑中：
  - 休息状态区域
  - Background activity
  - Delta/theta waves
```

### Type 2: Normal (alpha rhythm)
```
Parameters: B = 18-28, G = 12-20
Waveform:
  - 8-13 Hz oscillations
  - Moderate amplitude (~5-10 mV)
  - Regular rhythm
  - Moderate energy
  
在大脑中：
  - 正常清醒状态
  - Alpha/beta rhythm
  - 我们现在大部分节点都是这个
```

### Type 3: Epileptic SWD
```
Parameters: B = 28-50, G = 10-20
Waveform:
  - 3-4 Hz spike-and-wave
  - High amplitude (~15-30 mV)
  - Sharp spikes
  - High energy bursts
  
在大脑中：
  - 癫痫发作
  - 我们特意避免这个
```

### Type 4: Low Voltage Fast
```
Parameters: B = 50+, G = 30+
Waveform:
  - >20 Hz fast activity
  - Low amplitude (~2-4 mV)
  - Irregular, noisy
  - High frequency, low power
  
在大脑中：
  - High frequency oscillations
  - Desynchronized states
  - 我们完全没有这个
```

---

## ✅ 解决方案：增加波形多样性

### 选项 1: 扩大参数范围 ⭐ (推荐)

```python
# In loadDefaultParams.py
B_base = 25.0  # 提高中心值
heterogeneity = 0.50  # 增加到 0.5

# Result:
# B range: 12.5 - 37.5
# → Type 1: B=12-18 (Background)
# → Type 2: B=18-28 (Normal)
# → Type 3: B=28-38 (少量 SWD)
```

**预期分布**：
- Type 1: 20-30% (Background) ✅
- Type 2: 40-50% (Normal) ✅
- Type 2/3: 20-30% (Borderline) ✅

### 选项 2: 双模态分布

```python
# 让一半节点是 background，一半是 active
np.random.seed(seed)
is_background = np.random.rand(N) < 0.3  # 30% background

B_background = 15.0
B_active = 25.0

params.B = np.where(is_background,
                    B_background * (1 + np.random.uniform(-0.2, 0.2, N)),
                    B_active * (1 + np.random.uniform(-0.3, 0.3, N)))
```

**预期**：
- 明确的 background nodes (慢波)
- 明确的 active nodes (alpha)
- 波形更多样

### 选项 3: 区域特定参数

```python
# 模拟不同脑区的特性
region_types = {
    'frontal': {'B': 20, 'G': 18},      # Moderate activity
    'parietal': {'B': 15, 'G': 15},     # Background
    'temporal': {'B': 25, 'G': 16},     # Active
    'occipital': {'B': 22, 'G': 20},    # Alpha rhythm
}
```

---

## 🎯 具体实现

### Step 1: 修改 loadDefaultParams.py

```python
# Option A: Simply increase heterogeneity
B_base = 23.0
G_base = 17.0
heterogeneity = 0.50  # From 0.30 to 0.50

# B range: 11.5 - 34.5
# G range: 8.5 - 25.5
# → Will produce Type 1, 2, and some Type 3
```

### Step 2: 降低耦合（保持独立性）

```python
# In your test script
model.params['K_gl'] = 0.05  # From 0.15 to 0.05
```

**原因**：
- 低耦合 → 节点保持各自特性
- Background nodes 保持慢波
- Active nodes 保持快速振荡

### Step 3: 验证多样性

运行后检查：
```python
# Should see:
# - Some nodes with slow waves (2-4 Hz)
# - Some nodes with alpha (8-13 Hz)
# - Diverse amplitudes
# - Diverse energy levels
```

---

## 📊 预期改进

### Before (heterogeneity=0.30)
```
Waveforms: 都很像 (mostly Type 2)
Frequencies: 7-10 Hz (narrow range)
Amplitudes: 5-8 mV (similar)
Energy: Uniform
Visual: "Too clean", lack of diversity
```

### After (heterogeneity=0.50, K_gl=0.05)
```
Waveforms: 多样化 ✅
  - Some slow waves (Type 1)
  - Some alpha rhythm (Type 2)
  - Some borderline (Type 2/3)
  
Frequencies: 2-15 Hz (wide range) ✅
Amplitudes: 3-15 mV (diverse) ✅
Energy: Variable (low to high) ✅
Visual: More realistic, brain-like diversity ✅
```

---

## ⚠️ 权衡：多样性 vs 癫痫风险

| heterogeneity | Type 1 | Type 2 | Type 3 | 多样性 | 风险 |
|--------------|--------|--------|--------|--------|------|
| 0.20 | 5% | 90% | 5% | Low | Very safe |
| **0.30** | 15% | 75% | 10% | Medium | Safe (当前) |
| **0.50** | 30% | 50% | 20% | **High** | Acceptable |
| 0.70 | 35% | 35% | 30% | Very high | ⚠️ Monitor |

### 建议：heterogeneity = 0.50

**理由**：
- ✅ 产生明显的 Type 1 background (30%)
- ✅ 保持主要 Type 2 normal (50%)
- ✅ 少量 Type 3 (20%) 可接受
- ✅ 波形多样性大大提高
- ⚠️ 需要监控，但在安全范围

---

## 🔬 快速测试脚本

```python
# Test with high diversity
model = WendlingModel(Cmat=Cmat, Dmat=Dmat, 
                     heterogeneity=0.50,  # High diversity
                     seed=42)
model.params['K_gl'] = 0.05  # Low coupling
model.params['duration'] = 10000
model.run()

# Check diversity
for i in range(N):
    B_i = model.params['B'][i]
    if B_i < 18:
        print(f"Node {i}: Type 1 (Background)")
    elif B_i < 28:
        print(f"Node {i}: Type 2 (Normal)")
    else:
        print(f"Node {i}: Type 2/3 (Borderline)")

# Visual check - should see DIFFERENT waveforms
plt.figure(figsize=(15, 10))
for i in range(N):
    plt.subplot(N, 1, i+1)
    plt.plot(t[:20000], signals[i, :20000])
    plt.ylabel(f'Node {i}')
plt.show()
```

---

## 💡 关键发现

你的观察指出了一个重要问题：

**我们为了安全避免癫痫，牺牲了波形多样性**

真实大脑应该有：
1. ✅ Background activity (慢波，低能量)
2. ✅ Normal rhythms (alpha/beta)
3. ✅ 各种能量水平
4. ❌ 我们现在缺乏这些多样性

**解决**：
- 增加 heterogeneity (0.30 → 0.50)
- 降低 coupling (0.15 → 0.05)
- 接受少量 Type 3 nodes (< 20%)

---

## 📝 实施步骤

### 1. 修改参数（最简单）

编辑你的测试脚本：
```python
model = WendlingModel(Cmat=Cmat, Dmat=Dmat, 
                     heterogeneity=0.50)  # 改这里
model.params['K_gl'] = 0.05  # 改这里
```

### 2. 或者修改 loadDefaultParams.py（全局）

```python
# Line 107-109
B_base = 23.0  # 可选：调整中心
G_base = 17.0
p_mean_base = 90.0
```

### 3. 重新运行测试

```bash
python test_03_complete_analysis.py
```

### 4. 检查波形

应该看到：
- ✅ 一些节点有慢波 (2-4 Hz)
- ✅ 一些节点有 alpha (8-13 Hz)
- ✅ 振幅差异大
- ✅ 波形看起来不同

---

## 🎉 总结

### 你的观察完全正确！

**问题**：
- ❌ 波形太干净，都很像
- ❌ 缺乏 background slow waves
- ❌ 缺乏能量/振幅多样性
- ❌ 像"一个频道的多个副本"

**原因**：
- 参数范围太窄 (B: 15-29)
- 集中在 Type 2
- 缺乏 Type 1 和 Type 4

**解决**：
- ✅ heterogeneity = 0.50 (扩大范围)
- ✅ K_gl = 0.05 (降低耦合)
- ✅ 接受波形多样性 (包括少量 Type 3)

**预期**：
- 30% Type 1 (background, 慢波)
- 50% Type 2 (normal, alpha)
- 20% Type 2/3 (borderline)
- 波形多样化！

---

**Generated**: 2025-10-13 23:22  
**Status**: ✅ Problem identified, solution provided  
**Next**: Test with heterogeneity=0.50, K_gl=0.05
