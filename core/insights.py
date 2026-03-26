# 工业质量统计 - 智能分析引擎
# 2026-03-26

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
                highlights.append(f"✅ 数据符合正态分布 (p={p_normal:.4f})")
            else:
                highlights.append(f"⚠️  数据偏离正态分布 (p={p_normal:.4f})")
                recommendations.append("考虑数据转换或使用非参数方法")
        
        # 异常值检测
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = data[(data < lower) | (data > upper)]
        
        if len(outliers) > 0:
            highlights.append(f"⚠️  检测到 {len(outliers)} 个异常值 (IQR方法)")
            recommendations.append("建议调查异常原因并考虑剔除或修正")
        else:
            highlights.append("✅ 未发现明显异常值")
        
        # 变异系数评估
        cv = std / mean if mean != 0 else 0
        if cv < 0.03:
            variation = "过程非常稳定"
        elif cv < 0.06:
            variation = "过程稳定"
        elif cv < 0.10:
            variation = "过程略有波动"
        else:
            variation = "过程波动较大，需关注"
        highlights.append(f"变异系数 (CV): {cv:.2%} - {variation}")
        
        summary = f"{column} 数据评估完成 (n={n})。平均值={mean:.4f}，标准差={std:.4f}。{variation}。"
        
        return AnalysisInsight(
            summary=summary,
            highlights=highlights,
            recommendations=recommendations,
            stability="稳定" if cv < 0.06 else "需关注"
        )
    
    @staticmethod
    def spc_insight(subgroup_means: List[float], subgroup_ranges: List[float], 
                   chart_data: Dict[str, float]) -> AnalysisInsight:
        """SPC控制图分析洞察"""
        x_bar = chart_data['X_bar']
        r_bar = chart_data['R_bar']
        ucl_x = chart_data['UCL_X']
        lcl_x = chart_data['LCL_X']
        ucl_r = chart_data['UCL_R']
        lcl_r = chart_data['LCL_R']
        
        highlights = []
        recommendations = []
        
        # 检查X-bar图是否受控
        x_outliers = sum(1 for x in subgroup_means if x > ucl_x or x < lcl_x)
        r_outliers = sum(1 for r in subgroup_ranges if r > ucl_r)
        
        if x_outliers == 0 and r_outliers == 0:
            highlights.append("✅ 过程处于统计受控状态")
            stability = "受控"
        else:
            highlights.append(f"⚠️  过程存在异常：X-bar异常点{x_outliers}个，R图异常点{r_outliers}个")
            recommendations.append("检查特殊原因变异，找出失控点")
            stability = "失控"
        
        # 控制限宽度评估
        process_width = ucl_x - lcl_x
        if process_width > 0:
            cv_process = (r_bar / x_bar) * 100 if x_bar != 0 else 0
            highlights.append(f"过程变异系数: {cv_process:.1f}%")
        
        summary = f"SPC控制图分析完成。X̄={x_bar:.4f}, R̄={r_bar:.4f}。控制限: X̄ [{lcl_x:.4f}, {ucl_x:.4f}], R [{lcl_r:.4f}, {ucl_r:.4f}]。"
        
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
        
        # R²评估
        if r_squared >= 0.7:
            fit = "优秀"
        elif r_squared >= 0.5:
            fit = "良好"
        elif r_squared >= 0.3:
            fit = "一般"
        else:
            fit = "较弱"
        highlights.append(f"模型拟合度 (R²): {r_squared:.4f} - {fit}")
        
        # 斜率显著性
        if slope_p < 0.05:
            sig = "显著"
            direction = "正相关" if slope > 0 else "负相关"
            highlights.append(f"✅ 斜率{direction}且统计显著 (p={slope_p:.4g})")
        else:
            sig = "不显著"
            highlights.append(f"⚠️  斜率统计不显著 (p={slope_p:.4g})")
            recommendations.append("考虑增加样本量或变换模型")
        
        # 方程
        equation = f"Y = {intercept:.4f} + {slope:.4f} * X"
        summary = f"回归分析完成。方程: {equation}。R²={r_squared:.4f}，斜率{sig}。"
        
        return AnalysisInsight(
            summary=summary,
            highlights=highlights,
            recommendations=recommendations,
            trends=f"X每增加1单位，Y预计变化{slope:.4f}单位"
        )
    
    @staticmethod
    def capability_insight(data: List[float], lsl: Optional[float], usl: Optional[float],
                          capability_results: Dict[str, float]) -> AnalysisInsight:
        """过程能力分析洞察"""
        highlights = []
        recommendations = []
        
        if lsl is None or usl is None:
            return AnalysisInsight(
                summary="未提供规格限，无法进行过程能力评估。",
                highlights=["请提供LSL和USL以计算Cp/Cpk"],
                recommendations=["添加规格限重新分析"]
            )
        
        cp = capability_results.get('Cp', 0)
        cpk = capability_results.get('Cpk', 0)
        mean = np.mean(data)
        
        # 评级
        if cpk >= 1.67:
            rating = "优秀"
            highlights.append(f"✅ Cpk={cpk:.2f} - {rating} (过程能力充足)")
            recommendations.append("保持当前过程，持续监控")
        elif cpk >= 1.33:
            rating = "良好"
            highlights.append(f"✅ Cpk={cpk:.2f} - {rating} (过程能力足够)")
            recommendations.append("过程稳定，可适当放宽监控")
        elif cpk >= 1.00:
            rating = "合格"
            highlights.append(f"⚠️  Cpk={cpk:.2f} - {rating} (勉强合格)")
            recommendations.append("需关注过程变异，考虑降低波动")
        else:
            rating = "不足"
            highlights.append(f"❌ Cpk={cpk:.2f} - {rating} (需改进)")
            recommendations.append("立即采取纠正措施，重新评估过程")
        
        # 中心度检查
        target = (lsl + usl) / 2
        deviation = abs(mean - target)
        if deviation > (usl - lsl) * 0.1:
            highlights.append(f"⚠️  均值偏离目标值 {deviation:.4f}")
            recommendations.append("调整过程均值以接近目标值")
        else:
            highlights.append("✅ 均值接近目标值")
        
        summary = f"过程能力分析完成。Cp={cp:.2f}, Cpk={cpk:.2f}，评级：{rating}。均值={mean:.4f}，规格限=[{lsl}, {usl}]。"
        
        return AnalysisInsight(
            summary=summary,
            highlights=highlights,
            recommendations=recommendations,
            stability="稳定" if cpk >= 1.33 else "不稳定"
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
