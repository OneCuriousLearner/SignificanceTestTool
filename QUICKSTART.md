# 🚀 快速启动指南

## 启动服务（推荐方式 - 使用 Nginx）

### 一键启动

```bash
./start.sh
```

你将看到：
```
========================================
  🎉 服务启动成功！
========================================

📌 访问地址:
   应用入口: http://localhost:8080
   后端 API: http://localhost:5000 (直接访问)
```

### 访问应用

在浏览器中打开：**http://localhost:8080**

### 停止服务

快速关闭后端与 Nginx 服务：

```bash
./kill.sh
```

### 刷新 Nginx 配置

当修改了前端文件（HTML/CSS/JS）或 Nginx 配置后，运行此命令使更改生效：

```bash
nginx -s reload -c /data/workspace/nginx/nginx.conf
```

**什么时候需要刷新？**
- 修改了 `frontend/` 目录下的任何文件（HTML、CSS、JS）
- 修改了 `nginx/nginx.conf` 配置文件
- 更新了前端静态资源（如图标）

**注意**：修改后端代码需要重启后端服务，不能只刷新 Nginx

---

## 服务架构说明

### 当前架构（生产模式）

```
浏览器 (http://localhost:8080)
    ↓
Nginx (端口 8080)
    ├── / → 静态文件服务（frontend/ 目录）
    └── /api/* → 反向代理到后端
            ↓
        Flask 后端 (端口 5000)
```

**架构优势：**
- ✅ 统一入口，无需跨域
- ✅ Nginx 高效处理静态文件
- ✅ API 请求自动代理到后端
- ✅ 生产环境最佳实践

### 旧架构（开发模式 - 已弃用）

> **⚠️ 注意**：以下方式已不推荐使用，仅作参考。前端现已由 Nginx 托管。

<details>
<summary>点击查看旧的开发模式启动方式</summary>

#### 第一步：启动后端服务

```bash
./start_backend.sh
```

#### 第二步：启动前端服务（已废弃）

```bash
./start_frontend.sh  # ⚠️ 此脚本已不再需要
```

前端现在由 Nginx 直接提供，无需单独启动 Python HTTP 服务器。

#### 访问方式

- ❌ 旧方式：http://localhost:3000（已弃用）
- ✅ 新方式：http://localhost:8080（推荐）

</details>

## 使用流程

1. **上传 CSV 文件**：点击"选择文件"按钮，上传你的数据文件（支持最大 1024MB）
2. **选择 Baseline 列**：从下拉菜单选择作为基准的数值列（自动过滤非数值列）
3. **选择参与分析的列**：点击列名切换选中状态，支持多选
4. **（可选）设置列别名**：在每列右侧输入框中可为列设置别名，便于报告展示
5. **运行分析**：点击"运行分析"按钮
6. **查看结果**：美化的分析报告将显示在页面下方，包含数据概览、统计表格、显著性检验等
7. **导出报告**：点击"导出为 HTML"按钮可将完整报告保存到本地

## 停止服务

在各个终端中按 `Ctrl+C` 即可停止相应的服务。

## 故障排除

### 后端启动失败

检查是否已安装依赖：
```bash
cd backend
uv sync
```

### 无法访问 http://localhost:8080

1. **检查服务状态**：
   ```bash
   lsof -i:8080  # 检查 Nginx 是否运行
   lsof -i:5000  # 检查后端是否运行
   ```

2. **查看 Nginx 日志**：
   ```bash
   tail -f /var/log/nginx/csv_analysis_error.log
   ```

3. **重启服务**：
   ```bash
   ./kill.sh
   ./start.sh
   ```

### 文件上传失败（413 错误）

如果上传大文件时出现 "413 Payload Too Large" 错误：

1. Nginx 配置已支持 1024MB 文件上传
2. 检查配置是否生效：
   ```bash
   nginx -t -c /data/workspace/nginx/nginx.conf
   nginx -s reload -c /data/workspace/nginx/nginx.conf
   ```

### 前端修改不生效

修改前端文件（HTML/CSS/JS）后，需要刷新 Nginx：
```bash
nginx -s reload -c /data/workspace/nginx/nginx.conf
```

同时在浏览器中**强制刷新**页面（Ctrl+Shift+R 或 Cmd+Shift+R）清除缓存。

### 端口被占用

#### 端口 8080 被占用（Nginx）

```bash
# 查找占用进程
lsof -ti:8080 | xargs kill -9

# 或者修改 nginx/nginx.conf 中的端口号
listen 8081;  # 改为其他端口
```

#### 端口 5000 被占用（后端）

```bash
# 查找占用进程
lsof -ti:5000 | xargs kill -9

# 或者修改 backend/app.py 中的端口号
app.run(host='0.0.0.0', port=5001, debug=True)
```

### API 请求失败

确保：
1. 后端服务正常运行（http://localhost:5000）
2. Nginx 反向代理配置正确（/api/* 路径）
3. 查看后端日志：`tail -f /tmp/backend.log`

## 测试数据

可以使用 `data/` 目录中的示例 CSV 文件进行测试。

---

**祝使用愉快！** 🎉
