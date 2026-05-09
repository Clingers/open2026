import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
import mimetypes

class FileHandler:
    """文件处理工具类"""
    
    @staticmethod
    def allowed_file(filename):
        """检查文件类型是否允许"""
        if '.' not in filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in current_app.config['ALLOWED_EXTENSIONS']
    
    @staticmethod
    def get_file_mimetype(filename):
        """获取文件的MIME类型"""
        return mimetypes.guess_type(filename)[0]
    
    @staticmethod
    def generate_unique_filename(filename):
        """生成唯一的文件名"""
        extension = filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{extension}"
        return unique_name
    
    @staticmethod
    def save_uploaded_file(file, filename=None):
        """保存上传的文件"""
        if not filename:
            filename = FileHandler.generate_unique_filename(file.filename)
        
        safe_filename = secure_filename(filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(file_path)
        
        return {
            'original_filename': file.filename,
            'saved_filename': safe_filename,
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'mime_type': FileHandler.get_file_mimetype(file.filename)
        }
    
    @staticmethod
    def get_file_info(file_path):
        """获取文件信息"""
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'is_file': os.path.isfile(file_path)
        }
    
    @staticmethod
    def delete_file(file_path):
        """删除文件"""
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
    @staticmethod
    def validate_file_size(file):
        """验证文件大小"""
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        max_size = current_app.config['MAX_CONTENT_LENGTH']
        
        if file_size > max_size:
            return False, f"文件大小超过限制 ({file_size} > {max_size})"
        
        return True, "文件大小验证通过"
