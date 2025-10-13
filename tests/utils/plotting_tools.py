"""
绘图工具函数

提供标准化的绘图函数。
"""

import numpy as np
import matplotlib.pyplot as plt


def plot_timeseries(t, signals, node_labels=None, ax=None, offset=10, title=None):
    """
    绘制多节点时间序列（带偏移）。
    
    Parameters
    ----------
    t : ndarray
        时间数组
    signals : ndarray, shape (N, T)
        N个节点的时间序列
    node_labels : list, optional
        节点标签
    ax : matplotlib.axes.Axes, optional
        绘图轴
    offset : float
        节点间垂直偏移
    title : str, optional
        标题
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))
    
    N = signals.shape[0]
    
    for i in range(N):
        label = node_labels[i] if node_labels else f'Node {i}'
        ax.plot(t, signals[i, :] + i * offset, linewidth=0.8, alpha=0.8, label=label)
    
    ax.set_xlabel('Time (ms)', fontsize=10)
    ax.set_ylabel('Activity (mV)', fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(True, alpha=0.3)
    
    return ax


def plot_psd(freqs, psds, node_labels=None, ax=None, freq_range=(1, 50), title=None):
    """
    绘制多节点功率谱密度。
    
    Parameters
    ----------
    freqs : ndarray
        频率数组
    psds : ndarray, shape (N, F)
        N个节点的PSD
    node_labels : list, optional
        节点标签
    ax : matplotlib.axes.Axes, optional
        绘图轴
    freq_range : tuple
        频率范围
    title : str, optional
        标题
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    N = psds.shape[0]
    
    # 频率范围掩码
    freq_mask = (freqs >= freq_range[0]) & (freqs <= freq_range[1])
    
    for i in range(N):
        label = node_labels[i] if node_labels else f'Node {i}'
        psd_db = 10 * np.log10(psds[i, freq_mask] + 1e-12)
        ax.plot(freqs[freq_mask], psd_db, linewidth=1.2, alpha=0.7, label=label)
    
    ax.set_xlabel('Frequency (Hz)', fontsize=10)
    ax.set_ylabel('Power (dB)', fontsize=10)
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(freq_range)
    
    return ax


def plot_fc_matrix(fc_matrix, ax=None, title='Functional Connectivity', vrange=(-1, 1)):
    """
    绘制功能连接矩阵。
    
    Parameters
    ----------
    fc_matrix : ndarray, shape (N, N)
        功能连接矩阵
    ax : matplotlib.axes.Axes, optional
        绘图轴
    title : str
        标题
    vrange : tuple
        颜色范围
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 7))
    
    im = ax.imshow(fc_matrix, cmap='RdBu_r', vmin=vrange[0], vmax=vrange[1], 
                   aspect='auto', interpolation='nearest')
    ax.set_xlabel('Node', fontsize=10)
    ax.set_ylabel('Node', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    
    return ax


def plot_sc_fc_comparison(sc_matrix, fc_matrix, ax=None):
    """
    绘制 SC vs FC 散点图。
    
    Parameters
    ----------
    sc_matrix : ndarray
        结构连接矩阵
    fc_matrix : ndarray
        功能连接矩阵
    ax : matplotlib.axes.Axes, optional
        绘图轴
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
    
    N = len(sc_matrix)
    mask = ~np.eye(N, dtype=bool)
    
    sc_flat = sc_matrix[mask]
    fc_flat = np.abs(fc_matrix[mask])
    
    ax.scatter(sc_flat, fc_flat, s=20, alpha=0.5)
    ax.set_xlabel('Structural Connectivity', fontsize=10)
    ax.set_ylabel('|Functional Connectivity|', fontsize=10)
    ax.set_title('SC vs FC', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 计算相关性
    from scipy.stats import pearsonr
    corr, pval = pearsonr(sc_flat, fc_flat)
    ax.text(0.05, 0.95, f'r = {corr:.3f}\np < {pval:.3e}', 
            transform=ax.transAxes, fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    return ax
