"""
分析工具函数

提供 FC, PSD, 模块性等分析功能。
"""

import numpy as np
from scipy.stats import pearsonr
from scipy.signal import welch


def compute_fc(signals, method='pearson'):
    """
    计算功能连接矩阵。
    
    Parameters
    ----------
    signals : ndarray, shape (N, T)
        N个节点的时间序列，T为时间点数
    method : str
        'pearson' 或 'spearman'
    
    Returns
    -------
    fc : ndarray, shape (N, N)
        功能连接矩阵
    """
    N = signals.shape[0]
    fc = np.zeros((N, N))
    
    for i in range(N):
        for j in range(N):
            if method == 'pearson':
                fc[i, j], _ = pearsonr(signals[i, :], signals[j, :])
            else:
                raise NotImplementedError(f"Method {method} not implemented")
    
    return fc


def compute_psd(signal, fs=10000.0, nperseg=4096):
    """
    计算功率谱密度。
    
    Parameters
    ----------
    signal : ndarray, shape (T,)
        时间序列
    fs : float
        采样频率 (Hz)
    nperseg : int
        Welch 窗口长度
    
    Returns
    -------
    freqs : ndarray
        频率数组
    psd : ndarray
        功率谱密度
    """
    freqs, psd = welch(signal, fs=fs, nperseg=min(nperseg, len(signal)//4))
    return freqs, psd


def extract_peak_frequency(signal, fs=10000.0, freq_range=(1, 50)):
    """
    提取峰值频率。
    
    Parameters
    ----------
    signal : ndarray
        时间序列
    fs : float
        采样频率
    freq_range : tuple
        感兴趣的频率范围 (Hz)
    
    Returns
    -------
    peak_freq : float
        峰值频率 (Hz)
    peak_power : float
        峰值功率 (dB)
    """
    freqs, psd = compute_psd(signal, fs=fs)
    
    # 限制频率范围
    freq_mask = (freqs >= freq_range[0]) & (freqs <= freq_range[1])
    freqs_band = freqs[freq_mask]
    psd_band = psd[freq_mask]
    
    # 找到峰值
    peak_idx = np.argmax(psd_band)
    peak_freq = freqs_band[peak_idx]
    peak_power = 10 * np.log10(psd_band[peak_idx] + 1e-12)
    
    return peak_freq, peak_power


def compute_modularity(fc_matrix, communities):
    """
    计算模块性指数 Q。
    
    Parameters
    ----------
    fc_matrix : ndarray, shape (N, N)
        功能连接矩阵
    communities : ndarray, shape (N,)
        社区标签（0, 1, 2, ...）
    
    Returns
    -------
    Q : float
        模块性指数
    """
    N = len(fc_matrix)
    m = np.sum(fc_matrix) / 2  # 总边数
    
    Q = 0
    for i in range(N):
        for j in range(N):
            if communities[i] == communities[j]:
                k_i = np.sum(fc_matrix[i, :])
                k_j = np.sum(fc_matrix[:, j])
                Q += fc_matrix[i, j] - (k_i * k_j) / (2 * m)
    
    Q = Q / (2 * m)
    return Q


def compute_fc_statistics(fc_matrix, sc_matrix=None):
    """
    计算 FC 统计指标。
    
    Parameters
    ----------
    fc_matrix : ndarray
        功能连接矩阵
    sc_matrix : ndarray, optional
        结构连接矩阵
    
    Returns
    -------
    stats : dict
        统计指标字典
    """
    N = len(fc_matrix)
    
    # 提取非对角线元素
    mask = ~np.eye(N, dtype=bool)
    fc_flat = fc_matrix[mask]
    
    stats = {
        'mean_fc': np.mean(fc_flat),
        'mean_abs_fc': np.mean(np.abs(fc_flat)),
        'std_fc': np.std(fc_flat),
        'min_fc': np.min(fc_flat),
        'max_fc': np.max(fc_flat),
    }
    
    # SC-FC 相关性
    if sc_matrix is not None:
        sc_flat = sc_matrix[mask]
        corr, _ = pearsonr(sc_flat, np.abs(fc_flat))
        stats['sc_fc_corr'] = corr
    
    return stats
