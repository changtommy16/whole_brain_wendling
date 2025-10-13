"""
严格的六种活动类型测试（移植自 wendling_nmm_replication/level3_six_types.py）

使用 neurolib Wendling 模型，验证六种活动类型：
- Type 1: 正常背景活动
- Type 2: 零星尖波
- Type 3: 持续性尖慢波 (SWD)
- Type 4: 慢节律活动（alpha-like）
- Type 5: 低压快速活动 (LVFA)
- Type 6: 慢准正弦波活动

要求：
- 特征提取和定量分析
- PSD 分析和峰值检测
- 时域和频域验证
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch, find_peaks
from neurolib.models.wendling import WendlingModel

print("="*80)
print("严格的六种活动类型测试（neurolib Wendling 模型）")
print("="*80)

# 参数集（基于 Wendling 2002 和验证测试）
ACTIVITY_PARAMS = {
    'Type1': {
        'name': 'Type 1: Background activity',
        'params': {'A': 5.0, 'B': 50, 'G': 15, 'p_mean': 90, 'p_sigma': 30.0},
        'seed': 100,
        'expected_freq_range': (1, 7),  # Hz
        'expected_type': 'background'
    },
    'Type2': {
        'name': 'Type 2: Sporadic spikes',
        'params': {'A': 5.0, 'B': 40, 'G': 15, 'p_mean': 90, 'p_sigma': 30.0},
        'seed': 200,
        'expected_freq_range': (1, 5),
        'expected_type': 'sporadic_spikes'
    },
    'Type3': {
        'name': 'Type 3: Sustained SWD',
        'params': {'A': 5.0, 'B': 25, 'G': 15, 'p_mean': 90, 'p_sigma': 2.0},
        'seed': 300,
        'expected_freq_range': (3, 6),
        'expected_type': 'sustained_SWD'
    },
    'Type4': {
        'name': 'Type 4: Slow rhythmic (alpha-like)',
        'params': {'A': 5.0, 'B': 10, 'G': 15, 'p_mean': 90, 'p_sigma': 30.0},
        'seed': 400,
        'expected_freq_range': (8, 13),
        'expected_type': 'alpha-like'
    },
    'Type5': {
        'name': 'Type 5: Low-voltage fast activity',
        'params': {'A': 5.0, 'B': 5, 'G': 25, 'p_mean': 90, 'p_sigma': 30.0},
        'seed': 500,
        'expected_freq_range': (10, 20),
        'expected_type': 'LVFA'
    },
    'Type6': {
        'name': 'Type 6: Slow quasi-sinusoidal',
        'params': {'A': 5.0, 'B': 15, 'G': 0, 'p_mean': 90, 'p_sigma': 2.0},
        'seed': 600,
        'expected_freq_range': (9, 13),
        'expected_type': 'quasi-sinusoidal'
    }
}


def extract_features(t, v_pyr, freqs, psd):
    """提取定量特征"""
    features = {}
    
    # 时域特征
    features['RMS'] = np.sqrt(np.mean(v_pyr**2))
    features['max_amplitude'] = np.max(np.abs(v_pyr))
    features['mean'] = np.mean(v_pyr)
    features['std'] = np.std(v_pyr)
    
    # 频域特征
    freq_mask = (freqs >= 1) & (freqs <= 50)
    freqs_band = freqs[freq_mask]
    psd_band = psd[freq_mask]
    psd_db = 10*np.log10(psd_band + 1e-12)
    
    # 峰值频率
    peak_idx = np.argmax(psd_band)
    features['f_star'] = freqs_band[peak_idx]
    features['P_star'] = psd_db[peak_idx]
    
    # 显著峰数量
    distance_val = max(1, int(0.5*len(psd_db)/50))
    peaks, properties = find_peaks(psd_db, prominence=3, distance=distance_val)
    features['N_peaks'] = len(peaks)
    
    # 频带功率比
    delta_band = (freqs >= 1) & (freqs <= 4)
    theta_band = (freqs >= 4) & (freqs <= 8)
    alpha_band = (freqs >= 8) & (freqs <= 13)
    beta_band = (freqs >= 13) & (freqs <= 30)
    gamma_band = (freqs >= 30) & (freqs <= 50)
    
    total_power = np.sum(psd[freq_mask])
    features['delta_ratio'] = np.sum(psd[delta_band]) / (total_power + 1e-12)
    features['theta_ratio'] = np.sum(psd[theta_band]) / (total_power + 1e-12)
    features['alpha_ratio'] = np.sum(psd[alpha_band]) / (total_power + 1e-12)
    features['beta_ratio'] = np.sum(psd[beta_band]) / (total_power + 1e-12)
    features['gamma_ratio'] = np.sum(psd[gamma_band]) / (total_power + 1e-12)
    
    # 尖波检测
    threshold = features['mean'] + 3 * features['std']
    spikes = v_pyr > threshold
    spike_times = t[spikes]
    features['spike_count'] = len(spike_times)
    features['spike_rate'] = len(spike_times) / (t[-1] - t[0])  # spikes/sec
    
    # ISI CV
    if len(spike_times) > 2:
        isis = np.diff(spike_times)
        features['cv_isi'] = np.std(isis) / (np.mean(isis) + 1e-12)
    else:
        features['cv_isi'] = 0.0
    
    return features


def classify_type(features, params_dict):
    """简单分类：检查频率是否在预期范围内"""
    expected_range = params_dict['expected_freq_range']
    f_star = features['f_star']
    
    in_range = (f_star >= expected_range[0]) and (f_star <= expected_range[1])
    
    return in_range


# 创建图形
fig = plt.figure(figsize=(20, 15))
gs = fig.add_gridspec(3, 4, hspace=0.4, wspace=0.3)

results = []

for idx, (type_key, params_dict) in enumerate(ACTIVITY_PARAMS.items()):
    print("\n" + "="*80)
    print(f"测试: {params_dict['name']}")
    print("="*80)
    
    # 创建模型
    model = WendlingModel(seed=params_dict['seed'])
    for key, val in params_dict['params'].items():
        model.params[key] = val
    
    model.params['duration'] = 20000  # 20秒
    model.params['dt'] = 0.1  # 0.1 ms
    model.params['integration_method'] = 'euler'
    
    print(f"\n参数:")
    for key, val in params_dict['params'].items():
        print(f"  {key} = {val}")
    print(f"  seed = {params_dict['seed']}")
    
    # 运行模拟
    print("运行模拟...")
    model.run()
    
    # 提取结果
    t = model.t
    y1 = model.y1[0, :]
    y2 = model.y2[0, :]
    y3 = model.y3[0, :]
    v_pyr = y1 - y2 - y3
    
    # 丢弃前4秒
    discard_idx = int(4000 / model.params['dt'])
    t_clean = t[discard_idx:]
    v_pyr_clean = v_pyr[discard_idx:]
    t_clean = t_clean - t_clean[0]
    
    # 计算PSD
    fs = 1000.0 / model.params['dt']  # Hz
    freqs, psd = welch(v_pyr_clean, fs=fs, nperseg=min(8192, len(v_pyr_clean)//4))
    
    # 提取特征
    print("\n提取特征...")
    features = extract_features(t_clean, v_pyr_clean, freqs, psd)
    
    # 分类
    is_correct = classify_type(features, params_dict)
    
    # 打印结果
    print("\n" + "-"*80)
    print("结果:")
    print("-"*80)
    print(f"  RMS 幅度:        {features['RMS']:.3f} mV")
    print(f"  最大幅度:        {features['max_amplitude']:.3f} mV")
    print(f"  峰值频率:        {features['f_star']:.2f} Hz")
    print(f"  预期范围:        {params_dict['expected_freq_range']} Hz")
    print(f"  峰值功率:        {features['P_star']:.1f} dB")
    print(f"  显著峰数:        {features['N_peaks']}")
    print(f"  尖波率:          {features['spike_rate']:.2f} spikes/sec")
    print(f"  ISI CV:          {features['cv_isi']:.3f}")
    print(f"  Delta 功率比:    {features['delta_ratio']:.3f}")
    print(f"  Theta 功率比:    {features['theta_ratio']:.3f}")
    print(f"  Alpha 功率比:    {features['alpha_ratio']:.3f}")
    print(f"  Beta 功率比:     {features['beta_ratio']:.3f}")
    print(f"  Gamma 功率比:    {features['gamma_ratio']:.3f}")
    
    if is_correct:
        print(f"\n[PASS] ✅ 频率在预期范围内")
    else:
        print(f"\n[FAIL] ❌ 频率不在预期范围内")
    
    # 保存结果
    results.append({
        'type_key': type_key,
        'name': params_dict['name'],
        'expected_type': params_dict['expected_type'],
        'features': features,
        'correct': is_correct
    })
    
    # 绘图
    row = idx // 2
    col_time = (idx % 2) * 2
    ax_time = fig.add_subplot(gs[row, col_time])
    
    # 时间序列
    time_window = 3000  # ms
    time_idx = int(time_window / model.params['dt'])
    ax_time.plot(t_clean[:time_idx], v_pyr_clean[:time_idx], 'b-', linewidth=0.8, alpha=0.9)
    ax_time.set_xlabel('Time (ms)', fontsize=10)
    ax_time.set_ylabel('v_pyr (mV)', fontsize=10)
    status = "✅" if is_correct else "❌"
    ax_time.set_title(f'{params_dict["name"]} {status}\nf={features["f_star"]:.1f}Hz (expect {params_dict["expected_freq_range"]})',
                      fontsize=10, fontweight='bold')
    ax_time.grid(True, alpha=0.3)
    ax_time.tick_params(labelsize=9)
    
    # PSD
    col_psd = (idx % 2) * 2 + 1
    ax_psd = fig.add_subplot(gs[row, col_psd])
    
    freq_mask = (freqs >= 1) & (freqs <= 50)
    freqs_plot = freqs[freq_mask]
    psd_plot = psd[freq_mask]
    psd_db = 10*np.log10(psd_plot + 1e-12)
    
    ax_psd.plot(freqs_plot, psd_db, 'r-', linewidth=1.5, alpha=0.9)
    ax_psd.plot(features['f_star'], features['P_star'], 'ko', markersize=10,
                markerfacecolor='yellow', markeredgewidth=2)
    
    # 标注预期范围
    ax_psd.axvspan(params_dict['expected_freq_range'][0], 
                   params_dict['expected_freq_range'][1],
                   alpha=0.2, color='green' if is_correct else 'red')
    
    ax_psd.set_xlabel('Frequency (Hz)', fontsize=10)
    ax_psd.set_ylabel('Power (dB)', fontsize=10)
    ax_psd.set_title(f'PSD (Peak: {features["f_star"]:.1f} Hz, {features["N_peaks"]} peaks)',
                     fontsize=10)
    ax_psd.set_xlim(0, 50)
    ax_psd.grid(True, alpha=0.3)
    ax_psd.tick_params(labelsize=9)

plt.suptitle('严格的六种活动类型测试（neurolib Wendling 统一积分器）',
             fontsize=16, fontweight='bold', y=0.998)

plt.savefig('test_six_types_strict_result.png', dpi=150, bbox_inches='tight')
print(f"\n✓ 保存图片: test_six_types_strict_result.png")

# 总结
print("\n" + "="*80)
print("测试总结")
print("="*80)

n_correct = sum(1 for r in results if r['correct'])
n_total = len(results)

for r in results:
    status = "[PASS] ✅" if r['correct'] else "[FAIL] ❌"
    f_star = r['features']['f_star']
    print(f"{status} {r['name']:45s} f={f_star:5.1f} Hz")

print("\n" + "-"*80)
print(f"Score: {n_correct}/{n_total} ({100*n_correct/n_total:.0f}%)")

if n_correct >= 5:
    print("[PASS] ✅ 至少 5/6 类型通过")
elif n_correct >= 4:
    print("[MARGINAL] ⚠️  4/6 类型通过（可接受）")
else:
    print("[FAIL] ❌ 少于 4/6 类型通过")

print("="*80)
