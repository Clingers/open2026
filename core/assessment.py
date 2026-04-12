# 工业质量统计 - 评估图模块
# 2026-03-26

# 确保中文字体配置
from . import font_config  # noqa

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from typing import List, Dict, Optional
import pandas as pd


class AssessmentCharts:
    """评估图表生成器 (Minitab风格)"""
    
    @staticmethod
    def histogram(data: List[float], title: str = "Histogram", **kwargs) -> plt.Figure:
        """Histogram (with normal distribution fit)"""
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
        
        ax.set_xlabel(kwargs.get("xlabel", "Measurement"))
        ax.set_ylabel(kwargs.get("ylabel", "Frequency" if not kwargs.get("density", True) else "Density"))
        ax.set_title(title, fontsize=14, pad=15)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig
    
    @staticmethod
    def boxplot(data: List[float], title: str = "Boxplot", **kwargs) -> plt.Figure:
        """Boxplot (Outlier Detection)"""
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
            ax.text(1.05, upper, f'Outliers: {len(outliers)}', va='center', fontsize=9)
        
        ax.set_xticks([1])
        ax.set_xticklabels([kwargs.get("label", "Data")])
        ax.set_ylabel(kwargs.get("ylabel", "Measurement"))
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
    def qqplot(data: List[float], title: str = "Q-Q Plot (Normality Test)", **kwargs) -> plt.Figure:
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
        
        ax.set_xlabel("Theoretical Quantiles (Normal Distribution)")
        ax.set_ylabel("Sample Quantiles")
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
    def stem_leaf(data: List[float], title: str = "Stem-and-Leaf Plot") -> str:
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
            lines.append(f"{stem:>3} | {leaves_str}")  # Stem = {stem}, leaves = {leaves}
        
        return "\n".join(lines)
    
    @staticmethod
    def timeseries(data: List[float], title: str = "时间序列图", **kwargs) -> plt.Figure:
        """时间序列图 (显示数据采集顺序的趋势)"""
        fig, ax = plt.subplots(figsize=kwargs.get("figsize", (12, 6)))
        
        x = list(range(1, len(data) + 1))
        y = data
        
        # 绘制数据点和连线
        ax.plot(x, y, marker='o', linewidth=2, markersize=6, 
                color=kwargs.get("color", "#1f77b4"), label='测量值')
        
        # 计算并绘制中心线（均值）
        mean = np.mean(data)
        ax.axhline(mean, color='red', linestyle='--', linewidth=2, label=f'均值={mean:.4f}')
        
        # 计算并绘制警告限（±2σ）和动作限（±3σ）
        std = np.std(data, ddof=1)
        ax.axhline(mean + 2*std, color='orange', linestyle=':', linewidth=1.5, label='+2σ 警告限')
        ax.axhline(mean - 2*std, color='orange', linestyle=':', linewidth=1.5, label='-2σ 警告限')
        ax.axhline(mean + 3*std, color='red', linestyle=':', linewidth=1.5, label='+3σ 动作限')
        ax.axhline(mean - 3*std, color='red', linestyle=':', linewidth=1.5, label='-3σ 动作限')
        
        # 异常点检测（超出3σ）
        outliers = [(i, val) for i, val in enumerate(y, 1) if abs(val - mean) > 3*std]
        if outliers:
            outlier_x, outlier_y = zip(*outliers)
            ax.scatter(outlier_x, outlier_y, color='red', s=100, zorder=5, 
                      marker='X', label=f'异常点 ({len(outliers)}个)')
        
        ax.set_xlabel(kwargs.get("xlabel", "Observation Index"))
        ax.set_ylabel(kwargs.get("ylabel", "Measurement"))
        ax.set_title(title, fontsize=14, pad=15)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        # 添加统计文本
        stats_text = f'n={len(data)}, μ={mean:.4f}, σ={std:.4f}, CV={std/mean*100:.1f}%'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                va='top', ha='left', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def pareto(data: List[float], title: str = "Pareto Chart", **kwargs) -> plt.Figure:
        """Pareto Chart (Frequency Distribution Analysis)
        
        Parameters:
            data: Can be numeric frequencies or category labels (auto-count)
        """
        # 判断数据类型：如果看起来像类别（整数或字符串），则统计频数
        unique_vals = set(data)
        
        # 如果数据点不多但唯一值较多，可能是原始观测值，需要统计频数
        if len(unique_vals) <= len(data) * 0.5 and not all(isinstance(x, (int, float)) for x in unique_vals):
            # 类别数据：统计频数
            from collections import Counter
            counter = Counter(data)
            values = list(counter.values())
            labels = list(counter.keys())
        else:
            # Assume data already contains frequencies, use index as label
            values = data
            labels = [f"Category {i+1}" for i in range(len(data))]
        
        # 排序：从大到小
        sorted_pairs = sorted(zip(values, labels), reverse=True)
        vals, labs = zip(*sorted_pairs) if sorted_pairs else ([], [])
        
        # 计算累计百分比
        total = sum(vals)
        cum_percent = np.cumsum(vals) / total * 100
        
        fig, ax1 = plt.subplots(figsize=kwargs.get("figsize", (12, 7)))
        
        # 柱状图
        bars = ax1.bar(range(len(vals)), vals, 
                       color=kwargs.get("color", "#1f77b4"), 
                       alpha=0.7, edgecolor='black')
        ax1.set_xlabel(kwargs.get("xlabel", "Category"))
        ax1.set_ylabel(kwargs.get("ylabel", "Frequency"))
        ax1.set_xticks(range(len(labs)))
        ax1.set_xticklabels(labs, rotation=45, ha='right')
        if vals:
            ax1.set_ylim(0, max(vals) * 1.1)
        
        # 累计百分比线
        ax2 = ax1.twinx()
        ax2.plot(range(len(vals)), cum_percent, color='red', marker='o', 
                linewidth=2, markersize=6, label='Cumulative Percentage')
        ax2.set_ylabel('Cumulative Percentage (%)')
        ax2.set_ylim(0, 110)
        
        # 80%线
        ax2.axhline(80, color='orange', linestyle='--', linewidth=1.5, label='80% Threshold')
        
        # Highlight vital few
        critical_indices = [i for i, cp in enumerate(cum_percent) if cp <= 80]
        if critical_indices:
            ax2.fill_between(critical_indices, 0, [cum_percent[i] for i in critical_indices], 
                            alpha=0.3, color='orange', label='Vital Few')
        
        ax1.set_title(title, fontsize=14, pad=15)
        fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))
        plt.tight_layout()
        return fig