"""
网络生成器

提供各种拓扑结构的网络生成函数。
"""

import numpy as np


def create_modular_network(n_modules=4, nodes_per_module=5, 
                          intra_density=0.8, inter_density=0.2, seed=None):
    """
    创建模块化网络。
    
    Parameters
    ----------
    n_modules : int
        模块数量
    nodes_per_module : int
        每个模块的节点数
    intra_density : float
        模块内连接密度 (0-1)
    inter_density : float
        模块间连接密度 (0-1)
    seed : int, optional
        随机种子
    
    Returns
    -------
    Cmat : ndarray
        连接矩阵
    communities : ndarray
        社区标签
    """
    if seed is not None:
        np.random.seed(seed)
    
    N = n_modules * nodes_per_module
    Cmat = np.zeros((N, N))
    communities = np.zeros(N, dtype=int)
    
    # 为每个模块分配节点
    for mod_idx in range(n_modules):
        start = mod_idx * nodes_per_module
        end = start + nodes_per_module
        communities[start:end] = mod_idx
        
        # 模块内连接
        for i in range(start, end):
            for j in range(i+1, end):
                if np.random.rand() < intra_density:
                    Cmat[i, j] = 1.0
                    Cmat[j, i] = 1.0
    
    # 模块间连接
    for mod_i in range(n_modules):
        for mod_j in range(mod_i+1, n_modules):
            start_i = mod_i * nodes_per_module
            end_i = start_i + nodes_per_module
            start_j = mod_j * nodes_per_module
            end_j = start_j + nodes_per_module
            
            for i in range(start_i, end_i):
                for j in range(start_j, end_j):
                    if np.random.rand() < inter_density:
                        Cmat[i, j] = 1.0
                        Cmat[j, i] = 1.0
    
    return Cmat, communities


def create_random_network(N=10, density=0.3, seed=None):
    """
    创建随机网络（Erdős-Rényi）。
    
    Parameters
    ----------
    N : int
        节点数
    density : float
        连接密度 (0-1)
    seed : int, optional
        随机种子
    
    Returns
    -------
    Cmat : ndarray
        连接矩阵
    """
    if seed is not None:
        np.random.seed(seed)
    
    Cmat = np.zeros((N, N))
    
    for i in range(N):
        for j in range(i+1, N):
            if np.random.rand() < density:
                Cmat[i, j] = 1.0
                Cmat[j, i] = 1.0
    
    return Cmat


def create_ring_network(N=10, k=2):
    """
    创建环形网络。
    
    Parameters
    ----------
    N : int
        节点数
    k : int
        每个节点连接到左右各 k 个邻居
    
    Returns
    -------
    Cmat : ndarray
        连接矩阵
    """
    Cmat = np.zeros((N, N))
    
    for i in range(N):
        for offset in range(1, k+1):
            j = (i + offset) % N
            Cmat[i, j] = 1.0
            Cmat[j, i] = 1.0
    
    return Cmat


def create_small_world_network(N=10, k=4, p=0.1, seed=None):
    """
    创建小世界网络（Watts-Strogatz）。
    
    Parameters
    ----------
    N : int
        节点数
    k : int
        初始环形网络的邻居数
    p : float
        重连概率 (0-1)
    seed : int, optional
        随机种子
    
    Returns
    -------
    Cmat : ndarray
        连接矩阵
    """
    if seed is not None:
        np.random.seed(seed)
    
    # 从环形网络开始
    Cmat = create_ring_network(N, k)
    
    # 重连边
    for i in range(N):
        for j in range(i+1, N):
            if Cmat[i, j] == 1.0 and np.random.rand() < p:
                # 断开 (i, j)
                Cmat[i, j] = 0
                Cmat[j, i] = 0
                
                # 重连到随机节点
                available = [n for n in range(N) if n != i and Cmat[i, n] == 0]
                if available:
                    new_j = np.random.choice(available)
                    Cmat[i, new_j] = 1.0
                    Cmat[new_j, i] = 1.0
    
    return Cmat


def create_distance_matrix(Cmat, min_dist=10, max_dist=100, seed=None):
    """
    根据连接矩阵创建距离矩阵。
    
    有连接的节点距离较短，无连接的节点距离较长。
    
    Parameters
    ----------
    Cmat : ndarray
        连接矩阵
    min_dist : float
        最小距离 (mm)
    max_dist : float
        最大距离 (mm)
    seed : int, optional
        随机种子
    
    Returns
    -------
    Dmat : ndarray
        距离矩阵
    """
    if seed is not None:
        np.random.seed(seed)
    
    N = len(Cmat)
    Dmat = np.zeros((N, N))
    
    for i in range(N):
        for j in range(i+1, N):
            if Cmat[i, j] > 0:
                # 有连接：短距离
                dist = np.random.uniform(min_dist, min_dist + (max_dist - min_dist) * 0.3)
            else:
                # 无连接：长距离
                dist = np.random.uniform(min_dist + (max_dist - min_dist) * 0.5, max_dist)
            
            Dmat[i, j] = dist
            Dmat[j, i] = dist
    
    return Dmat
