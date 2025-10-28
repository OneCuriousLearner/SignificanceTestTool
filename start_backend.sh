#!/bin/bash

# 仅启动后端服务的脚本

echo "🚀 启动后端服务..."

# 检查并释放 5000 端口
check_and_free_port() {
    PORT=5000
    echo "🔍 检查端口 $PORT..."
    
    # 查找占用端口的进程
    PID=$(lsof -ti:$PORT 2>/dev/null)
    
    if [ ! -z "$PID" ]; then
        echo "⚠️  端口 $PORT 已被进程 $PID 占用"
        echo "🔧 正在释放端口..."
        kill -9 $PID 2>/dev/null
        sleep 1
        echo "✅ 端口 $PORT 已释放"
    else
        echo "✅ 端口 $PORT 可用"
    fi
}

# 检查并释放端口
check_and_free_port

cd backend

# 使用 uv run 启动 Flask（自动管理虚拟环境）
echo "📡 后端服务启动于: http://localhost:5000"
uv run app.py
