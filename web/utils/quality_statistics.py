"""
质量统计分析工具类
提供完整的质量统计分析功能，包括方差分析、回归分析、Gage R&R分析等
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Any, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    import statsmodels.api as sm
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("警告: statsmodels未安装，部分高级统计功能可能不可用")

class QualityStatisticsAnalyzer:
    """质量统计分析工具类"""
    
    def __init__(self):
        self.analysis_results = {}
        
    def perform_anova(self, data: pd.DataFrame, factor_col: str, response_col: str) -> Dict[str, Any]:
        """执行方差分析 (ANOVA)"""
        try:
            # 数据验证
            if factor_col not in data.columns or response_col not in data.columns:
                return {
                    'success': False,
                    'error': f'指定的列 {factor_col} 或 {response_col} 不存在'
                }
            
            # 检查因子列的唯一值数量
            factor_levels = data[factor_col].nunique()
            if factor_levels < 2:
                return {
                    'success': False,
                    'error': '方差分析需要至少2个因子水平'
                }
            
            # 检查每个组的样本量
            group_counts = data.groupby(factor_col)[response_col].count()
            min_group_size = group_counts.min()
            if min_group_size < 2:
                return {
                    'success': False,
                    'error': '每个因子水平至少需要2个观测值'
                }
            
            # 按因子分组
            groups = []
            group_names = []
            for name, group in data.groupby(factor_col):
                values = group[response_col].dropna()
                if len(values) >= 2:  # 至少需要2个有效值
                    groups.append(values)
                    group_names.append(str(name))
            
            if len(groups) < 2:
                return {
                    'success': False,
                    'error': '至少需要两个有效的组进行方差分析'
                }
            
            # 执行单因素方差分析
            f_stat, p_value = stats.f_oneway(*groups)
            
            # 计算描述性统计
            descriptive_stats = {}
            for i, (name, group) in enumerate(data.groupby(factor_col)):
                values = group[response_col].dropna()
                if len(values) > 0:
                    descriptive_stats[str(name)] = {
                        'count': len(values),
                        'mean': float(values.mean()),
                        'std': float(values.std()) if len(values) > 1 else 0.0,
                        'min': float(values.min()),
                        'max': float(values.max()),
                        'median': float(values.median()),
                        'q1': float(values.quantile(0.25)),
                        'q3': float(values.quantile(0.75))
                    }
            
            # 计算总统计量
            total_values = data[response_col].dropna()
            total_stats = {
                'count': len(total_values),
                'mean': float(total_values.mean()),
                'std': float(total_values.std()) if len(total_values) > 1 else 0.0,
                'variance': float(total_values.var()) if len(total_values) > 1 else 0.0
            }
            
            # 计算平方和
            overall_mean = total_values.mean()
            
            # 组间平方和 (SSB)
            ss_between = 0
            for name, group in data.groupby(factor_col):
                group_values = group[response_col].dropna()
                if len(group_values) > 0:
                    group_mean = group_values.mean()
                    ss_between += len(group_values) * (group_mean - overall_mean)**2
            
            # 组内平方和 (SSW)
            ss_within = 0
            for name, group in data.groupby(factor_col):
                group_values = group[response_col].dropna()
                if len(group_values) > 1:
                    group_mean = group_values.mean()
                    ss_within += sum((group_values - group_mean)**2)
            
            ss_total = ss_between + ss_within
            
            # 计算自由度
            df_between = len(groups) - 1
            df_within = len(total_values) - len(groups)
            df_total = df_between + df_within
            
            # 计算均方
            ms_between = ss_between / df_between if df_between > 0 else 0
            ms_within = ss_within / df_within if df_within > 0 else 0
            
            # 计算F值
            f_value = ms_between / ms_within if ms_within > 0 else 0
            
            # 计算效应量 (eta-squared)
            eta_squared = ss_between / ss_total if ss_total > 0 else 0
            
            # 多重比较 (Tukey HSD) - 如果statsmodels可用
            tukey_results = None
            if STATSMODELS_AVAILABLE and len(group_names) > 2:
                try:
                    tukey_results = self._perform_tukey_hsd(data, factor_col, response_col)
                except Exception as e:
                    tukey_results = {'error': f'Tukey HSD检验失败: {str(e)}'}
            
            # 检查ANOVA假设
            assumptions = self._check_anova_assumptions(data, factor_col, response_col)
            
            return {
                'success': True,
                'anova_table': {
                    'source': ['组间', '组内', '总计'],
                    'ss': [float(ss_between), float(ss_within), float(ss_total)],
                    'df': [df_between, df_within, df_total],
                    'ms': [float(ms_between), float(ms_within), None],
                    'f_value': [float(f_value), None, None],
                    'p_value': [float(p_value), None, None]
                },
                'descriptive_statistics': descriptive_stats,
                'total_statistics': total_stats,
                'f_statistic': float(f_stat),
                'p_value': float(p_value),
                'significance': '显著' if p_value < 0.05 else '不显著',
                'effect_size': {
                    'eta_squared': float(eta_squared),
                    'interpretation': self._interpret_eta_squared(eta_squared)
                },
                'tukey_hsd': tukey_results,
                'assumptions': assumptions,
                'interpretation': self._interpret_anova_results(p_value, eta_squared, assumptions)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'方差分析失败: {str(e)}'
            }
    
    def perform_regression_analysis(self, data: pd.DataFrame, x_cols: List[str], y_col: str) -> Dict[str, Any]:
        """执行回归分析"""
        try:
            # 数据验证
            for col in x_cols + [y_col]:
                if col not in data.columns:
                    return {
                        'success': False,
                        'error': f'列 {col} 不存在'
                    }
            
            # 检查多重共线性
            if len(x_cols) > 1:
                correlation_matrix = data[x_cols].corr()
                high_correlation = []
                for i in range(len(x_cols)):
                    for j in range(i+1, len(x_cols)):
                        if abs(correlation_matrix.iloc[i, j]) > 0.9:
                            high_correlation.append(f'{x_cols[i]} 和 {x_cols[j]}')
                
                if high_correlation:
                    return {
                        'success': False,
                        'error': f'检测到高度相关的预测变量: {", ".join(high_correlation)}'
                    }
            
            # 准备数据
            X = data[x_cols].dropna()
            y = data.loc[X.index, y_col]
            
            if len(X) == 0:
                return {
                    'success': False,
                    'error': '没有有效数据进行分析'
                }
            
            if len(X) < len(x_cols) + 2:
                return {
                    'success': False,
                    'error': '样本量不足以进行回归分析'
                }
            
            # 检查statsmodels是否可用
            if not STATSMODELS_AVAILABLE:
                return {
                    'success': False,
                    'error': 'statsmodels未安装，无法执行回归分析'
                }
            
            # 添加常数项
            X_with_const = sm.add_constant(X)
            
            # 执行线性回归
            model = sm.OLS(y, X_with_const).fit()
            
            # 提取回归结果
            coefficients = model.params.to_dict()
            std_errors = model.bse.to_dict()
            t_stats = model.tvalues.to_dict()
            p_values = model.pvalues.to_dict()
            
            # 模型评估指标
            r_squared = model.rsquared
            adj_r_squared = model.rsquared_adj
            f_statistic = model.fvalue
            f_p_value = model.f_pvalue
            
            # 残差分析
            residuals = model.resid
            predicted = model.fittedvalues
            
            # 残差统计
            residual_stats = {
                'mean': float(residuals.mean()),
                'std': float(residuals.std()),
                'min': float(residuals.min()),
                'max': float(residuals.max()),
                'skewness': float(stats.skew(residuals)),
                'kurtosis': float(stats.kurtosis(residuals))
            }
            
            # 正态性检验
            if len(residuals) >= 3:
                shapiro_stat, shapiro_p = stats.shapiro(residuals)
            else:
                shapiro_stat, shapiro_p = 0, 1
            
            # 异方差性检验 (Breusch-Pagan)
            try:
                from statsmodels.stats.diagnostic import het_breuschpagan
                bp_stat, bp_p, bp_f_stat, bp_f_p = het_breuschpagan(residuals, X_with_const)
                heteroscedasticity_test = {
                    'breusch_pagan_statistic': float(bp_stat),
                    'breusch_pagan_p_value': float(bp_p),
                    'f_statistic': float(bp_f_stat),
                    'f_p_value': float(bp_f_p),
                    'heteroscedasticity_detected': bp_p < 0.05
                }
            except:
                heteroscedasticity_test = {
                    'error': '异方差性检验失败'
                }
            
            # 多重共线性检验 (VIF)
            vif_results = {}
            try:
                from statsmodels.stats.outliers_influence import variance_inflation_factor
                for i, col in enumerate(x_cols):
                    vif = variance_inflation_factor(X_with_const.values, i + 1)  # +1 因为常数项
                    vif_results[col] = float(vif)
            except:
                vif_results = {'error': 'VIF计算失败'}
            
            # 影响点检测
            try:
                from statsmodels.stats.outliers_influence import OLSInfluence
                influence = OLSInfluence(model)
                cooks_d = influence.cooks_distance[0]
                leverage = influence.hat_matrix_diag
                
                # 识别影响点
                influence_points = []
                for i, (cook, lev) in enumerate(zip(cooks_d, leverage)):
                    if cook > 4/len(X) or lev > 2*len(x_cols)/len(X):  # 常用阈值
                        influence_points.append({
                            'index': i,
                            'cooks_distance': float(cook),
                            'leverage': float(lev)
                        })
            except:
                influence_points = []
            
            return {
                'success': True,
                'regression_summary': {
                    'r_squared': float(r_squared),
                    'adjusted_r_squared': float(adj_r_squared),
                    'f_statistic': float(f_statistic),
                    'f_p_value': float(f_p_value),
                    'sample_size': len(X),
                    'n_predictors': len(x_cols)
                },
                'coefficients': {
                    'estimate': coefficients,
                    'std_error': std_errors,
                    't_value': t_stats,
                    'p_value': p_values,
                    'significant_predictors': [col for col, p in p_values.items() if p < 0.05 and col != 'const']
                },
                'residual_analysis': {
                    'statistics': residual_stats,
                    'normality_test': {
                        'shapiro_wilk_statistic': float(shapiro_stat),
                        'shapiro_wilk_p_value': float(shapiro_p),
                        'normality_assumption': '满足' if shapiro_p > 0.05 else '不满足'
                    },
                    'heteroscedasticity_test': heteroscedasticity_test
                },
                'multicollinearity': {
                    'vif_values': vif_results,
                    'high_vif_variables': [col for col, vif in vif_results.items() if vif > 10] if isinstance(vif_results, dict) and 'error' not in vif_results else []
                },
                'influence_analysis': {
                    'influence_points': influence_points,
                    'n_influence_points': len(influence_points)
                },
                'predictions': {
                    'fitted_values': predicted.tolist(),
                    'residuals': residuals.tolist()
                },
                'interpretation': self._interpret_regression_results(
                    r_squared, adj_r_squared, f_p_value, p_values, residual_stats
                )
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'回归分析失败: {str(e)}'
            }
    
    def perform_gage_rnr(self, data: pd.DataFrame, part_col: str, operator_col: str, 
                        measurement_col: str) -> Dict[str, Any]:
        """执行测量系统分析 (Gage R&R)"""
        try:
            # 数据验证
            required_cols = [part_col, operator_col, measurement_col]
            for col in required_cols:
                if col not in data.columns:
                    return {
                        'success': False,
                        'error': f'列 {col} 不存在'
                    }
            
            # 获取唯一值数量
            n_parts = data[part_col].nunique()
            n_operators = data[operator_col].nunique()
            
            # 计算重复测量次数
            replicates_per_combination = len(data) // (n_parts * n_operators)
            
            if replicates_per_combination < 2:
                return {
                    'success': False,
                    'error': '需要至少2次重复测量进行Gage R&R分析'
                }
            
            if n_parts < 5:
                return {
                    'success': False,
                    'error': '建议至少5个部件进行Gage R&R分析'
                }
            
            if n_operators < 2:
                return {
                    'success': False,
                    'error': '需要至少2个操作员进行Gage R&R分析'
                }
            
            # 计算方差分量
            variance_components = self._calculate_variance_components(
                data, part_col, operator_col, measurement_col
            )
            
            # 计算总变差
            total_variance = sum(variance_components.values())
            
            # 计算Gage R&R指标
            repeatability = variance_components['repeatability']
            reproducibility = variance_components['reproducibility']
            part_to_part = variance_components['part_to_part']
            total_gage_rnr = repeatability + reproducibility
            
            # 计算研究变异 (6 * sigma)
            study_variation = {
                'repeatability_sv': np.sqrt(repeatability) * 6 if repeatability > 0 else 0,
                'reproducibility_sv': np.sqrt(reproducibility) * 6 if reproducibility > 0 else 0,
                'total_gage_rnr_sv': np.sqrt(total_gage_rnr) * 6 if total_gage_rnr > 0 else 0,
                'part_to_part_sv': np.sqrt(part_to_part) * 6 if part_to_part > 0 else 0,
                'total_sv': np.sqrt(total_variance) * 6 if total_variance > 0 else 0
            }
            
            # 计算百分比贡献
            percentages = {
                'repeatability_pct': (repeatability / total_variance * 100) if total_variance > 0 else 0,
                'reproducibility_pct': (reproducibility / total_variance * 100) if total_variance > 0 else 0,
                'total_gage_rnr_pct': (total_gage_rnr / total_variance * 100) if total_variance > 0 else 0,
                'part_to_part_pct': (part_to_part / total_variance * 100) if total_variance > 0 else 0
            }
            
            # 计算研究变异百分比
            sv_percentages = {
                'repeatability_sv_pct': (study_variation['repeatability_sv'] / study_variation['total_sv'] * 100) if study_variation['total_sv'] > 0 else 0,
                'reproducibility_sv_pct': (study_variation['reproducibility_sv'] / study_variation['total_sv'] * 100) if study_variation['total_sv'] > 0 else 0,
                'total_gage_rnr_sv_pct': (study_variation['total_gage_rnr_sv'] / study_variation['total_sv'] * 100) if study_variation['total_sv'] > 0 else 0,
                'part_to_part_sv_pct': (study_variation['part_to_part_sv'] / study_variation['total_sv'] * 100) if study_variation['total_sv'] > 0 else 0
            }
            
            # 计算NDC (区别分类数)
            ndc = int(1.41 * np.sqrt(part_to_part / total_gage_rnr)) if total_gage_rnr > 0 else 0
            
            # 评估测量系统
            assessment = self._assess_gage_rnr(percentages['total_gage_rnr_pct'], sv_percentages['total_gage_rnr_sv_pct'], ndc)
            
            # 计算操作员统计
            operator_stats = self._calculate_operator_statistics(data, operator_col, measurement_col)
            
            # 计算部件统计
            part_stats = self._calculate_part_statistics(data, part_col, measurement_col)
            
            return {
                'success': True,
                'gauge_rnr_summary': {
                    'variance_components': variance_components,
                    'total_variance': total_variance,
                    'percent_contributions': percentages,
                    'study_variation': study_variation,
                    'study_variation_percentages': sv_percentages,
                    'ndc': ndc,
                    'assessment': assessment
                },
                'study_parameters': {
                    'n_parts': n_parts,
                    'n_operators': n_operators,
                    'n_replicates': replicates_per_combination,
                    'total_observations': len(data)
                },
                'operator_statistics': operator_stats,
                'part_statistics': part_stats,
                'interpretation': self._interpret_gage_rnr_results(assessment, ndc, variance_components)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Gage R&R分析失败: {str(e)}'
            }
    
    def perform_capability_analysis(self, data: pd.Series, usl: float, lsl: float, 
                                  target: Optional[float] = None) -> Dict[str, Any]:
        """执行过程能力分析"""
        try:
            # 数据验证
            if usl <= lsl:
                return {
                    'success': False,
                    'error': '上规格限必须大于下规格限'
                }
            
            if len(data) < 30:
                return {
                    'success': False,
                    'error': '过程能力分析建议至少30个数据点'
                }
            
            # 基本统计量
            n = len(data)
            mean = data.mean()
            std = data.std(ddof=1)  # 样本标准差
            
            # 设置目标值
            if target is None:
                target = (usl + lsl) / 2
            
            # 计算能力指数
            if std == 0:
                return {
                    'success': False,
                    'error': '数据标准差为0，无法计算过程能力'
                }
            
            # Cp (过程潜在能力)
            cp = (usl - lsl) / (6 * std)
            
            # Cpk (过程实际能力)
            cpu = (usl - mean) / (3 * std)
            cpl = (mean - lsl) / (3 * std)
            cpk = min(cpu, cpl)
            
            # Pp (过程性能)
            pp = cp  # 假设使用样本标准差
            
            # Ppk (过程实际性能)
            ppu = (usl - mean) / (3 * std)
            ppl = (mean - lsl) / (3 * std)
            ppk = min(ppu, ppl)
            
            # 计算西格玛水平
            sigma_level = 3 * cpk
            
            # 计算预期不合格品率
            from scipy.stats import norm
            z_usl = (usl - mean) / std
            z_lsl = (lsl - mean) / std
            
            p_defective_upper = 1 - norm.cdf(z_usl) if z_usl > 0 else 0
            p_defective_lower = norm.cdf(z_lsl) if z_lsl < 0 else 0
            p_defective_total = p_defective_upper + p_defective_lower
            
            ppm_defective = p_defective_total * 1000000
            
            # 计算置信区间
            ci_cp = self._calculate_cp_confidence_interval(cp, n, 0.95)
            ci_cpk = self._calculate_cpk_confidence_interval(cpk, n, 0.95)
            
            # 正态性检验
            shapiro_stat, shapiro_p = stats.shapiro(data)
            
            # 过程能力评估
            capability_assessment = self._assess_process_capability(cpk, ppk)
            
            return {
                'success': True,
                'basic_statistics': {
                    'sample_size': n,
                    'mean': float(mean),
                    'std_deviation': float(std),
                    'min': float(data.min()),
                    'max': float(data.max()),
                    'range': float(data.max() - data.min())
                },
                'specification': {
                    'usl': usl,
                    'lsl': lsl,
                    'target': target,
                    'tolerance': usl - lsl
                },
                'capability_indices': {
                    'cp': float(cp),
                    'cpk': float(cpk),
                    'pp': float(pp),
                    'ppk': float(ppk),
                    'cpu': float(cpu),
                    'cpl': float(cpl),
                    'ppu': float(ppu),
                    'ppl': float(ppl)
                },
                'confidence_intervals': {
                    'cp_ci': ci_cp,
                    'cpk_ci': ci_cpk
                },
                'sigma_level': float(sigma_level),
                'defective_rate': {
                    'probability': float(p_defective_total),
                    'ppm': float(ppm_defective),
                    'percentage': float(p_defective_total * 100)
                },
                'normality_test': {
                    'shapiro_wilk_statistic': float(shapiro_stat),
                    'shapiro_wilk_p_value': float(shapiro_p),
                    'normality_assumption': '满足' if shapiro_p > 0.05 else '不满足'
                },
                'assessment': capability_assessment
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'过程能力分析失败: {str(e)}'
            }
    
    def _perform_tukey_hsd(self, data: pd.DataFrame, factor_col: str, response_col: str) -> Dict[str, Any]:
        """执行Tukey HSD多重比较"""
        try:
            # 执行Tukey HSD检验
            tukey = pairwise_tukeyhsd(
                endog=data[response_col],
                groups=data[factor_col],
                alpha=0.05
            )
            
            # 提取结果
            results = tukey._results_table.data
            
            comparisons = []
            for i in range(1, len(results)):
                comparison = {
                    'group1': results[i][0],
                    'group2': results[i][1],
                    'meandiff': float(results[i][2]),
                    'p_adj': float(results[i][3]),
                    'lower': float(results[i][4]),
                    'upper': float(results[i][5]),
                    'reject': bool(results[i][6])
                }
                comparisons.append(comparison)
            
            return {
                'comparisons': comparisons,
                'significant_comparisons': [c for c in comparisons if c['reject']],
                'n_total_comparisons': len(comparisons),
                'n_significant_comparisons': len([c for c in comparisons if c['reject']])
            }
            
        except Exception as e:
            return {
                'error': f'Tukey HSD检验失败: {str(e)}'
            }
    
    def _check_anova_assumptions(self, data: pd.DataFrame, factor_col: str, response_col: str) -> Dict[str, Any]:
        """检查ANOVA假设"""
        # 正态性检验
        groups = [group[response_col].dropna() for name, group in data.groupby(factor_col)]
        
        normality_results = []
        for i, group in enumerate(groups):
            if len(group) >= 3:  # Shapiro-Wilk检验需要至少3个样本
                stat, p = stats.shapiro(group)
                normality_results.append({
                    'group': i,
                    'statistic': float(stat),
                    'p_value': float(p),
                    'normal': p > 0.05
                })
        
        # 方差齐性检验
        if len(groups) >= 2:
            levene_stat, levene_p = stats.levene(*groups)
            homogeneity = levene_p > 0.05
        else:
            levene_stat, levene_p = 0, 1
            homogeneity = True
        
        return {
            'normality_test': normality_results,
            'homogeneity_test': {
                'levene_statistic': float(levene_stat),
                'levene_p_value': float(levene_p),
                'homogeneous': homogeneity
            },
            'assumptions_met': all(result['normal'] for result in normality_results) and homogeneity
        }
    
    def _calculate_variance_components(self, data: pd.DataFrame, part_col: str, 
                                     operator_col: str, measurement_col: str) -> Dict[str, float]:
        """计算方差分量"""
        # 计算均值
        overall_mean = data[measurement_col].mean()
        
        # 按部件和操作者分组
        part_means = data.groupby(part_col)[measurement_col].mean()
        operator_means = data.groupby(operator_col)[measurement_col].mean()
        
        # 获取样本大小信息
        n_replicates = len(data) // (len(part_means) * len(operator_means))
        n_parts = len(part_means)
        n_operators = len(operator_means)
        
        # 计算平方和
        ss_total = ((data[measurement_col] - overall_mean) ** 2).sum()
        
        # 部件平方和
        ss_parts = n_operators * n_replicates * ((part_means - overall_mean) ** 2).sum()
        
        # 操作员平方和
        ss_operators = n_parts * n_replicates * ((operator_means - overall_mean) ** 2).sum()
        
        # 交互作用平方和
        interaction_data = data.groupby([part_col, operator_col])[measurement_col].agg(['mean', 'count'])
        ss_interaction = 0
        for (part, operator), row in interaction_data.iterrows():
            expected_mean = part_means[part] + operator_means[operator] - overall_mean
            ss_interaction += row['count'] * (row['mean'] - expected_mean) ** 2
        
        # 重复性平方和
        ss_repeatability = ss_total - ss_parts - ss_operators - ss_interaction
        
        # 计算自由度
        df_parts = n_parts - 1
        df_operators = n_operators - 1
        df_interaction = df_parts * df_operators
        df_repeatability = n_parts * n_operators * (n_replicates - 1)
        
        # 计算均方
        ms_parts = ss_parts / df_parts if df_parts > 0 else 0
        ms_operators = ss_operators / df_operators if df_operators > 0 else 0
        ms_interaction = ss_interaction / df_interaction if df_interaction > 0 else 0
        ms_repeatability = ss_repeatability / df_repeatability if df_repeatability > 0 else 0
        
        # 计算方差分量
        sigma2_repeatability = ms_repeatability
        sigma2_interaction = (ms_interaction - ms_repeatability) / n_replicates if n_replicates > 1 else 0
        sigma2_operators = (ms_operators - ms_interaction) / (n_parts * n_replicates) if n_parts * n_replicates > 0 else 0
        sigma2_parts = (ms_parts - ms_interaction) / (n_operators * n_replicates) if n_operators * n_replicates > 0 else 0
        
        return {
            'repeatability': max(0, sigma2_repeatability),
            'reproducibility': max(0, sigma2_operators + sigma2_interaction),
            'part_to_part': max(0, sigma2_parts)
        }
    
    def _calculate_operator_statistics(self, data: pd.DataFrame, operator_col: str, measurement_col: str) -> List[Dict[str, Any]]:
        """计算操作员统计信息"""
        operator_stats = []
        for name, group in data.groupby(operator_col):
            values = group[measurement_col]
            operator_stats.append({
                'operator': str(name),
                'mean': float(values.mean()),
                'std': float(values.std()) if len(values) > 1 else 0.0,
                'min': float(values.min()),
                'max': float(values.max()),
                'count': len(values)
            })
        return operator_stats
    
    def _calculate_part_statistics(self, data: pd.DataFrame, part_col: str, measurement_col: str) -> List[Dict[str, Any]]:
        """计算部件统计信息"""
        part_stats = []
        for name, group in data.groupby(part_col):
            values = group[measurement_col]
            part_stats.append({
                'part': str(name),
                'mean': float(values.mean()),
                'std': float(values.std()) if len(values) > 1 else 0.0,
                'min': float(values.min()),
                'max': float(values.max()),
                'count': len(values)
            })
        return part_stats
    
    def _calculate_cp_confidence_interval(self, cp: float, n: int, alpha: float) -> List[float]:
        """计算Cp的置信区间"""
        from scipy.stats import chi2
        
        df = n - 1
        chi2_lower = chi2.ppf(alpha/2, df)
        chi2_upper = chi2.ppf(1-alpha/2, df)
        
        lower = cp * np.sqrt(df / chi2_upper)
        upper = cp * np.sqrt(df / chi2_lower)
        
        return [float(lower), float(upper)]
    
    def _calculate_cpk_confidence_interval(self, cpk: float, n: int, alpha: float) -> List[float]:
        """计算Cpk的置信区间"""
        # 使用近似方法计算Cpk置信区间
        se = np.sqrt(1 / (9 * n * cpk**2) + 1 / (2 * (n - 1))) if cpk > 0 else 0
        z = stats.norm.ppf(1 - alpha/2)
        
        lower = cpk - z * se
        upper = cpk + z * se
        
        return [float(max(0, lower)), float(upper)]
    
    def _interpret_eta_squared(self, eta_squared: float) -> str:
        """解释eta-squared效应量"""
        if eta_squared >= 0.14:
            return "大效应"
        elif eta_squared >= 0.06:
            return "中效应"
        elif eta_squared >= 0.01:
            return "小效应"
        else:
            return "无效应"
    
    def _interpret_anova_results(self, p_value: float, eta_squared: float, assumptions: Dict[str, Any]) -> Dict[str, str]:
        """解释ANOVA结果"""
        interpretation = {
            'significance': '显著' if p_value < 0.05 else '不显著',
            'effect_size': self._interpret_eta_squared(eta_squared),
            'assumptions_met': '满足' if assumptions['assumptions_met'] else '不满足'
        }
        
        if p_value < 0.05:
            interpretation['conclusion'] = '拒绝原假设，因子水平间存在显著差异'
        else:
            interpretation['conclusion'] = '无法拒绝原假设，因子水平间无显著差异'
        
        return interpretation
    
    def _interpret_regression_results(self, r_squared: float, adj_r_squared: float, 
                                    f_p_value: float, p_values: Dict[str, float],
                                    residual_stats: Dict[str, float]) -> Dict[str, str]:
        """解释回归分析结果"""
        interpretation = {
            'model_fit': '良好' if r_squared > 0.7 else '一般' if r_squared > 0.5 else '较差',
            'model_significance': '显著' if f_p_value < 0.05 else '不显著',
            'residual_normality': '正常' if residual_stats['skewness'] < 1 and residual_stats['kurtosis'] < 3 else '异常'
        }
        
        # 统计显著的自变量数量
        significant_predictors = sum(1 for p in p_values.values() if p < 0.05)
        interpretation['significant_predictors'] = f'{significant_predictors}个显著预测变量'
        
        return interpretation
    
    def _assess_gage_rnr(self, variance_pct: float, sv_pct: float, ndc: int) -> Dict[str, str]:
        """评估Gage R&R结果"""
        if sv_pct <= 10 and ndc >= 5:
            rating = "优秀"
            recommendation = "测量系统可接受"
        elif sv_pct <= 20 and ndc >= 3:
            rating = "良好"
            recommendation = "测量系统可接受，建议改进"
        elif sv_pct <= 30 and ndc >= 2:
            rating = "一般"
            recommendation = "测量系统有条件接受"
        else:
            rating = "不足"
            recommendation = "测量系统不可接受，需要改进"
        
        return {
            'rating': rating,
            'recommendation': recommendation
        }
    
    def _interpret_gage_rnr_results(self, assessment: Dict[str, str], ndc: int, 
                                  variance_components: Dict[str, float]) -> Dict[str, str]:
        """解释Gage R&R结果"""
        interpretation = {
            'overall_rating': assessment['rating'],
            'recommendation': assessment['recommendation'],
            'ndc_assessment': f'NDC = {ndc}，{"满足要求" if ndc >= 5 else "不满足要求"}'
        }
        
        # 分析各分量贡献
        total_variance = sum(variance_components.values())
        if total_variance > 0:
            repeatability_pct = variance_components['repeatability'] / total_variance * 100
            reproducibility_pct = variance_components['reproducibility'] / total_variance * 100
            
            if repeatability_pct > 50:
                interpretation['repeatability_issue'] = '重复性问题较大，需要改进测量设备或方法'
            
            if reproducibility_pct > 50:
                interpretation['reproducibility_issue'] = '再现性问题较大，需要改进操作员培训或测量标准'
        
        return interpretation
    
    def _assess_process_capability(self, cpk: float, ppk: float) -> Dict[str, str]:
        """评估过程能力"""
        def get_rating(value: float) -> str:
            if value >= 1.67:
                return "优秀"
            elif value >= 1.33:
                return "良好"
            elif value >= 1.0:
                return "一般"
            elif value >= 0.67:
                return "不足"
            else:
                return "严重不足"
        
        return {
            'cpk_rating': get_rating(cpk),
            'ppk_rating': get_rating(ppk),
            'overall_assessment': '良好' if min(cpk, ppk) >= 1.33 else '需要改进'
        }