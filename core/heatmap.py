# 工业质量统计 - 热力图模块
# 2026-03-26

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import List, Optional, Dict


class HeatmapGenerator:
    """热力图生成器"""
    
    @staticmethod
    def correlation(data: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
        """计算相关性矩阵"""
        return data.corr(method=method)
    
    @staticmethod
    def generate_figure(corr_matrix: pd.DataFrame, title: str = "Heatmap", **kwargs) -> plt.Figure:
        """生成热力图"""
        fig, ax = plt.subplots(figsize=kwargs.get("figsize", (12, 10)))
        
        cmap = kwargs.get("cmap", "RdBu_r")
        annot = kwargs.get("annot", True)
        fmt = kwargs.get("fmt", ".2f")
        
        sns.heatmap(
            corr_matrix,
            annot=annot,
            fmt=fmt,
            cmap=cmap,
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax
        )
        ax.set_title(title, fontsize=16, pad=20)
        plt.tight_layout()
        return fig
    
    @staticmethod
    def density_heatmap(x: List[float], y: List[float], title: str = "Density Heatmap", **kwargs) -> plt.Figure:
        """二维密度热力图"""
        fig, ax = plt.subplots(figsize=kwargs.get("figsize", (10, 8)))
        
        hb = ax.hexbin(x, y, gridsize=kwargs.get("gridsize", 50), 
                      cmap=kwargs.get("cmap", "viridis"))
        ax.set_xlabel(kwargs.get("xlabel", "X"))
        ax.set_ylabel(kwargs.get("ylabel", "Y"))
        ax.set_title(title, fontsize=14, pad=15)
        fig.colorbar(hb, ax=ax, label="密度")
        
        plt.tight_layout()
        return fig