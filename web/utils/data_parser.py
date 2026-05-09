import pandas as pd
import os
from flask import current_app
from typing import Dict, List, Any
import json

class DataParser:
    """数据解析工具类"""
    
    @staticmethod
    def parse_csv(file_path: str, sample_rows: int = 5) -> Dict[str, Any]:
        """解析CSV文件"""
        try:
            # 读取CSV文件
            df = pd.read_csv(file_path)
            
            # 获取列信息
            columns = []
            for col in df.columns:
                # 推断数据类型
                dtype = str(df[col].dtype)
                if dtype.startswith('int') or dtype.startswith('float'):
                    col_type = 'numeric'
                elif dtype.startswith('datetime'):
                    col_type = 'datetime'
                else:
                    col_type = 'text'
                
                columns.append({
                    'name': col,
                    'type': col_type,
                    'dtype': dtype
                })
            
            # 获取数据预览
            preview = df.head(sample_rows).to_dict('records')
            
            # 获取基本统计信息
            stats = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum()
            }
            
            return {
                'success': True,
                'columns': columns,
                'preview': preview,
                'stats': stats,
                'file_path': file_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'CSV解析失败: {str(e)}'
            }
    
    @staticmethod
    def parse_excel(file_path: str, sample_rows: int = 5) -> Dict[str, Any]:
        """解析Excel文件"""
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 获取列信息
            columns = []
            for col in df.columns:
                # 推断数据类型
                dtype = str(df[col].dtype)
                if dtype.startswith('int') or dtype.startswith('float'):
                    col_type = 'numeric'
                elif dtype.startswith('datetime'):
                    col_type = 'datetime'
                else:
                    col_type = 'text'
                
                columns.append({
                    'name': col,
                    'type': col_type,
                    'dtype': dtype
                })
            
            # 获取数据预览
            preview = df.head(sample_rows).to_dict('records')
            
            # 获取基本统计信息
            stats = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum()
            }
            
            return {
                'success': True,
                'columns': columns,
                'preview': preview,
                'stats': stats,
                'file_path': file_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Excel解析失败: {str(e)}'
            }
    
    @staticmethod
    def get_columns_info(file_path: str) -> Dict[str, Any]:
        """获取文件列信息"""
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': '文件不存在'
            }
        
        # 根据文件扩展名选择解析方法
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.csv':
            return DataParser.parse_csv(file_path)
        elif ext in ['.xlsx', '.xls']:
            return DataParser.parse_excel(file_path)
        else:
            return {
                'success': False,
                'error': f'不支持的文件类型: {ext}'
            }
    
    @staticmethod
    def validate_data_types(df: pd.DataFrame, column_mapping: Dict[str, str]) -> Dict[str, Any]:
        """验证数据类型映射"""
        validation_results = {}
        
        for col, expected_type in column_mapping.items():
            if col not in df.columns:
                validation_results[col] = {
                    'valid': False,
                    'error': '列不存在'
                }
                continue
            
            actual_dtype = str(df[col].dtype)
            
            if expected_type == 'numeric':
                if actual_dtype.startswith('int') or actual_dtype.startswith('float'):
                    validation_results[col] = {'valid': True}
                else:
                    validation_results[col] = {
                        'valid': False,
                        'error': f'期望数值类型，实际为: {actual_dtype}'
                    }
            elif expected_type == 'datetime':
                if actual_dtype.startswith('datetime'):
                    validation_results[col] = {'valid': True}
                else:
                    validation_results[col] = {
                        'valid': False,
                        'error': f'期望日期时间类型，实际为: {actual_dtype}'
                    }
            else:
                validation_results[col] = {'valid': True}
        
        return validation_results
