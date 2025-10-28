#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速模型对比分析脚本
简化版本，适合快速使用

使用方法：
1. 直接修改下面的配置参数
2. 运行脚本：python quick_analysis.py

配置参数说明：
- CSV_FILE_PATH: CSV文件路径
- BASELINE_MODEL: 基线模型字段名（可选）
- SCORE_COLUMNS: 参评模型字段名列表（可选，为None时自动检测）
- MODEL_NAMES: 模型名称列表（可选，为None时从字段名自动提取）
- TEST_TYPE: 统计检验类型
- ALPHA: 显著性水平
- SCORE_PATTERN: 分数字段检测模式
"""

from model_comparison_tool import ModelComparisonTool
import sys
import os
import pandas as pd

# ==================== 配置参数 ====================
# 在这里直接修改这些参数，无需命令行输入

# CSV文件路径
CSV_FILE_PATH = "/Users/hjy/Desktop/多轮标注工具/显著性分析/搜应引擎评测-Prompt2Doclist.csv"  # 修改为你的CSV文件路径

# 基线模型字段名（可选，如果不需要基线对比可以设为None）
BASELINE_MODEL = "overall_score-0916-聚合"  # 例如: "分_基线模型" 或 None

# 参评模型字段名列表（如果为None则自动检测）
SCORE_COLUMNS = [
    "overall_score-0916-聚合",
    "overall_score-0928-聚合",
]  # 例如: ["分_模型A", "分_模型B", "分_模型C"] 或 None

# 模型名称列表（如果为None则从字段名自动提取）
MODEL_NAMES = [
    "模型-0916-Prompt2Doclist",
    "模型-0928-Prompt2Doclist", 
]  # 例如: ["模型A", "模型B", "模型C"] 或 None

# 统计检验类型 ('wilcoxon', 'ttest', 'mannwhitney')
TEST_TYPE = 'wilcoxon'

# 显著性水平
ALPHA = 0.05

# 分数字段检测模式（用于自动检测）
SCORE_PATTERN = "overall_score"  # 检测包含此模式的字段作为分数字段

# ==================== 配置参数结束 ====================

def generate_html_report(stats_df, score_df, tool, baseline_model, test_type, alpha):
    """
    生成HTML格式的分析报告
    
    Args:
        stats_df: 基本统计信息
        score_df: 分数字据
        tool: 分析工具实例
        baseline_model: 基线模型
        test_type: 统计检验类型
        alpha: 显著性水平
        
    Returns:
        str: HTML格式的报告
    """
    # HTML报告开始
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>模型显著性对比报告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-top: 30px;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 25px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .info-card {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .info-card strong {{
            color: #2c3e50;
            font-size: 1.2em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        th {{
            background: #3498db;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        tr:hover {{
            background: #e8f4f8;
        }}
        .best-model {{
            background: linear-gradient(135deg, #f39c12, #e67e22);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
            font-size: 1.2em;
        }}
        .significant {{
            color: #27ae60;
            font-weight: bold;
        }}
        .not-significant {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .summary {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            color: #7f8c8d;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
        }}
        .emoji {{
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1><span class="emoji">📊</span> 模型显著性对比报告</h1>
        
        <h2><span class="emoji">📊</span> 数据概览</h2>
        <div class="info-grid">
            <div class="info-card">
                <strong>{len(score_df)}</strong><br>样本数量
            </div>
            <div class="info-card">
                <strong>{len(stats_df)}</strong><br>模型数量
            </div>
            <div class="info-card">
                <strong>{test_type}</strong><br>统计检验
            </div>
            <div class="info-card">
                <strong>α = {alpha}</strong><br>显著性水平
            </div>
        </div>
        
        <h2><span class="emoji">📈</span> 得分情况</h2>
        <table>
            <thead>
                <tr>
                    <th>模型</th>
                    <th>样本数</th>
                    <th>均值(百分制)</th>
                    <th>标准差</th>
                    <th>中位数</th>
                    <th>25%分位数</th>
                    <th>75%分位数</th>
                </tr>
            </thead>
            <tbody>"""
    
    # 基本统计信息表格
    for _, row in stats_df.iterrows():
        # 检查是否为基线模型
        is_baseline = baseline_model and row['模型'] in [tool.model_names[i] if i < len(tool.model_names) else tool.score_columns[i] for i in range(len(tool.score_columns)) if tool.score_columns[i] == baseline_model]
        model_display = f"{row['模型']} ✅" if is_baseline else row['模型']
        
        html += f"""
                <tr>
                    <td><strong>{model_display}</strong></td>
                    <td>{row['样本数']}</td>
                    <td>{(row['均值'] * 50):.2f}</td>
                    <td>{row['标准差']:.2f}</td>
                    <td>{row['中位数']:.2f}</td>
                    <td>{row['25%分位数']:.2f}</td>
                    <td>{row['75%分位数']:.2f}</td>
                </tr>"""
    
    html += """
            </tbody>
        </table>"""
    
    # 最佳模型
    best_model_idx = stats_df['均值'].idxmax()
    best_model = stats_df.loc[best_model_idx, '模型']
    best_score = stats_df.loc[best_model_idx, '均值']
    html += f"""
        <div class="best-model">
            <span class="emoji">🏆</span> 最佳模型: <strong>{best_model}</strong> (平均得分: {(best_score * 50):.2f})
        </div>"""
    
    # 两两对比结果
    html += f"""
        <h2><span class="emoji">🔍</span> 两两模型对比</h2>
        <table>
            <thead>
                <tr>
                    <th>模型1</th>
                    <th>模型2</th>
                    <th>模型1均值</th>
                    <th>模型2均值</th>
                    <th>均值差异</th>
                    <th>检验统计量</th>
                    <th>p值</th>
                    <th>是否显著</th>
                </tr>
            </thead>
            <tbody>"""
    
    pairwise_results = tool.pairwise_comparison(score_df, test_type=test_type, alpha=alpha)
    
    if pairwise_results is not None and len(pairwise_results) > 0:
        for _, row in pairwise_results.iterrows():
            significance_class = "significant" if row['是否显著'] else "not-significant"
            significance_text = "✅ 是" if row['是否显著'] else "❌ 否"
            
            # 检查模型是否为基线模型
            model1_display = f"{row['模型1']} ✅" if baseline_model and row['模型1'] in [tool.model_names[i] if i < len(tool.model_names) else tool.score_columns[i] for i in range(len(tool.score_columns)) if tool.score_columns[i] == baseline_model] else row['模型1']
            model2_display = f"{row['模型2']} ✅" if baseline_model and row['模型2'] in [tool.model_names[i] if i < len(tool.model_names) else tool.score_columns[i] for i in range(len(tool.score_columns)) if tool.score_columns[i] == baseline_model] else row['模型2']
            
            html += f"""
                <tr>
                    <td><strong>{model1_display}</strong></td>
                    <td><strong>{model2_display}</strong></td>
                    <td>{row['模型1均值']:.4f}</td>
                    <td>{row['模型2均值']:.4f}</td>
                    <td>{row['均值差异']:.4f}</td>
                    <td>{row['检验统计量']:.4f}</td>
                    <td>{row['p值']:.4f}</td>
                    <td class="{significance_class}">{significance_text}</td>
                </tr>"""
        
        html += """
            </tbody>
        </table>"""
        
        # 显著差异总结
        significant_pairs = pairwise_results[pairwise_results['是否显著'] == True]
        if len(significant_pairs) > 0:
            html += f"""
        <h3><span class="emoji">📋</span> 显著差异总结</h3>
        <div class="summary">
            <p>发现 <strong>{len(significant_pairs)}</strong> 对模型存在显著差异:</p>
            <ul>"""
            for _, row in significant_pairs.iterrows():
                direction = "优于" if row['均值差异'] > 0 else "劣于"
                
                # 检查模型是否为基线模型
                model1_display = f"{row['模型1']} ✅" if baseline_model and row['模型1'] in [tool.model_names[i] if i < len(tool.model_names) else tool.score_columns[i] for i in range(len(tool.score_columns)) if tool.score_columns[i] == baseline_model] else row['模型1']
                model2_display = f"{row['模型2']} ✅" if baseline_model and row['模型2'] in [tool.model_names[i] if i < len(tool.model_names) else tool.score_columns[i] for i in range(len(tool.score_columns)) if tool.score_columns[i] == baseline_model] else row['模型2']
                
                html += f"""
                <li><strong>{model1_display}</strong> {direction} <strong>{model2_display}</strong> 
                    (差异: {row['均值差异']:.4f}, p = {row['p值']:.4f})</li>"""
            html += """
            </ul>
        </div>"""
        else:
            html += """
        <h3><span class="emoji">📋</span> 显著差异总结</h3>
        <div class="summary">
            <p>未发现模型间存在显著差异</p>
        </div>"""
    else:
        html += """
            </tbody>
        </table>
        <p>无法进行两两对比分析</p>"""
    
    # 基线对比结果
    if baseline_model and baseline_model in tool.score_columns:
        # 获取基线模型的友好名称
        baseline_index = tool.score_columns.index(baseline_model)
        baseline_friendly_name = tool.model_names[baseline_index] if baseline_index < len(tool.model_names) else baseline_model
        
        html += f"""
        <h2><span class="emoji">🎯</span> 与基线模型对比</h2>
        <div class="summary">
            <p><strong>基线模型</strong>: {baseline_friendly_name}</p>
            <p><em>注：基线模型作为对比基准，其他模型的表现将与此模型进行比较</em></p>
        </div>
        <table>
            <thead>
                <tr>
                    <th>模型</th>
                    <th>模型均值</th>
                    <th>基线均值({baseline_friendly_name})</th>
                    <th>均值差异</th>
                    <th>检验统计量</th>
                    <th>p值</th>
                    <th>是否显著</th>
                    <th>优于基线</th>
                </tr>
            </thead>
            <tbody>"""
        
        baseline_results = tool.baseline_comparison(score_df, baseline_model, test_type=test_type, alpha=alpha)
        
        if baseline_results is not None and len(baseline_results) > 0:
            for _, row in baseline_results.iterrows():
                significance_class = "significant" if row['是否显著'] else "not-significant"
                significance_text = "✅ 是" if row['是否显著'] else "❌ 否"
                better_class = "significant" if row['优于基线'] else "not-significant"
                better_text = "✅ 是" if row['优于基线'] else "❌ 否"
                
                # 检查模型是否为基线模型
                model_display = f"{row['模型']} ✅" if baseline_model and row['模型'] in [tool.model_names[i] if i < len(tool.model_names) else tool.score_columns[i] for i in range(len(tool.score_columns)) if tool.score_columns[i] == baseline_model] else row['模型']
                
                html += f"""
                <tr>
                    <td><strong>{model_display}</strong></td>
                    <td>{row['模型均值']:.4f}</td>
                    <td>{row['基线均值']:.4f}</td>
                    <td>{row['均值差异']:.4f}</td>
                    <td>{row['检验统计量']:.4f}</td>
                    <td>{row['p值']:.4f}</td>
                    <td class="{significance_class}">{significance_text}</td>
                    <td class="{better_class}">{better_text}</td>
                </tr>"""
            
            html += """
            </tbody>
        </table>"""
            
            # 优于基线的模型
            better_models = baseline_results[baseline_results['优于基线'] == True]
            if len(better_models) > 0:
                html += f"""
        <h3><span class="emoji">🎉</span> 优于基线的模型</h3>
        <div class="summary">"""
                for _, row in better_models.iterrows():
                    # 检查模型是否为基线模型
                    model_display = f"{row['模型']} ✅" if baseline_model and row['模型'] in [tool.model_names[i] if i < len(tool.model_names) else tool.score_columns[i] for i in range(len(tool.score_columns)) if tool.score_columns[i] == baseline_model] else row['模型']
                    
                    html += f"""
            <p><strong>{model_display}</strong>: 差异 = {row['均值差异']:.4f}, p = {row['p值']:.4f}</p>"""
                html += """
        </div>"""
            else:
                html += """
        <h3><span class="emoji">😔</span> 基线对比结果</h3>
        <div class="summary">
            <p>没有模型显著优于基线</p>
        </div>"""
        else:
            html += """
            </tbody>
        </table>
        <p>无法进行基线对比分析</p>"""
    
    # 分析总结
    html += f"""
        <h2><span class="emoji">📝</span> 分析总结</h2>
        <div class="summary">"""
    
    if pairwise_results is not None:
        significant_count = len(pairwise_results[pairwise_results['是否显著'] == True])
        total_pairs = len(pairwise_results)
        html += f"""
            <ul>
                <li>共进行了 <strong>{total_pairs}</strong> 对模型对比</li>
                <li>发现 <strong>{significant_count}</strong> 对模型存在显著差异</li>"""
        
        if significant_count > 0:
            html += """
                <li>模型间存在显著差异，建议进一步分析具体原因</li>"""
        else:
            html += """
                <li>模型间未发现显著差异，可能需要更多样本或调整评估标准</li>"""
        html += """
            </ul>"""
    else:
        html += """
            <p>无法进行完整的对比分析</p>"""
    
    html += f"""
        </div>
        
        <div class="footer">
            <p>报告生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>"""
    
    return html

def quick_analysis(csv_file, baseline_model=None, test_type='wilcoxon', alpha=0.05):
    """
    快速分析函数
    
    Args:
        csv_file: CSV文件路径
        baseline_model: 基线模型名称（可选）
        test_type: 统计检验类型
        alpha: 显著性水平
    """
    print("🚀 开始快速模型对比分析...")
    print("=" * 50)
    
    # 检查文件是否存在
    if not os.path.exists(csv_file):
        print(f"❌ 文件不存在: {csv_file}")
        return
    
    try:
        # 初始化工具
        tool = ModelComparisonTool(csv_file)
        
        # 加载数据
        print("📊 加载数据...")
        df = tool.load_data()
        if df is None:
            return
        
        # 设置分数字段
        if SCORE_COLUMNS is not None:
            print("🔧 使用手动设置的分数字段...")
            tool.set_score_columns(SCORE_COLUMNS, MODEL_NAMES)
            score_columns = SCORE_COLUMNS
        else:
            print("🔍 自动检测分数字段...")
            score_columns = tool.detect_score_columns(pattern=SCORE_PATTERN)
            if not score_columns:
                print("❌ 未检测到分数字段，请检查数据格式或手动设置SCORE_COLUMNS")
                return
        
        # 清理数据
        print("🧹 清理数据...")
        score_df = tool.clean_score_data()
        if score_df is None:
            return
        
        # 基本统计信息
        print("\n📈 基本统计信息:")
        stats_df = tool.calculate_basic_stats(score_df)
        print(stats_df.to_string(index=False))
        
        # 找出最佳模型
        best_model_idx = stats_df['均值'].idxmax()
        best_model = stats_df.loc[best_model_idx, '模型']
        best_score = stats_df.loc[best_model_idx, '均值']
        print(f"\n🏆 最佳模型: {best_model} (平均得分: {best_score:.4f})")
        
        # 生成HTML格式的分析报告
        html_report = generate_html_report(
            stats_df, 
            score_df, 
            tool, 
            baseline_model, 
            test_type, 
            alpha
        )
        
        # 输出HTML报告信息
        print("\n" + "="*80)
        print("📋 HTML格式分析报告")
        print("="*80)
        print("✅ HTML报告已生成，包含完整的统计分析结果")
        print("📊 报告包含：数据概览、基本统计、两两对比、基线对比、分析总结")
        
        # 保存HTML报告到文件
        report_file = f"{os.path.splitext(csv_file)[0]}_analysis_report.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        print(f"\n💾 详细报告已保存到: {report_file}")
        print(f"🌐 请在浏览器中打开查看: {report_file}")
        
        # 创建可视化
        print("\n📊 生成可视化图表...")
        tool.create_visualization(score_df, save_path=f"{os.path.splitext(csv_file)[0]}_analysis.png")
        print(f"图表已保存到: {os.path.splitext(csv_file)[0]}_analysis.png")
        
        print("\n✅ 分析完成!")
        
    except Exception as e:
        print(f"❌ 分析过程中出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    主函数 - 使用配置参数
    """
    print("🚀 使用配置参数进行模型对比分析")
    print("=" * 50)
    print(f"📁 CSV文件: {CSV_FILE_PATH}")
    print(f"🎯 基线模型: {BASELINE_MODEL if BASELINE_MODEL else '无'}")
    print(f"📊 参评模型: {SCORE_COLUMNS if SCORE_COLUMNS else '自动检测'}")
    print(f"🔬 统计检验: {TEST_TYPE}")
    print(f"📈 显著性水平: {ALPHA}")
    print("=" * 50)
    
    # 使用配置参数进行分析
    quick_analysis(CSV_FILE_PATH, BASELINE_MODEL, TEST_TYPE, ALPHA)

if __name__ == "__main__":
    main()
