#!/bin/bash

# CSV 数据显著性分析工具 - 服务停止脚本
# 基于端口关闭服务，确保彻底清理

echo "========================================"
echo "  停止 CSV 数据显著性分析工具"
echo "========================================"
echo ""

# 停止指定端口的服务
kill_port() {
    local PORT=$1
    local SERVICE_NAME=$2
    
    echo "🔍 检查端口 $PORT ($SERVICE_NAME)..."
    
    # 查找占用端口的进程
    PIDS=$(lsof -ti:$PORT 2>/dev/null)
    
    if [ -z "$PIDS" ]; then
        echo "ℹ️  端口 $PORT 未被占用"
        return 0
    fi
    
    echo "⚠️  发现进程占用端口 $PORT: $PIDS"
    echo "🛑 正在停止 $SERVICE_NAME..."
    
    # 尝试优雅停止
    for PID in $PIDS; do
        kill $PID 2>/dev/null
    done
    
    # 等待进程退出
    sleep 2
    
    # 检查是否还有进程占用端口
    REMAINING=$(lsof -ti:$PORT 2>/dev/null)
    
    if [ ! -z "$REMAINING" ]; then
        echo "⚠️  进程未响应，强制终止..."
        for PID in $REMAINING; do
            kill -9 $PID 2>/dev/null
        done
        sleep 1
    fi
    
    # 最终检查
    if lsof -ti:$PORT > /dev/null 2>&1; then
        echo "❌ 无法停止端口 $PORT 上的服务"
        return 1
    else
        echo "✅ $SERVICE_NAME 已停止"
        return 0
    fi
}

# 停止 Nginx (端口 8080)
stop_nginx() {
    echo ""
    echo "========================================"
    echo "停止 Nginx 服务"
    echo "========================================"
    
    # 先尝试优雅停止
    if command -v nginx &> /dev/null; then
        nginx -s stop 2>/dev/null
        sleep 2
    fi
    
    # 基于端口强制清理
    kill_port 8080 "Nginx"
}

# 停止后端服务 (端口 5000)
stop_backend() {
    echo ""
    echo "========================================"
    echo "停止后端服务"
    echo "========================================"
    
    kill_port 5000 "后端服务 (Flask)"
}

# 停止前端服务 (端口 3000，如果独立运行)
stop_frontend() {
    echo ""
    echo "========================================"
    echo "停止前端服务（如果独立运行）"
    echo "========================================"
    
    if lsof -ti:3000 > /dev/null 2>&1; then
        kill_port 3000 "前端服务"
    else
        echo "ℹ️  前端服务未独立运行（由 Nginx 提供）"
    fi
}

# 清理临时文件
cleanup_temp() {
    echo ""
    echo "========================================"
    echo "清理临时文件"
    echo "========================================"
    
    if [ -f /tmp/backend_startup.log ]; then
        echo "🗑️  删除后端日志: /tmp/backend_startup.log"
        rm -f /tmp/backend_startup.log
    fi
    
    echo "✅ 临时文件清理完成"
}

# 显示最终状态
show_status() {
    echo ""
    echo "========================================"
    echo "  服务状态检查"
    echo "========================================"
    echo ""
    
    local ALL_STOPPED=true
    
    # 检查各端口状态
    if lsof -ti:8080 > /dev/null 2>&1; then
        echo "⚠️  端口 8080 (Nginx) 仍在运行"
        ALL_STOPPED=false
    else
        echo "✅ 端口 8080 (Nginx) 已停止"
    fi
    
    if lsof -ti:5000 > /dev/null 2>&1; then
        echo "⚠️  端口 5000 (后端) 仍在运行"
        ALL_STOPPED=false
    else
        echo "✅ 端口 5000 (后端) 已停止"
    fi
    
    if lsof -ti:3000 > /dev/null 2>&1; then
        echo "⚠️  端口 3000 (前端) 仍在运行"
        ALL_STOPPED=false
    else
        echo "✅ 端口 3000 (前端) 已停止"
    fi
    
    echo ""
    
    if [ "$ALL_STOPPED" = true ]; then
        echo "========================================"
        echo "  🎉 所有服务已成功停止！"
        echo "========================================"
        echo ""
        echo "💡 重新启动服务: ./start.sh"
        echo ""
    else
        echo "========================================"
        echo "  ⚠️  部分服务未能停止"
        echo "========================================"
        echo ""
        echo "💡 手动检查: lsof -ti:8080 -ti:5000 -ti:3000"
        echo "💡 强制清理: sudo lsof -ti:8080 -ti:5000 -ti:3000 | xargs kill -9"
        echo ""
    fi
}

# 主流程
main() {
    stop_nginx
    stop_backend
    stop_frontend
    cleanup_temp
    show_status
}

# 运行主流程
main
