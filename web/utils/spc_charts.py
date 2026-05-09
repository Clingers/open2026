"""
SPC (统计过程控制) 图表生成器
提供完整的SPC控制图功能，包括X-bar R图、X-bar S图、I-MR图、P图、C图等
"""

import pandas as pd
import numpy as np
import math
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class SPCChartGenerator:
    """SPC (统计过程控制) 图表生成器"""
    
    def __init__(self):
        self.control_limits = {}
        self.process_capability = {}
        
    def generate_xbar_r_chart(self, data: pd.DataFrame, subgroup_col: str, value_col: str) -> Dict[str, Any]:
        """生成X-bar R控制图"""
        try:
            # 数据验证
            if subgroup_col not in data.columns or value_col not in data.columns:
                return {
                    'success': False,
                    'error': f'列 {subgroup_col} 或 {value_col} 不存在'
                }
            
            # 按子组分组
            subgroups = data.groupby(subgroup_col)[value_col]
            
            # 验证子组大小
            subgroup_sizes = subgroups.size()
            if len(subgroup_sizes.unique()) > 1:
                return {
                    'success': False,
                    'error': '所有子组必须具有相同的大小'
                }
            
            n = subgroup_sizes.iloc[0]  # 子组大小
            if n < 2 or n > 10:
                return {
                    'success': False,
                    'error': 'X-bar R图适用于子组大小2-10的情况'
                }
            
            # 计算子组均值和极差
            xbar_values = subgroups.mean()
            r_values = subgroups.max() - subgroups.min()
            
            # 计算中心线
            xbar_bar = xbar_values.mean()
            r_bar = r_values.mean()
            
            # 获取控制限常数
            A2 = self._get_A2_factor(n)
            D3 = self._get_D3_factor(n)
            D4 = self._get_D4_factor(n)
            
            # 计算控制限
            xbar_ucl = xbar_bar + A2 * r_bar
            xbar_lcl = xbar_bar - A2 * r_bar
            
            r_ucl = D4 * r_bar
            r_lcl = max(0, D3 * r_bar)  # R图的下控制限不能为负
            
            # 检测异常点
            xbar_outliers = self._detect_outliers(xbar_values, xbar_ucl, xbar_lcl)
            r_outliers = self._detect_outliers(r_values, r_ucl, r_lcl)
            
            # 计算子组统计信息
            subgroup_stats = []
            for name, group in data.groupby(subgroup_col):
                values = group[value_col]
                subgroup_stats.append({
                    'subgroup': str(name),
                    'mean': float(values.mean()),
                    'range': float(values.max() - values.min()),
                    'std': float(values.std()),
                    'count': len(values)
                })
            
            return {
                'success': True,
                'chart_type': 'xbar_r',
                'subgroup_size': n,
                'xbar_chart': {
                    'center_line': float(xbar_bar),
                    'ucl': float(xbar_ucl),
                    'lcl': float(xbar_lcl),
                    'data_points': xbar_values.tolist(),
                    'outliers': xbar_outliers,
                    'outlier_count': len(xbar_outliers)
                },
                'r_chart': {
                    'center_line': float(r_bar),
                    'ucl': float(r_ucl),
                    'lcl': float(r_lcl),
                    'data_points': r_values.tolist(),
                    'outliers': r_outliers,
                    'outlier_count': len(r_outliers)
                },
                'subgroup_statistics': subgroup_stats,
                'control_constants': {
                    'A2': A2,
                    'D3': D3,
                    'D4': D4
                },
                'interpretation': self._interpret_xbar_r_chart(xbar_outliers, r_outliers)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'X-bar R图生成失败: {str(e)}'
            }
    
    def generate_xbar_s_chart(self, data: pd.DataFrame, subgroup_col: str, value_col: str) -> Dict[str, Any]:
        """生成X-bar S控制图"""
        try:
            # 数据验证
            if subgroup_col not in data.columns or value_col not in data.columns:
                return {
                    'success': False,
                    'error': f'列 {subgroup_col} 或 {value_col} 不存在'
                }
            
            # 按子组分组
            subgroups = data.groupby(subgroup_col)[value_col]
            
            # 验证子组大小
            subgroup_sizes = subgroups.size()
            n = subgroup_sizes.iloc[0]  # 子组大小
            if n < 11:
                return {
                    'success': False,
                    'error': 'X-bar S图适用于子组大小大于10的情况'
                }
            
            # 计算子组均值和标准差
            xbar_values = subgroups.mean()
            s_values = subgroups.std().fillna(0)
            
            # 计算中心线
            xbar_bar = xbar_values.mean()
            s_bar = s_values.mean()
            
            # 获取控制限常数
            A3 = self._get_A3_factor(n)
            B3 = self._get_B3_factor(n)
            B4 = self._get_B4_factor(n)
            
            # 计算控制限
            xbar_ucl = xbar_bar + A3 * s_bar
            xbar_lcl = xbar_bar - A3 * s_bar
            
            s_ucl = B4 * s_bar
            s_lcl = max(0, B3 * s_bar)  # S图的下控制限不能为负
            
            # 检测异常点
            xbar_outliers = self._detect_outliers(xbar_values, xbar_ucl, xbar_lcl)
            s_outliers = self._detect_outliers(s_values, s_ucl, s_lcl)
            
            # 计算子组统计信息
            subgroup_stats = []
            for name, group in data.groupby(subgroup_col):
                values = group[value_col]
                subgroup_stats.append({
                    'subgroup': str(name),
                    'mean': float(values.mean()),
                    'std': float(values.std()),
                    'range': float(values.max() - values.min()),
                    'count': len(values)
                })
            
            return {
                'success': True,
                'chart_type': 'xbar_s',
                'subgroup_size': n,
                'xbar_chart': {
                    'center_line': float(xbar_bar),
                    'ucl': float(xbar_ucl),
                    'lcl': float(xbar_lcl),
                    'data_points': xbar_values.tolist(),
                    'outliers': xbar_outliers,
                    'outlier_count': len(xbar_outliers)
                },
                's_chart': {
                    'center_line': float(s_bar),
                    'ucl': float(s_ucl),
                    'lcl': float(s_lcl),
                    'data_points': s_values.tolist(),
                    'outliers': s_outliers,
                    'outlier_count': len(s_outliers)
                },
                'subgroup_statistics': subgroup_stats,
                'control_constants': {
                    'A3': A3,
                    'B3': B3,
                    'B4': B4
                },
                'interpretation': self._interpret_xbar_s_chart(xbar_outliers, s_outliers)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'X-bar S图生成失败: {str(e)}'
            }
    
    def generate_individual_moving_range_chart(self, data: pd.Series) -> Dict[str, Any]:
        """生成单值移动极差控制图 (I-MR图)"""
        try:
            # 数据验证
            if len(data) < 3:
                return {
                    'success': False,
                    'error': 'I-MR图至少需要3个数据点'
                }
            
            # 计算移动极差
            moving_ranges = abs(data.diff().dropna())
            
            # 计算中心线
            x_bar = data.mean()
            mr_bar = moving_ranges.mean()
            
            # 计算控制限 (使用2.66和3.27常数)
            x_ucl = x_bar + 2.66 * mr_bar
            x_lcl = x_bar - 2.66 * mr_bar
            
            mr_ucl = 3.27 * mr_bar
            mr_lcl = 0  # MR图的下控制限为0
            
            # 确保下控制限不为负
            if x_lcl < 0 and data.min() >= 0:  # 如果数据都是非负的
                x_lcl = 0
            
            # 检测异常点
            x_outliers = self._detect_outliers(data, x_ucl, x_lcl)
            mr_outliers = self._detect_outliers(moving_ranges, mr_ucl, mr_lcl)
            
            # 计算运行统计信息
            runs_analysis = self._analyze_runs(data, x_bar)
            
            return {
                'success': True,
                'chart_type': 'individual_moving_range',
                'individual_chart': {
                    'center_line': float(x_bar),
                    'ucl': float(x_ucl),
                    'lcl': float(x_lcl),
                    'data_points': data.tolist(),
                    'outliers': x_outliers,
                    'outlier_count': len(x_outliers)
                },
                'moving_range_chart': {
                    'center_line': float(mr_bar),
                    'ucl': float(mr_ucl),
                    'lcl': float(mr_lcl),
                    'data_points': moving_ranges.tolist(),
                    'outliers': mr_outliers,
                    'outlier_count': len(mr_outliers)
                },
                'basic_statistics': {
                    'mean': float(data.mean()),
                    'std': float(data.std()),
                    'min': float(data.min()),
                    'max': float(data.max()),
                    'count': len(data)
                },
                'runs_analysis': runs_analysis,
                'interpretation': self._interpret_imr_chart(x_outliers, mr_outliers, runs_analysis)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'单值移动极差图生成失败: {str(e)}'
            }
    
    def generate_p_chart(self, data: pd.DataFrame, subgroup_col: str, defect_col: str) -> Dict[str, Any]:
        """生成P控制图 (不合格品率图)"""
        try:
            # 数据验证
            if subgroup_col not in data.columns or defect_col not in data.columns:
                return {
                    'success': False,
                    'error': f'列 {subgroup_col} 或 {defect_col} 不存在'
                }
            
            # 按子组分组并计算统计量
            subgroup_stats = data.groupby(subgroup_col).agg({
                defect_col: ['count', 'sum']
            })
            subgroup_stats.columns = ['total', 'defects']
            
            # 验证数据
            if (subgroup_stats['defects'] > subgroup_stats['total']).any():
                return {
                    'success': False,
                    'error': '缺陷数不能大于总数'
                }
            
            # 计算不合格品率
            p_values = subgroup_stats['defects'] / subgroup_stats['total']
            
            # 计算中心线
            p_bar = p_values.mean()
            
            # 计算控制限
            # 对于P图，控制限可能因样本大小不同而变化
            control_limits = []
            for i, (idx, row) in enumerate(subgroup_stats.iterrows()):
                n = row['total']
                if n == 0:
                    continue
                
                std_error = math.sqrt(p_bar * (1 - p_bar) / n)
                ucl = p_bar + 3 * std_error
                lcl = max(0, p_bar - 3 * std_error)  # 确保LCL不为负
                
                control_limits.append({
                    'subgroup': str(idx),
                    'sample_size': int(n),
                    'ucl': float(ucl),
                    'lcl': float(lcl),
                    'center_line': float(p_bar)
                })
            
            # 检测异常点 (使用平均样本大小进行简化检测)
            n_bar = subgroup_stats['total'].mean()
            std_error_avg = math.sqrt(p_bar * (1 - p_bar) / n_bar)
            p_ucl = p_bar + 3 * std_error_avg
            p_lcl = max(0, p_bar - 3 * std_error_avg)
            
            outliers = self._detect_outliers(p_values, p_ucl, p_lcl)
            
            # 计算过程能力指标
            average_sample_size = float(subgroup_stats['total'].mean())
            sample_size_variation = float(subgroup_stats['total'].std() / subgroup_stats['total'].mean())
            
            return {
                'success': True,
                'chart_type': 'p_chart',
                'center_line': float(p_bar),
                'average_sample_size': average_sample_size,
                'sample_size_variation': sample_size_variation,
                'data_points': p_values.tolist(),
                'outliers': outliers,
                'outlier_count': len(outliers),
                'subgroup_statistics': [
                    {
                        'subgroup': str(idx),
                        'sample_size': int(row['total']),
                        'defect_count': int(row['defects']),
                        'defect_rate': float(row['defects'] / row['total']),
                        'ucl': limits['ucl'],
                        'lcl': limits['lcl']
                    }
                    for (idx, row), limits in zip(subgroup_stats.iterrows(), control_limits)
                ],
                'control_limits': control_limits,
                'interpretation': self._interpret_p_chart(outliers, sample_size_variation)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'P图生成失败: {str(e)}'
            }
    
    def generate_c_chart(self, data: pd.DataFrame, subgroup_col: str, defect_count_col: str) -> Dict[str, Any]:
        """生成C控制图 (缺陷数图)"""
        try:
            # 数据验证
            if subgroup_col not in data.columns or defect_count_col not in data.columns:
                return {
                    'success': False,
                    'error': f'列 {subgroup_col} 或 {defect_count_col} 不存在'
                }
            
            # 按子组分组并计算缺陷数
            c_values = data.groupby(subgroup_col)[defect_count_col].sum()
            
            # 验证数据
            if (c_values < 0).any():
                return {
                    'success': False,
                    'error': '缺陷数不能为负数'
                }
            
            # 计算中心线
            c_bar = c_values.mean()
            
            if c_bar == 0:
                return {
                    'success': False,
                    'error': '平均缺陷数为0，无法生成C图'
                }
            
            # 计算控制限
            c_ucl = c_bar + 3 * math.sqrt(c_bar)
            c_lcl = max(0, c_bar - 3 * math.sqrt(c_bar))  # 确保LCL不为负
            
            # 检测异常点
            outliers = self._detect_outliers(c_values, c_ucl, c_lcl)
            
            # 计算子组统计信息
            subgroup_stats = []
            for name, count in c_values.items():
                subgroup_stats.append({
                    'subgroup': str(name),
                    'defect_count': int(count),
                    'deviation_from_mean': float(count - c_bar),
                    'standardized_value': float((count - c_bar) / math.sqrt(c_bar)) if c_bar > 0 else 0
                })
            
            # 计算泊松分布概率
            from scipy.stats import poisson
            probabilities = []
            for count in c_values:
                prob = poisson.pmf(count, c_bar)
                probabilities.append(float(prob))
            
            return {
                'success': True,
                'chart_type': 'c_chart',
                'center_line': float(c_bar),
                'ucl': float(c_ucl),
                'lcl': float(c_lcl),
                'data_points': c_values.tolist(),
                'outliers': outliers,
                'outlier_count': len(outliers),
                'subgroup_statistics': subgroup_stats,
                'probabilities': probabilities,
                'poisson_parameters': {
                    'lambda': float(c_bar),
                    'variance': float(c_bar)
                },
                'interpretation': self._interpret_c_chart(outliers, c_bar)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'C图生成失败: {str(e)}'
            }
    
    def calculate_process_capability(self, data: pd.Series, usl: float, lsl: float, 
                                   target: float = None) -> Dict[str, Any]:
        """计算过程能力指数"""
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
            
            # 计算过程能力指数
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
            from scipy.stats import shapiro
            shapiro_stat, shapiro_p = shapiro(data)
            
            # 过程能力评估
            capability_assessment = self._assess_process_capability(cpk, ppk)
            
            # 计算过程偏移
            process_shift = abs(mean - target) / (usl - lsl) * 100
            
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
                    'cp_ci_lower': float(ci_cp[0]),
                    'cp_ci_upper': float(ci_cp[1]),
                    'cpk_ci_lower': float(ci_cpk[0]),
                    'cpk_ci_upper': float(ci_cpk[1])
                },
                'sigma_level': float(sigma_level),
                'defective_rate': {
                    'probability': float(p_defective_total),
                    'ppm': float(ppm_defective),
                    'percentage': float(p_defective_total * 100)
                },
                'process_shift': {
                    'absolute_shift': float(abs(mean - target)),
                    'relative_shift': float(process_shift),
                    'centering': float((mean - target) / (usl - lsl) * 100)
                },
                'normality_test': {
                    'shapiro_wilk_statistic': float(shapiro_stat),
                    'shapiro_wilk_p_value': float(shapiro_p),
                    'normality_assumption': '满足' if shapiro_p > 0.05 else '不满足'
                },
                'assessment': capability_assessment,
                'recommendations': self._generate_capability_recommendations(cpk, ppk, process_shift, shapiro_p)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'过程能力计算失败: {str(e)}'
            }
    
    def _get_A2_factor(self, n: int) -> float:
        """获取A2常数 (X-bar R图)"""
        factors = {
            2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483,
            7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308
        }
        return factors.get(n, 0.308)
    
    def _get_D3_factor(self, n: int) -> float:
        """获取D3常数 (R图LCL)"""
        factors = {
            2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0.077,
            8: 0.136, 9: 0.184, 10: 0.223
        }
        return factors.get(n, 0.223)
    
    def _get_D4_factor(self, n: int) -> float:
        """获取D4常数 (R图UCL)"""
        factors = {
            2: 3.267, 3: 2.575, 4: 2.282, 5: 2.115, 6: 2.004,
            7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777
        }
        return factors.get(n, 1.777)
    
    def _get_A3_factor(self, n: int) -> float:
        """获取A3常数 (X-bar S图)"""
        factors = {
            11: 0.969, 12: 0.937, 13: 0.912, 14: 0.892, 15: 0.874,
            16: 0.858, 17: 0.843, 18: 0.830, 19: 0.818, 20: 0.807,
            21: 0.797, 22: 0.788, 23: 0.779, 24: 0.771, 25: 0.763
        }
        return factors.get(n, 0.763)
    
    def _get_B3_factor(self, n: int) -> float:
        """获取B3常数 (S图LCL)"""
        factors = {
            11: 0.184, 12: 0.232, 13: 0.276, 14: 0.313, 15: 0.347,
            16: 0.377, 17: 0.404, 18: 0.428, 19: 0.450, 20: 0.470,
            21: 0.488, 22: 0.504, 23: 0.519, 24: 0.533, 25: 0.546
        }
        return factors.get(n, 0.546)
    
    def _get_B4_factor(self, n: int) -> float:
        """获取B4常数 (S图UCL)"""
        factors = {
            11: 1.816, 12: 1.768, 13: 1.724, 14: 1.687, 15: 1.653,
            16: 1.623, 17: 1.596, 18: 1.572, 19: 1.550, 20: 1.530,
            21: 1.512, 22: 1.496, 23: 1.481, 24: 1.467, 25: 1.454
        }
        return factors.get(n, 1.454)
    
    def _detect_outliers(self, data: pd.Series, ucl: float, lcl: float) -> List[int]:
        """检测异常点"""
        outliers = []
        for i, value in enumerate(data):
            if value > ucl or value < lcl:
                outliers.append(i)
        return outliers
    
    def _analyze_runs(self, data: pd.Series, center_line: float) -> Dict[str, Any]:
        """分析运行规律"""
        # 计算运行数
        above = data > center_line
        runs = 1
        for i in range(1, len(above)):
            if above[i] != above[i-1]:
                runs += 1
        
        # 期望运行数
        n1 = above.sum()  # 高于中心线的点数
        n2 = len(data) - n1  # 低于中心线的点数
        expected_runs = (2 * n1 * n2) / (n1 + n2) + 1
        
        # 运行数标准差
        std_runs = math.sqrt((2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / 
                           ((n1 + n2)**2 * (n1 + n2 - 1)))
        
        return {
            'total_runs': runs,
            'expected_runs': float(expected_runs),
            'std_runs': float(std_runs),
            'points_above': int(n1),
            'points_below': int(n2),
            'runs_test_significant': abs(runs - expected_runs) > 2 * std_runs
        }
    
    def _calculate_cp_confidence_interval(self, cp: float, n: int, alpha: float) -> List[float]:
        """计算Cp的置信区间"""
        from scipy.stats import chi2
        
        df = n - 1
        chi2_lower = chi2.ppf(alpha/2, df)
        chi2_upper = chi2.ppf(1-alpha/2, df)
        
        lower = cp * math.sqrt(df / chi2_upper)
        upper = cp * math.sqrt(df / chi2_lower)
        
        return [lower, upper]
    
    def _calculate_cpk_confidence_interval(self, cpk: float, n: int, alpha: float) -> List[float]:
        """计算Cpk的置信区间"""
        from scipy.stats import norm
        
        # 使用近似方法计算Cpk置信区间
        se = math.sqrt(1 / (9 * n * cpk**2) + 1 / (2 * (n - 1))) if cpk > 0 else 0
        z = norm.ppf(1 - alpha/2)
        
        lower = cpk - z * se
        upper = cpk + z * se
        
        return [max(0, lower), upper]
    
    def _interpret_xbar_r_chart(self, xbar_outliers: List[int], r_outliers: List[int]) -> Dict[str, str]:
        """解释X-bar R图结果"""
        total_outliers = len(xbar_outliers) + len(r_outliers)
        
        if total_outliers == 0:
            return {
                'status': '受控',
                'message': '过程处于统计控制状态',
                'recommendation': '继续监控，保持当前过程设置'
            }
        elif len(r_outliers) > 0:
            return {
                'status': '变异异常',
                'message': '过程变异存在异常，R图显示失控',
                'recommendation': '检查测量系统、设备维护、材料批次'
            }
        else:
            return {
                'status': '均值异常',
                'message': '过程均值存在异常，X-bar图显示失控',
                'recommendation': '检查过程设置、原材料、操作人员'
            }
    
    def _interpret_xbar_s_chart(self, xbar_outliers: List[int], s_outliers: List[int]) -> Dict[str, str]:
        """解释X-bar S图结果"""
        return self._interpret_xbar_r_chart(xbar_outliers, s_outliers)
    
    def _interpret_imr_chart(self, x_outliers: List[int], mr_outliers: List[int], 
                           runs_analysis: Dict[str, Any]) -> Dict[str, str]:
        """解释I-MR图结果"""
        total_outliers = len(x_outliers) + len(mr_outliers)
        
        if total_outliers == 0 and not runs_analysis['runs_test_significant']:
            return {
                'status': '受控',
                'message': '过程处于统计控制状态',
                'recommendation': '继续监控，保持当前过程设置'
            }
        elif runs_analysis['runs_test_significant']:
            return {
                'status': '模式异常',
                'message': '数据存在非随机模式',
                'recommendation': '检查数据收集方法、过程稳定性'
            }
        else:
            return {
                'status': '失控',
                'message': '过程存在异常点',
                'recommendation': '调查特殊原因，采取纠正措施'
            }
    
    def _interpret_p_chart(self, outliers: List[int], sample_size_variation: float) -> Dict[str, str]:
        """解释P图结果"""
        if len(outliers) == 0 and sample_size_variation < 0.25:
            return {
                'status': '受控',
                'message': '不合格品率过程处于控制状态',
                'recommendation': '继续监控，保持当前质量水平'
            }
        elif sample_size_variation >= 0.25:
            return {
                'status': '样本变异大',
                'message': '样本大小变异过大，影响控制图有效性',
                'recommendation': '标准化样本大小或考虑使用标准化控制图'
            }
        else:
            return {
                'status': '失控',
                'message': '不合格品率过程失控',
                'recommendation': '调查质量问题的根本原因'
            }
    
    def _interpret_c_chart(self, outliers: List[int], c_bar: float) -> Dict[str, str]:
        """解释C图结果"""
        if len(outliers) == 0:
            return {
                'status': '受控',
                'message': '缺陷数过程处于控制状态',
                'recommendation': '继续监控，保持当前质量水平'
            }
        elif c_bar < 1:
            return {
                'status': '低缺陷率',
                'message': '平均缺陷率很低，考虑使用U图',
                'recommendation': '评估是否需要使用单位缺陷率控制图'
            }
        else:
            return {
                'status': '失控',
                'message': '缺陷数过程失控',
                'recommendation': '调查缺陷产生的根本原因'
            }
    
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
    
    def _generate_capability_recommendations(self, cpk: float, ppk: float, 
                                           process_shift: float, normality_p: float) -> List[str]:
        """生成过程能力改进建议"""
        recommendations = []
        
        if cpk < 1.33:
            recommendations.append("过程能力不足，需要减少过程变异")
        
        if process_shift > 15:
            recommendations.append("过程存在明显偏移，需要调整过程中心")
        
        if normality_p < 0.05:
            recommendations.append("数据不服从正态分布，考虑数据转换或非参数方法")
        
        if ppk < cpk * 0.8:
            recommendations.append("长期性能低于短期能力，需要改进过程稳定性")
        
        if not recommendations:
            recommendations.append("过程能力良好，继续保持当前水平")
        
        return recommendations