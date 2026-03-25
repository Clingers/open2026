# 工业质量统计 - 核心统计模块
# 2026-03-26

import numpy as np
from typing import Dict, List, Tuple, Optional
import pandas as pd


class DescriptiveStatistics:
    """描述性统计计算"""
    
    @staticmethod
    def calculate(data: List[float], name: str = "数据") -> Dict:
        """计算完整描述性统计"""
        arr = np.array(data)
        return {
            "名称": name,
            "样本量": int(len(arr)),
            "平均值": float(np.mean(arr)),
            "中位数": float(np.median(arr)),
            "众数": float(pd.Series(arr).mode()[0]) if len(pd.Series(arr).mode()) > 0 else None,
            "标准差": float(np.std(arr, ddof=1)),
            "方差": float(np.var(arr, ddof=1)),
            "最小值": float(np.min(arr)),
            "最大值": float(np.max(arr)),
            "极差": float(np.ptp(arr)),
            "变异系数": float(np.std(arr, ddof=1) / np.mean(arr)) if np.mean(arr) != 0 else None,
            "偏度": float(pd.Series(arr).skew()),
            "峰度": float(pd.Series(arr).kurtosis()),
            "Q1": float(np.percentile(arr, 25)),
            "Q3": float(np.percentile(arr, 75)),
            "IQR": float(np.percentile(arr, 75) - np.percentile(arr, 25))
        }
    
    @staticmethod
    def outliers(data: List[float], method: str = "iqr") -> List[float]:
        """检测异常值"""
        arr = np.array(data)
        q1 = np.percentile(arr, 25)
        q3 = np.percentile(arr, 75)
        iqr = q3 - q1
        
        if method == "iqr":
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
        elif method == "3sigma":
            mean = np.mean(arr)
            std = np.std(arr, ddof=1)
            lower = mean - 3 * std
            upper = mean + 3 * std
        else:
            raise ValueError(f"Unknown method: {method}")
            
        return arr[(arr < lower) | (arr > upper)].tolist()


class SPCControlChart:
    """SPC控制图计算"""
    
    @staticmethod
    def x_r_chart(data: List[List[float]]) -> Dict:
        """X-R控制图 (子组数据)"""
        # data: 每个子组的观测值列表
        subgroups = [np.array(group) for group in data]
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
    def p_chart(data: List[Tuple[int, int]]) -> Dict:  # (不合格数, 样本量)
        """p控制图 (不合格率)"""
        counts, sizes = zip(*data)
        p_bar = np.sum(counts) / np.sum(sizes)
        
        # 计算每个点的 p 和标准差
        p_values = [c / n for c, n in zip(counts, sizes)]
        std_values = [np.sqrt(p_bar * (1 - p_bar) / n) for n in sizes]
        
        UCLs = [p_bar + 3 * s for s in std_values]
        LCLs = [p_bar - 3 * s for s in std_values]
        LCLs = [max(0, l) for l in LCLs]  # 不能为负
        
        return {
            "chart_type": "p",
            "p_bar": p_bar,
            "p_values": p_values,
            "sample_sizes": sizes,
            "UCL": max(UCLs) if len(UCLs) > 0 else p_bar + 3 * np.sqrt(p_bar*(1-p_bar)/np.mean(sizes)),
            "LCL": min(LCLs) if len(LCLs) > 0 else 0,
            "std_values": std_values
        }


class HeatmapGenerator:
    """热力图生成"""
    
    @staticmethod
    def correlation(data: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
        """计算相关性矩阵"""
        return data.corr(method=method)
    
    @staticmethod
    def generate_figure(corr_matrix: pd.DataFrame, title: str = "Heatmap", **kwargs):
        """生成热力图 (返回matplotlib figure)"""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        fig, ax = plt.subplots(figsize=kwargs.get("figsize", (10, 8)))
        cmap = kwargs.get("cmap", "RdBu_r")
        
        sns.heatmap(
            corr_matrix,
            annot=kwargs.get("annot", True),
            fmt=kwargs.get("fmt", ".2f"),
            cmap=cmap,
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax
        )
        ax.set_title(title, fontsize=14, pad=20)
        plt.tight_layout()
        return fig