#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask 后端服务
提供 CSV 数据显著性分析 API 接口
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from model_comparison_tool import ModelComparisonTool
import pandas as pd
import os
import tempfile
import traceback

app = Flask(__name__)

# 配置 CORS - 允许所有源的跨域请求
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": False
    }
})

# 配置上传文件夹
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 最大 1024MB

# 存储当前加载的 CSV 数据
current_csv_file = None
current_tool = None


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传 CSV 文件并解析列"""
    global current_csv_file, current_tool
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': '只支持 CSV 文件'}), 400
        
        # 保存文件
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        current_csv_file = filename
        
        # 读取 CSV 获取列信息
        df = pd.read_csv(filename)
        columns = df.columns.tolist()
        
        # 识别数值列（排除非数值列）
        numeric_columns = []
        for col in columns:
            try:
                # 尝试转换为数值类型，如果成功则为数值列
                pd.to_numeric(df[col], errors='coerce')
                # 检查是否大部分值可以转换为数值（至少50%）
                numeric_values = pd.to_numeric(df[col], errors='coerce').notna().sum()
                if numeric_values / len(df) >= 0.5:
                    numeric_columns.append(col)
            except:
                continue
        
        # 初始化分析工具
        current_tool = ModelComparisonTool(filename)
        
        return jsonify({
            'message': '文件上传成功',
            'filename': file.filename,
            'columns': columns,
            'numeric_columns': numeric_columns,
            'rowCount': len(df)
        })
    
    except Exception as e:
        return jsonify({'error': f'上传文件失败: {str(e)}'}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """执行显著性分析"""
    global current_csv_file, current_tool
    
    try:
        if not current_csv_file or not current_tool:
            return jsonify({'error': '请先上传 CSV 文件'}), 400
        
        data = request.json
        baseline = data.get('baseline')
        data_columns = data.get('dataColumns', [])
        test_type = data.get('testType', 'wilcoxon')
        alpha = data.get('alpha', 0.05)
        
        if not baseline:
            return jsonify({'error': '请选择 Baseline 列'}), 400
        
        if not data_columns or len(data_columns) == 0:
            return jsonify({'error': '请至少选择一个数据列'}), 400
        
        # 加载数据
        df = current_tool.load_data()
        if df is None:
            return jsonify({'error': '加载数据失败'}), 500
        
        # 设置分数列（包含 baseline 和其他数据列）
        all_columns = [baseline] + [col for col in data_columns if col != baseline]
        model_names = all_columns.copy()
        current_tool.set_score_columns(all_columns, model_names)
        
        # 清理数据
        score_df = current_tool.clean_score_data()
        if score_df is None:
            return jsonify({'error': '数据清理失败'}), 500
        
        # 计算基本统计信息
        stats_df = current_tool.calculate_basic_stats(score_df)
        
        # 进行两两对比
        pairwise_results = current_tool.pairwise_comparison(
            score_df, 
            test_type=test_type, 
            alpha=alpha
        )
        
        # 与基线模型对比
        baseline_results = None
        if baseline in all_columns:
            baseline_results = current_tool.baseline_comparison(
                score_df,
                baseline,
                test_type=test_type,
                alpha=alpha
            )
        
        # 构建响应
        response = {
            'dataOverview': {
                'sampleCount': len(score_df),
                'modelCount': len(all_columns),
                'testType': test_type,
                'alpha': alpha
            },
            'basicStats': stats_df.to_dict('records') if stats_df is not None else [],
            'pairwiseComparison': pairwise_results.to_dict('records') if pairwise_results is not None else [],
            'baselineComparison': baseline_results.to_dict('records') if baseline_results is not None else []
        }
        
        # 找出最佳模型
        if stats_df is not None and len(stats_df) > 0:
            best_model_idx = stats_df['均值'].idxmax()
            response['bestModel'] = {
                'name': stats_df.loc[best_model_idx, '模型'],
                'meanScore': float(stats_df.loc[best_model_idx, '均值'])
            }
        
        # 统计显著差异数量
        if pairwise_results is not None:
            significant_count = len(pairwise_results[pairwise_results['是否显著'] == True])
            response['significantPairsCount'] = significant_count
        
        return jsonify(response)
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'分析失败: {str(e)}'}), 500


@app.route('/api/detect-columns', methods=['POST'])
def detect_columns():
    """自动检测分数列"""
    global current_tool
    
    try:
        if not current_tool:
            return jsonify({'error': '请先上传 CSV 文件'}), 400
        
        data = request.json
        pattern = data.get('pattern', '_score')
        
        # 加载数据
        df = current_tool.load_data()
        if df is None:
            return jsonify({'error': '加载数据失败'}), 500
        
        # 自动检测分数列
        score_columns = current_tool.detect_score_columns(pattern=pattern)
        
        return jsonify({
            'scoreColumns': score_columns,
            'modelNames': current_tool.model_names
        })
    
    except Exception as e:
        return jsonify({'error': f'检测列失败: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'message': '服务正常运行'})


@app.route('/')
def index():
    """首页"""
    return jsonify({
        'name': 'CSV 数据显著性分析 API',
        'version': '1.0.0',
        'endpoints': {
            '/api/upload': 'POST - 上传 CSV 文件',
            '/api/analyze': 'POST - 执行显著性分析',
            '/api/detect-columns': 'POST - 自动检测分数列',
            '/health': 'GET - 健康检查'
        }
    })


if __name__ == '__main__':
    print("🚀 启动 Flask 后端服务...")
    print("=" * 50)
    print("📡 服务地址: http://localhost:5000")
    print("📋 API 文档: http://localhost:5000/")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
