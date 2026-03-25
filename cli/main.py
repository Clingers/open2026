#!/usr/bin/env python3
"""
工业质量统计 CLI
2026-03-26
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt  # 新增
from pathlib import Path
from typing import List, Optional

from core.statistics import DescriptiveStatistics
from core.spc import SPCControlChart
from core.assessment import AssessmentCharts
from core.heatmap import HeatmapGenerator
from core.regression import RegressionAnalysis
from core.capability import ProcessCapability
from core.report import PDFReport, create_quality_report


@click.group()
@click.version_option(version='1.0.0-mvp')
def cli():
    """工业质量统计分析工具 (Industrial Quality Stats)
    
    类似 Minitab 的质量统计工具，支持 SPC 控制图、评估图、
    热力图、回归分析等功能。
    """
    pass


@cli.command()
@click.option('--file', '-f', required=True, type=click.Path(exists=True), help='CSV 文件路径')
@click.option('--column', '-c', required=True, help='要分析的列名')
@click.option('--output', '-o', default=None, help='输出报告文件 (JSON)')
def stats(file: str, column: str, output: str):
    """基础描述性统计"""
    try:
        df = pd.read_csv(file)
        if column not in df.columns:
            click.echo(f"错误: 列 '{column}' 不存在", err=True)
            click.echo(f"可用列: {', '.join(df.columns)}", err=True)
            sys.exit(1)
            
        data = df[column].dropna().tolist()
        result = DescriptiveStatistics.calculate(data, column)
        
        click.echo(f"\n=== 描述性统计: {column} ===")
        for key, value in result.items():
            if isinstance(value, float):
                click.echo(f"{key:>12}: {value:>.4f}")
            else:
                click.echo(f"{key:>12}: {value}")
                
        # 检测异常值
        outliers = DescriptiveStatistics.outliers(data)
        if outliers:
            click.echo(f"\n异常值 (IQR方法): {len(outliers)} 个")
            click.echo(f"  值: {outliers}")
        else:
            click.echo("\n无异常值")
            
        if output:
            import json
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            click.echo(f"\n报告已保存: {output}")
            
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', '-f', required=True, type=click.Path(exists=True), help='数据文件 (CSV)')
@click.option('--column', '-c', required=True, help='数据列名')
@click.option('--subgroup-size', '-n', default=5, help='子组大小 (默认: 5)')
@click.option('--output-dir', '-o', default='output', help='输出目录')
def spc(file: str, column: str, subgroup_size: int, output_dir: str):
    """生成 SPC 控制图 (X-R)"""
    try:
        df = pd.read_csv(file)
        if column not in df.columns:
            click.echo(f"错误: 列 '{column}' 不存在", err=True)
            sys.exit(1)
            
        data = df[column].dropna().tolist()
        
        # 按子组大小分组
        if len(data) < subgroup_size * 2:
            click.echo(f"错误: 数据点不足 (需要至少 {subgroup_size*2} 个)", err=True)
            sys.exit(1)
            
        subgroups = [data[i:i+subgroup_size] for i in range(0, len(data)-subgroup_size+1, subgroup_size)]
        if len(subgroups) < 2:
            click.echo("错误: 子组数量不足 (需要至少2个子组)", err=True)
            sys.exit(1)
            
        # 计算控制图
        chart_data = SPCControlChart.x_r_chart(subgroups)
        
        click.echo(f"\n=== X-R 控制图 (子组大小 n={subgroup_size}) ===")
        click.echo(f"子组数: {len(subgroups)}")
        click.echo(f"X̄ = {chart_data['X_bar']:.4f}")
        click.echo(f"R̄ = {chart_data['R_bar']:.4f}")
        click.echo(f"X̄ 控制限: UCL={chart_data['UCL_X']:.4f}, LCL={chart_data['LCL_X']:.4f}")
        click.echo(f"R   控制限: UCL={chart_data['UCL_R']:.4f}, LCL={chart_data['LCL_R']:.4f}")
        
        # 判断是否受控
        x_out_of_control = sum(1 for x in chart_data['x_bars'] 
                              if x > chart_data['UCL_X'] or x < chart_data['LCL_X'])
        r_out_of_control = sum(1 for r in chart_data['ranges'] 
                              if r > chart_data['UCL_R'])
        
        click.echo(f"\n异常点子组: X̄={x_out_of_control}, R={r_out_of_control}")
        if x_out_of_control == 0 and r_out_of_control == 0:
            click.echo("✅ 过程处于统计受控状态")
        else:
            click.echo("⚠️  过程存在异常，请检查数据")
            
        # 生成图表
        fig = SPCControlChart.plot_x_r(chart_data)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'spc_xr_{column}.png')
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        click.echo(f"\n图表已保存: {output_path}")
        
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', '-f', required=True, type=click.Path(exists=True), help='数据文件 (CSV)')
@click.option('--column', '-c', required=True, help='数据列名')
@click.option('--type', '-t', 'chart_type', required=True, 
              type=click.Choice(['histogram', 'boxplot', 'qqplot', 'stemleaf'], case_sensitive=False),
              help='图表类型')
@click.option('--output', '-o', default=None, help='输出文件 (PNG/文本)')
def assess(file: str, column: str, chart_type: str, output: str):
    """生成评估图 (直方图/箱线图/QQ图/茎叶图)"""
    try:
        df = pd.read_csv(file)
        if column not in df.columns:
            click.echo(f"错误: 列 '{column}' 不存在", err=True)
            sys.exit(1)
            
        data = df[column].dropna().tolist()
        
        if chart_type == 'stemleaf':
            # 茎叶图是文本输出
            result = AssessmentCharts.stem_leaf(data, title=f"茎叶图: {column}")
            click.echo("\n" + result)
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(result)
                click.echo(f"\n已保存: {output}")
            return
            
        # 图表类型映射
        chart_funcs = {
            'histogram': AssessmentCharts.histogram,
            'boxplot': AssessmentCharts.boxplot,
            'qqplot': AssessmentCharts.qqplot
        }
        
        func = chart_funcs[chart_type]
        fig = func(data, title=f"{chart_type.title()} - {column}")
        
        if output:
            fig.savefig(output, dpi=300, bbox_inches='tight')
            click.echo(f"图表已保存: {output}")
        else:
            plt.show()
            
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', '-f', required=True, type=click.Path(exists=True), help='数据矩阵文件 (CSV)')
@click.option('--method', '-m', default='pearson', 
              type=click.Choice(['pearson', 'spearman', 'kendall']),
              help='相关性计算方法')
@click.option('--output', '-o', default='output/heatmap.png', help='输出文件')
def heatmap(file: str, method: str, output: str):
    """生成热力图 (相关性矩阵)"""
    try:
        df = pd.read_csv(file)
        corr_matrix = HeatmapGenerator.correlation(df, method=method)
        
        click.echo(f"\n=== 热力图 (相关系数矩阵) ===")
        click.echo(f"数据维度: {df.shape[0]} 行 × {df.shape[1]} 列")
        click.echo(f"计算方法: {method}")
        click.echo("\n相关系数 Top 5:")
        # 找出最大的5个相关系数 (排除对角线)
        corr_unstack = corr_matrix.unstack()
        corr_unstack = corr_unstack[corr_unstack.index.get_level_values(0) != corr_unstack.index.get_level_values(1)]
        top5 = corr_unstack.sort_values(ascending=False).head(5)
        for (col1, col2), value in top5.items():
            click.echo(f"  {col1} - {col2}: {value:.4f}")
        
        fig = HeatmapGenerator.generate_figure(corr_matrix, title=f"相关性热力图 ({method})")
        os.makedirs(os.path.dirname(output), exist_ok=True)
        fig.savefig(output, dpi=300, bbox_inches='tight')
        plt.close(fig)
        click.echo(f"\n热力图已保存: {output}")
        
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', '-f', required=True, type=click.Path(exists=True), help='数据文件 (CSV)')
@click.option('--x', '-x', required=True, help='自变量列名')
@click.option('--y', '-y', required=True, help='因变量列名')
@click.option('--output-dir', '-o', default='output', help='输出目录')
def regression(file: str, x: str, y: str, output_dir: str):
    """回归分析 (方程分析)"""
    try:
        df = pd.read_csv(file)
        for col in [x, y]:
            if col not in df.columns:
                click.echo(f"错误: 列 '{col}' 不存在", err=True)
                sys.exit(1)
                
        x_data = df[x].dropna().tolist()
        y_data = df[y].dropna().tolist()
        
        if len(x_data) != len(y_data):
            click.echo(f"错误: 数据长度不匹配 ({len(x_data)} vs {len(y_data)})", err=True)
            sys.exit(1)
            
        results = RegressionAnalysis.linear(x_data, y_data)
        
        click.echo(f"\n=== 回归分析: {y} ~ {x} ===")
        click.echo(f"方程: {results['equation']}")
        click.echo(f"R²: {results['r_squared']:.4f}")
        click.echo(f"MSE: {results['mse']:.4f}")
        click.echo(f"斜率 p值: {results['slope_p_value']:.4g}")
        click.echo(f"样本量: {results['n']}")
        
        fig = RegressionAnalysis.plot_regression(x_data, y_data, results, 
                                                xlabel=x, ylabel=y,
                                                title=f"回归分析: {y} vs {x}")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'regression_{x}_{y}.png')
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        click.echo(f"\n图表已保存: {output_path}")
        
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', '-f', required=True, type=click.Path(exists=True), help='数据文件 (CSV)')
@click.option('--column', '-c', required=True, help='数据列名')
@click.option('--lsl', type=float, default=None, help='下规格限')
@click.option('--usl', type=float, default=None, help='上规格限')
@click.option('--output-dir', '-o', default='output', help='输出目录')
def capability(file: str, column: str, lsl: Optional[float], usl: Optional[float], output_dir: str):
    """过程能力分析 (Cp/Cpk)"""
    try:
        df = pd.read_csv(file)
        if column not in df.columns:
            click.echo(f"错误: 列 '{column}' 不存在", err=True)
            sys.exit(1)
            
        data = df[column].dropna().tolist()
        results = ProcessCapability.calculate(data, lsl, usl)
        
        click.echo(f"\n=== 过程能力分析: {column} ===")
        click.echo(f"样本量: {results['n']}")
        click.echo(f"均值: {results['mean']:.4f}")
        click.echo(f"标准差: {results['std']:.4f}")
        
        if 'Cp' in results:
            click.echo(f"\n规格限: LSL={lsl}, USL={usl}")
            click.echo(f"Cp:  {results['Cp']:.4f}")
            click.echo(f"Cpk: {results['Cpk']:.4f}")
            
            # 评级
            if results['Cpk'] >= 1.67:
                rating = "优秀 (过程能力充足)"
            elif results['Cpk'] >= 1.33:
                rating = "良好 (过程能力足够)"
            elif results['Cpk'] >= 1.00:
                rating = "勉强合格 (需关注)"
            else:
                rating = "不足 (需改进)"
            click.echo(f"评级: {rating}")
            
        fig = ProcessCapability.plot_capability(data, (lsl, usl), 
                                               title=f"过程能力: {column}")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'capability_{column}.png')
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        click.echo(f"\n图表已保存: {output_path}")
        
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', '-f', required=True, type=click.Path(exists=True), help='数据文件 (CSV)')
@click.option('--column', '-c', required=True, help='数据列名')
@click.option('--lsl', type=float, default=None, help='下规格限 (用于过程能力分析)')
@click.option('--usl', type=float, default=None, help='上规格限 (用于过程能力分析)')
@click.option('--subgroup-size', '-n', default=5, help='子组大小 (用于SPC控制图，默认: 5)')
@click.option('--output-dir', '-o', default='output', help='输出目录')
@click.option('--pdf-name', '-p', default=None, help='PDF报告文件名 (默认: quality_report_列名.pdf)')
def report(file: str, column: str, lsl: Optional[float], usl: Optional[float], 
           subgroup_size: int, output_dir: str, pdf_name: str):
    """生成完整的质量统计报告 (PNG图表 + PDF文档)"""
    try:
        df = pd.read_csv(file)
        if column not in df.columns:
            click.echo(f"错误: 列 '{column}' 不存在", err=True)
            sys.exit(1)
            
        data = df[column].dropna().tolist()
        os.makedirs(output_dir, exist_ok=True)
        
        click.echo("正在生成描述性统计...")
        stats_result = DescriptiveStatistics.calculate(data, column)
        
        click.echo("正在生成评估图...")
        image_paths = {}
        
        fig_hist = AssessmentCharts.histogram(data, title=f"直方图 - {column}")
        hist_path = os.path.join(output_dir, f'histogram_{column}.png')
        fig_hist.savefig(hist_path, dpi=300, bbox_inches='tight')
        plt.close(fig_hist)
        image_paths['histogram'] = hist_path
        
        fig_box = AssessmentCharts.boxplot(data, title=f"箱线图 - {column}")
        box_path = os.path.join(output_dir, f'boxplot_{column}.png')
        fig_box.savefig(box_path, dpi=300, bbox_inches='tight')
        plt.close(fig_box)
        image_paths['boxplot'] = box_path
        
        fig_qq = AssessmentCharts.qqplot(data, title=f"QQ图 - {column}")
        qq_path = os.path.join(output_dir, f'qqplot_{column}.png')
        fig_qq.savefig(qq_path, dpi=300, bbox_inches='tight')
        plt.close(fig_qq)
        image_paths['qqplot'] = qq_path
        
        spc_result = None
        if len(data) >= subgroup_size * 2:
            click.echo("正在生成SPC控制图...")
            subgroups = [data[i:i+subgroup_size] for i in range(0, len(data)-subgroup_size+1, subgroup_size)]
            if len(subgroups) >= 2:
                spc_result = SPCControlChart.x_r_chart(subgroups)
                fig_spc = SPCControlChart.plot_x_r(spc_result)
                spc_path = os.path.join(output_dir, f'spc_xr_{column}.png')
                fig_spc.savefig(spc_path, dpi=300, bbox_inches='tight')
                plt.close(fig_spc)
                image_paths['spc'] = spc_path
        
        capability_result = None
        if lsl is not None or usl is not None:
            click.echo("正在生成过程能力分析...")
            capability_result = ProcessCapability.calculate(data, lsl, usl)
            fig_cap = ProcessCapability.plot_capability(data, (lsl, usl), 
                                                       title=f"过程能力: {column}")
            cap_path = os.path.join(output_dir, f'capability_{column}_plot.png')
            fig_cap.savefig(cap_path, dpi=300, bbox_inches='tight')
            plt.close(fig_cap)
            image_paths['capability'] = cap_path
        
        click.echo("正在生成PDF报告...")
        if not pdf_name:
            pdf_name = f'quality_report_{column}.pdf'
        pdf_path = os.path.join(output_dir, pdf_name)
        
        create_quality_report(
            stats_result=stats_result,
            spc_result=spc_result,
            capability_result=capability_result,
            image_paths=image_paths,
            output_pdf=pdf_path,
            data_file=os.path.basename(file),
            column_name=column
        )
        
        click.echo(f"\n✅ 报告生成完成!")
        click.echo(f"📄 PDF报告: {pdf_path}")
        
        click.echo(f"🖼️  PNG图表目录: {output_dir}")
        click.echo(f"   - 直方图: {image_paths.get('histogram')}")
        click.echo(f"   - 箱线图: {image_paths.get('boxplot')}")
        click.echo(f"   - QQ图: {image_paths.get('qqplot')}")
        if spc_result:
            click.echo(f"   - SPC控制图: {image_paths.get('spc')}")
        if capability_result:
            click.echo(f"   - 过程能力图: {image_paths.get('capability')}")
        
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    cli()
