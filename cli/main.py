#!/usr/bin/env python3
"""
Industrial Quality Statistics CLI
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
from core.report import create_quality_report
from core.insights import InsightGenerator


@click.group()
@click.version_option(version='1.0.0-mvp')
def cli():
    """Industrial Quality Statistics Analysis Tool
    
    A Minitab-like quality statistics tool supporting SPC control charts,
    assessment charts, heatmaps, regression analysis, and more.
    """
    pass


@cli.command()
@click.option('--file', '-f', required=True, type=click.Path(exists=True), help='Path to CSV file')
@click.option('--column', '-c', required=True, help='Column name to analyze')
@click.option('--output', '-o', default=None, help='Output report file (JSON)')
def stats(file: str, column: str, output: str):
    """Basic descriptive statistics"""
    try:
        df = pd.read_csv(file, comment='#')
        df.columns = df.columns.str.strip()
        if column not in df.columns:
            click.echo(f"Error: Column '{column}' does not exist", err=True)
            click.echo(f"Available columns: {', '.join(df.columns)}", err=True)
            sys.exit(1)
            
        data = df[column].dropna().tolist()
        result = DescriptiveStatistics.calculate(data, column)
        
        click.echo(f"\n=== Descriptive Statistics: {column} ===")
        for key, value in result.items():
            if isinstance(value, float):
                click.echo(f"{key:>12}: {value:>.4f}")
            else:
                click.echo(f"{key:>12}: {value}")
                
        # Detect outliers
        outliers = DescriptiveStatistics.outliers(data)
        if outliers:
            click.echo(f"\nOutliers (IQR method): {len(outliers)}")
            click.echo(f"  Values: {outliers}")
        else:
            click.echo("\nNo outliers")
            
        if output:
            import json
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            click.echo(f"\nReport saved: {output}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', '-f', required=True, type=click.Path(exists=True), help='Data file (CSV)')
@click.option('--column', '-c', required=True, help='Data column name')
@click.option('--subgroup-size', '-n', default=5, help='Subgroup size (default: 5)')
@click.option('--output-dir', '-o', default='output', help='Output directory')
def spc(file: str, column: str, subgroup_size: int, output_dir: str):
    """Generate SPC Control Chart (X-R)"""
    try:
        df = pd.read_csv(file, comment='#')
        df.columns = df.columns.str.strip()
        if column not in df.columns:
            click.echo(f"错误: 列 '{column}' 不存在", err=True)
            sys.exit(1)
            
        data = df[column].dropna().tolist()
        
        # 按子组大小分组
        if len(data) < subgroup_size * 2:
            click.echo(f"Error: Insufficient data points (need at least {subgroup_size*2})", err=True)
            sys.exit(1)
            
        subgroups = [data[i:i+subgroup_size] for i in range(0, len(data)-subgroup_size+1, subgroup_size)]
        if len(subgroups) < 2:
            click.echo("Error: Insufficient subgroups (need at least 2)", err=True)
            sys.exit(1)
            
        # 计算控制图
        chart_data = SPCControlChart.x_r_chart(subgroups)
        
        click.echo(f"\n=== X-R Control Chart (subgroup size n={subgroup_size}) ===")
        click.echo(f"Subgroups: {len(subgroups)}")
        click.echo(f"X̄ = {chart_data['X_bar']:.4f}")
        click.echo(f"R̄ = {chart_data['R_bar']:.4f}")
        click.echo(f"X̄ Control Limits: UCL={chart_data['UCL_X']:.4f}, LCL={chart_data['LCL_X']:.4f}")
        click.echo(f"R   Control Limits: UCL={chart_data['UCL_R']:.4f}, LCL={chart_data['LCL_R']:.4f}")
        
        # 判断是否受控
        x_out_of_control = sum(1 for x in chart_data['x_bars'] 
                              if x > chart_data['UCL_X'] or x < chart_data['LCL_X'])
        r_out_of_control = sum(1 for r in chart_data['ranges'] 
                              if r > chart_data['UCL_R'])
        
        click.echo(f"\nOut-of-control subgroups: X̄={x_out_of_control}, R={r_out_of_control}")
        if x_out_of_control == 0 and r_out_of_control == 0:
            click.echo("✅ Process in statistical control")
        else:
            click.echo("⚠️  Process out of control - check data")
            
        # 生成图表
        fig = SPCControlChart.plot_x_r(chart_data)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'spc_xr_{column}')
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        click.echo(f"\nChart saved: {output_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', '-f', required=True, type=click.Path(exists=True), help='Data file (CSV)')
@click.option('--column', '-c', required=True, help='Data column name')
@click.option('--type', '-t', 'chart_type', required=True, 
              type=click.Choice(['histogram', 'boxplot', 'qqplot', 'stemleaf', 'timeseries', 'pareto'], case_sensitive=False),
              help='Chart type')
@click.option('--output', '-o', default=None, help='Output file (PNG/Text)')

def assess(file: str, column: str, chart_type: str, output: str):
    """Generate Assessment Charts (Histogram/Boxplot/Q-Q Plot/Stem-leaf)"""
    try:
        df = pd.read_csv(file, comment='#')
        df.columns = df.columns.str.strip()
        if column not in df.columns:
            click.echo(f"Error: Column '{column}' does not exist", err=True)
            sys.exit(1)
            
        data = df[column].dropna().tolist()
        
        # Chart type mapping
        chart_funcs = {
            'histogram': AssessmentCharts.histogram,
            'boxplot': AssessmentCharts.boxplot,
            'qqplot': AssessmentCharts.qqplot,
            'timeseries': AssessmentCharts.timeseries,
            'pareto': AssessmentCharts.pareto
        }
        
        if chart_type == 'stemleaf':
            # Stem-leaf is text output
            result = AssessmentCharts.stem_leaf(data, title=f"Stem-and-Leaf Plot: {column}")
            click.echo("\n" + result)
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(result)
                click.echo(f"\nSaved: {output}")
            return
        
        # 生成图表
        func = chart_funcs[chart_type]
        fig = func(data, title=f"{chart_type.title()} - {column}")
        
        # 保存或显示图表
        if output:
            fig.savefig(output, dpi=300, bbox_inches='tight')
            click.echo(f"Chart saved: {output}")
        else:
            plt.show()
            
        # 输出洞察分析
        click.echo("\n" + "="*60)
        click.echo("📊 Data Insights:")
        insight = InsightGenerator.assess_insight(data, column, chart_type)
        click.echo(insight.summary)
        click.echo("\nKey Findings:")
        for h in insight.highlights:
            click.echo(f"  • {h}")
        if insight.recommendations:
            click.echo("\nRecommendations:")
            for r in insight.recommendations:
                click.echo(f"  🔧 {r}")
        click.echo("="*60)
            
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', '-f', required=True, type=click.Path(exists=True), help='Data matrix file (CSV)')
@click.option('--method', '-m', default='pearson', 
              type=click.Choice(['pearson', 'spearman', 'kendall']),
              help='Correlation method')
@click.option('--output', '-o', default='output/heatmap.png', help='Output file')
def heatmap(file: str, method: str, output: str):
    """Generate Heatmap (Correlation Matrix)"""
    try:
        df = pd.read_csv(file, comment='#')
        df.columns = df.columns.str.strip()
        corr_matrix = HeatmapGenerator.correlation(df, method=method)
        
        click.echo(f"\n=== Heatmap (Correlation Matrix) ===")
        click.echo(f"Data dimensions: {df.shape[0]} rows × {df.shape[1]} columns")
        click.echo(f"Method: {method}")
        click.echo("\nTop 5 correlations:")
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
@click.option('--file', '-f', required=True, type=click.Path(exists=True), help='Data file (CSV)')
@click.option('--x', '-x', required=True, help='Independent variable column name')
@click.option('--y', '-y', required=True, help='Dependent variable column name')
@click.option('--output-dir', '-o', default='output', help='Output directory')
def regression(file: str, x: str, y: str, output_dir: str):
    """Regression Analysis (Equation)"""
    try:
        df = pd.read_csv(file, comment='#')
        df.columns = df.columns.str.strip()
        for col in [x, y]:
            if col not in df.columns:
                click.echo(f"Error: Column '{col}' does not exist", err=True)
                sys.exit(1)
                
        x_data = df[x].dropna().tolist()
        y_data = df[y].dropna().tolist()
        
        if len(x_data) != len(y_data):
            click.echo(f"Error: Data length mismatch ({len(x_data)} vs {len(y_data)})", err=True)
            sys.exit(1)
            
        results = RegressionAnalysis.linear(x_data, y_data)
        
        click.echo(f"\n=== Regression Analysis: {y} ~ {x} ===")
        click.echo(f"Equation: {results['equation']}")
        click.echo(f"R²: {results['r_squared']:.4f}")
        click.echo(f"MSE: {results['mse']:.4f}")
        click.echo(f"Slope p-value: {results['slope_p_value']:.4g}")
        click.echo(f"Sample size: {results['n']}")
        
        fig = RegressionAnalysis.plot_regression(x_data, y_data, results, 
                                                xlabel=x, ylabel=y,
                                                title=f"Regression Analysis: {y} vs {x}")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'regression_{x}_{y}.png')
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        click.echo(f"\nChart saved: {output_path}")
        
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', '-f', required=True, type=click.Path(exists=True), help='Data file (CSV)')
@click.option('--column', '-c', required=True, help='Data column name')
@click.option('--lsl', type=float, default=None, help='Lower specification limit')
@click.option('--usl', type=float, default=None, help='Upper specification limit')
@click.option('--output-dir', '-o', default='output', help='Output directory')
def capability(file: str, column: str, lsl: Optional[float], usl: Optional[float], output_dir: str):
    """Process Capability Analysis (Cp/Cpk)"""
    try:
        df = pd.read_csv(file, comment='#')
        df.columns = df.columns.str.strip()
        if column not in df.columns:
            click.echo(f"错误: 列 '{column}' 不存在", err=True)
            sys.exit(1)
            
        data = df[column].dropna().tolist()
        results = ProcessCapability.calculate(data, lsl, usl)
        
        click.echo(f"\n=== Process Capability Analysis: {column} ===")
        click.echo(f"Sample size: {results['n']}")
        click.echo(f"Mean: {results['mean']:.4f}")
        click.echo(f"Standard deviation: {results['std']:.4f}")
        
        if 'Cp' in results:
            click.echo(f"\n规格限: LSL={lsl}, USL={usl}")
            click.echo(f"Cp:  {results['Cp']:.4f}")
            click.echo(f"Cpk: {results['Cpk']:.4f}")
            
            # Rating
            if results['Cpk'] >= 1.67:
                rating = "Excellent (Process capable)"
            elif results['Cpk'] >= 1.33:
                rating = "Good (Adequately capable)"
            elif results['Cpk'] >= 1.00:
                rating = "Marginal (Acceptable but borderline)"
            else:
                rating = "Inadequate (Needs improvement)"
            click.echo(f"Rating: {rating}")
            
        fig = ProcessCapability.plot_capability(data, (lsl, usl), 
                                               title=f"Process Capability: {column}")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'capability_{column}.png')
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        click.echo(f"\nChart saved: {output_path}")
        
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', '-f', required=True, type=click.Path(exists=True), help='Data file (CSV)')
@click.option('--column', '-c', required=True, help='Data column name')
@click.option('--lsl', type=float, default=None, help='Lower specification limit (for process capability)')
@click.option('--usl', type=float, default=None, help='Upper specification limit (for process capability)')
@click.option('--subgroup-size', '-n', default=5, help='Subgroup size for SPC control chart (default: 5)')
@click.option('--output-dir', '-o', default='output', help='Output directory')
@click.option('--pdf-name', '-p', default=None, help='PDF report filename (default: quality_report_<column>.pdf)')
def report(file: str, column: str, lsl: Optional[float], usl: Optional[float], 
           subgroup_size: int, output_dir: str, pdf_name: str):
    """Generate complete quality statistics report (PNG charts + PDF document)"""
    try:
        df = pd.read_csv(file, comment='#')
        df.columns = df.columns.str.strip()
        if column not in df.columns:
            click.echo(f"Error: Column '{column}' does not exist", err=True)
            sys.exit(1)
            
        data = df[column].dropna().tolist()
        os.makedirs(output_dir, exist_ok=True)
        
        click.echo("Generating descriptive statistics...")
        stats_result = DescriptiveStatistics.calculate(data, column)
        
        click.echo("Generating assessment charts...")
        image_paths = {}
        
        fig_hist = AssessmentCharts.histogram(data, title=f"Histogram - {column}")
        hist_path = os.path.join(output_dir, f'histogram_{column}.png')
        fig_hist.savefig(hist_path, dpi=300, bbox_inches='tight')
        plt.close(fig_hist)
        image_paths['histogram'] = hist_path
        
        fig_box = AssessmentCharts.boxplot(data, title=f"Boxplot - {column}")
        box_path = os.path.join(output_dir, f'boxplot_{column}.png')
        fig_box.savefig(box_path, dpi=300, bbox_inches='tight')
        plt.close(fig_box)
        image_paths['boxplot'] = box_path
        
        fig_qq = AssessmentCharts.qqplot(data, title=f"Q-Q Plot - {column}")
        qq_path = os.path.join(output_dir, f'qqplot_{column}.png')
        fig_qq.savefig(qq_path, dpi=300, bbox_inches='tight')
        plt.close(fig_qq)
        image_paths['qqplot'] = qq_path
        
        spc_result = None
        if len(data) >= subgroup_size * 2:
            click.echo("Generating SPC control chart...")
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
            click.echo("Generating process capability analysis...")
            capability_result = ProcessCapability.calculate(data, lsl, usl)
            fig_cap = ProcessCapability.plot_capability(data, (lsl, usl), 
                                                       title=f"Process Capability: {column}")
            cap_path = os.path.join(output_dir, f'capability_{column}_plot.png')
            fig_cap.savefig(cap_path, dpi=300, bbox_inches='tight')
            plt.close(fig_cap)
            image_paths['capability'] = cap_path
        
        click.echo("Generating PDF report...")
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
        
        click.echo(f"\n✅ Report generation completed!")
        click.echo(f"📄 PDF report: {pdf_path}")
        
        click.echo(f"🖼️  PNG charts directory: {output_dir}")
        click.echo(f"   - Histogram: {image_paths.get('histogram')}")
        click.echo(f"   - Boxplot: {image_paths.get('boxplot')}")
        click.echo(f"   - Q-Q Plot: {image_paths.get('qqplot')}")
        if spc_result:
            click.echo(f"   - SPC control chart: {image_paths.get('spc')}")
        if capability_result:
            click.echo(f"   - Process capability chart: {image_paths.get('capability')}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    cli()
