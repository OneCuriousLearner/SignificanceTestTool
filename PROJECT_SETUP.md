# 📝 项目配置总结

## ✅ 已完成的配置

### 1. Python 环境（使用 UV）

✅ 使用 `uv init` 初始化项目
✅ 使用 `uv add` 添加所有依赖：
  - flask (Web 框架)
  - flask-cors (跨域支持)
  - pandas (数据处理)
  - numpy (数值计算)
  - scipy (统计分析)
  - matplotlib (可视化)
  - seaborn (高级可视化)
  - openpyxl (Excel 支持)

✅ 所有依赖已正确安装并锁定在 `uv.lock` 中
✅ CORS 配置已优化，支持跨域请求

### 2. 后端服务（Flask）

✅ 创建 `backend/app.py` - Flask API 服务
  - `/api/upload` - 上传 CSV 文件，返回列信息和数值列列表
  - `/api/analyze` - 执行显著性分析
  - `/api/health` - 健康检查
  - 文件大小限制1204MB
  - 完整的错误处理

✅ 核心分析工具 `model_comparison_tool.py`
  - Wilcoxon 符号秩检验
  - 配对 t 检验
  - Mann-Whitney U 检验
  - 基本统计分析（均值、标准差、中位数、分位数）
  - 两两对比分析
  - 基线对比分析

✅ 配置增强的 Flask-CORS 支持（/api/* 路径）
✅ 自动检测数值列功能
✅ 详细的分析结果输出（中文字段名）

### 3. 前端页面（React）

✅ 文件结构（已拆分）
  - `index.html` - 主 HTML 文件，引入外部 CSS 和 JS
  - `style.css` - 完整样式表（卡片、表格、按钮等）
  - `app.js` - React 应用主逻辑

✅ 核心功能
  - 文件上传（FormData，支持大文件）
  - 与后端 API 通信（相对路径，通过 Nginx 代理）
  - 数值列自动过滤
  - 列选择（Baseline 单选 + 数据列多选切换）
  - 列别名设置
  - 美化的报告展示
  - HTML 报告导出
  - 加载状态提示

✅ 使用 CDN 引入 React 18（无需构建）
✅ 网页图标（`icons8-94.png`）

### 4. Nginx 反向代理

✅ 安装 Nginx 服务器
✅ 创建完整的 Nginx 配置文件 (`nginx/nginx.conf`)
  - 监听端口 8080（可通过外网访问）
  - 提供前端静态文件服务（`frontend/` 目录）
  - 代理 `/api/*` 请求到后端 Flask (5000)
  - 文件上传大小限制 (1024MB)
  - 超时设置（60秒）
  - 完整的日志配置
  - CORS 头部处理

✅ 解决跨域问题（统一通过 8080 端口访问）
✅ 支持热重载（`nginx -s reload`）

### 5. 启动脚本

✅ `start.sh` - 主启动脚本（推荐使用）
  - 依赖检查（Python、UV、Nginx）
  - 按顺序启动：后端 → Nginx → 前端
  - 端口检测与自动释放（5000、8080）
  - Nginx 反向代理测试
  - 后端使用 nohup 启动，关闭终端不影响服务

✅ `start_backend.sh` - 后端启动脚本
  - 使用 `uv run` 运行 Flask
  - 端口 5000 检测与释放
  - 后台运行，日志输出到 `/tmp/backend.log`

✅ `start_nginx.sh` - Nginx 启动脚本
  - 端口 8080 检测与释放（多次重试）
  - 配置文件语法检查
  - 启动前停止旧进程

✅ `start_frontend.sh` - 前端启动脚本（已废弃）
  - ⚠️ 前端现由 Nginx 直接提供，无需此脚本

### 6. 关闭脚本

✅ `kill.sh` - 关闭脚本
  - 依赖检查（Python、Nginx）
  - 按顺序关闭：Nginx → 后端
  - 端口检测与自动释放（5000、8080）

✅ 所有脚本已添加执行权限
✅ 完善的错误处理与日志输出

### 6. 文档

✅ `README.md` - 完整项目说明
✅ `QUICKSTART.md` - 快速启动指南
✅ `PROJECT_SETUP.md` - 本文件（配置总结）
✅ `.gitignore` - Git 忽略配置

## 📊 项目结构

```
.
├── backend/                        # 后端代码
│   ├── .venv/                      # UV 虚拟环境
│   ├── app.py                      # Flask API 服务
│   ├── model_comparison_tool.py    # 核心分析工具
│   ├── quick_analysis.py           # 快速分析脚本
│   ├── example_usage.py            # 使用示例
│   ├── pyproject.toml              # UV 项目配置
│   ├── uv.lock                     # UV 依赖锁定
│   ├── requirements.txt            # pip 兼容的依赖列表
│   └── .gitignore                  # Git 忽略配置
├── frontend/                       # 前端代码
│   ├── 前端效果.jsx                 # 前端预期效果
│   ├── 搜应引擎评测-Prompt2Doclist_analysis_report.html    # 示例报告
│   ├── icons8-94.png               # 网页图标
│   ├── app.js                      # 主 React 组件
│   ├── style.css                   # 样式表
│   └── index.html                  # React 单页应用
├── data/                           # 数据文件目录
├── document/                       # 项目文档
├── nginx/                          # Nginx 配置
│   └── nginx.conf                  # 反向代理配置
├── start_backend.sh                # 后端启动脚本
├── start_frontend.sh               # 前端启动脚本
├── start_nginx.sh                  # 单独启动 Nginx
├── start.sh                        # 一键启动脚本
├── kill.sh                         # 一键关闭脚本
├── README.md                       # 项目说明
└── QUICKSTART.md                   # 快速启动指南
```

## 🔧 技术栈

### 后端
- **Python 3.10+**
- **UV** - Python 包管理器
- **Flask** - Web 框架
- **Flask-CORS** - 跨域支持
- **Pandas** - 数据处理
- **NumPy** - 数值计算
- **SciPy** - 统计分析
- **Matplotlib** - 可视化
- **Seaborn** - 高级可视化

### 前端
- **React 18** (CDN)
- **原生 JavaScript**
- **HTML5 + CSS3**

### 部署
- **Python HTTP Server** - 前端静态服务
- **Flask Development Server** - 后端 API 服务
- **Nginx** (可选) - 反向代理

## 🚀 启动命令

这部分请见[快速启动指南](./QUICKSTART.md)

## 🌐 服务地址

### 生产模式（推荐）- Nginx 反向代理
- **应用入口**: http://localhost:8080
  - 前端页面：`/` → `frontend/` 目录
  - API 代理：`/api/*` → `http://localhost:5000`
- **后端直接访问**: http://localhost:5000（通常无需直接访问）

### 架构图
```
浏览器 ──→ Nginx (8080) ──┬──→ 静态文件 (frontend/)
                          └──→ /api/* → Flask (5000)
```

**优势**：
- ✅ 单一入口，无跨域问题
- ✅ Nginx 高效处理静态资源
- ✅ 生产环境标准架构

## 📋 API 接口

### POST /api/upload
上传 CSV 文件并返回列信息

**请求**: `multipart/form-data`
- `file`: CSV 文件（最大 1024MB）

**响应**:
```json
{
  "message": "文件上传成功",
  "filename": "data.csv",
  "columns": ["col1", "col2", "col3"],
  "numeric_columns": ["col1", "col3"],
  "rowCount": 1000
}
```

### POST /api/analyze
执行显著性分析

**请求**: `application/json`
```json
{
  "baseline": "baseline_column",
  "dataColumns": ["col1", "col2"],
  "testType": "wilcoxon",
  "alpha": 0.05
}
```

**响应**:
```json
{
  "数据概览": {
    "样本数量": 1000,
    "模型数量": 3,
    "统计检验": "wilcoxon",
    "显著性水平": 0.05
  },
  "基本统计": [
    {
      "列名": "col1",
      "样本数": 1000,
      "均值": 1.234,
      "标准差": 0.456,
      "中位数": 1.2,
      "25%分位数": 0.9,
      "75%分位数": 1.5
    }
  ],
  "两两对比": [
    {
      "模型1": "col1",
      "模型2": "col2",
      "均值1": 1.234,
      "均值2": 1.456,
      "均值差异": -0.222,
      "检验统计量": 123456.5,
      "p值": 0.0234,
      "是否显著": true
    }
  ],
  "基线对比": [...],
  "最佳模型": {
    "列名": "col2",
    "均值": 1.456
  }
}
```

### GET /api/health
健康检查

**响应**:
```json
{
  "status": "healthy"
}
```

## ✨ 核心功能

### 数据处理
1. ✅ CSV 文件上传与解析（支持最大 1024MB）
2. ✅ 自动列检测与分类（数值列/非数值列）
3. ✅ 智能过滤非数值列（仅显示可分析的数值列）

### 分析配置
4. ✅ Baseline 列选择（仅显示数值列）
5. ✅ 多列对比分析（点击切换选中状态）
6. ✅ 列别名设置（自定义报告中的列名显示）

### 统计检验
7. ✅ Wilcoxon 符号秩检验
8. ✅ 配对 t 检验
9. ✅ Mann-Whitney U 检验
10. ✅ 自动选择最优检验方法

### 结果展示
11. ✅ 数据概览卡片（样本数、模型数、检验类型、显著性水平）
12. ✅ 得分统计表格（均值、标准差、中位数、分位数）
13. ✅ 最佳模型高亮显示
14. ✅ 两两模型对比表格（统计量、p值、显著性判断）
15. ✅ 与基线模型对比表格（均值差异、优于基线判断）
16. ✅ 分析总结（显著差异数量、基线对比结果）
17. ✅ 原始 JSON 数据查看（可折叠）

### 报告导出
18. ✅ HTML 报告导出（包含完整样式和别名）
19. ✅ 报告生成时间戳
20. ✅ 本地文件保存

## 📞 技术支持

如遇到问题，请检查：
1. Python 版本是否 >= 3.10
2. UV 是否已正确安装
3. 依赖是否完整安装（运行 `cd backend && uv sync`）
4. 端口 3000 和 5000 是否被占用
5. 浏览器控制台是否有错误信息

---

**配置完成时间**: 2025-10-21
**配置者**: GitHub Copilot
**项目状态**: ✅ 可用
