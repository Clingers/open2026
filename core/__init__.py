# 工业质量统计核心模块

# 自动配置中文字体（避免重复）
try:
    from .font_config import configure_chinese_font
    configure_chinese_font()
except Exception:
    pass  # 字体配置失败不影响核心功能

# 确保字体配置在所有图表模块使用前已完成
import matplotlib
matplotlib.use('Agg')