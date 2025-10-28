#!/bin/bash

# 简单的前端启动脚本

echo "🌐 启动前端服务..."

# 检查并释放 3000 端口
check_and_free_port() {
    PORT=3000
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

cd frontend

echo "📡 前端服务启动于: http://localhost:3000"
echo "💡 提示: 请在另一个终端运行 ./start_backend.sh 启动后端服务"
echo ""

python3 -m http.server 3000
