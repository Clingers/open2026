# 工业质量统计 - SPC控制图模块
# 2026-03-26

# 确保中文字体配置
from . import font_config  # noqa

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple


class SPCControlChart:
    """SPC控制图计算"""
    
    @staticmethod
    def x_r_chart(data: List[List[float]]) -> Dict:
        """X-R控制图 (子组数据)"""
        subgroups = [np.array(g) for g in data]
        n = len(subgroups[0])  # 子组大小
        
        # 计算各子组统计量
        x_bars = [np.mean(g) for g in subgroups]
        ranges = [np.ptp(g) for g in subgroups]
        
        X_bar = np.mean(x_bars)
        R_bar = np.mean(ranges)
        
        # 控制限系数 (简化的常用值)
        factors = {
            2: {"A2": 1.880, "D3": 0, "D4": 3.267},
            3: {"A2": 1.023, "D3": 0, "D4": 2.575},
            4: {"A2": 0.729, "D3": 0, "D4": 2.282},
            5: {"A2": 0.577, "D3": 0, "D4": 2.114},
            6: {"A2": 0.483, "D3": 0.076, "D4": 1.924},
            7: {"A2": 0.419, "D3": 0.136, "D4": 1.864},
            8: {"A2": 0.373, "D3": 0.184, "D4": 1.816},
            9: {"A2": 0.337, "D3": 0.223, "D4": 1.777},
            10: {"A2": 0.308, "D3": 0.256, "D4": 1.744}
        }
        
        if n not in factors:
            raise ValueError(f"子组大小 n={n} 不支持，请使用 2-10")
            
        A2 = factors[n]["A2"]
        D3 = factors[n]["D3"]
        D4 = factors[n]["D4"]
        
        return {
            "chart_type": "X-R",
            "subgroup_size": n,
            "X_bar": X_bar,
            "R_bar": R_bar,
            "UCL_X": X_bar + A2 * R_bar,
            "LCL_X": X_bar - A2 * R_bar,
            "UCL_R": D4 * R_bar,
            "LCL_R": D3 * R_bar,
            "x_bars": x_bars,
            "ranges": ranges,
            "factors": factors[n]
        }
    
    @staticmethod
    def p_chart(data: List[Tuple[int, int]]) -> Dict:
        """p控制图 (不合格率)"""
        counts, sizes = zip(*data)
        p_bar = np.sum(counts) / np.sum(sizes)
        
        p_values = [c / n for c, n in zip(counts, sizes)]
        std_values = [np.sqrt(p_bar * (1 - p_bar) / n) for n in sizes]
        
        UCLs = [p_bar + 3 * s for s in std_values]
        LCLs = [p_bar - 3 * s for s in std_values]
        LCLs = [max(0, l) for l in LCLs]
        
        return {
            "chart_type": "p",
            "p_bar": p_bar,
            "p_values": p_values,
            "sample_sizes": sizes,
            "UCL": max(UCLs) if len(UCLs) > 0 else p_bar + 3 * np.sqrt(p_bar*(1-p_bar)/np.mean(sizes)),
            "LCL": min(LCLs) if len(LCLs) > 0 else 0,
            "std_values": std_values
        }
    
    @staticmethod
    def plot_x_r(chart_data: Dict, **kwargs):
        """绘制X-R控制图，返回matplotlib.figure.Figure"""
        import matplotlib.pyplot as plt
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        x_bars = chart_data["x_bars"]
        ranges = chart_data["ranges"]
        n = chart_data["subgroup_size"]
        X_bar = chart_data["X_bar"]
        R_bar = chart_data["R_bar"]
        UCL_X = chart_data["UCL_X"]
        LCL_X = chart_data["LCL_X"]
        UCL_R = chart_data["UCL_R"]
        LCL_R = chart_data["LCL_R"]
        
        # X-bar 图
        ax1.plot(x_bars, 'bo-', markersize=4, linewidth=1.5)
        ax1.axhline(X_bar, color='green', linestyle='-', linewidth=2, label=f'X̄={X_bar:.2f}')
        ax1.axhline(UCL_X, color='red', linestyle='--', linewidth=2, label=f'UCL={UCL_X:.2f}')
        ax1.axhline(LCL_X, color='red', linestyle='--', linewidth=2, label=f'LCL={LCL_X:.2f}')
        ax1.fill_between(range(len(x_bars)), LCL_X, UCL_X, alpha=0.1, color='green')
        ax1.set_ylabel('X̄ Value')
        ax1.set_title(f'X-R Control Chart (n={n})', fontsize=14, pad=15)
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        
        # R 图
        ax2.plot(ranges, 'go-', markersize=4, linewidth=1.5)
        ax2.axhline(R_bar, color='green', linestyle='-', linewidth=2, label=f'R̄={R_bar:.2f}')
        ax2.axhline(UCL_R, color='red', linestyle='--', linewidth=2, label=f'UCL={UCL_R:.2f}')
        ax2.axhline(LCL_R, color='red', linestyle='--', linewidth=2, label=f'LCL={LCL_R:.2f}')
        ax2.fill_between(range(len(ranges)), LCL_R, UCL_R, alpha=0.1, color='green')
        ax2.set_xlabel('Subgroup Index')
        ax2.set_ylabel('Range R')
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig