#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型对比工具使用示例
展示如何使用ModelComparisonTool进行模型对比分析
"""

from model_comparison_tool import ModelComparisonTool
import pandas as pd

def example_1_basic_usage():
    """
    示例1: 基本使用方法
    """
    print("=" * 60)
    print("示例1: 基本使用方法")
    print("=" * 60)
    
    # 初始化工具
    tool = ModelComparisonTool("merged_result-1.csv")
    
    # 加载数据
    df = tool.load_data()
    if df is None:
        return
    
    # 自动检测分数字段
    score_columns = tool.detect_score_columns(pattern="_score")
    
    # 清理数据
    score_df = tool.clean_score_data()
    if score_df is None:
        return
    
    # 生成分析报告
    report = tool.generate_report(score_df, test_type='wilcoxon', alpha=0.05)
    print(report)
    
    # 创建可视化
    tool.create_visualization(score_df, save_path="model_comparison_plot.png")

def example_2_custom_columns():
    """
    示例2: 自定义字段设置
    """
    print("\n" + "=" * 60)
    print("示例2: 自定义字段设置")
    print("=" * 60)
    
    # 初始化工具
    tool = ModelComparisonTool("Healthbench 组合.csv")
    
    # 加载数据
    df = tool.load_data()
    if df is None:
        return
    
    # 手动设置分数字段
    score_columns = [
        "overall_score-0916",
        "overall_score-0928", 
    ]
    
    model_names = [
        "0916",
        "0928", 
    ]
    
    tool.set_score_columns(score_columns, model_names)
    
    # 清理数据
    score_df = tool.clean_score_data()
    if score_df is None:
        return
    
    # 生成分析报告
    report = tool.generate_report(score_df, test_type='wilcoxon', alpha=0.05)
    print(report)

def example_3_baseline_comparison():
    """
    示例3: 与基线模型对比
    """
    print("\n" + "=" * 60)
    print("示例3: 与基线模型对比")
    print("=" * 60)
    
    # 初始化工具
    tool = ModelComparisonTool("归因组合.csv")
    
    # 加载数据
    df = tool.load_data()
    if df is None:
        return
    
    # 自动检测分数字段
    score_columns = tool.detect_score_columns(pattern="分_")
    
    # 清理数据
    score_df = tool.clean_score_data()
    if score_df is None:
        return
    
    # 选择基线模型（假设第一个模型为基线）
    baseline_model = score_columns[0]
    print(f"基线模型: {baseline_model}")
    
    # 与基线模型对比
    baseline_results = tool.baseline_comparison(
        score_df, 
        baseline_model, 
        test_type='wilcoxon', 
        alpha=0.05
    )
    
    print("\n与基线模型对比结果:")
    print(baseline_results.to_string(index=False))
    
    # 找出优于基线的模型
    better_models = baseline_results[baseline_results['优于基线'] == True]
    if len(better_models) > 0:
        print(f"\n🎉 发现 {len(better_models)} 个模型优于基线:")
        for _, row in better_models.iterrows():
            print(f"  - {row['模型']}: 均值差异 = {row['均值差异']:.4f}, p = {row['p值']:.4f}")
    else:
        print("\n😔 没有模型显著优于基线")

def example_4_different_tests():
    """
    示例4: 不同统计检验方法对比
    """
    print("\n" + "=" * 60)
    print("示例4: 不同统计检验方法对比")
    print("=" * 60)
    
    # 初始化工具
    tool = ModelComparisonTool("归因组合.csv")
    
    # 加载数据
    df = tool.load_data()
    if df is None:
        return
    
    # 自动检测分数字段
    score_columns = tool.detect_score_columns(pattern="分_")
    
    # 清理数据
    score_df = tool.clean_score_data()
    if score_df is None:
        return
    
    # 测试不同的统计方法
    test_methods = ['wilcoxon', 'ttest', 'mannwhitney']
    
    for test_method in test_methods:
        print(f"\n📊 使用 {test_method} 检验:")
        results = tool.pairwise_comparison(score_df, test_type=test_method, alpha=0.05)
        if results is not None and len(results) > 0:
            significant_count = len(results[results['是否显著'] == True])
            print(f"  发现 {significant_count} 对模型存在显著差异")
            
            # 显示前3个结果
            print("  前3个对比结果:")
            for i, (_, row) in enumerate(results.head(3).iterrows()):
                print(f"    {i+1}. {row['模型1']} vs {row['模型2']}: "
                      f"差异={row['均值差异']:.4f}, p={row['p值']:.4f}, "
                      f"显著={'是' if row['是否显著'] else '否'}")

def example_5_advanced_analysis():
    """
    示例5: 高级分析功能
    """
    print("\n" + "=" * 60)
    print("示例5: 高级分析功能")
    print("=" * 60)
    
    # 初始化工具
    tool = ModelComparisonTool("归因组合.csv")
    
    # 加载数据
    df = tool.load_data()
    if df is None:
        return
    
    # 自动检测分数字段
    score_columns = tool.detect_score_columns(pattern="分_")
    
    # 清理数据
    score_df = tool.clean_score_data()
    if score_df is None:
        return
    
    # 基本统计信息
    stats_df = tool.calculate_basic_stats(score_df)
    print("📈 基本统计信息:")
    print(stats_df.to_string(index=False))
    
    # 找出最佳模型
    best_model_idx = stats_df['均值'].idxmax()
    best_model = stats_df.loc[best_model_idx, '模型']
    best_score = stats_df.loc[best_model_idx, '均值']
    
    print(f"\n🏆 最佳模型: {best_model} (平均得分: {best_score:.4f})")
    
    # 模型排名
    print("\n📊 模型排名 (按平均得分):")
    ranked_models = stats_df.sort_values('均值', ascending=False)
    for i, (_, row) in enumerate(ranked_models.iterrows(), 1):
        print(f"  {i}. {row['模型']}: {row['均值']:.4f} ± {row['标准差']:.4f}")
    
    # 创建详细的可视化
    tool.create_visualization(score_df, save_path="detailed_analysis.png")
    print("\n📊 详细分析图表已保存到: detailed_analysis.png")

def main():
    """
    运行所有示例
    """
    print("🚀 模型对比工具使用示例")
    print("本示例将展示如何使用ModelComparisonTool进行模型对比分析")
    
    try:
        # 运行示例1: 基本使用
        example_1_basic_usage()
        
        # 运行示例2: 自定义字段
        example_2_custom_columns()
        
        # 运行示例3: 基线对比
        example_3_baseline_comparison()
        
        # 运行示例4: 不同检验方法
        example_4_different_tests()
        
        # 运行示例5: 高级分析
        example_5_advanced_analysis()
        
        print("\n" + "=" * 60)
        print("✅ 所有示例运行完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 运行示例时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
