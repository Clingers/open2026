"""
中文字体配置模块
解决 matplotlib 中文显示问题
"""

import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 标记是否已配置，避免重复
_FONT_CONFIGURED = False

def configure_chinese_font():
    """
    配置matplotlib中文字体，只需调用一次。
    返回所选字体名称或配置状态
    """
    global _FONT_CONFIGURED
    if _FONT_CONFIGURED:
        return plt.rcParams.get('font.sans-serif', [''])[0]

    # 常见中文字体列表
    chinese_fonts = [
        'Source Han Sans HW SC', '思源黑体 HW SC',  # 新增：优先使用思源黑体
        'Noto Sans CJK SC', 'Noto Serif CJK SC',
        'WenQuanYi Micro Hei', 'WenQuanYi Zen Hei',
        'SimHei', 'SimSun', 'Microsoft YaHei', 'NSimSun',
        'DejaVu Sans', 'DejaVu Sans CJK',
        'Arial Unicode MS', 'Lucida Sans Unicode',
    ]

    # 首先尝试加载项目本地字体（最优先）
    project_font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    if os.path.exists(project_font_dir):
        try:
            # 加载 OTF 目录下的所有字体
            otf_dir = os.path.join(project_font_dir, 'OTF')
            if os.path.exists(otf_dir):
                for root, dirs, files in os.walk(otf_dir):
                    for file in files:
                        if file.lower().endswith(('.ttf', '.otf')):
                            font_path = os.path.join(root, file)
                            try:
                                fm.fontManager.addfont(font_path)
                            except Exception:
                                pass
                # 重新构建字体缓存
                fm._load_fontmanager()
        except Exception:
            pass

    # 尝试查找系统可用字体
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    selected_font = None

    for font_name in chinese_fonts:
        if font_name in available_fonts:
            selected_font = font_name
            break

    # 如果仍未找到，尝试加载用户目录字体
    if not selected_font:
        user_font_path = os.path.expanduser('~/.local/share/fonts/wqy-microhei.ttf')
        if os.path.exists(user_font_path):
            try:
                fm.fontManager.addfont(user_font_path)
                # 重新构建字体缓存（避免全局影响，尽量局部）
                fm._load_fontmanager()
                # 再次检查
                available_fonts = [f.name for f in fm.fontManager.ttflist]
                for font_name in ['WenQuanYi Micro Hei', 'WenQuanYi MicroHei']:
                    if font_name in available_fonts:
                        selected_font = font_name
                        break
            except Exception:
                pass

    if selected_font:
        plt.rcParams['font.family'] = ['sans-serif']
        plt.rcParams['font.sans-serif'] = [selected_font] + plt.rcParams.get('font.sans-serif', [])
    else:
        plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False
    _FONT_CONFIGURED = True
    return selected_font or 'DejaVu Sans (may miss Chinese chars)'
