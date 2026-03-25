# 工业质量统计 - PDF 报告生成模块
# 2026-03-26

import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib import colors


class PDFReport:
    """PDF 报告生成器（类似 Minitab 的质量报告）"""
    
    def __init__(self, output_path: str, title: str = "工业质量统计报告"):
        self.doc = SimpleDocTemplate(
            output_path, 
            pagesize=A4, 
            rightMargin=2*cm, 
            leftMargin=2*cm, 
            topMargin=2*cm, 
            bottomMargin=2*cm
        )
        self.story = []
        self.title = title
        self.styles = getSampleStyleSheet()
        self._add_custom_styles()
    
    def _add_custom_styles(self):
        """添加自定义样式"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            textColor=colors.HexColor('#1E3A8A'),
            alignment=TA_CENTER
        ))
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=12,
            textColor=colors.HexColor('#1E40AF')
        ))
        self.styles.add(ParagraphStyle(
            name='NormalCN',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            spaceAfter=6
        ))
    
    def add_title(self):
        """添加报告标题"""
        self.story.append(Paragraph(self.title, self.styles['CustomTitle']))
        self.story.append(Spacer(1, 0.5*cm))
        
        now = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        meta = f"<b>生成时间:</b> {now}<br/><b>工具版本:</b> Industrial Quality Stats v1.0.0-MVP"
        self.story.append(Paragraph(meta, self.styles['NormalCN']))
        self.story.append(Spacer(1, 1*cm))
    
    def add_section(self, title: str):
        """添加章节标题"""
        self.story.append(Paragraph(title, self.styles['SectionTitle']))
        self.story.append(Spacer(1, 0.3*cm))
    
    def add_text(self, text: str):
        """添加文本"""
        self.story.append(Paragraph(text, self.styles['NormalCN']))
    
    def add_table(self, data: List[List[str]], headers: Optional[List[str]] = None):
        """添加表格"""
        if headers:
            table_data = [headers] + data
        else:
            table_data = data
        
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        self.story.append(table)
        self.story.append(Spacer(1, 0.5*cm))
    
    def add_image(self, image_path: str, width: float = 15*cm, height: Optional[float] = None):
        """添加图片（PNG 图表）"""
        if os.path.exists(image_path):
            # 限制最大高度为 10cm，防止超出页面
            max_height = 10*cm
            if height is None:
                height = max_height
            else:
                height = min(height, max_height)
            
            img = Image(image_path, width=width, height=height)
            self.story.append(img)
            self.story.append(Spacer(1, 0.5*cm))
    
    def add_plot(self, fig, width: float = 15*cm, height: Optional[float] = None, keep_fig: bool = False):
        """直接添加 matplotlib 图形"""
        import io
        try:
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            img = Image(buffer, width=width, height=height)
            self.story.append(img)
            self.story.append(Spacer(1, 0.5*cm))
        finally:
            if not keep_fig:
                plt.close(fig)
    
    def add_page_break(self):
        """添加分页符"""
        self.story.append(PageBreak())
    
    def build(self):
        """生成 PDF"""
        self.doc.build(self.story)
        return self.doc.filename


def create_quality_report(
    stats_result: Dict, 
    spc_result: Optional[Dict], 
    capability_result: Optional[Dict],
    image_paths: Dict[str, str],
    output_pdf: str,
    data_file: str,
    column_name: str
):
    """创建完整的质量统计 PDF 报告"""
    report = PDFReport(output_pdf, title=f"质量统计分析报告 - {column_name}")
    
    # 标题
    report.add_title()
    
    # 数据信息
    report.add_section("1. 数据信息")
    report.add_text(f"<b>数据文件:</b> {data_file}")
    report.add_text(f"<b>分析列:</b> {column_name}")
    report.add_text(f"<b>样本量:</b> {stats_result.get('count', 'N/A')}")
    
    # 描述性统计
    report.add_section("2. 描述性统计")
    stat_table = [
        ["统计量", "值"],
        ["均值", f"{stats_result.get('mean', 0):.4f}"],
        ["中位数", f"{stats_result.get('median', 0):.4f}"],
        ["标准差", f"{stats_result.get('std', 0):.4f}"],
        ["变异系数", f"{stats_result.get('cv', 0):.4f}%"],
        ["最小值", f"{stats_result.get('min', 0):.4f}"],
        ["最大值", f"{stats_result.get('max', 0):.4f}"],
        ["极差", f"{stats_result.get('range', 0):.4f}"],
        ["偏度", f"{stats_result.get('skewness', 0):.4f}"],
        ["峰度", f"{stats_result.get('kurtosis', 0):.4f}"],
    ]
    report.add_table(stat_table)
    
    # 添加直方图
    if 'histogram' in image_paths and os.path.exists(image_paths['histogram']):
        report.add_section("3. 分布分析 - 直方图")
        report.add_image(image_paths['histogram'])
    
    # 添加箱线图
    if 'boxplot' in image_paths and os.path.exists(image_paths['boxplot']):
        report.add_section("4. 分布分析 - 箱线图")
        report.add_image(image_paths['boxplot'])
    
    # 添加QQ图
    if 'qqplot' in image_paths and os.path.exists(image_paths['qqplot']):
        report.add_section("5. 正态性检验 - QQ图")
        report.add_image(image_paths['qqplot'])
    
    # SPC控制图
    if spc_result:
        report.add_section("6. SPC 控制图")
        
        # 控制限表格
        spc_table = [
            ["项目", "X̄", "R"],
            ["中心线", f"{spc_result['X_bar']:.4f}", f"{spc_result['R_bar']:.4f}"],
            ["上控制限", f"{spc_result['UCL_X']:.4f}", f"{spc_result['UCL_R']:.4f}"],
            ["下控制限", f"{spc_result['LCL_X']:.4f}", f"{spc_result['LCL_R']:.4f}"],
        ]
        report.add_table(spc_table)
        
        if 'spc' in image_paths and os.path.exists(image_paths['spc']):
            report.add_image(image_paths['spc'])
    
    # 过程能力分析
    if capability_result:
        report.add_section("7. 过程能力分析")
        
        # 如果有规格限，计算 Cp/Cpk
        if 'Cp' in capability_result:
            cp_table = [
                ["指标", "值"],
                ["Cp", f"{capability_result['Cp']:.4f}"],
                ["Cpk", f"{capability_result['Cpk']:.4f}"],
                ["均值", f"{capability_result['mean']:.4f}"],
                ["标准差", f"{capability_result['std']:.4f}"],
            ]
            report.add_table(cp_table)
            
            # 评级
            if capability_result['Cpk'] >= 1.67:
                rating = "优秀 (过程能力充足) - A级"
                color = "绿色"
            elif capability_result['Cpk'] >= 1.33:
                rating = "良好 (过程能力足够) - B级"
                color = "蓝色"
            elif capability_result['Cpk'] >= 1.00:
                rating = "勉强合格 (需关注) - C级"
                color = "黄色"
            else:
                rating = "不足 (需改进) - D级"
                color = "红色"
            
            report.add_text(f"<b>评级:</b> {rating}")
            
            if 'capability' in image_paths and os.path.exists(image_paths['capability']):
                report.add_image(image_paths['capability'])
    
    # 生成 PDF
    pdf_path = report.build()
    return pdf_path
