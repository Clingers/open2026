"""
SPC图表API接口
提供SPC控制图生成和分析的REST API接口
"""

from flask import Blueprint, request, jsonify
import pandas as pd
import numpy as np
from typing import Dict, Any
import traceback

from utils.spc_charts import SPCChartGenerator

spc_bp = Blueprint('spc', __name__, url_prefix='/api/spc')
spc_generator = SPCChartGenerator()

@spc_bp.route('/xbar-r', methods=['POST'])
def generate_xbar_r_chart():
    """生成X-bar R控制图"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        # 验证必需参数
        required_fields = ['subgroup_col', 'value_col', 'data']
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
        subgroup_col = data['subgroup_col']
        value_col = data['value_col']
        
        if subgroup_col not in df.columns:
            return jsonify({
                'success': False,
                'error': f'子组列 {subgroup_col} 不存在'
            }), 400
        
        if value_col not in df.columns:
            return jsonify({
                'success': False,
                'error': f'数值列 {value_col} 不存在'
            }), 400
        
        # 验证数值列数据类型
        if not pd.api.types.is_numeric_dtype(df[value_col]):
            return jsonify({
                'success': False,
                'error': f'数值列 {value_col} 必须是数值类型'
            }), 400
        
        # 执行X-bar R图分析
        result = spc_generator.generate_xbar_r_chart(df, subgroup_col, value_col)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@spc_bp.route('/xbar-s', methods=['POST'])
def generate_xbar_s_chart():
    """生成X-bar S控制图"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        # 验证必需参数
        required_fields = ['subgroup_col', 'value_col', 'data']
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
        subgroup_col = data['subgroup_col']
        value_col = data['value_col']
        
        if subgroup_col not in df.columns:
            return jsonify({
                'success': False,
                'error': f'子组列 {subgroup_col} 不存在'
            }), 400
        
        if value_col not in df.columns:
            return jsonify({
                'success': False,
                'error': f'数值列 {value_col} 不存在'
            }), 400
        
        # 验证数值列数据类型
        if not pd.api.types.is_numeric_dtype(df[value_col]):
            return jsonify({
                'success': False,
                'error': f'数值列 {value_col} 必须是数值类型'
            }), 400
        
        # 执行X-bar S图分析
        result = spc_generator.generate_xbar_s_chart(df, subgroup_col, value_col)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@spc_bp.route('/individual-mr', methods=['POST'])
def generate_individual_mr_chart():
    """生成单值移动极差控制图"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        # 验证必需参数
        required_fields = ['value_col', 'data']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需参数: {field}'
                }), 400
        
        # 转换数据为Series
        try:
            if isinstance(data['data'], list):
                # 如果直接提供数据列表
                series = pd.Series(data['data'])
            else:
                # 如果提供DataFrame格式数据
                df = pd.DataFrame(data['data'])
                value_col = data['value_col']
                
                if value_col not in df.columns:
                    return jsonify({
                        'success': False,
                        'error': f'数值列 {value_col} 不存在'
                    }), 400
                
                if not pd.api.types.is_numeric_dtype(df[value_col]):
                    return jsonify({
                        'success': False,
                        'error': f'数值列 {value_col} 必须是数值类型'
                    }), 400
                
                series = df[value_col]
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'数据格式错误: {str(e)}'
            }), 400
        
        # 验证数据长度
        if len(series) < 3:
            return jsonify({
                'success': False,
                'error': 'I-MR图至少需要3个数据点'
            }), 400
        
        # 执行I-MR图分析
        result = spc_generator.generate_individual_moving_range_chart(series)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@spc_bp.route('/p-chart', methods=['POST'])
def generate_p_chart():
    """生成P控制图 (不合格品率图)"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        # 验证必需参数
        required_fields = ['subgroup_col', 'defect_col', 'data']
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
        subgroup_col = data['subgroup_col']
        defect_col = data['defect_col']
        
        if subgroup_col not in df.columns:
            return jsonify({
                'success': False,
                'error': f'子组列 {subgroup_col} 不存在'
            }), 400
        
        if defect_col not in df.columns:
            return jsonify({
                'success': False,
                'error': f'缺陷数列 {defect_col} 不存在'
            }), 400
        
        # 验证数值列数据类型
        if not pd.api.types.is_numeric_dtype(df[defect_col]):
            return jsonify({
                'success': False,
                'error': f'缺陷数列 {defect_col} 必须是数值类型'
            }), 400
        
        # 验证缺陷数不能为负
        if (df[defect_col] < 0).any():
            return jsonify({
                'success': False,
                'error': '缺陷数不能为负数'
            }), 400
        
        # 执行P图分析
        result = spc_generator.generate_p_chart(df, subgroup_col, defect_col)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@spc_bp.route('/c-chart', methods=['POST'])
def generate_c_chart():
    """生成C控制图 (缺陷数图)"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        # 验证必需参数
        required_fields = ['subgroup_col', 'defect_count_col', 'data']
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
        subgroup_col = data['subgroup_col']
        defect_count_col = data['defect_count_col']
        
        if subgroup_col not in df.columns:
            return jsonify({
                'success': False,
                'error': f'子组列 {subgroup_col} 不存在'
            }), 400
        
        if defect_count_col not in df.columns:
            return jsonify({
                'success': False,
                'error': f'缺陷计数列 {defect_count_col} 不存在'
            }), 400
        
        # 验证数值列数据类型
        if not pd.api.types.is_numeric_dtype(df[defect_count_col]):
            return jsonify({
                'success': False,
                'error': f'缺陷计数列 {defect_count_col} 必须是数值类型'
            }), 400
        
        # 验证缺陷数不能为负
        if (df[defect_count_col] < 0).any():
            return jsonify({
                'success': False,
                'error': '缺陷数不能为负数'
            }), 400
        
        # 执行C图分析
        result = spc_generator.generate_c_chart(df, subgroup_col, defect_count_col)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@spc_bp.route('/process-capability', methods=['POST'])
def calculate_process_capability():
    """计算过程能力指数"""
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
        usl = float(data['usl'])
        lsl = float(data['lsl'])
        
        if usl <= lsl:
            return jsonify({
                'success': False,
                'error': '上规格限必须大于下规格限'
            }), 400
        
        # 获取可选参数
        target = data.get('target')
        if target is not None:
            target = float(target)
        
        # 转换数据为Series
        try:
            if isinstance(data['data'], list):
                # 如果直接提供数据列表
                series = pd.Series(data['data'])
            else:
                # 如果提供DataFrame格式数据
                df = pd.DataFrame(data['data'])
                value_col = data.get('value_col', df.columns[0])  # 默认使用第一列
                
                if value_col not in df.columns:
                    return jsonify({
                        'success': False,
                        'error': f'数值列 {value_col} 不存在'
                    }), 400
                
                if not pd.api.types.is_numeric_dtype(df[value_col]):
                    return jsonify({
                        'success': False,
                        'error': f'数值列 {value_col} 必须是数值类型'
                    }), 400
                
                series = df[value_col]
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'数据格式错误: {str(e)}'
            }), 400
        
        # 验证数据长度
        if len(series) < 30:
            return jsonify({
                'success': False,
                'error': '过程能力分析建议至少30个数据点'
            }), 400
        
        # 执行过程能力分析
        result = spc_generator.calculate_process_capability(series, usl, lsl, target)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@spc_bp.route('/health', methods=['GET'])
def spc_health_check():
    """SPC API健康检查"""
    return jsonify({
        'success': True,
        'message': 'SPC API服务正常运行',
        'available_charts': [
            'xbar-r',
            'xbar-s', 
            'individual-mr',
            'p-chart',
            'c-chart'
        ],
        'available_analyses': [
            'process-capability'
        ]
    })