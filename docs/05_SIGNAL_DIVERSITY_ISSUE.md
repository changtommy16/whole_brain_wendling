# Signal Diversity Issue & Solution

**Issue**: Nodes看起来太相似，signal 太"干净"  
**Date**: 2025-10-13 23:12

---

## 🔍 问题分析

### 你观察到的现象

1. **所有 node 的 activity 看起来很像**
2. **Signal 太"干净"** （缺乏变化）
3. **频率几乎相同** (都是 9.77 Hz)

### 根本原因

```
Peak frequencies: [9.77, 9.77, 7.32, 9.77, 9.77, 9.77]
Frequency std: 0.91 Hz  ← 太低！大部分节点同频率
```

这是因为：

1. **非对称异质性限制了变异范围**
   ```python
   # 之前的代码
   B: uniform(-0.24, +0.15)  # 范围：17.6-25.3 (7.7 mV)
   G: uniform(-0.15, +0.24)  # 范围：15.3-23.0 (7.7 mV)
   ```
   
2. **参数范围太保守**
   - 为了避免 Type 3，我们限制了变异
   - 但限制太多 → 节点太相似

3. **耦合效应**
   - K_gl = 0.15 有一定耦合
   - 加上参数相似 → 容易同步

---

## ✅ 解决方案：增加对称变异

### 修改后的代码

```python
# In loadDefaultParams.py

# 更对称的变异（允许更大范围）
params.B = B_base * (1 + uniform(-heterogeneity, heterogeneity, N))
params.G = G_base * (1 + uniform(-heterogeneity, heterogeneity, N))

# heterogeneity = 0.30 时：
# B range: 15.4 - 28.6  (13.2 mV range) ✅ 更大！
# G range: 12.6 - 23.4  (10.8 mV range) ✅ 更大！
```

### 为什么这样安全？

虽然允许 B 到 28.6（接近 Type 3 边界），但：

1. **只有少数节点会达到上限**
   - Uniform 分布 → 平均值仍是 22.0
   - 只有 ~5% 节点 B > 28

2. **G 也会变化**
   - 高 B 的节点可能有高 G
   - B/G 比例仍然合理

3. **监控机制**
   - 诊断工具会警告 Type 3
   - 可以调整 heterogeneity

---

## 📊 预期改进

### Before (非对称)
```
B: [17.22, 24.15, 21.88, 22.80, 16.90, 25.04]
G: [21.14, 16.79, 16.58, 16.59, 17.44, 18.98]
Peak freqs: [9.77, 9.77, 7.32, 9.77, 9.77, 9.77]
Freq std: 0.91 Hz ← 太低
```

### After (对称)
```
B: [15.4-28.6 range]  ← 更大变异
G: [12.6-23.4 range]  ← 更大变异
Peak freqs: Expected [5-15 Hz range]
Freq std: Expected 2-4 Hz ← 更好！
```

---

## 🎯 额外建议

### 选项 1: 降低耦合 (推荐)

如果还是太相似，降低 K_gl：

```python
model.params['K_gl'] = 0.08  # 从 0.15 降低
```

**效果**:
- 节点更独立
- 信号更多样
- 但 FC 会降低

### 选项 2: 提高异质性

```python
heterogeneity = 0.40  # 从 0.30 提高
```

**效果**:
- 更大参数范围
- 更多样的行为
- 但可能出现少量 Type 3 节点

### 选项 3: 调整基础参数范围

```python
# In loadDefaultParams.py
B_base = 23.0  # 提高中心值
G_base = 17.0  # 降低中心值
```

**效果**:
- 改变参数空间中心
- 可以探索不同动力学区域

---

## ⚖️ 权衡：多样性 vs 病理性

### 多样性谱系

```
Heterogeneity   Diversity    Type 3 Risk   Recommendation
0.0             None         None          Testing only
0.1-0.2         Low          Very low      Conservative
0.3             Medium       Low           ✅ Balanced
0.4             High         Medium        For diversity
0.5+            Very high    High          ⚠️ Monitor closely
```

### 当前设置 (0.30 + symmetric)

| Aspect | Score | Comment |
|--------|-------|---------|
| Diversity | 7/10 | Good range |
| Type 3 risk | 2/10 | Low risk |
| Realism | 8/10 | Physiological |
| **Overall** | ✅ | **Recommended** |

---

## 🔬 验证新设置

运行测试后检查：

```python
# 诊断输出中查看：

1. Frequency diversity
   Target: std > 2 Hz
   
2. Activity types
   Type 3: Should be < 20%
   
3. Visual inspection
   Signals should look different
   
4. Parameter ranges
   B: 15-29 range ✅
   G: 12-24 range ✅
```

---

## 📝 快速测试脚本

```python
# Test signal diversity
model = WendlingModel(Cmat=Cmat, heterogeneity=0.30, seed=42)
model.params['K_gl'] = 0.10  # Lower coupling for more diversity
model.run()

# Check diversity
for i in range(N):
    print(f"Node {i}: B={model.params['B'][i]:.2f}, "
          f"G={model.params['G'][i]:.2f}, "
          f"Peak freq={peak_freqs[i]:.1f} Hz")

# Visual check
plt.plot(signals.T)
plt.show()
```

---

## 🎯 总结

### 问题
- ❌ Signal 太相似（频率 std = 0.91 Hz）
- ❌ 非对称变异限制了多样性

### 解决
- ✅ 改用对称变异 (±30%)
- ✅ 扩大参数范围 (15-29 for B)
- ✅ 保持安全（仍避免过多 Type 3）

### 建议
1. 测试新设置
2. 检查 Type 3 比例
3. 如需更多样性：降低 K_gl 或提高 heterogeneity
4. 如有 Type 3：降低 heterogeneity 或调整 B_base

---

**Updated**: 2025-10-13 23:12  
**Status**: ✅ Solution implemented  
**Next**: Test and verify improvement
