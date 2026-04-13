# 工业质量统计 - 智能分析引擎
# 2026-03-26

# 确保中文字体配置
from . import font_config  # noqa

import numpy as np
from scipy import stats
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AnalysisInsight:
    """分析洞察结果"""
    summary: str          # 总体结论
    highlights: List[str]  # 关键发现
    recommendations: List[str]  # 建议
    trends: Optional[str] = None  # 趋势描述
    stability: Optional[str] = None  # 稳定性评估


class InsightGenerator:
    """智能分析生成器 - 为统计图表提供数据洞察"""
    
    @staticmethod
    def assess_insight(data: List[float], column: str, chart_type: str) -> AnalysisInsight:
        """评估图分析洞察"""
        data = np.array(data)
        n = len(data)
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        
        highlights = []
        recommendations = []
        
        # 正态性检验（Shapiro-Wilk）
        if n <= 5000:
            _, p_normal = stats.shapiro(data)
            if p_normal > 0.05:
                highlights.append(f"✅ Data is normally distributed (p={p_normal:.4f})")
            else:
                highlights.append(f"⚠️  Data deviates from normality (p={p_normal:.4f})")
                recommendations.append("Consider data transformation or non-parametric methods")
        
        # 异常值检测
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = data[(data < lower) | (data > upper)]
        
        if len(outliers) > 0:
            highlights.append(f"⚠️  Detected {len(outliers)} outliers (IQR method)")
            recommendations.append("Investigate root cause and consider removal or correction")
        else:
            highlights.append("✅ No evident outliers")
        
        # 变异系数评估
        cv = std / mean if mean != 0 else 0
        if cv < 0.03:
            variation = "Very stable process"
        elif cv < 0.06:
            variation = "Stable process"
        elif cv < 0.10:
            variation = "Slight variation"
        else:
            variation = "High variation - needs attention"
        highlights.append(f"Coefficient of Variation (CV): {cv:.2%} - {variation}")
        
        summary = f"{column} data assessment completed (n={n}). Mean={mean:.4f}, StdDev={std:.4f}. {variation}."
        
        return AnalysisInsight(
            summary=summary,
            highlights=highlights,
            recommendations=recommendations,
            stability="Stable" if cv < 0.06 else "Needs attention"
        )
    
    @staticmethod
    def spc_insight(
        subgroup_means: List[float],
        subgroup_ranges: Optional[List[float]] = None,
        subgroup_stds: Optional[List[float]] = None,
        chart_data: Optional[Dict[str, float]] = None
    ) -> AnalysisInsight:
        """SPC控制图分析洞察（支持 X-R, X-S）"""
        highlights = []
        recommendations = []
        stability = "Unknown"
        
        # Determine chart type
        chart_type = chart_data.get('chart_type') if chart_data else None
        
        if chart_type in ('X-R', 'x-r'):
            # X-R chart
            x_bar = chart_data['X_bar']
            r_bar = chart_data['R_bar']
            ucl_x = chart_data['UCL_X']
            lcl_x = chart_data['LCL_X']
            ucl_r = chart_data['UCL_R']
            lcl_r = chart_data['LCL_R']
            
            # Check X-bar and R charts
            x_outliers = sum(1 for x in subgroup_means if x > ucl_x or x < lcl_x)
            r_outliers = sum(1 for r in (subgroup_ranges or []) if r > ucl_r)
            
            if x_outliers == 0 and r_outliers == 0:
                highlights.append("✅ Process in statistical control")
                stability = "In control"
            else:
                highlights.append(f"⚠️  Process out of control: {x_outliers} X-bar outliers, {r_outliers} R chart outliers")
                recommendations.append("Investigate special causes and identify out-of-control points")
                stability = "Out of control"
            
            cv_process = (r_bar / x_bar) * 100 if x_bar != 0 else 0
            highlights.append(f"Process Variation Coefficient: {cv_process:.1f}%")
            
            summary = f"SPC control chart analysis completed. X̄={x_bar:.4f}, R̄={r_bar:.4f}. Control limits: X̄ [{lcl_x:.4f}, {ucl_x:.4f}], R [{lcl_r:.4f}, {ucl_r:.4f}]."
            
        elif chart_type in ('X-S', 'x-s'):
            # X-S chart
            x_bar = chart_data['X_bar']
            s_bar = chart_data['S_bar']
            ucl_x = chart_data['UCL_X']
            lcl_x = chart_data['LCL_X']
            ucl_s = chart_data['UCL_S']
            lcl_s = chart_data['LCL_S']
            
            x_outliers = sum(1 for x in subgroup_means if x > ucl_x or x < lcl_x)
            s_outliers = sum(1 for s in (subgroup_stds or []) if s > ucl_s)
            
            if x_outliers == 0 and s_outliers == 0:
                highlights.append("✅ Process in statistical control")
                stability = "In control"
            else:
                highlights.append(f"⚠️  Process out of control: {x_outliers} X-bar outliers, {s_outliers} S chart outliers")
                recommendations.append("Investigate special causes and identify out-of-control points")
                stability = "Out of control"
            
            cv_process = (s_bar / x_bar) * 100 if x_bar != 0 else 0
            highlights.append(f"Process Variation Coefficient: {cv_process:.1f}% (based on S)")
            
            summary = f"SPC control chart analysis completed. X̄={x_bar:.4f}, S̄={s_bar:.4f}. Control limits: X̄ [{lcl_x:.4f}, {ucl_x:.4f}], S [{lcl_s:.4f}, {ucl_s:.4f}]."
            
        elif chart_type in ('np', 'p'):
            # For now, simply use generic
            summary = "SPC control chart analysis completed."
            highlights.append("Analysis complete. Review chart for out-of-control points.")
            stability = "Review required"
        else:
            summary = "SPC analysis completed."
            highlights.append("No specific insight generator for this chart type.")
            stability = "Unknown"
        
        return AnalysisInsight(
            summary=summary,
            highlights=highlights,
            recommendations=recommendations,
            stability=stability
        )
    
    @staticmethod
    def regression_insight(x_data: List[float], y_data: List[float], 
                          results: Dict[str, Any]) -> AnalysisInsight:
        """回归分析洞察"""
        r_squared = results['r_squared']
        slope = results['slope']
        intercept = results['intercept']
        slope_p = results['slope_p_value']
        
        highlights = []
        recommendations = []
        
        # R² evaluation
        if r_squared >= 0.7:
            fit = "Excellent"
        elif r_squared >= 0.5:
            fit = "Good"
        elif r_squared >= 0.3:
            fit = "Fair"
        else:
            fit = "Weak"
        highlights.append(f"Model Fit (R²): {r_squared:.4f} - {fit}")
        
        # Slope significance
        if slope_p < 0.05:
            sig = "significant"
            direction = "positive" if slope > 0 else "negative"
            highlights.append(f"✅ Slope is {direction} and statistically significant (p={slope_p:.4g})")
        else:
            sig = "not significant"
            highlights.append(f"⚠️  Slope is not statistically significant (p={slope_p:.4g})")
            recommendations.append("Consider increasing sample size or transformation")
        
        # 方程
        equation = f"Y = {intercept:.4f} + {slope:.4f} * X"
        summary = f"Regression analysis completed. Equation: {equation}. R²={r_squared:.4f}, slope is {sig}."
        
        return AnalysisInsight(
            summary=summary,
            highlights=highlights,
            recommendations=recommendations,
            trends=f"For each 1-unit increase in X, Y changes by approximately {slope:.4f} units"
        )
    
    @staticmethod
    def capability_insight(data: List[float], lsl: Optional[float], usl: Optional[float],
                          capability_results: Dict[str, float]) -> AnalysisInsight:
        """过程能力分析洞察"""
        highlights = []
        recommendations = []
        
        if lsl is None or usl is None:
            return AnalysisInsight(
                summary="Specification limits not provided. Process capability cannot be assessed.",
                highlights=["Provide LSL and USL to calculate Cp/Cpk"],
                recommendations=["Add specification limits and re-analyze"]
            )
        
        cp = capability_results.get('Cp', 0)
        cpk = capability_results.get('Cpk', 0)
        mean = np.mean(data)
        
        # Rating
        if cpk >= 2.0:
            rating = "Excellent"
            highlights.append(f"✅ Cpk={cpk:.2f} - {rating} (Process capable)")
            recommendations.append("Maintain current process, continue monitoring")
        elif cpk >= 1.33:
            rating = "Good"
            highlights.append(f"✅ Cpk={cpk:.2f} - {rating} (Adequately capable)")
            recommendations.append("Process is stable, monitoring can be relaxed")
        elif cpk >= 1.00:
            rating = "Marginal"
            highlights.append(f"⚠️  Cpk={cpk:.2f} - {rating} (Acceptable but borderline)")
            recommendations.append("Monitor process variation, consider reduction efforts")
        else:
            rating = "Inadequate"
            highlights.append(f"❌ Cpk={cpk:.2f} - {rating} (Needs improvement)")
            recommendations.append("Take immediate corrective actions, re-evaluate the process")
        
        # Centering check
        target = (lsl + usl) / 2
        deviation = abs(mean - target)
        if deviation > (usl - lsl) * 0.1:
            highlights.append(f"⚠️  Mean deviates from target by {deviation:.4f}")
            recommendations.append("Adjust process mean to be closer to target")
        else:
            highlights.append("✅ Mean is close to target")
        
        summary = f"Process capability analysis completed. Cp={cp:.2f}, Cpk={cpk:.2f}, Rating: {rating}. Mean={mean:.4f}, Spec Limits=[{lsl}, {usl}]."
        
        return AnalysisInsight(
            summary=summary,
            highlights=highlights,
            recommendations=recommendations,
            stability="Stable" if cpk >= 1.33 else "Unstable"
        )
    
    @staticmethod
    def report_insight(data: List[float], lsl: Optional[float], usl: Optional[float],
                      all_results: Dict[str, Any]) -> AnalysisInsight:
        """完整报告综合洞察"""
        # 调用评估洞察作为基础
        base_insight = InsightGenerator.assess_insight(data, "综合", "histogram")
        
        highlights = base_insight.highlights.copy()
        recommendations = base_insight.recommendations.copy()
        
        # 添加SPC信息（如果可用）
        if all_results.get('spc'):
            spc_insight = InsightGenerator.spc_insight(
                all_results['spc'].get('subgroup_means', []),
                all_results['spc'].get('subgroup_ranges', []),
                all_results['spc']
            )
            highlights.append(f"SPC状态: {spc_insight.stability}")
        
        # 添加能力分析（如果可用）
        if all_results.get('capability'):
            cap_insight = InsightGenerator.capability_insight(
                data, lsl, usl, all_results['capability']
            )
            highlights.extend(cap_insight.highlights[:2])  # 只取前2条
        
        # 综合评级
        n = len(data)
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        cv = std / mean if mean != 0 else 0
        
        if cv < 0.03 and (lsl is None or (lsl <= mean - 3*std and usl >= mean + 3*std)):
            overall = "优秀"
        elif cv < 0.06 and (lsl is None or (lsl <= mean - 2*std and usl >= mean + 2*std)):
            overall = "良好"
        elif cv < 0.10:
            overall = "合格"
        else:
            overall = "需改进"
        
        summary = f"综合评估完成。n={n}，均值={mean:.4f}，标准差={std:.4f}，变异系数={cv:.2%}。整体评级：{overall}。"
        
        return AnalysisInsight(
            summary=summary,
            highlights=highlights[:6],  # 限制条数
            recommendations=list(set(recommendations))[:5],  # 去重并限制
            stability=overall
        )
