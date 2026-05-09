"""
质量统计分析API接口
提供方差分析、回归分析、Gage R&R分析等质量统计功能的REST API接口
"""

from flask import Blueprint, request, jsonify
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import traceback

from utils.quality_statistics import QualityStatisticsAnalyzer

quality_bp = Blueprint('quality', __name__, url_prefix='/api/quality')
analyzer = QualityStatisticsAnalyzer()

@quality_bp.route('/anova', methods=['POST'])
def perform_anova():
    """执行方差分析 (ANOVA)"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        # 验证必需参数
        required_fields = ['factor_col', 'response_col', 'data']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需参数: {field}'
                }), 400
        
        # 转换数据为DataFrame
        try:
            df = pd.DataFrame(data['data'])
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'数据格式错误: {str(e)}'
            }), 400
        
        # 验证数据列存在
        factor_col = data['factor_col']
        response_col = data['response_col']
        
        if factor_col not in df.columns:
            return jsonify({
                'success': False,
                'error': f'因子列 {factor_col} 不存在'
            }), 400
        
        if response_col not in df.columns:
            return jsonify({
                'success': False,
                'error': f'响应变量列 {response_col} 不存在'
            }), 400
        
        # 验证响应变量数据类型
        if not pd.api.types.is_numeric_dtype(df[response_col]):
            return jsonify({
                'success': False,
                'error': f'响应变量列 {response_col} 必须是数值类型'
            }), 400
        
        # 检查因子水平数量
        factor_levels = df[factor_col].nunique()
        if factor_levels < 2:
            return jsonify({
                'success': False,
                'error': '方差分析需要至少2个因子水平'
            }), 400
        
        # 检查每个组的样本量
        group_counts = df.groupby(factor_col)[response_col].count()
        min_group_size = group_counts.min()
        if min_group_size < 2:
            return jsonify({
                'success': False,
                'error': f'每个因子水平至少需要2个观测值，最小样本量为 {min_group_size}'
            }), 400
        
        # 执行方差分析
        result = analyzer.perform_anova(df, factor_col, response_col)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@quality_bp.route('/regression', methods=['POST'])
def perform_regression():
    """执行回归分析"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        # 验证必需参数
        required_fields = ['x_cols', 'y_col', 'data']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需参数: {field}'
                }), 400
        
        # 验证x_cols是列表
        x_cols = data['x_cols']
        if not isinstance(x_cols, list) or len(x_cols) == 0:
            return jsonify({
                'success': False,
                'error': 'x_cols必须是包含至少一个元素的列表'
            }), 400
        
        # 转换数据为DataFrame
        try:
            df = pd.DataFrame(data['data'])
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'数据格式错误: {str(e)}'
            }), 400
        
        y_col = data['y_col']
        
        # 验证所有列存在
        missing_cols = []
        for col in x_cols + [y_col]:
            if col not in df.columns:
                missing_cols.append(col)
        
        if missing_cols:
            return jsonify({
                'success': False,
                'error': f'列不存在: {", ".join(missing_cols)}'
            }), 400
        
        # 验证数值列数据类型
        for col in x_cols + [y_col]:
            if not pd.api.types.is_numeric_dtype(df[col]):
                return jsonify({
                    'success': False,
                    'error': f'列 {col} 必须是数值类型'
                }), 400
        
        # 检查样本量
        n_samples = len(df.dropna(subset=x_cols + [y_col]))
        if n_samples < len(x_cols) + 2:
            return jsonify({
                'success': False,
                'error': f'样本量不足，需要至少 {len(x_cols) + 2} 个有效样本，当前有 {n_samples} 个'
            }), 400
        
        # 执行回归分析
        result = analyzer.perform_regression_analysis(df, x_cols, y_col)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@quality_bp.route('/gage-rnr', methods=['POST'])
def perform_gage_rnr():
    """执行测量系统分析 (Gage R&R)"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        # 验证必需参数
        required_fields = ['part_col', 'operator_col', 'measurement_col', 'data']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需参数: {field}'
                }), 400
        
        # 转换数据为DataFrame
        try:
            df = pd.DataFrame(data['data'])
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'数据格式错误: {str(e)}'
            }), 400
        
        # 验证数据列存在
        part_col = data['part_col']
        operator_col = data['operator_col']
        measurement_col = data['measurement_col']
        
        required_cols = [part_col, operator_col, measurement_col]
        for col in required_cols:
            if col not in df.columns:
                return jsonify({
                    'success': False,
                    'error': f'列 {col} 不存在'
                }), 400
        
        # 验证测量值数据类型
        if not pd.api.types.is_numeric_dtype(df[measurement_col]):
            return jsonify({
                'success': False,
                'error': f'测量值列 {measurement_col} 必须是数值类型'
            }), 400
        
        # 检查数据完整性
        n_parts = df[part_col].nunique()
        n_operators = df[operator_col].nunique()
        
        if n_parts < 5:
            return jsonify({
                'success': False,
                'error': f'建议至少5个部件进行Gage R&R分析，当前有 {n_parts} 个'
            }), 400
        
        if n_operators < 2:
            return jsonify({
                'success': False,
                'error': f'需要至少2个操作员进行Gage R&R分析，当前有 {n_operators} 个'
            }), 400
        
        # 检查重复测量次数
        replicates_per_combination = len(df) // (n_parts * n_operators)
        if replicates_per_combination < 2:
            return jsonify({
                'success': False,
                'error': f'需要至少2次重复测量，当前每个组合有 {replicates_per_combination} 次测量'
            }), 400
        
        # 执行Gage R&R分析
        result = analyzer.perform_gage_rnr(df, part_col, operator_col, measurement_col)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@quality_bp.route('/capability', methods=['POST'])
def perform_capability_analysis():
    """执行过程能力分析"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        # 验证必需参数
        required_fields = ['data', 'usl', 'lsl']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需参数: {field}'
                }), 400
        
        # 验证规格限
        try:
            usl = float(data['usl'])
            lsl = float(data['lsl'])
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': '规格限必须是数值'
            }), 400
        
        if usl <= lsl:
            return jsonify({
                'success': False,
                'error': '上规格限必须大于下规格限'
            }), 400
        
        # 获取可选参数
        target = data.get('target')
        if target is not None:
            try:
                target = float(target)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': '目标值必须是数值'
                }), 400
        
        # 转换数据为Series
        try:
            if isinstance(data['data'], list):
                # 如果直接提供数据列表
                series = pd.Series(data['data'])
            else:
                # 如果提供DataFrame格式数据
                df = pd.DataFrame(data['data'])
                value_col = data.get('value_col')
                
                if value_col:
                    if value_col not in df.columns:
                        return jsonify({
                            'success': False,
                            'error': f'数值列 {value_col} 不存在'
                        }), 400
                    series = df[value_col]
                else:
                    # 如果没有指定列，使用第一列数值列
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) == 0:
                        return jsonify({
                            'success': False,
                            'error': '未找到数值类型的列'
                        }), 400
                    series = df[numeric_cols[0]]
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'数据格式错误: {str(e)}'
            }), 400
        
        # 验证数据长度
        if len(series) < 30:
            return jsonify({
                'success': False,
                'error': f'过程能力分析建议至少30个数据点，当前有 {len(series)} 个'
            }), 400
        
        # 验证数据有效性
        if series.isnull().any():
            return jsonify({
                'success': False,
                'error': '数据包含空值，请先清理数据'
            }), 400
        
        if not pd.api.types.is_numeric_dtype(series):
            return jsonify({
                'success': False,
                'error': '数据必须是数值类型'
            }), 400
        
        # 执行过程能力分析
        result = analyzer.perform_capability_analysis(series, usl, lsl, target)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@quality_bp.route('/health', methods=['GET'])
def quality_health_check():
    """质量统计API健康检查"""
    return jsonify({
        'success': True,
        'message': '质量统计API服务正常运行',
        'available_analyses': [
            'anova',
            'regression',
            'gage-rnr',
            'capability'
        ],
        'api_version': '1.0.0',
        'supported_features': [
            '方差分析 (ANOVA)',
            '回归分析',
            '测量系统分析 (Gage R&R)',
            '过程能力分析'
        ]
    })