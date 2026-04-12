# 工业质量统计 - 回归分析与方程分析
# 2026-03-26

# 确保中文字体配置
from . import font_config  # noqa

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from scipy import stats
from typing import List, Dict, Tuple, Optional

# 尝试导入 sklearn，如果失败则使用简单线性回归
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score, mean_squared_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class RegressionAnalysis:
    """回归分析模块"""
    
    @staticmethod
    def linear(x: List[float], y: List[float]) -> Dict:
        """简单线性回归 y = a + b*x"""
        x_arr = np.array(x).reshape(-1, 1)
        y_arr = np.array(y)
        
        model = LinearRegression()
        model.fit(x_arr, y_arr)
        
        y_pred = model.predict(x_arr)
        r2 = r2_score(y_arr, y_pred)
        mse = mean_squared_error(y_arr, y_pred)
        
        # 残差分析
        residuals = y_arr - y_pred
        
        # 斜率/截距的标准误差
        n = len(x)
        sse = np.sum(residuals**2)
        s2 = sse / (n - 2)
        
        # 计算X的均值和平方和
        x_mean = np.mean(x)
        Sxx = np.sum((np.array(x) - x_mean)**2)
        
        se_slope = np.sqrt(s2 / Sxx)
        se_intercept = np.sqrt(s2 * (1/n + x_mean**2 / Sxx))
        
        # t统计量
        t_slope = model.coef_[0] / se_slope
        t_intercept = model.intercept_ / se_intercept
        
        # p值 (双尾检验)
        p_slope = 2 * (1 - stats.t.cdf(abs(t_slope), n-2))
        p_intercept = 2 * (1 - stats.t.cdf(abs(t_intercept), n-2))
        
        return {
            "type": "linear",
            "equation": f"y = {model.intercept_:.4f} + {model.coef_[0]:.4f}*x",
            "intercept": float(model.intercept_),
            "slope": float(model.coef_[0]),
            "intercept_std_error": float(se_intercept),
            "slope_std_error": float(se_slope),
            "intercept_p_value": float(p_intercept),
            "slope_p_value": float(p_slope),
            "r_squared": float(r2),
            "mse": float(mse),
            "predictions": y_pred.tolist(),
            "residuals": residuals.tolist(),
            "n": n
        }
    
    @staticmethod
    def plot_regression(x: List[float], y: List[float], results: Dict, **kwargs) -> plt.Figure:
        """绘制回归分析图"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        x_arr = np.array(x)
        y_arr = np.array(y)
        
        # 1. 散点图 + 回归线
        ax1 = axes[0, 0]
        ax1.scatter(x_arr, y_arr, alpha=0.6, color='blue', label='Data points')
        
        # Regression line
        x_line = np.linspace(min(x_arr), max(x_arr), 100)
        y_line = results["intercept"] + results["slope"] * x_line
        ax1.plot(x_line, y_line, 'r-', linewidth=2, label='Regression line')
        
        ax1.set_xlabel(kwargs.get("xlabel", "X"))
        ax1.set_ylabel(kwargs.get("ylabel", "Y"))
        ax1.set_title("Regression Fit", fontsize=12, pad=10)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 残差图
        ax2 = axes[0, 1]
        residuals = np.array(results["residuals"])
        ax2.scatter(x_arr, residuals, alpha=0.6, color='green')
        ax2.axhline(y=0, color='red', linestyle='--', linewidth=2)
        ax2.set_xlabel(kwargs.get("xlabel", "X"))
        ax2.set_ylabel("Residuals")
        ax2.set_title("Residuals Plot", fontsize=12, pad=10)
        ax2.grid(True, alpha=0.3)
        
        # 3. 残差直方图
        ax3 = axes[1, 0]
        ax3.hist(residuals, bins=15, density=True, alpha=0.7, color='orange')
        ax3.set_xlabel("Residuals")
        ax3.set_ylabel("Density")
        ax3.set_title("Residual Distribution", fontsize=12, pad=10)
        ax3.grid(True, alpha=0.3)
        
        # 4. QQ图 (残差正态性)
        ax4 = axes[1, 1]
        stats.probplot(residuals, dist="norm", plot=ax4)
        ax4.set_title("Residual Q-Q Plot", fontsize=12, pad=10)
        ax4.grid(True, alpha=0.3)
        
        # 添加统计文本框
        stats_text = f"R² = {results['r_squared']:.4f}\n"
        stats_text += f"y = {results['intercept']:.4f} + {results['slope']:.4f}*x\n"
        stats_text += f"p(斜率) = {results['slope_p_value']:.4g}\n"
        stats_text += f"n = {results['n']}"
        
        fig.text(0.02, 0.02, stats_text, fontsize=9,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.suptitle(kwargs.get("title", "Regression Analysis Report"), fontsize=16, y=1.02)
        plt.tight_layout()
        return fig


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
        
        ax.set_xlabel(kwargs.get("xlabel", "测量值"))
        ax.set_ylabel("密度")
        ax.set_title(kwargs.get("title", "过程能力分析"), fontsize=14, pad=15)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig