from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
from datetime import datetime
import traceback

# 导入工具类
from utils.file_handler import FileHandler
from utils.data_processor import DataProcessor
from utils.statistics import StatisticsAnalyzer
from utils.visualization import VisualizationGenerator
from utils.export_handler import ExportHandler
from utils.realtime_monitor import RealtimeDataMonitor
from utils.spc_charts import SPCChartGenerator
from utils.quality_statistics import QualityStatisticsAnalyzer

# 导入API蓝图
from api.spc import spc_bp
from api.quality import quality_bp

app = Flask(__name__)
app.config.from_object('config')

# 注册API蓝图
app.register_blueprint(spc_bp)
app.register_blueprint(quality_bp)

# 初始化工具类
file_handler = FileHandler()
data_processor = DataProcessor()
statistics_analyzer = StatisticsAnalyzer()
visualization_generator = VisualizationGenerator()
export_handler = ExportHandler()
realtime_monitor = RealtimeDataMonitor()
spc_generator = SPCChartGenerator()
quality_analyzer = QualityStatisticsAnalyzer()

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """仪表板页面"""
    return render_template('dashboard.html')

@app.route('/mobile')
def mobile():
    """移动端页面"""
    return render_template('mobile.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '文件名为空'
            }), 400
        
        result = file_handler.save_file(file)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'文件上传失败: {str(e)}'
        }), 500

@app.route('/api/columns', methods=['POST'])
def get_columns():
    """获取数据列信息"""
    try:
        data = request.get_json()
        if not data or 'file_path' not in data:
            return jsonify({
                'success': False,
                'error': '缺少文件路径参数'
            }), 400
        
        result = data_processor.get_column_info(data['file_path'])
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取列信息失败: {str(e)}'
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    """数据分析接口"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        file_path = data.get('file_path')
        selected_columns = data.get('columns', [])
        analysis_type = data.get('analysis_type', 'basic')
        
        if not file_path:
            return jsonify({
                'success': False,
                'error': '缺少文件路径参数'
            }), 400
        
        # 根据分析类型执行不同的分析
        if analysis_type == 'basic':
            result = statistics_analyzer.basic_analysis(file_path, selected_columns)
        elif analysis_type == 'advanced':
            result = statistics_analyzer.advanced_analysis(file_path, selected_columns)
        elif analysis_type == 'correlation':
            result = statistics_analyzer.correlation_analysis(file_path, selected_columns)
        elif analysis_type == 'outlier':
            result = statistics_analyzer.outlier_detection(file_path, selected_columns)
        else:
            return jsonify({
                'success': False,
                'error': f'不支持的分析类型: {analysis_type}'
            }), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'数据分析失败: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/visualize', methods=['POST'])
def visualize_data():
    """数据可视化接口"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        file_path = data.get('file_path')
        chart_type = data.get('chart_type', 'bar')
        x_column = data.get('x_column')
        y_column = data.get('y_column')
        
        if not file_path:
            return jsonify({
                'success': False,
                'error': '缺少文件路径参数'
            }), 400
        
        result = visualization_generator.generate_chart(
            file_path, chart_type, x_column, y_column
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'数据可视化失败: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/export', methods=['POST'])
def export_results():
    """结果导出接口"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        export_format = data.get('format', 'excel')
        analysis_results = data.get('results', {})
        
        if export_format not in ['excel', 'pdf']:
            return jsonify({
                'success': False,
                'error': '不支持的导出格式'
            }), 400
        
        result = export_handler.export_results(analysis_results, export_format)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'结果导出失败: {str(e)}'
        }), 500

@app.route('/api/realtime/status', methods=['GET'])
def get_realtime_status():
    """获取实时监控状态"""
    try:
        result = realtime_monitor.get_status()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取监控状态失败: {str(e)}'
        }), 500

@app.route('/api/realtime/alerts', methods=['GET', 'POST'])
def manage_alerts():
    """管理实时告警"""
    try:
        if request.method == 'GET':
            result = realtime_monitor.get_alerts()
        else:
            data = request.get_json()
            result = realtime_monitor.configure_alerts(data)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'告警管理失败: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'success': True,
        'message': '工业质量统计工具API服务正常运行',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'features': [
            '文件上传和解析',
            '基础统计分析',
            '数据可视化',
            '结果导出',
            '实时监控',
            'SPC控制图',
            '质量统计分析',
            '过程能力分析'
        ]
    })

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'success': False,
        'error': '接口不存在',
        'message': '请检查API路径是否正确'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'success': False,
        'error': '服务器内部错误',
        'message': '请稍后重试或联系管理员'
    }), 500

if __name__ == '__main__':
    # 确保必要的目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)
    
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )