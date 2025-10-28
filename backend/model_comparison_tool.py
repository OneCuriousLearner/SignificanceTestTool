#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型对比统计分析工具
支持多个模型之间的总分差距显著性检验
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import wilcoxon, ttest_rel, mannwhitneyu
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple, Optional, Union
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ModelComparisonTool:
    """
    模型对比统计分析工具类
    """
    
    def __init__(self, csv_file_path: str, encoding: str = 'utf-8'):
        """
        初始化工具
        
        Args:
            csv_file_path: CSV文件路径
            encoding: 文件编码，默认为utf-8
        """
        self.csv_file_path = csv_file_path
        self.encoding = encoding
        self.df = None
        self.score_columns = []
        self.model_names = []
        
    def load_data(self) -> pd.DataFrame:
        """
        加载CSV数据
        
        Returns:
            pd.DataFrame: 加载的数据框
        """
        try:
            self.df = pd.read_csv(self.csv_file_path, encoding=self.encoding)
            print(f"✅ 成功加载数据，共 {len(self.df)} 行，{len(self.df.columns)} 列")
            return self.df
        except Exception as e:
            print(f"❌ 加载数据失败: {e}")
            return None
    
    def detect_score_columns(self, pattern: str = "分_") -> List[str]:
        """
        自动检测分数字段
        
        Args:
            pattern: 分数字段的命名模式，默认为"分_"
            
        Returns:
            List[str]: 分数字段列表
        """
        if self.df is None:
            print("❌ 请先加载数据")
            return []
        
        # 查找包含分数字段的列
        score_columns = [col for col in self.df.columns if pattern in col]
        self.score_columns = score_columns
        self.model_names = [col.replace(pattern, "") for col in score_columns]
        
        print(f"🔍 检测到 {len(score_columns)} 个分数字段:")
        for i, (col, name) in enumerate(zip(score_columns, self.model_names)):
            print(f"  {i+1}. {col} -> {name}")
        
        return score_columns
    
    def set_score_columns(self, score_columns: List[str], model_names: Optional[List[str]] = None):
        """
        手动设置分数字段
        
        Args:
            score_columns: 分数字段列表
            model_names: 模型名称列表，如果为None则从字段名自动提取
        """
        if self.df is None:
            print("❌ 请先加载数据")
            return
        
        # 验证字段是否存在
        missing_cols = [col for col in score_columns if col not in self.df.columns]
        if missing_cols:
            print(f"❌ 以下字段不存在: {missing_cols}")
            return
        
        self.score_columns = score_columns
        if model_names is None:
            self.model_names = score_columns
        else:
            self.model_names = model_names
        
        print(f"✅ 设置完成，共 {len(score_columns)} 个模型")
    
    def clean_score_data(self) -> pd.DataFrame:
        """
        清理分数字据，处理缺失值和异常值
        
        Returns:
            pd.DataFrame: 清理后的数据
        """
        if not self.score_columns:
            print("❌ 请先设置分数字段")
            return None
        
        # 创建分数字据的副本
        score_df = self.df[self.score_columns].copy()
        
        # 转换数据类型
        for col in self.score_columns:
            score_df[col] = pd.to_numeric(score_df[col], errors='coerce')
        
        # 统计缺失值
        missing_count = score_df.isnull().sum()
        if missing_count.sum() > 0:
            print("⚠️  发现缺失值:")
            for col, count in missing_count.items():
                if count > 0:
                    print(f"  {col}: {count} 个缺失值")
        
        # 移除包含缺失值的行
        original_len = len(score_df)
        score_df = score_df.dropna()
        removed_len = original_len - len(score_df)
        
        if removed_len > 0:
            print(f"🧹 移除了 {removed_len} 行包含缺失值的数据")
        
        print(f"✅ 数据清理完成，剩余 {len(score_df)} 行有效数据")
        return score_df
    
    def calculate_basic_stats(self, score_df: pd.DataFrame) -> pd.DataFrame:
        """
        计算基本统计信息
        
        Args:
            score_df: 分数字据框
            
        Returns:
            pd.DataFrame: 统计信息
        """
        stats_data = []
        
        for i, col in enumerate(self.score_columns):
            scores = score_df[col].dropna()
            model_name = self.model_names[i] if i < len(self.model_names) else col
            stats_data.append({
                '模型': model_name,
                '样本数': len(scores),
                '均值': scores.mean(),
                '标准差': scores.std(),
                '中位数': scores.median(),
                '最小值': scores.min(),
                '最大值': scores.max(),
                '25%分位数': scores.quantile(0.25),
                '75%分位数': scores.quantile(0.75)
            })
        
        stats_df = pd.DataFrame(stats_data)
        return stats_df
    
    def pairwise_comparison(self, score_df: pd.DataFrame, 
                          test_type: str = 'wilcoxon',
                          alpha: float = 0.05) -> pd.DataFrame:
        """
        进行两两模型对比
        
        Args:
            score_df: 分数字据框
            test_type: 统计检验类型 ('wilcoxon', 'ttest', 'mannwhitney')
            alpha: 显著性水平
            
        Returns:
            pd.DataFrame: 对比结果
        """
        if len(self.score_columns) < 2:
            print("❌ 至少需要2个模型进行对比")
            return None
        
        results = []
        
        for i in range(len(self.score_columns)):
            for j in range(i + 1, len(self.score_columns)):
                model1_col = self.score_columns[i]
                model2_col = self.score_columns[j]
                model1_name = self.model_names[i] if i < len(self.model_names) else model1_col
                model2_name = self.model_names[j] if j < len(self.model_names) else model2_col
                
                scores1 = score_df[model1_col].dropna()
                scores2 = score_df[model2_col].dropna()
                
                # 确保两个模型的数据长度一致
                min_len = min(len(scores1), len(scores2))
                if min_len == 0:
                    continue
                
                scores1 = scores1.iloc[:min_len]
                scores2 = scores2.iloc[:min_len]
                
                # 计算差异
                diff = scores1 - scores2
                mean_diff = diff.mean()
                
                # 进行统计检验
                if test_type == 'wilcoxon':
                    try:
                        stat, p_value = wilcoxon(scores1, scores2, alternative='two-sided')
                        test_name = "Wilcoxon符号秩检验"
                    except ValueError:
                        stat, p_value = np.nan, np.nan
                        test_name = "Wilcoxon符号秩检验(无法计算)"
                elif test_type == 'ttest':
                    try:
                        stat, p_value = ttest_rel(scores1, scores2)
                        test_name = "配对t检验"
                    except ValueError:
                        stat, p_value = np.nan, np.nan
                        test_name = "配对t检验(无法计算)"
                elif test_type == 'mannwhitney':
                    try:
                        stat, p_value = mannwhitneyu(scores1, scores2, alternative='two-sided')
                        test_name = "Mann-Whitney U检验"
                    except ValueError:
                        stat, p_value = np.nan, np.nan
                        test_name = "Mann-Whitney U检验(无法计算)"
                else:
                    print(f"❌ 不支持的检验类型: {test_type}")
                    continue
                
                # 判断显著性
                is_significant = p_value < alpha if not np.isnan(p_value) else False
                
                results.append({
                    '模型1': model1_name,
                    '模型2': model2_name,
                    '模型1均值': scores1.mean(),
                    '模型2均值': scores2.mean(),
                    '均值差异': mean_diff,
                    '检验统计量': stat,
                    'p值': p_value,
                    '显著性水平': alpha,
                    '是否显著': is_significant,
                    '检验方法': test_name
                })
        
        results_df = pd.DataFrame(results)
        return results_df
    
    def baseline_comparison(self, score_df: pd.DataFrame, 
                           baseline_model: str,
                           test_type: str = 'wilcoxon',
                           alpha: float = 0.05) -> pd.DataFrame:
        """
        与基线模型对比
        
        Args:
            score_df: 分数字据框
            baseline_model: 基线模型名称
            test_type: 统计检验类型
            alpha: 显著性水平
            
        Returns:
            pd.DataFrame: 对比结果
        """
        if baseline_model not in self.score_columns:
            print(f"❌ 基线模型 {baseline_model} 不存在")
            return None
        
        results = []
        baseline_scores = score_df[baseline_model].dropna()
        
        for i, model in enumerate(self.score_columns):
            if model == baseline_model:
                continue
            
            model_scores = score_df[model].dropna()
            model_name = self.model_names[i] if i < len(self.model_names) else model
            
            # 确保数据长度一致
            min_len = min(len(baseline_scores), len(model_scores))
            if min_len == 0:
                continue
            
            baseline_subset = baseline_scores.iloc[:min_len]
            model_subset = model_scores.iloc[:min_len]
            
            # 计算差异
            diff = model_subset - baseline_subset
            mean_diff = diff.mean()
            
            # 进行统计检验
            if test_type == 'wilcoxon':
                try:
                    stat, p_value = wilcoxon(model_subset, baseline_subset, alternative='two-sided')
                    test_name = "Wilcoxon符号秩检验"
                except ValueError:
                    stat, p_value = np.nan, np.nan
                    test_name = "Wilcoxon符号秩检验(无法计算)"
            elif test_type == 'ttest':
                try:
                    stat, p_value = ttest_rel(model_subset, baseline_subset)
                    test_name = "配对t检验"
                except ValueError:
                    stat, p_value = np.nan, np.nan
                    test_name = "配对t检验(无法计算)"
            else:
                print(f"❌ 不支持的检验类型: {test_type}")
                continue
            
            # 判断显著性
            is_significant = p_value < alpha if not np.isnan(p_value) else False
            
            # 判断模型是否优于基线
            better_than_baseline = mean_diff > 0 and is_significant
            
            results.append({
                '模型': model_name,
                '基线模型': baseline_model,
                '模型均值': model_subset.mean(),
                '基线均值': baseline_subset.mean(),
                '均值差异': mean_diff,
                '检验统计量': stat,
                'p值': p_value,
                '显著性水平': alpha,
                '是否显著': is_significant,
                '优于基线': better_than_baseline,
                '检验方法': test_name
            })
        
        results_df = pd.DataFrame(results)
        return results_df
    
    def create_visualization(self, score_df: pd.DataFrame, 
                           save_path: Optional[str] = None) -> None:
        """
        创建可视化图表
        
        Args:
            score_df: 分数字据框
            save_path: 保存路径，如果为None则显示图表
        """
        # 设置图表样式
        plt.style.use('default')
        
        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('模型对比分析可视化', fontsize=16, fontweight='bold')
        
        # 1. 箱线图
        ax1 = axes[0, 0]
        score_df.boxplot(ax=ax1, rot=45)
        ax1.set_title('模型得分分布箱线图')
        ax1.set_ylabel('得分')
        
        # 2. 密度图
        ax2 = axes[0, 1]
        for col in self.score_columns:
            scores = score_df[col].dropna()
            ax2.hist(scores, alpha=0.6, label=col, bins=20)
        ax2.set_title('模型得分分布直方图')
        ax2.set_xlabel('得分')
        ax2.set_ylabel('频次')
        ax2.legend()
        
        # 3. 均值对比条形图
        ax3 = axes[1, 0]
        means = [score_df[col].mean() for col in self.score_columns]
        bars = ax3.bar(range(len(self.score_columns)), means)
        ax3.set_title('模型平均得分对比')
        ax3.set_xlabel('模型')
        ax3.set_ylabel('平均得分')
        ax3.set_xticks(range(len(self.score_columns)))
        ax3.set_xticklabels(self.score_columns, rotation=45)
        
        # 添加数值标签
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}', ha='center', va='bottom')
        
        # 4. 相关性热力图
        ax4 = axes[1, 1]
        corr_matrix = score_df.corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=ax4)
        ax4.set_title('模型得分相关性热力图')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 图表已保存到: {save_path}")
        else:
            plt.show()
    
    def generate_report(self, score_df: pd.DataFrame, 
                       baseline_model: Optional[str] = None,
                       test_type: str = 'wilcoxon',
                       alpha: float = 0.05) -> str:
        """
        生成分析报告
        
        Args:
            score_df: 分数字据框
            baseline_model: 基线模型名称
            test_type: 统计检验类型
            alpha: 显著性水平
            
        Returns:
            str: 分析报告
        """
        report = []
        report.append("=" * 60)
        report.append("模型对比统计分析报告")
        report.append("=" * 60)
        
        # 基本信息
        report.append(f"\n📊 数据概览:")
        report.append(f"  - 样本数量: {len(score_df)}")
        report.append(f"  - 模型数量: {len(self.score_columns)}")
        report.append(f"  - 统计检验: {test_type}")
        report.append(f"  - 显著性水平: α = {alpha}")
        
        # 基本统计信息
        stats_df = self.calculate_basic_stats(score_df)
        report.append(f"\n📈 基本统计信息:")
        report.append(stats_df.to_string(index=False))
        
        # 两两对比结果
        pairwise_results = self.pairwise_comparison(score_df, test_type, alpha)
        report.append(f"\n🔍 两两模型对比结果:")
        report.append(pairwise_results.to_string(index=False))
        
        # 基线对比结果
        if baseline_model:
            baseline_results = self.baseline_comparison(score_df, baseline_model, test_type, alpha)
            report.append(f"\n🎯 与基线模型 {baseline_model} 的对比结果:")
            report.append(baseline_results.to_string(index=False))
        
        # 总结
        report.append(f"\n📝 分析总结:")
        significant_pairs = pairwise_results[pairwise_results['是否显著'] == True]
        if len(significant_pairs) > 0:
            report.append(f"  - 发现 {len(significant_pairs)} 对模型之间存在显著差异")
            for _, row in significant_pairs.iterrows():
                report.append(f"    * {row['模型1']} vs {row['模型2']}: p = {row['p值']:.4f}")
        else:
            report.append("  - 未发现模型间存在显著差异")
        
        return "\n".join(report)


def main():
    """
    主函数 - 使用示例
    """
    # 示例用法
    print("🚀 模型对比统计分析工具")
    print("=" * 50)
    
    # 初始化工具
    tool = ModelComparisonTool("归因组合.csv")
    
    # 加载数据
    df = tool.load_data()
    if df is None:
        return
    
    # 自动检测分数字段
    score_columns = tool.detect_score_columns()
    
    # 清理数据
    score_df = tool.clean_score_data()
    if score_df is None:
        return
    
    # 生成分析报告
    report = tool.generate_report(score_df, test_type='wilcoxon', alpha=0.05)
    print(report)
    
    # 创建可视化
    tool.create_visualization(score_df)


if __name__ == "__main__":
    main()
