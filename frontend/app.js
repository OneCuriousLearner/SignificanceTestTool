// CSV 数据显著性分析工具 - 主应用逻辑

const { useState } = React;

function App() {
  const [columns, setColumns] = useState([]);
  const [numericColumns, setNumericColumns] = useState([]);
  const [baselineColumn, setBaselineColumn] = useState("");
  const [dataColumns, setDataColumns] = useState([]);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [fileName, setFileName] = useState("未选择文件");
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [showRawData, setShowRawData] = useState(false);
  const [columnAliases, setColumnAliases] = useState({}); // 存储列别名

  // 导出HTML报告
  const exportHTMLReport = () => {
    if (!analysisResult) return;

    const dataOverview = analysisResult.dataOverview || {};
    const basicStats = analysisResult.basicStats || [];
    const pairwiseComparison = analysisResult.pairwiseComparison || [];
    const baselineComparison = analysisResult.baselineComparison || [];
    const bestModel = analysisResult.bestModel || null;

    const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>显著性分析报告 - ${fileName}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7ff 0%, #f1f5f9 100%);
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 10px 24px rgba(0,0,0,0.1);
        }
        .result-header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid #1677ff;
        }
        .result-header h2 {
            margin: 0;
            font-size: 24px;
            color: #1d2129;
            font-weight: 600;
        }
        .emoji {
            font-size: 1.3em;
            margin-right: 8px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin: 24px 0;
        }
        .info-card {
            background: linear-gradient(135deg, #f5f7ff 0%, #e8f0ff 100%);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #d6e0f5;
        }
        .info-card .value {
            display: block;
            font-size: 28px;
            font-weight: 700;
            color: #1677ff;
            margin-bottom: 8px;
        }
        .info-card .label {
            display: block;
            font-size: 13px;
            color: #64748b;
            font-weight: 500;
        }
        .result-section {
            margin: 32px 0;
        }
        .result-section h3 {
            color: #1d2129;
            font-size: 18px;
            font-weight: 600;
            border-left: 4px solid #1677ff;
            padding-left: 12px;
            margin-bottom: 16px;
        }
        .result-table {
            width: 100%;
            border-collapse: collapse;
            background: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
            margin: 16px 0;
        }
        .result-table thead {
            background: linear-gradient(135deg, #1677ff, #4096ff);
        }
        .result-table th {
            color: #ffffff;
            padding: 14px 16px;
            text-align: left;
            font-weight: 600;
            font-size: 14px;
        }
        .result-table td {
            padding: 12px 16px;
            border-bottom: 1px solid #f1f5f9;
            font-size: 14px;
            color: #475569;
        }
        .result-table tbody tr:nth-child(even) {
            background: #f8fafc;
        }
        .result-table tbody tr:hover {
            background: #f0f7ff;
        }
        .best-model {
            background: linear-gradient(135deg, #f59e0b, #f97316);
            color: #ffffff;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            margin: 20px 0;
            font-size: 16px;
            font-weight: 600;
            box-shadow: 0 8px 20px rgba(245, 158, 11, 0.3);
        }
        .significant {
            color: #10b981;
            font-weight: 600;
        }
        .not-significant {
            color: #ef4444;
            font-weight: 600;
        }
        .summary-box {
            background: #f8fafc;
            border-left: 4px solid #1677ff;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .summary-box p {
            margin: 8px 0;
            color: #475569;
            line-height: 1.6;
        }
        .summary-box ul {
            margin: 12px 0;
            padding-left: 24px;
        }
        .summary-box li {
            margin: 8px 0;
            color: #475569;
        }
        .result-footer {
            text-align: center;
            color: #94a3b8;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="result-header">
            <h2><span class="emoji">📊</span>显著性分析报告</h2>
        </div>

        ${dataOverview ? `
        <div class="result-section">
            <h3><span class="emoji">📊</span> 数据概览</h3>
            <div class="info-grid">
                <div class="info-card">
                    <span class="value">${dataOverview.sampleCount ?? 0}</span>
                    <span class="label">样本数量</span>
                </div>
                <div class="info-card">
                    <span class="value">${dataOverview.modelCount ?? 0}</span>
                    <span class="label">模型数量</span>
                </div>
                <div class="info-card">
                    <span class="value">${dataOverview.testType ?? 'N/A'}</span>
                    <span class="label">统计检验</span>
                </div>
                <div class="info-card">
                    <span class="value">α = ${dataOverview.alpha ?? 0.05}</span>
                    <span class="label">显著性水平</span>
                </div>
            </div>
        </div>
        ` : ''}

        ${basicStats && basicStats.length > 0 ? `
        <div class="result-section">
            <h3><span class="emoji">📈</span> 得分统计</h3>
            <table class="result-table">
                <thead>
                    <tr>
                        <th>模型</th>
                        <th>样本数</th>
                        <th>均值</th>
                        <th>标准差</th>
                        <th>中位数</th>
                        <th>25%分位数</th>
                        <th>75%分位数</th>
                    </tr>
                </thead>
                <tbody>
                    ${basicStats.map(stat => `
                    <tr>
                        <td><strong>${getDisplayName(stat['模型'] ?? stat.column)}</strong></td>
                        <td>${stat['样本数'] ?? stat.count}</td>
                        <td>${(stat['均值'] ?? stat.mean)?.toFixed(4)}</td>
                        <td>${(stat['标准差'] ?? stat.std)?.toFixed(4)}</td>
                        <td>${(stat['中位数'] ?? stat.median)?.toFixed(4)}</td>
                        <td>${(stat['25%分位数'] ?? stat.q25)?.toFixed(4)}</td>
                        <td>${(stat['75%分位数'] ?? stat.q75)?.toFixed(4)}</td>
                    </tr>
                    `).join('')}
                </tbody>
            </table>

            ${bestModel ? `
            <div class="best-model">
                <span class="emoji">🏆</span>
                最佳模型: <strong>${getDisplayName(bestModel.name)}</strong> 
                (平均得分: ${bestModel.meanScore?.toFixed(4)})
            </div>
            ` : ''}
        </div>
        ` : ''}

        ${pairwiseComparison && pairwiseComparison.length > 0 ? `
        <div class="result-section">
            <h3><span class="emoji">🔍</span> 两两模型对比</h3>
            <table class="result-table">
                <thead>
                    <tr>
                        <th>模型1</th>
                        <th>模型2</th>
                        <th>均值1</th>
                        <th>均值2</th>
                        <th>均值差异</th>
                        <th>检验统计量</th>
                        <th>p值</th>
                        <th>是否显著</th>
                    </tr>
                </thead>
                <tbody>
                    ${pairwiseComparison.map(comp => `
                    <tr>
                        <td><strong>${getDisplayName(comp['模型1'] ?? comp.model1)}</strong></td>
                        <td><strong>${getDisplayName(comp['模型2'] ?? comp.model2)}</strong></td>
                        <td>${(comp['模型1均值'] ?? comp.mean1)?.toFixed(4)}</td>
                        <td>${(comp['模型2均值'] ?? comp.mean2)?.toFixed(4)}</td>
                        <td>${(comp['均值差异'] ?? comp.mean_diff)?.toFixed(4)}</td>
                        <td>${(comp['检验统计量'] ?? comp.statistic)?.toFixed(4)}</td>
                        <td>${(comp['p值'] ?? comp.p_value)?.toFixed(6)}</td>
                        <td class="${(comp['是否显著'] ?? comp.significant) ? 'significant' : 'not-significant'}">
                            ${(comp['是否显著'] ?? comp.significant) ? '✅ 是' : '❌ 否'}
                        </td>
                    </tr>
                    `).join('')}
                </tbody>
            </table>

            <h3 style="font-size: 16px; margin-top: 24px;">
                <span class="emoji">📋</span> 显著差异总结
            </h3>
            <div class="summary-box">
                ${pairwiseComparison.some(c => c['是否显著'] || c.significant) ? `
                <p>发现 <strong>${pairwiseComparison.filter(c => c['是否显著'] || c.significant).length}</strong> 对模型间存在显著差异</p>
                ` : `
                <p>未发现模型间存在显著差异</p>
                `}
            </div>
        </div>
        ` : ''}

        ${baselineComparison && baselineComparison.length > 0 ? `
        <div class="result-section">
            <h3><span class="emoji">🎯</span> 与基线模型对比</h3>
            <div class="summary-box">
                <p><strong>基线模型</strong>: ${getDisplayName(baselineColumn)}</p>
                <p style="font-size: 13px; color: #64748b;">
                    <em>其他模型的表现将与此基线进行显著性比较</em>
                </p>
            </div>
            <table class="result-table">
                <thead>
                    <tr>
                        <th>模型</th>
                        <th>模型均值</th>
                        <th>基线均值</th>
                        <th>均值差异</th>
                        <th>统计量</th>
                        <th>p值</th>
                        <th>是否显著</th>
                        <th>优于基线</th>
                    </tr>
                </thead>
                <tbody>
                    ${baselineComparison.map(comp => `
                    <tr>
                        <td><strong>${getDisplayName(comp['模型'] ?? comp.model)}</strong></td>
                        <td>${(comp['模型均值'] ?? comp.model_mean)?.toFixed(4)}</td>
                        <td>${(comp['基线均值'] ?? comp.baseline_mean)?.toFixed(4)}</td>
                        <td>${(comp['均值差异'] ?? comp.mean_diff)?.toFixed(4)}</td>
                        <td>${(comp['检验统计量'] ?? comp.statistic)?.toFixed(4)}</td>
                        <td>${(comp['p值'] ?? comp.p_value)?.toFixed(6)}</td>
                        <td class="${(comp['是否显著'] ?? comp.significant) ? 'significant' : 'not-significant'}">
                            ${(comp['是否显著'] ?? comp.significant) ? '✅ 是' : '❌ 否'}
                        </td>
                        <td class="${(comp['优于基线'] ?? comp.better_than_baseline) ? 'significant' : 'not-significant'}">
                            ${(comp['优于基线'] ?? comp.better_than_baseline) ? '✅ 是' : '❌ 否'}
                        </td>
                    </tr>
                    `).join('')}
                </tbody>
            </table>

            <h3 style="font-size: 16px; margin-top: 24px;">
                <span class="emoji">${baselineComparison.some(c => c['优于基线'] || c.better_than_baseline) ? '🎉' : '😔'}</span> 
                基线对比结果
            </h3>
            <div class="summary-box">
                ${baselineComparison.some(c => c['优于基线'] || c.better_than_baseline) ? `
                <p>有 <strong>${baselineComparison.filter(c => c['优于基线'] || c.better_than_baseline).length}</strong> 个模型显著优于基线</p>
                ` : `
                <p>没有模型显著优于基线</p>
                `}
            </div>
        </div>
        ` : ''}

        <div class="result-section">
            <h3><span class="emoji">📝</span> 分析总结</h3>
            <div class="summary-box">
                <ul>
                    <li>共进行了 <strong>${pairwiseComparison.length}</strong> 对模型对比</li>
                    <li>发现 <strong>${analysisResult.significantPairsCount ?? 0}</strong> 对模型存在显著差异</li>
                    ${(analysisResult.significantPairsCount ?? 0) === 0 ? `
                    <li style="color: #64748b;">未发现显著差异，可能需要更多样本或调整评估标准</li>
                    ` : ''}
                    ${baselineComparison && baselineComparison.length > 0 ? `
                    <li>与基线模型对比: ${baselineComparison.filter(c => c['优于基线'] ?? c.better_than_baseline).length} 个模型显著优于基线</li>
                    ` : ''}
                </ul>
            </div>
        </div>

        <div class="result-footer">
            <p>报告生成时间: ${new Date().toLocaleString('zh-CN')}</p>
            <p>数据文件: ${fileName}</p>
        </div>
    </div>
</body>
</html>`;

    // 创建下载链接
    const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `分析报告_${fileName.replace('.csv', '')}_${new Date().toISOString().slice(0, 10)}.html`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // 设置列别名
  const setColumnAlias = (column, alias) => {
    setColumnAliases(prev => ({
      ...prev,
      [column]: alias
    }));
  };

  // 获取列的显示名称（别名优先）
  const getDisplayName = (column) => {
    return columnAliases[column] || column;
  };

  // 切换数据列选择状态
  const toggleDataColumn = (column) => {
    setDataColumns(prev => {
      if (prev.includes(column)) {
        // 如果已选中，则取消选中
        return prev.filter(c => c !== column);
      } else {
        // 如果未选中，则添加到选中列表
        return [...prev, column];
      }
    });
  };

  // 渲染报告组件
  const renderAnalysisReport = () => {
    if (!analysisResult) return null;
    if (analysisResult.error) {
      return (
        <div className="result-card">
          <div className="summary-box" style={{ borderLeftColor: '#ef4444' }}>
            <p style={{ color: '#ef4444', fontWeight: 600 }}>❌ 分析出错: {analysisResult.error}</p>
          </div>
        </div>
      );
    }

    // 适配后端返回的数据格式
    const dataOverview = analysisResult.dataOverview || {};
    const basicStats = analysisResult.basicStats || [];
    const pairwiseComparison = analysisResult.pairwiseComparison || [];
    const baselineComparison = analysisResult.baselineComparison || [];
    const bestModel = analysisResult.bestModel || null;

    return (
      <div className="result-card">
        {/* 报告标题 */}
        <div className="result-header">
          <h2><span className="emoji">📊</span>显著性分析报告</h2>
        </div>

        {/* 数据概览 */}
        {dataOverview && (
          <div className="result-section">
            <h3><span className="emoji">📊</span> 数据概览</h3>
            <div className="info-grid">
              <div className="info-card">
                <span className="value">{dataOverview.sampleCount ?? 0}</span>
                <span className="label">样本数量</span>
              </div>
              <div className="info-card">
                <span className="value">{dataOverview.modelCount ?? 0}</span>
                <span className="label">模型数量</span>
              </div>
              <div className="info-card">
                <span className="value">{dataOverview.testType ?? 'N/A'}</span>
                <span className="label">统计检验</span>
              </div>
              <div className="info-card">
                <span className="value">α = {dataOverview.alpha ?? 0.05}</span>
                <span className="label">显著性水平</span>
              </div>
            </div>
          </div>
        )}

        {/* 统计描述 */}
        {basicStats && basicStats.length > 0 && (
          <div className="result-section">
            <h3><span className="emoji">📈</span> 得分统计</h3>
            <table className="result-table">
              <thead>
                <tr>
                  <th>模型</th>
                  <th>样本数</th>
                  <th>均值</th>
                  <th>标准差</th>
                  <th>中位数</th>
                  <th>25%分位数</th>
                  <th>75%分位数</th>
                </tr>
              </thead>
              <tbody>
                {basicStats.map((stat, idx) => (
                  <tr key={idx}>
                    <td><strong>{getDisplayName(stat['模型'] ?? stat.column)}</strong></td>
                    <td>{stat['样本数'] ?? stat.count}</td>
                    <td>{(stat['均值'] ?? stat.mean)?.toFixed(4)}</td>
                    <td>{(stat['标准差'] ?? stat.std)?.toFixed(4)}</td>
                    <td>{(stat['中位数'] ?? stat.median)?.toFixed(4)}</td>
                    <td>{(stat['25%分位数'] ?? stat.q25)?.toFixed(4)}</td>
                    <td>{(stat['75%分位数'] ?? stat.q75)?.toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* 最佳模型 */}
            {bestModel && (
              <div className="best-model">
                <span className="emoji">🏆</span>
                最佳模型: <strong>{getDisplayName(bestModel.name)}</strong> 
                (平均得分: {bestModel.meanScore?.toFixed(4)})
              </div>
            )}
          </div>
        )}

        {/* 两两对比 */}
        {pairwiseComparison && pairwiseComparison.length > 0 && (
          <div className="result-section">
            <h3><span className="emoji">🔍</span> 两两模型对比</h3>
            <table className="result-table">
              <thead>
                <tr>
                  <th>模型1</th>
                  <th>模型2</th>
                  <th>均值1</th>
                  <th>均值2</th>
                  <th>均值差异</th>
                  <th>检验统计量</th>
                  <th>p值</th>
                  <th>是否显著</th>
                </tr>
              </thead>
              <tbody>
                {pairwiseComparison.map((comp, idx) => (
                  <tr key={idx}>
                    <td><strong>{getDisplayName(comp['模型1'] ?? comp.model1)}</strong></td>
                    <td><strong>{getDisplayName(comp['模型2'] ?? comp.model2)}</strong></td>
                    <td>{(comp['模型1均值'] ?? comp.mean1)?.toFixed(4)}</td>
                    <td>{(comp['模型2均值'] ?? comp.mean2)?.toFixed(4)}</td>
                    <td>{(comp['均值差异'] ?? comp.mean_diff)?.toFixed(4)}</td>
                    <td>{(comp['检验统计量'] ?? comp.statistic)?.toFixed(4)}</td>
                    <td>{(comp['p值'] ?? comp.p_value)?.toFixed(6)}</td>
                    <td className={(comp['是否显著'] ?? comp.significant) ? "significant" : "not-significant"}>
                      {(comp['是否显著'] ?? comp.significant) ? "✅ 是" : "❌ 否"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* 显著差异总结 */}
            <h3 style={{ fontSize: '16px', marginTop: '24px' }}>
              <span className="emoji">📋</span> 显著差异总结
            </h3>
            <div className="summary-box">
              {pairwiseComparison.some(c => c['是否显著'] ?? c.significant) ? (
                <p>
                  发现 <strong>
                    {pairwiseComparison.filter(c => c['是否显著'] ?? c.significant).length}
                  </strong> 对模型间存在显著差异
                </p>
              ) : (
                <p>未发现模型间存在显著差异</p>
              )}
            </div>
          </div>
        )}

        {/* 与基线对比 */}
        {baselineComparison && baselineComparison.length > 0 && (
          <div className="result-section">
            <h3><span className="emoji">🎯</span> 与基线模型对比</h3>
            <div className="summary-box">
              <p><strong>基线模型</strong>: {getDisplayName(baselineColumn)}</p>
              <p style={{ fontSize: '13px', color: '#64748b' }}>
                <em>其他模型的表现将与此基线进行显著性比较</em>
              </p>
            </div>
            <table className="result-table">
              <thead>
                <tr>
                  <th>模型</th>
                  <th>模型均值</th>
                  <th>基线均值</th>
                  <th>均值差异</th>
                  <th>统计量</th>
                  <th>p值</th>
                  <th>是否显著</th>
                  <th>优于基线</th>
                </tr>
              </thead>
              <tbody>
                {baselineComparison.map((comp, idx) => (
                  <tr key={idx}>
                    <td><strong>{getDisplayName(comp['模型'] ?? comp.model)}</strong></td>
                    <td>{(comp['模型均值'] ?? comp.model_mean)?.toFixed(4)}</td>
                    <td>{(comp['基线均值'] ?? comp.baseline_mean)?.toFixed(4)}</td>
                    <td>{(comp['均值差异'] ?? comp.mean_diff)?.toFixed(4)}</td>
                    <td>{(comp['检验统计量'] ?? comp.statistic)?.toFixed(4)}</td>
                    <td>{(comp['p值'] ?? comp.p_value)?.toFixed(6)}</td>
                    <td className={(comp['是否显著'] ?? comp.significant) ? "significant" : "not-significant"}>
                      {(comp['是否显著'] ?? comp.significant) ? "✅ 是" : "❌ 否"}
                    </td>
                    <td className={(comp['优于基线'] ?? comp.better_than_baseline) ? "significant" : "not-significant"}>
                      {(comp['优于基线'] ?? comp.better_than_baseline) ? "✅ 是" : "❌ 否"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* 基线对比结果总结 */}
            <h3 style={{ fontSize: '16px', marginTop: '24px' }}>
              <span className="emoji">
                {baselineComparison.some(c => c['优于基线'] ?? c.better_than_baseline) ? '🎉' : '😔'}
              </span> 基线对比结果
            </h3>
            <div className="summary-box">
              {baselineComparison.some(c => c['优于基线'] ?? c.better_than_baseline) ? (
                <p>
                  有 <strong>
                    {baselineComparison.filter(c => c['优于基线'] ?? c.better_than_baseline).length}
                  </strong> 个模型显著优于基线
                </p>
              ) : (
                <p>没有模型显著优于基线</p>
              )}
            </div>
          </div>
        )}

        {/* 分析总结 */}
        <div className="result-section">
          <h3><span className="emoji">📝</span> 分析总结</h3>
          <div className="summary-box">
            <ul>
              <li>共进行了 <strong>{pairwiseComparison.length}</strong> 对模型对比</li>
              <li>发现 <strong>{analysisResult.significantPairsCount ?? 0}</strong> 对模型存在显著差异</li>
              {(analysisResult.significantPairsCount ?? 0) === 0 && (
                <li style={{ color: '#64748b' }}>
                  未发现显著差异，可能需要更多样本或调整评估标准
                </li>
              )}
              {baselineComparison && baselineComparison.length > 0 && (
                <li>
                  与基线模型对比: {baselineComparison.filter(c => c['优于基线'] ?? c.better_than_baseline).length} 个模型显著优于基线
                </li>
              )}
            </ul>
          </div>
        </div>

        {/* 原始数据（可折叠） */}
        <div className="raw-data">
          <button 
            className="raw-data-toggle"
            onClick={() => setShowRawData(!showRawData)}
          >
            <span>{showRawData ? '▼' : '▶'}</span>
            <span>{showRawData ? '隐藏' : '查看'}原始JSON数据</span>
          </button>
          {showRawData && (
            <div className="raw-data-content">
              <pre>{JSON.stringify(analysisResult, null, 2)}</pre>
            </div>
          )}
        </div>

        {/* 报告页脚 */}
        <div className="result-footer">
          <p>报告生成时间: {new Date().toLocaleString('zh-CN')}</p>
        </div>
      </div>
    );
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setUploading(true);
    setAnalysisResult(null);

    try {
      // 使用 FormData 上传文件到后端
      const formData = new FormData();
      formData.append('file', file);

      // 使用相对路径，Nginx 会代理到后端
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`上传失败: ${response.status}`);
      }

      const result = await response.json();
      
      // 设置列信息（包括数值列）
      setColumns(result.columns || []);
      setNumericColumns(result.numeric_columns || []);
      setBaselineColumn("");
      setDataColumns([]);
      setColumnAliases({}); // 重置别名
      
      console.log("文件上传成功:", result);
      console.log("数值列:", result.numeric_columns);
    } catch (error) {
      console.error("上传文件出错:", error);
      alert(`上传文件失败: ${error.message}`);
      setColumns([]);
    } finally {
      setUploading(false);
    }
  };

  const handleRunAnalysis = async () => {
    if (!baselineColumn || dataColumns.length === 0) {
      alert("请选择 Baseline 列和至少一个数据列");
      return;
    }

    setAnalyzing(true);
    setAnalysisResult(null);

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          baseline: baselineColumn,
          dataColumns: dataColumns,
          testType: "wilcoxon",
          alpha: 0.05
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `请求失败: ${response.status}`);
      }

      const result = await response.json();
      setAnalysisResult(result);
      console.log("分析结果:", result);
    } catch (error) {
      console.error("分析出错:", error);
      setAnalysisResult({ error: error.message });
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="app-shell">
      <div className="card">
        <div className="card-header">
          <h1>CSV 数据显著性分析</h1>
          <p>上传数据文件，选择基准列和对照列，即刻获取显著性分析结果。</p>
        </div>

        <div className="upload-block">
          <span className="upload-label">上传 CSV 文件</span>
          <label className="upload-button" htmlFor="csv-input">
            {uploading ? "上传中..." : "选择文件"}
          </label>
          <input
            id="csv-input"
            className="upload-input"
            type="file"
            accept=".csv"
            onChange={handleFileUpload}
            disabled={uploading}
          />
          <span className="upload-filename" title={fileName}>
            {fileName}
          </span>
        </div>

        {columns.length > 0 ? (
          <>
            <div>
              <h3 className="section-title">选择 Baseline 列</h3>
              <select
                className="select"
                value={baselineColumn}
                onChange={(event) => setBaselineColumn(event.target.value)}
              >
                <option value="">请选择</option>
                {numericColumns.map((column) => (
                  <option key={column} value={column}>
                    {column}
                  </option>
                ))}
              </select>
              <div className="hint-text">
                用于作为对照组进行显著性比较的列（仅显示数值列）。【若要添加模型别名，请在下方多选处修改】
                {numericColumns.length === 0 && (
                  <span style={{ color: '#ef4444', marginLeft: '8px' }}>
                    ⚠️ 未检测到数值列，请检查数据格式
                  </span>
                )}
              </div>
            </div>

            <div>
              <h3 className="section-title">选择参与分析的列</h3>
              <div className="custom-multi-select">
                {numericColumns.map((column) => (
                  <div
                    key={column}
                    className={`multi-select-item ${dataColumns.includes(column) ? 'selected' : ''}`}
                  >
                    <div 
                      className="multi-select-checkbox"
                      onClick={() => toggleDataColumn(column)}
                    ></div>
                    <span 
                      className="multi-select-label"
                      onClick={() => toggleDataColumn(column)}
                    >
                      {column}
                    </span>
                    <input
                      type="text"
                      className="alias-input"
                      placeholder="输入别名（可选）"
                      value={columnAliases[column] || ''}
                      onChange={(e) => setColumnAlias(column, e.target.value)}
                      onClick={(e) => e.stopPropagation()}
                    />
                  </div>
                ))}
              </div>
              <div className="hint-text">
                点击切换选中状态，至少选择一列进行显著性检验（仅显示数值列）。
              </div>
            </div>

            <div className="action-area">
              <button
                className="primary-btn"
                onClick={handleRunAnalysis}
                disabled={!baselineColumn || dataColumns.length === 0 || analyzing}
              >
                {analyzing ? "分析中..." : "运行分析"}
              </button>
            </div>
          </>
        ) : (
          <div className="hint-text" style={{ textAlign: "center" }}>
            请先上传 CSV 文件以加载可选列。
          </div>
        )}

        {analysisResult && (
          <>
            {renderAnalysisReport()}
            <div className="export-button-wrapper">
              <button className="export-button" onClick={exportHTMLReport}>
                <span className="emoji">📥</span>
                <span>导出HTML报告</span>
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// 渲染应用
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
