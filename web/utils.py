# Web UI 工具函数
# 2026-03-26

import os
import sys
import subprocess
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from flask import jsonify
from core.insights import InsightGenerator


# ============ 常量配置 ============

DEFAULT_SUBGROUP_SIZE = 5

# SPC 控制图系数 (子组大小 2-10)
A2_TABLE = {
    2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483,
    7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308
}
D3_TABLE = {
    2: 0, 3: 0, 4: 0, 5: 0, 6: 0.076, 7: 0.136,
    8: 0.184, 9: 0.223, 10: 0.256
}
D4_TABLE = {
    2: 3.267, 3: 2.575, 4: 2.282, 5: 2.115, 6: 2.004,
    7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777
}


# ============ 类型定义 ============

class AnalysisRequest:
    """分析请求参数"""
    filename: str
    column: str
    type: str
    chart_type: Optional[str] = None
    x: Optional[str] = None
    y: Optional[str] = None
    lsl: Optional[float] = None
    usl: Optional[float] = None
    subgroup_size: int = DEFAULT_SUBGROUP_SIZE


def standardize_error_response(error_message: str, status_code: int = 500):
    """标准化错误响应"""
    return jsonify({'error': error_message}), status_code


def run_subprocess_command(cmd: List[str], env: Dict[str, str], cwd: str) -> subprocess.CompletedProcess:
    """执行子进程命令（统一入口）"""
    return subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=cwd)


def collect_output_files(output_dir: str, extensions: List[str] = None) -> List[Dict[str, str]]:
    """收集输出目录中的文件"""
    if extensions is None:
        extensions = ['.png', '.pdf']
    
    files = []
    for f in os.listdir(output_dir):
        if any(f.endswith(ext) for ext in extensions):
            files.append({
                'name': f,
                'url': f'/download/{os.path.basename(output_dir)}/{f}'
            })
    return files


def load_dataframe(filepath: str) -> pd.DataFrame:
    """加载并规范化 CSV 数据"""
    df = pd.read_csv(filepath, comment='#')
    df.columns = df.columns.str.strip()
    return df


def get_column_data(df: pd.DataFrame, column: str) -> List[float]:
    """获取列数据（去除空值）"""
    if column not in df.columns:
        raise ValueError(f"列 '{column}' 不存在")
    return df[column].dropna().tolist()


# ============ SPC 计算函数 ============

def calculate_spc_parameters(data: List[float], subgroup_size: int) -> Dict[str, float]:
    """计算 SPC 控制图参数"""
    n = subgroup_size
    num_subgroups = len(data) // n
    
    # 构建子组
    subgroups = []
    if num_subgroups >= 2:
        subgroups = [data[i*n:(i+1)*n] for i in range(num_subgroups)]
    else:
        # 如果数据点少，按指定大小分组（至少2个点）
        for i in range(0, len(data), n):
            subgroup = data[i:i+n]
            if len(subgroup) >= 2:
                subgroups.append(subgroup)
    
    if not subgroups:
        raise ValueError("数据不足以计算SPC（至少需要2个数据点）")
    
    subgroup_means = [np.mean(s) for s in subgroups]
    subgroup_ranges = [np.max(s) - np.min(s) for s in subgroups]
    
    X_bar = np.mean(subgroup_means)
    R_bar = np.mean(subgroup_ranges)
    
    A2 = A2_TABLE.get(n, 0.577)
    D3 = D3_TABLE.get(n, 0)
    D4 = D4_TABLE.get(n, 2.115)
    
    return {
        'X_bar': X_bar,
        'R_bar': R_bar,
        'UCL_X': X_bar + A2 * R_bar,
        'LCL_X': X_bar - A2 * R_bar,
        'UCL_R': D4 * R_bar,
        'LCL_R': D3 * R_bar,
        'subgroup_means': subgroup_means,
        'subgroup_ranges': subgroup_ranges
    }


# ============ 洞察生成函数 ============

def generate_assess_insight(data: List[float], column: str, chart_type: str) -> str:
    """生成评估图洞察文本"""
    insight = InsightGenerator.assess_insight(data, column, chart_type)
    return format_insight_text("📊 数据洞察", insight)


def generate_spc_insight(spc_data: Dict[str, Any]) -> str:
    """生成 SPC 洞察文本（支持 X-R, X-S, np）"""
    # 必要参数
    subgroup_means = spc_data.get('subgroup_means', [])
    
    # 构造可选参数
    kwargs = {}
    if 'subgroup_ranges' in spc_data:
        kwargs['subgroup_ranges'] = spc_data['subgroup_ranges']
    if 'subgroup_stds' in spc_data:
        kwargs['subgroup_stds'] = spc_data['subgroup_stds']
    
    # 组装 chart_data (X-R 或 X-S 所需的参数)
    chart_data_keys = [
        'chart_type', 'subgroup_size',
        'X_bar', 'R_bar', 'UCL_X', 'LCL_X', 'UCL_R', 'LCL_R',
        'S_bar', 'UCL_S', 'LCL_S',
        'np_bar', 'UCL', 'LCL'
    ]
    chart_data = {k: spc_data[k] for k in chart_data_keys if k in spc_data}
    kwargs['chart_data'] = chart_data
    
    insight = InsightGenerator.spc_insight(subgroup_means, **kwargs)
    return format_insight_text("📈 SPC控制图分析", insight)


def generate_regression_insight(x_data: List[float], y_data: List[float], 
                               regression_results: Dict[str, Any]) -> str:
    """生成回归分析洞察文本"""
    insight = InsightGenerator.regression_insight(x_data, y_data, regression_results)
    return format_insight_text("📉 回归分析", insight)


def generate_capability_insight(data: List[float], lsl: Optional[float], 
                               usl: Optional[float], cap_results: Dict[str, float]) -> str:
    """生成过程能力洞察文本"""
    insight = InsightGenerator.capability_insight(data, lsl, usl, cap_results)
    return format_insight_text("🎯 过程能力分析", insight)


def generate_heatmap_insight(df: pd.DataFrame) -> str:
    """生成热力图洞察文本"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        return "⚠️ 数据中数值列不足，无法生成相关性洞察"
    
    corr_matrix = df[numeric_cols].corr(method='pearson')
    
    # 找出强相关
    strong_corrs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            col1 = corr_matrix.columns[i]
            col2 = corr_matrix.columns[j]
            corr_val = corr_matrix.iloc[i, j]
            if abs(corr_val) >= 0.7:
                direction = "正相关" if corr_val > 0 else "负相关"
                strong_corrs.append({
                    'pair': f"{col1} - {col2}",
                    'corr': corr_val,
                    'dir': direction
                })
    
    strong_corrs.sort(key=lambda x: abs(x['corr']), reverse=True)
    
    highlights = [f"基于 {len(numeric_cols)} 个数值变量计算相关性矩阵"]
    if strong_corrs:
        highlights.append(f"发现 {len(strong_corrs)} 对强相关 (|r|≥0.7):")
        for sc in strong_corrs[:3]:
            highlights.append(f"  • {sc['pair']}: r={sc['corr']:.3f} ({sc['dir']})")
    else:
        highlights.append("未发现强相关关系 (|r|≥0.7)")
    
    summary = f"热力图分析完成。基于 {len(numeric_cols)} 个变量计算相关性矩阵。"
    
    # 直接构造格式化的文本
    text = f"🔥 相关性分析\n{summary}\n\n关键发现:\n"
    text += "\n".join(highlights)
    return text


def format_insight_text(title: str, insight) -> str:
    """格式化洞察文本为标准格式"""
    text = f"{title}\n{insight.summary}\n\n关键发现:\n"
    text += "\n".join(f"  • {h}" for h in insight.highlights)
    if hasattr(insight, 'recommendations') and insight.recommendations:
        text += "\n\n建议:\n"
        text += "\n".join(f"  🔧 {r}" for r in insight.recommendations)
    return text
