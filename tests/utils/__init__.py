"""
共用工具函数模块

提供所有测试阶段共用的分析和绘图工具。
"""

from .analysis_tools import (
    compute_fc,
    compute_psd,
    extract_peak_frequency,
    compute_modularity
)

from .plotting_tools import (
    plot_timeseries,
    plot_psd,
    plot_fc_matrix,
    plot_sc_fc_comparison
)

from .network_generators import (
    create_modular_network,
    create_random_network,
    create_ring_network
)

__all__ = [
    # Analysis tools
    'compute_fc',
    'compute_psd',
    'extract_peak_frequency',
    'compute_modularity',
    
    # Plotting tools
    'plot_timeseries',
    'plot_psd',
    'plot_fc_matrix',
    'plot_sc_fc_comparison',
    
    # Network generators
    'create_modular_network',
    'create_random_network',
    'create_ring_network',
]
