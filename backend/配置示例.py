#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置参数示例文件
展示如何设置不同的参数组合
"""

# ==================== 配置参数示例 ====================

# 示例1: 基本使用 - 自动检测所有分数字段
CONFIG_BASIC = {
    "CSV_FILE_PATH": "merged_result-1.csv",
    "BASELINE_MODEL": None,
    "SCORE_COLUMNS": None,  # 自动检测
    "MODEL_NAMES": None,   # 自动提取
    "TEST_TYPE": 'wilcoxon',
    "ALPHA": 0.05,
    "SCORE_PATTERN": "分_"
}

# 示例2: 手动指定参评模型字段
CONFIG_MANUAL = {
    "CSV_FILE_PATH": "merged_result-1.csv",
    "BASELINE_MODEL": "分_基线模型",
    "SCORE_COLUMNS": [
        "分_模型A",
        "分_模型B", 
        "分_模型C",
        "分_模型D"
    ],
    "MODEL_NAMES": [
        "模型A",
        "模型B",
        "模型C", 
        "模型D"
    ],
    "TEST_TYPE": 'wilcoxon',
    "ALPHA": 0.05,
    "SCORE_PATTERN": "分_"
}

# 示例3: 与基线模型对比
CONFIG_BASELINE = {
    "CSV_FILE_PATH": "merged_result-1.csv",
    "BASELINE_MODEL": "分_基线模型",  # 指定基线模型
    "SCORE_COLUMNS": None,  # 自动检测其他模型
    "MODEL_NAMES": None,
    "TEST_TYPE": 'wilcoxon',
    "ALPHA": 0.01,  # 更严格的显著性水平
    "SCORE_PATTERN": "分_"
}

# 示例4: 使用不同的统计检验
CONFIG_TTEST = {
    "CSV_FILE_PATH": "merged_result-1.csv",
    "BASELINE_MODEL": None,
    "SCORE_COLUMNS": None,
    "MODEL_NAMES": None,
    "TEST_TYPE": 'ttest',  # 使用配对t检验
    "ALPHA": 0.05,
    "SCORE_PATTERN": "分_"
}

# 示例5: 自定义字段模式检测
CONFIG_CUSTOM_PATTERN = {
    "CSV_FILE_PATH": "merged_result-1.csv",
    "BASELINE_MODEL": None,
    "SCORE_COLUMNS": None,
    "MODEL_NAMES": None,
    "TEST_TYPE": 'wilcoxon',
    "ALPHA": 0.05,
    "SCORE_PATTERN": "score_"  # 检测包含"score_"的字段
}

# ==================== 使用方法 ====================

def show_config_examples():
    """
    显示配置示例
    """
    print("📋 配置参数示例:")
    print("=" * 50)
    
    examples = [
        ("基本使用", CONFIG_BASIC),
        ("手动指定字段", CONFIG_MANUAL),
        ("基线模型对比", CONFIG_BASELINE),
        ("配对t检验", CONFIG_TTEST),
        ("自定义模式", CONFIG_CUSTOM_PATTERN)
    ]
    
    for name, config in examples:
        print(f"\n🔧 {name}:")
        for key, value in config.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    show_config_examples()
