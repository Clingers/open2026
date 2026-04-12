# 工业质量统计 - 过程能力分析
# 2026-03-26

# 确保中文字体配置
from . import font_config  # noqa

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from typing import List, Tuple, Optional, Dict


class ProcessCapability:
    """过程能力分析 (Cp, Cpk)"""
    
    @staticmethod
    def calculate(data: List[float], spec_limit_lsl: Optional[float] = None, 
                  spec_limit_usl: Optional[float] = None) -> Dict:
        """计算过程能力指数"""
        arr = np.array(data)
        mean = np.mean(arr)
        std = np.std(arr, ddof=1)
        
        result = {
            "mean": float(mean),
            "std": float(std),
            "n": len(arr)
        }
        
        if spec_limit_lsl is not None and spec_limit_usl is not None:
            # 双侧规格限
            Cp = (spec_limit_usl - spec_limit_lsl) / (6 * std)
            Cpu = (spec_limit_usl - mean) / (3 * std)
            Cpl = (mean - spec_limit_lsl) / (3 * std)
            Cpk = min(Cpu, Cpl)
            
            result.update({
                "spec_lsl": spec_limit_lsl,
                "spec_usl": spec_limit_usl,
                "Cp": float(Cp),
                "Cpk": float(Cpk),
                "Cpu": float(Cpu),
                "Cpl": float(Cpl)
            })
        elif spec_limit_usl is not None:
            # 单上规格限
            Cpu = (spec_limit_usl - mean) / (3 * std)
            result.update({
                "spec_usl": spec_limit_usl,
                "Cpk": float(Cpu),
                "Cpu": float(Cpu)
            })
        elif spec_limit_lsl is not None:
            # 单下规格限
            Cpl = (mean - spec_limit_lsl) / (3 * std)
            result.update({
                "spec_lsl": spec_limit_lsl,
                "Cpk": float(Cpl),
                "Cpl": float(Cpl)
            })
        
        return result
    
    @staticmethod
    def plot_capability(data: List[float], spec_limits: Tuple[Optional[float], Optional[float]] = (None, None), 
                       **kwargs) -> plt.Figure:
        """绘制过程能力图"""
        lsl, usl = spec_limits
        arr = np.array(data)
        mean = np.mean(arr)
        std = np.std(arr, ddof=1)
        
        fig, ax = plt.subplots(figsize=kwargs.get("figsize", (10, 6)))
        
        # 直方图
        ax.hist(arr, bins='auto', density=True, alpha=0.6, color='skyblue', edgecolor='black')
        
        # 拟合正态曲线
        xmin, xmax = ax.get_xlim()
        x = np.linspace(xmin, xmax, 100)
        p = stats.norm.pdf(x, mean, std)
        ax.plot(x, p, 'r-', linewidth=2, label='正态拟合')
        
        # 标注均值
        ax.axvline(mean, color='green', linestyle='-', linewidth=2, label=f'均值 μ={mean:.2f}')
        
        # 标注规格限
        if lsl is not None:
            ax.axvline(lsl, color='orange', linestyle='--', linewidth=2, label=f'LSL={lsl}')
        if usl is not None:
            ax.axvline(usl, color='orange', linestyle='--', linewidth=2, label=f'USL={usl}')
        
        # 标注 ±3σ
        ax.axvline(mean + 3*std, color='gray', linestyle=':', linewidth=1, alpha=0.7)
        ax.axvline(mean - 3*std, color='gray', linestyle=':', linewidth=1, alpha=0.7)
        
        ax.set_xlabel(kwargs.get("xlabel", "Measurement"))
        ax.set_ylabel("Density")
        ax.set_title(kwargs.get("title", "Process Capability Analysis"), fontsize=14, pad=15)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig