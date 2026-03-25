# 工业质量统计工具 - Web UI (Flask)
# 2026-03-26

import os
import uuid
from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import sys
import json

# 将项目根目录添加到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli.main import stats, spc, assess, report as generate_report
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'web_output'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

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
    
    # 保存文件
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    
    # 读取列名
    try:
        df = pd.read_csv(filepath)
        columns = df.columns.tolist()
        return jsonify({
            'success': True,
            'filename': file.filename,
            'columns': columns,
            'rows': len(df)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analyze', methods=['POST'])
def analyze():
    """执行分析任务"""
    data = request.json
    filename = data.get('filename')
    column = data.get('column')
    analysis_type = data.get('type')  # 'stats', 'spc', 'assess', 'report'
    lsl = data.get('lsl')
    usl = data.get('usl')
    subgroup_size = data.get('subgroup_size', 5)
    
    if not filename or not column or not analysis_type:
        return jsonify({'error': '参数缺失'}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': '文件不存在'}), 404
    
    # 为每次请求创建临时输出目录
    session_id = str(uuid.uuid4())[:8]
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 执行分析（通过调用 CLI 函数）
        if analysis_type == 'stats':
            # 基础统计
            df = pd.read_csv(filepath)
            stats_data = df[column].dropna().tolist()
            result = {
                'count': len(stats_data),
                'mean': float(pd.Series(stats_data).mean()),
                'std': float(pd.Series(stats_data).std()),
                'min': float(pd.Series(stats_data).min()),
                'max': float(pd.Series(stats_data).max())
            }
            return jsonify({'success': True, 'result': result, 'session': session_id})
        
        elif analysis_type == 'report':
            # 生成完整报告
            # 使用 subprocess 调用命令行（简单方式）
            import subprocess
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
            if subgroup_size:
                cmd.extend(['--subgroup-size', str(subgroup_size)])
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(filepath))
            if result.returncode != 0:
                return jsonify({'error': result.stderr}), 500
            
            # 收集生成的文件
            files = []
            for f in os.listdir(output_dir):
                if f.endswith('.png') or f.endswith('.pdf'):
                    files.append({
                        'name': f,
                        'url': f'/download/{session_id}/{f}'
                    })
            
            return jsonify({
                'success': True,
                'session': session_id,
                'files': files,
                'message': '报告生成完成'
            })
        
        else:
            return jsonify({'error': '暂不支持该分析类型'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<session_id>/<filename>')
def download_file(session_id, filename):
    """下载生成的文件"""
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], session_id, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': '文件不存在'}), 404


@app.route('/templates/<path:path>')
def send_template(path):
    """提供HTML模板"""
    return send_file(os.path.join('templates', path))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
