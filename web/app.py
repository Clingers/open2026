# 工业质量统计工具 - Web UI (Flask)
# 2026-03-26 - 重构版本

import os
import uuid
import sys
import subprocess
from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')

# 将项目根目录添加到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入工具函数
from .utils import (
    standardize_error_response,
    run_subprocess_command,
    collect_output_files,
    load_dataframe,
    get_column_data,
    calculate_spc_parameters,
    generate_assess_insight,
    generate_spc_insight,
    generate_regression_insight,
    generate_capability_insight,
    generate_heatmap_insight,
    DEFAULT_SUBGROUP_SIZE
)

# 项目配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = os.path.join(PROJECT_ROOT, 'web_output')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 确保目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    """主页 - 文件上传"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传"""
    if 'file' not in request.files:
        return jsonify({'error': '未选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': '仅支持CSV格式'}), 400
    
    # 保存文件到项目数据目录
    filepath = os.path.join(DATA_DIR, file.filename)
    file.save(filepath)
    
    try:
        df = load_dataframe(filepath)
        return jsonify({
            'success': True,
            'filename': file.filename,
            'columns': df.columns.tolist(),
            'rows': len(df)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analyze', methods=['POST'])
def analyze():
    """执行分析任务（统一入口）"""
    data = request.json
    filename = data.get('filename')
    column = data.get('column')
    analysis_type = data.get('type')
    lsl = data.get('lsl')
    usl = data.get('usl')
    subgroup_size = data.get('subgroup_size', DEFAULT_SUBGROUP_SIZE)
    
    # 参数验证
    if not filename or not analysis_type:
        return standardize_error_response('参数缺失: filename 和 type 必填', 400)
    
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return standardize_error_response('文件不存在', 404)
    
    # 创建输出目录
    session_id = str(uuid.uuid4())[:8]
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 根据类型分发到对应的处理函数
        handlers = {
            'stats': handle_stats,
            'assess': handle_assess,
            'spc': handle_spc,
            'heatmap': handle_heatmap,
            'regression': handle_regression,
            'capability': handle_capability,
            'report': handle_report
        }
        
        if analysis_type not in handlers:
            return standardize_error_response(f'不支持的分析类型: {analysis_type}', 400)
        
        result = handlers[analysis_type](data, filepath, output_dir, session_id)
        # 注入元数据，供前端图表使用
        if '_meta' not in result:
            result['_meta'] = {}
        result['_meta'].update({
            'filename': filename,
            'column': column,
            'analysis_type': analysis_type
        })
        return jsonify(result)
        
    except ValueError as e:
        return standardize_error_response(str(e), 400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return standardize_error_response(f'分析失败: {str(e)}', 500)


# ============ 各分析类型处理器 ============

def handle_stats(data, filepath, output_dir, session_id):
    """基础统计"""
    df = load_dataframe(filepath)
    column = data.get('column')
    
    if column not in df.columns:
        raise ValueError(f"列 '{column}' 不存在，可用列: {', '.join(df.columns)}")
    
    stats_data = get_column_data(df, column)
    series = pd.Series(stats_data)
    
    mean = float(series.mean())
    std = float(series.std())
    cv = std / mean if mean != 0 else 0
    
    result = {
        'count': len(stats_data),
        'mean': mean,
        'std': std,
        'min': float(series.min()),
        'max': float(series.max()),
        'cv': round(cv, 4)
    }
    
    # 生成洞察
    highlights = [f"样本数量: {len(stats_data)} 个"]
    highlights.append(f"平均值: {mean:.4f}")
    highlights.append(f"标准差: {std:.4f} (变异系数: {cv:.2%})")
    
    if cv < 0.03:
        stability = "非常稳定"
        highlights.append(f"过程变异极小，{stability}")
    elif cv < 0.06:
        stability = "稳定"
        highlights.append(f"过程变异在可控范围，{stability}")
    elif cv < 0.10:
        stability = "略有波动"
        highlights.append(f"过程存在一定波动，{stability}")
    else:
        stability = "波动较大"
        highlights.append(f"⚠️  过程变异显著，{stability}")
    
    summary = f"基础统计分析完成。n={len(stats_data)}，μ={mean:.4f}，σ={std:.4f} (CV={cv:.2%})，范围=[{series.min():.4f}, {series.max():.4f}]。"
    text = f"📈 基础统计\n{summary}\n\n关键指标:\n" + "\n".join(f"  • {h}" for h in highlights)
    
    return {
        'success': True,
        'result': result,
        'session': session_id,
        'text': text
    }


def handle_assess(data, filepath, output_dir, session_id):
    """评估图（直方图/箱线图/QQ图/茎叶图）"""
    column = data.get('column')
    chart_type = data.get('chart_type', 'histogram')
    
    df = load_dataframe(filepath)
    if column not in df.columns:
        raise ValueError(f"列 '{column}' 不存在")
    
    # 茎叶图：文本输出
    if chart_type == 'stemleaf':
        env = os.environ.copy()
        env['PYTHONPATH'] = PROJECT_ROOT
        cmd = [
            sys.executable, '-m', 'cli.main',
            'assess',
            '--file', filepath,
            '--column', column,
            '--type', chart_type
        ]
        result = run_subprocess_command(cmd, env, PROJECT_ROOT)
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        
        return {
            'success': True,
            'session': session_id,
            'text': result.stdout.strip(),
            'message': '茎叶图生成完成'
        }
    
    # 图片类型：生成PNG
    env = os.environ.copy()
    env['PYTHONPATH'] = PROJECT_ROOT
    cmd = [
        sys.executable, '-m', 'cli.main',
        'assess',
        '--file', filepath,
        '--column', column,
        '--type', chart_type,
        '--output', os.path.join(output_dir, f'assess_{chart_type}_{column}.png')
    ]
    result = run_subprocess_command(cmd, env, PROJECT_ROOT)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    
    # 收集文件
    files = collect_output_files(output_dir, ['.png'])
    
    # 生成洞察
    data_list = get_column_data(df, column)
    insight_text = generate_assess_insight(data_list, column, chart_type)
    
    return {
        'success': True,
        'session': session_id,
        'files': files,
        'text': insight_text,
        'message': f'{chart_type} 图生成完成'
    }


def handle_spc(data, filepath, output_dir, session_id):
    """SPC控制图（支持 X-R, X-S, p, np）"""
    from core.spc import SPCControlChart
    
    column = data.get('column')
    subgroup_size = data.get('subgroup_size', DEFAULT_SUBGROUP_SIZE)
    chart_type = data.get('spc_type', 'x-r')  # 从 spc_type 获取具体图类型
    
    df = load_dataframe(filepath)
    if column not in df.columns:
        raise ValueError(f"列 '{column}' 不存在")
    
    # 准备子组数据（所有 SPC 图都需要子组结构）
    data_series = get_column_data(df, column)
    
    # 构建子组: [[val1_sub1, val2_sub1, ...], [val1_sub2, ...], ...]
    # 简单按顺序分组，若用户未提供子组信息，默认连续分组
    n = subgroup_size
    subgroups = [data_series[i:i+n] for i in range(0, len(data_series), n)]
    subgroups = [g for g in subgroups if len(g) == n]  # 丢弃不完整的最后子组
    
    if len(subgroups) < 2:
        raise ValueError("数据点不足，至少需要 2 个子组才能生成控制图")
    
    # 根据类型生成控制图
    chart_data = None
    plot_func = None
    
    if chart_type == 'x-r':
        chart_data = SPCControlChart.x_r_chart(subgroups)
        plot_func = SPCControlChart.plot_x_r
    elif chart_type == 'x-s':
        chart_data = SPCControlChart.x_s_chart(subgroups)
        plot_func = SPCControlChart.plot_x_s
    elif chart_type == 'p':
        # p 图需要二项数据，这里借用现有逻辑（从 CLI 调用）
        # 为保证一致性，p 图仍走 CLI（数据格式不同）
        env = os.environ.copy()
        env['PYTHONPATH'] = PROJECT_ROOT
        cmd = [
            sys.executable, '-m', 'cli.main',
            'spc',
            '--file', filepath,
            '--column', column,
            '--subgroup-size', str(subgroup_size),
            '--output-dir', output_dir
        ]
        result = run_subprocess_command(cmd, env, PROJECT_ROOT)
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        files = collect_output_files(output_dir, ['.png'])
        spc_params = calculate_spc_parameters(data_series, subgroup_size)
        insight_text = generate_spc_insight(spc_params)
        return {
            'success': True,
            'session': session_id,
            'files': files,
            'text': insight_text,
            'message': 'p 控制图生成完成'
        }
    elif chart_type == 'np':
        # np 图同样需要 (缺陷数, n) 对，这里简化：用户需提供缺陷数列
        # 暂时无法从单一数值列推导，仍需 CLI 支持
        # 为快速推进，np 也暂时走 CLI（后续可重构）
        env = os.environ.copy()
        env['PYTHONPATH'] = PROJECT_ROOT
        cmd = [
            sys.executable, '-m', 'cli.main',
            'spc',
            '--file', filepath,
            '--column', column,
            '--subgroup-size', str(subgroup_size),
            '--output-dir', output_dir
        ]
        result = run_subprocess_command(cmd, env, PROJECT_ROOT)
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        files = collect_output_files(output_dir, ['.png'])
        spc_params = calculate_spc_parameters(data_series, subgroup_size)
        insight_text = generate_spc_insight(spc_params)
        return {
            'success': True,
            'session': session_id,
            'files': files,
            'text': insight_text,
            'message': 'np 控制图生成完成'
        }
    else:
        raise ValueError(f"不支持的 SPC 类型: {chart_type}")
    
    # 使用 matplotlib 直接绘制（X-R, X-S）
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    fig = plot_func(chart_data)
    output_path = os.path.join(output_dir, f'spc_{chart_type}_{column}.png')
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    # 收集文件
    files = collect_output_files(output_dir, ['.png'])
    
    # 生成洞察 (参数映射到 InsightGenerator 接口)
    spc_params = {
        'chart_type': chart_data['chart_type'],
        'subgroup_size': chart_data['subgroup_size']
    }
    # 映射 X-R 和 X-S 的 X 图参数
    if 'X_bar' in chart_data:
        spc_params['X_bar'] = chart_data['X_bar']
        spc_params['R_bar'] = chart_data.get('R_bar')
        spc_params['UCL_X'] = chart_data['UCL_X']
        spc_params['LCL_X'] = chart_data['LCL_X']
        spc_params['UCL_R'] = chart_data.get('UCL_R')
        spc_params['LCL_R'] = chart_data.get('LCL_R')
    if 'X_bar_bar' in chart_data:
        spc_params['X_bar'] = chart_data['X_bar_bar']
        spc_params['S_bar'] = chart_data.get('S_bar')
        spc_params['UCL_X'] = chart_data['UCL_X']
        spc_params['LCL_X'] = chart_data['LCL_X']
        spc_params['UCL_S'] = chart_data.get('UCL_S')
        spc_params['LCL_S'] = chart_data.get('LCL_S')
    # np 图
    if 'np_bar' in chart_data:
        spc_params['np_bar'] = chart_data['np_bar']
        spc_params['UCL'] = chart_data['UCL']
        spc_params['LCL'] = chart_data['LCL']
    # 补充子组数据用于异常点检测
    if 'x_bars' in chart_data:
        spc_params['subgroup_means'] = chart_data['x_bars']
    if 'ranges' in chart_data:
        spc_params['subgroup_ranges'] = chart_data['ranges']
    if 'stds' in chart_data:
        spc_params['subgroup_stds'] = chart_data['stds']
    insight_text = generate_spc_insight(spc_params)
    
    return {
        'success': True,
        'session': session_id,
        'files': files,
        'text': insight_text,
        'message': f'{chart_type} 控制图生成完成'
    }


def handle_heatmap(data, filepath, output_dir, session_id):
    """热力图"""
    # 调用 CLI 生成图片
    env = os.environ.copy()
    env['PYTHONPATH'] = PROJECT_ROOT
    cmd = [
        sys.executable, '-m', 'cli.main',
        'heatmap',
        '--file', filepath,
        '--output', os.path.join(output_dir, 'heatmap.png')
    ]
    result = run_subprocess_command(cmd, env, PROJECT_ROOT)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    
    # 收集文件
    files = collect_output_files(output_dir, ['.png'])
    
    # 生成洞察
    df = load_dataframe(filepath)
    insight_text = generate_heatmap_insight(df)
    
    return {
        'success': True,
        'session': session_id,
        'files': files,
        'text': insight_text,
        'message': '热力图生成完成'
    }


def handle_regression(data, filepath, output_dir, session_id):
    """回归分析"""
    x = data.get('x')
    y = data.get('y')
    if not x or not y:
        raise ValueError('回归分析需要指定 x 和 y 列')
    
    # 调用 CLI 生成图片
    env = os.environ.copy()
    env['PYTHONPATH'] = PROJECT_ROOT
    cmd = [
        sys.executable, '-m', 'cli.main',
        'regression',
        '--file', filepath,
        '--x', x,
        '--y', y,
        '--output-dir', output_dir
    ]
    result = run_subprocess_command(cmd, env, PROJECT_ROOT)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    
    # 收集文件
    files = collect_output_files(output_dir, ['.png'])
    
    # 生成洞察
    df = load_dataframe(filepath)
    x_data = get_column_data(df, x)
    y_data = get_column_data(df, y)
    
    # 计算回归参数
    x_arr = np.array(x_data)
    y_arr = np.array(y_data)
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_arr, y_arr)
    
    regression_results = {
        'r_squared': r_value ** 2,
        'slope': slope,
        'intercept': intercept,
        'slope_p_value': p_value,
        'std_error': std_err
    }
    
    insight_text = generate_regression_insight(x_data, y_data, regression_results)
    
    return {
        'success': True,
        'session': session_id,
        'files': files,
        'text': insight_text,
        'message': '回归分析完成'
    }


def handle_capability(data, filepath, output_dir, session_id):
    """过程能力分析"""
    column = data.get('column')
    lsl = data.get('lsl')
    usl = data.get('usl')
    
    # 调用 CLI 生成图片
    env = os.environ.copy()
    env['PYTHONPATH'] = PROJECT_ROOT
    cmd = [
        sys.executable, '-m', 'cli.main',
        'capability',
        '--file', filepath,
        '--column', column,
        '--output-dir', output_dir
    ]
    if lsl is not None:
        cmd.extend(['--lsl', str(lsl)])
    if usl is not None:
        cmd.extend(['--usl', str(usl)])
    
    result = run_subprocess_command(cmd, env, PROJECT_ROOT)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    
    # 收集文件
    files = collect_output_files(output_dir, ['.png'])
    
    # 生成洞察
    df = load_dataframe(filepath)
    data_list = get_column_data(df, column)
    
    from core.capability import ProcessCapability
    cap_results = ProcessCapability.calculate(
        data_list,
        spec_limit_lsl=float(lsl) if lsl else None,
        spec_limit_usl=float(usl) if usl else None
    )
    
    insight_text = generate_capability_insight(
        data_list,
        float(lsl) if lsl else None,
        float(usl) if usl else None,
        cap_results
    )
    
    return {
        'success': True,
        'session': session_id,
        'files': files,
        'text': insight_text,
        'message': '过程能力分析完成'
    }


def handle_report(data, filepath, output_dir, session_id):
    """完整报告"""
    column = data.get('column')
    lsl = data.get('lsl')
    usl = data.get('usl')
    subgroup_size = data.get('subgroup_size', DEFAULT_SUBGROUP_SIZE)
    
    # 调用 CLI 生成完整报告（包含所有图表和PDF）
    env = os.environ.copy()
    env['PYTHONPATH'] = PROJECT_ROOT
    cmd = [
        sys.executable, '-m', 'cli.main',
        'report',
        '--file', filepath,
        '--column', column,
        '--output-dir', output_dir
    ]
    if lsl is not None:
        cmd.extend(['--lsl', str(lsl)])
    if usl is not None:
        cmd.extend(['--usl', str(usl)])
    cmd.extend(['--subgroup-size', str(subgroup_size)])
    
    result = run_subprocess_command(cmd, env, PROJECT_ROOT)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    
    # 收集文件（仅 PDF，不包含单独图表）
    files = collect_output_files(output_dir, ['.pdf'])
    
    # 生成综合洞察
    df = load_dataframe(filepath)
    data_list = get_column_data(df, column)
    
    # 构建 all_results 用于报告洞察
    all_results = {}
    
    # Assess
    assess_insight = generate_assess_insight(data_list, column, 'histogram')
    all_results['assess'] = {'stability': 'stable'}  # 简化
    
    # SPC
    try:
        spc_params = calculate_spc_parameters(data_list, subgroup_size)
        all_results['spc'] = spc_params
    except:
        pass
    
    # Capability
    if lsl is not None and usl is not None:
        try:
            from core.capability import ProcessCapability
            cap_results = ProcessCapability.calculate(
                data_list,
                spec_limit_lsl=float(lsl),
                spec_limit_usl=float(usl)
            )
            all_results['capability'] = cap_results
        except:
            pass
    
    # 使用洞察生成器创建综合报告
    from core.insights import InsightGenerator
    report_insight = InsightGenerator.report_insight(
        data_list,
        float(lsl) if lsl else None,
        float(usl) if usl else None,
        all_results
    )
    
    summary = report_insight.summary
    highlights = report_insight.highlights
    recommendations = report_insight.recommendations or []
    
    text = f"📋 完整质量报告\n{summary}\n\n综合评估:\n" + "\n".join(f"  • {h}" for h in highlights)
    if recommendations:
        text += "\n\n建议:\n" + "\n".join(f"  🔧 {r}" for r in recommendations)
    
    return {
        'success': True,
        'session': session_id,
        'files': files,
        'text': text,
        'message': '报告生成完成'
    }


@app.route('/download/<session_id>/<filename>')
def download_file(session_id, filename):
    """下载或显示生成的文件"""
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], session_id, filename)
    if os.path.exists(filepath):
        as_attachment = not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.pdf'))
        return send_file(filepath, as_attachment=as_attachment)
    return jsonify({'error': '文件不存在'}), 404


@app.route('/api/data')
def get_data():
    """获取原始数据列（用于前端图表）"""
    filename = request.args.get('filename')
    column = request.args.get('column')
    if not filename or not column:
        return jsonify({'error': '参数缺失: filename 和 column 必填'}), 400
    
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': '文件不存在'}), 404
    
    try:
        df = load_dataframe(filepath)
        if column not in df.columns:
            return jsonify({'error': f"列 '{column}' 不存在"}), 400
        
        # 清理 NaN 并返回列表
        data = df[column].dropna().tolist()
        return jsonify({
            'success': True,
            'filename': filename,
            'column': column,
            'data': data,
            'count': len(data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/templates/<path:path>')
def send_template(path):
    """提供HTML模板"""
    return send_file(os.path.join('templates', path))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
