# 阶段 4: 80-nodes HCP 数据验证

**状态**: ⏸️ 待开始  
**依赖**: 阶段 3 必须完成  
**预估时间**: 2小时

---

## 🎯 目标

在真实大脑网络数据上验证：
1. ✅ 使用 HCP 真实结构连接（SC）和距离矩阵（Dmat）
2. ✅ 模拟的 FC 与实验 FC 有合理相关性
3. ✅ 节点活动在生理范围内

---

## 📁 数据来源

### **选项 1: Neurolib 内建数据**

```python
from neurolib.utils.loadData import Dataset

ds = Dataset("hcp")
Cmat = ds.Cmat  # 结构连接矩阵 (80, 80)
Dmat = ds.Dmat  # 距离矩阵 (80, 80)
```

### **选项 2: 下载 HCP 数据**

从 Human Connectome Project 下载：
- SC: 结构连接（DTI 纤维束追踪）
- Dmat: 距离矩阵（欧氏距离）

保存到 `data/` 目录：
- `hcp_80_Cmat.npy`
- `hcp_80_Dmat.npy`

---

## 📋 测试清单

### **测试 4.1: HCP 数据验证** (`test_01_hcp_validation.py`)

**内容**:
1. 加载 HCP SC 和 Dmat
2. 设置节点异质性参数
3. 运行全脑模拟
4. 计算模拟 FC
5. 与实验 FC 对比（如果有）

**分析**:
1. SC 分布
2. 模拟 FC 分布
3. SC-FC 相关性
4. 节点活动统计

**参数调优**:
- 调整 `K_gl` 使 FC 在合理范围
- 调整 `heterogeneity` 避免过度同步

**验证标准**:
- Mean |FC| 在 0.3-0.7 范围
- SC-FC 相关性 > 0.2
- 节点振幅在 ±10 mV 范围

**输出**:
- `results/hcp_data/01_hcp_validation_2025-10-XX.png`
- 包含: SC, FC, SC-FC scatter, 节点活动

---

## 📊 成功标准

| 指标 | 合格标准 | 优秀标准 |
|------|---------|---------|
| Mean \|FC\| | 0.3 - 0.8 | 0.4 - 0.6 |
| SC-FC 相关性 | > 0.2 | > 0.4 |
| 节点振幅 | < 20 mV | < 10 mV |
| 模拟稳定性 | 无发散 | 无发散 |

---

## 🔧 参数建议

基于前期测试，建议初始参数：

```python
model = WendlingModel(Cmat=Cmat, Dmat=Dmat, 
                     heterogeneity=0.15,  # 15% 变异
                     seed=42)

model.params['K_gl'] = 0.2    # 全局耦合（可能需要调整）
model.params['duration'] = 30000  # 30秒
model.params['dt'] = 0.1
```

---

## 🚨 常见问题

### **Q1: 模拟太慢怎么办？**

**A**: 80 节点模拟可能需要较长时间

**优化方法**:
1. 缩短模拟时间（duration = 20000）
2. 使用较大的 dt（如果稳定的话）
3. 减少节点数（先测试 40 节点）

---

### **Q2: FC 仍然过高？**

**A**: 增加异质性或降低耦合

```python
model.params['heterogeneity'] = 0.2  # 增加到 20%
model.params['K_gl'] = 0.15          # 降低耦合
```

---

## 📝 文件清单

- [ ] `test_01_hcp_validation.py`
- [ ] `data/hcp_80_Cmat.npy`（如果需要）
- [ ] `data/hcp_80_Dmat.npy`（如果需要）

---

**创建日期**: 2025-10-13
