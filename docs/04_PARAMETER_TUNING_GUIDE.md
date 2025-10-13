# Parameter Tuning Guide - Wendling Model

**Purpose**: Guide for adjusting parameters based on diagnostic output  
**Date**: 2025-10-13

---

## 🎯 Activity Types Quick Reference

### Expected Parameter Ranges

| Activity Type | B Range | G Range | Frequency | Description |
|--------------|---------|---------|-----------|-------------|
| **Type 1** | 10-20 | 5-10 | 2-4 Hz | Background (slow waves) |
| **Type 2** | 20-30 | 12-20 | 8-13 Hz | **Normal (alpha/theta)** ✅ |
| **Type 3** | 30-50 | 10-20 | 3-4 Hz | Epileptic (SWD) ⚠️ |
| **Type 4** | 50+ | 20+ | >20 Hz | Low voltage fast |

**Target**: Most nodes should be **Type 2 (Normal)**

---

## 🔍 Diagnostic Interpretation

### What the Diagnostic Output Tells You

```
Node Activity Classification:
Node   B        G        Freq(Hz)   Type                     Reason
--------------------------------------------------------------------------------
0      17.63    15.30    9.77       Type 1 (Background)      Low B parameter
1      22.79    16.90    9.77       Type 2 (Normal)          Normal B,G range
2      25.41    14.05    9.77       Type 2/3 (transition)    B borderline
3      26.04    14.05    3.91       Type 3 (Epileptic)       High B + spikes
```

### Key Indicators

1. **B Parameter**
   - If B > 28: Risk of Type 3 (epileptic)
   - If B > 30: Almost certainly Type 3
   - Sweet spot: **20-26** for normal activity

2. **G Parameter**
   - If G < 12: Too low, may cause instability
   - If G > 25: Too high, may suppress activity
   - Sweet spot: **15-22** for normal activity

3. **B/G Ratio**
   - If B/G > 1.5: Risk of epileptic activity
   - If B/G < 0.8: Risk of background activity
   - Sweet spot: **B/G ≈ 1.0-1.3**

---

## ⚙️ Parameter Adjustment Strategies

### Problem 1: Too Many Type 3 (Epileptic) Nodes

**Symptoms**:
```
Activity Type Summary:
  Type 3: 4/6 nodes (67%)
  
⚠️  WARNING: 4 nodes are Type 3 (epileptic)!
```

**Solutions**:

#### Option A: Reduce B_base
```python
# In loadDefaultParams.py
B_base = 20.0  # Reduced from 22.0
```

#### Option B: Increase G_base
```python
# In loadDefaultParams.py
G_base = 20.0  # Increased from 18.0
```

#### Option C: Reduce heterogeneity
```python
# When creating model
model = WendlingModel(Cmat=Cmat, heterogeneity=0.20)  # Reduced from 0.30
```

#### Option D: Asymmetric variation (most conservative)
```python
# In loadDefaultParams.py
params.B = B_base * (1 + np.random.uniform(-heterogeneity * 0.9, heterogeneity * 0.3, N))
params.G = G_base * (1 + np.random.uniform(-heterogeneity * 0.3, heterogeneity * 0.9, N))
# This keeps B lower and G higher
```

---

### Problem 2: Too Many Type 1 (Background) Nodes

**Symptoms**:
```
Activity Type Summary:
  Type 1: 5/6 nodes (83%)
```

**Solutions**:

#### Option A: Increase B_base
```python
B_base = 24.0  # Increased from 22.0
```

#### Option B: Check p_mean (input drive)
```python
p_mean_base = 100.0  # Increased from 90.0
```

---

### Problem 3: FC Too Low (< 0.2)

**Symptoms**:
```
Mean |FC| = 0.114
```

**Solutions**:

#### Option A: Increase K_gl (coupling strength)
```python
model.params['K_gl'] = 0.20  # Increased from 0.15
```

#### Option B: Reduce heterogeneity
```python
heterogeneity = 0.20  # Nodes more similar = higher FC
```

#### Option C: Longer simulation
```python
model.params['duration'] = 10000  # 10 seconds instead of 5
```

---

### Problem 4: FC Too High (> 0.8)

**Symptoms**:
```
Mean |FC| = 0.889
```

**Solutions**:

#### Option A: Increase heterogeneity
```python
heterogeneity = 0.40  # More diverse nodes
```

#### Option B: Decrease K_gl
```python
model.params['K_gl'] = 0.10  # Reduced coupling
```

---

## 🧪 Systematic Parameter Search

### For Whole-Brain Models

```python
# Recommended starting points for different network sizes

# 6-20 nodes
B_base = 22.0
G_base = 18.0
heterogeneity = 0.30
K_gl = 0.15

# 20-50 nodes
B_base = 21.0
G_base = 19.0
heterogeneity = 0.25
K_gl = 0.12

# 80+ nodes (HCP data)
B_base = 20.0
G_base = 20.0
heterogeneity = 0.20
K_gl = 0.08-0.12
```

### Grid Search Template

```python
# If you need to find optimal parameters

B_bases = [19, 20, 21, 22, 23]
G_bases = [17, 18, 19, 20, 21]
K_gls = [0.10, 0.12, 0.15, 0.18, 0.20]

results = []
for B in B_bases:
    for G in G_bases:
        for K_gl in K_gls:
            # Modify loadDefaultParams.py with B, G
            model = WendlingModel(Cmat=Cmat, heterogeneity=0.30)
            model.params['K_gl'] = K_gl
            model.run()
            
            # Compute FC and count Type 3 nodes
            fc = compute_fc(model)
            mean_fc = np.mean(np.abs(fc))
            n_type3 = count_type3_nodes(model)
            
            results.append({
                'B': B, 'G': G, 'K_gl': K_gl,
                'mean_fc': mean_fc,
                'n_type3': n_type3
            })

# Find best parameters
best = min(results, key=lambda x: abs(x['mean_fc'] - 0.35) + x['n_type3'] * 0.1)
```

---

## 📊 Validation Checklist

### After Parameter Adjustment

Run your test and check:

- [ ] **Activity Types**: < 30% Type 3 nodes
- [ ] **Mean FC**: 0.3 - 0.7
- [ ] **B Parameters**: Most nodes B < 28
- [ ] **G Parameters**: Most nodes G > 14
- [ ] **Peak Frequencies**: Std > 1 Hz (diversity)
- [ ] **SC-FC Correlation**: > 0.1
- [ ] **Signals Stable**: Max < 50 mV

---

## 🎯 Recommended Workflow

### Step 1: Run Diagnostic Test
```bash
cd c:\Epilepsy_project\whole_brain_wendling\tests\2_six_nodes
python test_03_complete_analysis.py
```

### Step 2: Check Diagnostic Output

Look for:
```
Activity Type Summary:
  Type 2: X/6 nodes (should be >50%)
  Type 3: Y/6 nodes (should be <30%)
```

### Step 3: Adjust Parameters (if needed)

Edit `loadDefaultParams.py`:
```python
B_base = 21.0  # Adjust based on diagnostic
G_base = 19.0  # Adjust based on diagnostic
```

### Step 4: Re-run Test

Verify improvement in activity type distribution

### Step 5: Check FC

Adjust `K_gl` to get FC in target range (0.3-0.7)

---

## 💡 Pro Tips

### 1. **Start Conservative**
- Use lower B_base and higher G_base
- Gradually increase B if needed
- Better to have Type 1/2 than Type 3

### 2. **Network Size Matters**
- Larger networks need:
  - Lower K_gl (to avoid over-synchronization)
  - Lower heterogeneity (for stability)
  - More conservative B/G values

### 3. **Check Single Node First**
```python
# Test single node with your parameters
model = WendlingModel(heterogeneity=0.0)  # No heterogeneity
model.params['B'] = 22.0
model.params['G'] = 18.0
model.run()
# Should produce Type 2 activity
```

### 4. **Use Seeds for Reproducibility**
```python
model = WendlingModel(Cmat=Cmat, heterogeneity=0.30, seed=42)
# Always get same results for debugging
```

---

## 📖 Reference: Original Paper Parameters

### Wendling et al. (2002)

| Type | A | B | G | p_mean | Frequency |
|------|---|---|---|--------|-----------|
| 1 | 5.0 | 15.0 | 10.0 | 90 | ~3 Hz |
| 2 | 5.0 | 25.0 | 15.0 | 90 | ~11 Hz |
| 3 | 5.0 | 40.0 | 20.0 | 90 | ~3 Hz (SWD) |
| 4 | 5.0 | 60.0 | 30.0 | 90 | ~25 Hz |

**For whole-brain networks**: We use ranges around Type 2 to avoid pathological states.

---

## 🚨 Common Mistakes

### 1. **Too Much Heterogeneity**
```python
heterogeneity = 0.50  # ❌ Too high! Nodes too different
heterogeneity = 0.30  # ✅ Good balance
```

### 2. **K_gl Too High**
```python
K_gl = 0.50  # ❌ Will cause over-synchronization (FC → 1.0)
K_gl = 0.15  # ✅ Appropriate for 6-20 nodes
```

### 3. **Ignoring Diagnostic Warnings**
```
⚠️  WARNING: 5 nodes are Type 3 (epileptic)!
```
**Don't ignore this!** Adjust parameters immediately.

---

## 📞 Need Help?

If diagnostic shows unexpected results:

1. Check parameter values are actually applied:
   ```python
   print(model.params['B'])  # Should be array of 6 values
   ```

2. Verify heterogeneity is working:
   ```python
   print(np.std(model.params['B']))  # Should be > 0
   ```

3. Check single-node behavior:
   ```python
   model_test = WendlingModel(heterogeneity=0.0)
   model_test.params['B'] = 22.0
   model_test.run()
   # Classify the activity type
   ```

---

**Last Updated**: 2025-10-13  
**Version**: 1.0  
**Author**: AI Assistant
