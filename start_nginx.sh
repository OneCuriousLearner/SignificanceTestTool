#!/bin/bash

# Nginx 启动脚本

echo "🌐 启动 Nginx 服务..."

# 检查 Nginx 是否安装
if ! command -v nginx &> /dev/null; then
    echo "❌ 错误: Nginx 未安装"
    echo "💡 安装方法: sudo yum install nginx  或  sudo apt install nginx"
    exit 1
fi

# 检查并释放 8080 端口
check_and_free_port() {
    PORT=8080
    echo "🔍 检查端口 $PORT..."
    
    # 1. 先优雅停止所有 Nginx 进程
    echo "🛑 停止所有现有 Nginx 进程..."
    nginx -s stop 2>/dev/null || true
    pkill -9 nginx 2>/dev/null || true
    
    # 2. 等待进程完全终止
    sleep 3
    
    # 3. 强制清理占用端口的进程
    for i in {1..5}; do
        PID=$(lsof -ti:$PORT 2>/dev/null)
        
        if [ -z "$PID" ]; then
            echo "✅ 端口 $PORT 可用"
            return 0
        fi
        
        echo "⚠️  端口 $PORT 仍被进程 $PID 占用，尝试清理 ($i/5)..."
        kill -9 $PID 2>/dev/null || true
        sleep 2
    done
    
    # 4. 最后检查
    if lsof -ti:$PORT > /dev/null 2>&1; then
        echo "❌ 无法释放端口 $PORT，请手动执行: sudo lsof -ti:8080 | xargs kill -9"
        exit 1
    fi
    
    echo "✅ 端口 $PORT 已释放"
}

# 检查并释放端口
check_and_free_port

# 测试 Nginx 配置
echo "🧪 测试 Nginx 配置..."
nginx -t -c /data/workspace/nginx/nginx.conf

if [ $? -ne 0 ]; then
    echo "❌ Nginx 配置测试失败，请检查配置文件"
    exit 1
fi

# 启动 Nginx
echo "🚀 启动 Nginx..."
nginx -c /data/workspace/nginx/nginx.conf

if [ $? -eq 0 ]; then
    echo "✅ Nginx 启动成功"
    echo "📡 服务地址: http://localhost:8080"
else
    echo "❌ Nginx 启动失败"
    exit 1
fi
