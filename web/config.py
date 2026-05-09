import os
from datetime import timedelta

class Config:
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'industrial-quality-stats-secret-key'
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB最大文件大小
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    # 数据导出配置
    EXPORT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
    
    # 缓存配置
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 性能配置
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    @staticmethod
    def init_app(app):
        # 确保上传和导出目录存在
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.EXPORT_FOLDER, exist_ok=True)