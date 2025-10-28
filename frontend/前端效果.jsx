import React, { useState } from "react";
import Papa from "papaparse";

function App() {
  const [csvData, setCsvData] = useState(null);
  const [columns, setColumns] = useState([]);
  const [baselineColumn, setBaselineColumn] = useState('');
  const [dataColumns, setDataColumns] = useState([]);
  const [analysisResult, setAnalysisResult] = useState(null);

  // 处理文件上传
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    Papa.parse(file, {
      complete: (result) => {
        setCsvData(result.data);
        const cols = result.data[0] ? Object.keys(result.data[0]) : [];
        setColumns(cols);
      },
      header: true
    });
  };

  // 运行显著性分析
  const handleRunAnalysis = async () => {
    // 这里可以调用后端 API 来进行显著性分析
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        baseline: baselineColumn,
        dataColumns
      })
    });
    const result = await response.json();
    setAnalysisResult(result);
  };

  return (
    <div>
      <h1>CSV 数据显著性分析</h1>

      {/* 文件上传 */}
      <input type="file" accept=".csv" onChange={handleFileUpload} />
      
      {/* 列选择 */}
      {columns.length > 0 && (
        <>
          <h3>选择 Baseline 列</h3>
          <select onChange={(e) => setBaselineColumn(e.target.value)} value={baselineColumn}>
            <option value="">请选择</option>
            {columns.map((col) => (
              <option key={col} value={col}>{col}</option>
            ))}
          </select>

          <h3>选择参与分析的列</h3>
          <select multiple onChange={(e) => setDataColumns(Array.from(e.target.selectedOptions, option => option.value))}>
            {columns.map((col) => (
              <option key={col} value={col}>{col}</option>
            ))}
          </select>

          {/* 运行显著性分析 */}
          <button onClick={handleRunAnalysis}>运行分析</button>
        </>
      )}

      {/* 显示分析结果 */}
      {analysisResult && (
        <div>
          <h3>分析结果</h3>
          <pre>{JSON.stringify(analysisResult, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
