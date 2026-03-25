# 工业质量统计 - 评估图模块
# 2026-03-26

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from typing import List, Dict, Optional
import pandas as pd


class AssessmentCharts:
    """评估图表生成器 (Minitab风格)"""
    
    @staticmethod
    def histogram(data: List[float], title: str = "直方图", **kwargs) -> plt.Figure:
        """直方图 (带正态分布拟合)"""
        fig, ax = plt.subplots(figsize=kwargs.get("figsize", (10, 6)))
        
        # 计算统计量
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        
        # 绘制直方图
        ax.hist(data, bins=kwargs.get("bins", "auto"), density=kwargs.get("density", True),
                alpha=0.7, color=kwargs.get("color", "#1f77b4"), edgecolor='black')
        
        # 拟合正态分布曲线
        if kwargs.get("fit_normal", True):
            xmin, xmax = ax.get_xlim()
            x = np.linspace(xmin, xmax, 100)
            p = stats.norm.pdf(x, mean, std)
            ax.plot(x, p, 'r--', linewidth=2, label=f'正态拟合 (μ={mean:.2f}, σ={std:.2f})')
            ax.legend()
        
        ax.set_xlabel(kwargs.get("xlabel", "测量值"))
        ax.set_ylabel(kwargs.get("ylabel", "频数" if not kwargs.get("density", True) else "密度"))
        ax.set_title(title, fontsize=14, pad=15)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig
    
    @staticmethod
    def boxplot(data: List[float], title: str = "箱线图", **kwargs) -> plt.Figure:
        """箱线图 (异常值检测)"""
        fig, ax = plt.subplots(figsize=kwargs.get("figsize", (8, 6)))
        
        # 计算异常值
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = [x for x in data if x < lower or x > upper]
        
        # 绘制箱线图
        box = ax.boxplot(data, patch_artist=True, 
                         boxprops=dict(facecolor=kwargs.get("color", "#2ca02c")),
                         medianprops=dict(color="black", linewidth=2),
                         flierprops=dict(marker='o', color='red', alpha=0.5))
        
        # 标注异常值
        if outliers and kwargs.get("show_outliers", True):
            ax.text(1.05, upper, f'异常值: {len(outliers)}个', va='center', fontsize=9)
        
        ax.set_xticks([1])
        ax.set_xticklabels([kwargs.get("label", "数据")])
        ax.set_ylabel(kwargs.get("ylabel", "值"))
        ax.set_title(title, fontsize=14, pad=15)
        ax.grid(True, axis='y', alpha=0.3)
        
        # 添加统计文本
        stats_text = f'n={len(data)}, μ={np.mean(data):.2f}, σ={np.std(data, ddof=1):.2f}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                va='top', ha='left', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def qqplot(data: List[float], title: str = "QQ图 (正态性检验)", **kwargs) -> plt.Figure:
        """QQ图 (Quantile-Quantile Plot)"""
        fig, ax = plt.subplots(figsize=kwargs.get("figsize", (8, 8)))
        
        # 标准化数据
        standardized = (np.array(data) - np.mean(data)) / np.std(data, ddof=1)
        
        # 理论分位数
        theoretical_quantiles = stats.norm.ppf(np.arange(1, len(data) + 1) / (len(data) + 1))
        
        # 排序
        sample_quantiles = np.sort(standardized)
        
        # 绘制散点
        ax.scatter(theoretical_quantiles, sample_quantiles, 
                  alpha=0.7, color=kwargs.get("color", "#d62728"))
        
        # 45度参考线
        min_val = min(theoretical_quantiles.min(), sample_quantiles.min())
        max_val = max(theoretical_quantiles.max(), sample_quantiles.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='参考线')
        
        ax.set_xlabel("理论分位数 (正态分布)")
        ax.set_ylabel("样本分位数")
        ax.set_title(title, fontsize=14, pad=15)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Shapiro-Wilk 正态性检验
        if len(data) <= 5000:  # Shapiro-Wilk 限制
            stat, p_value = stats.shapiro(data)
            ax.text(0.02, 0.98, f'Shapiro-Wilk: p={p_value:.4f}', 
                   transform=ax.transAxes, va='top', ha='left', fontsize=9,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def stem_leaf(data: List[float], title: str = "茎叶图") -> str:
        """茎叶图 (文本输出)"""
        # 数据排序
        sorted_data = sorted(data)
        
        # 确定茎位数
        min_val = min(data)
        max_val = max(data)
        # 简单实现: 使用整数部分作为茎
        stems = {}
        for val in sorted_data:
            stem = int(val / 10)  # 十位为茎
            leaf = int(val % 10)  # 个位为叶
            if stem not in stems:
                stems[stem] = []
            stems[stem].append(leaf)
        
        # 生成文本
        lines = [title, "=" * 40]
        for stem in sorted(stems.keys()):
            leaves = sorted(stems[stem])
            leaves_str = " ".join(str(l) for l in leaves)
            lines.append(f"{stem:>3} | {leaves_str}")
        
        return "\n".join(lines)