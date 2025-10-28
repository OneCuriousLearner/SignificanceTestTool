#!/bin/bash

# CSV 数据显著性分析工具 - 主启动脚本
# 启动顺序: 后端 -> Nginx -> 前端（Nginx提供）

echo "========================================"
echo "  CSV 数据显著性分析工具"
echo "========================================"
echo ""

# 检查是否安装了必要的依赖
check_dependencies() {
    echo "🔍 检查依赖..."
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ 错误: 未找到 python3，请先安装 Python 3"
        exit 1
    fi
    
    # 检查 uv
    if ! command -v uv &> /dev/null; then
        echo "❌ 错误: 未找到 uv，请先安装 UV"
        exit 1
    fi
    
    # 检查 nginx
    if ! command -v nginx &> /dev/null; then
        echo "❌ 错误: 未找到 nginx，请先安装 Nginx"
        exit 1
    fi
    
    echo "✅ 依赖检查通过"
}

# 启动后端服务
start_backend() {
    echo ""
    echo "========================================"
    echo "第 1 步：启动后端服务"
    echo "========================================"
    
    # 使用 nohup 启动后端服务，确保终端关闭后继续运行
    nohup bash start_backend.sh > /tmp/backend_startup.log 2>&1 &
    BACKEND_PID=$!
    
    # 等待后端启动
    echo "⏳ 等待后端服务启动..."
    sleep 5
    
    # 检查后端是否启动成功
    if lsof -ti:5000 > /dev/null 2>&1; then
        echo "✅ 后端服务已启动（端口 5000，PID: $BACKEND_PID）"
        echo "ℹ️  后端服务已脱离终端，关闭窗口不会影响服务"
    else
        echo "❌ 后端服务启动失败，查看日志: tail -f /tmp/backend_startup.log"
        exit 1
    fi
}

# 启动 Nginx
start_nginx() {
    echo ""
    echo "========================================"
    echo "第 2 步：启动 Nginx 反向代理"
    echo "========================================"
    
    # 调用 Nginx 启动脚本（包含端口检查）
    bash start_nginx.sh
    
    if [ $? -ne 0 ]; then
        echo "❌ Nginx 启动失败"
        exit 1
    fi
    
    # 等待 Nginx 启动
    sleep 2
    
    # 检查 Nginx 是否启动成功
    if lsof -ti:8080 > /dev/null 2>&1; then
        echo "✅ Nginx 已启动（端口 8080）"
    else
        echo "❌ Nginx 未能成功绑定端口 8080"
        exit 1
    fi
}

# 检查前端服务
check_frontend() {
    echo ""
    echo "========================================"
    echo "第 3 步：前端服务状态"
    echo "========================================"
    echo "ℹ️  前端静态文件由 Nginx 提供，无需单独启动"
    echo "✅ 前端服务就绪"
}

# 测试 Nginx 反向代理
test_nginx_proxy() {
    echo ""
    echo "========================================"
    echo "第 4 步：测试 Nginx 反向代理"
    echo "========================================"
    
    # 测试前端页面
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ 2>/dev/null)
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ 前端页面访问正常（HTTP $HTTP_CODE）"
    else
        echo "⚠️  前端页面访问异常（HTTP $HTTP_CODE）"
    fi
    
    # 测试后端 API（通过 Nginx 代理）
    echo "🔍 测试 API 代理..."
    API_TEST=$(curl -s http://localhost:8080/api/health 2>/dev/null)
    if [ ! -z "$API_TEST" ]; then
        echo "✅ API 代理正常工作"
    else
        echo "⚠️  API 代理可能存在问题"
    fi
}

# 显示访问信息
show_info() {
    echo ""
    echo "========================================"
    echo "  🎉 服务启动成功！"
    echo "========================================"
    echo ""
    echo "📌 访问地址:"
    echo "   应用入口: http://localhost:8080"
    echo "   后端 API: http://localhost:5000 (直接访问)"
    echo ""
    echo "📋 架构说明:"
    echo "   - Nginx (8080) → 提供前端页面 + 代理 API 请求"
    echo "   - Flask (5000) → 后端 API 服务"
    echo ""
    echo "📖 使用说明:"
    echo "   1. 在浏览器打开 http://localhost:8080"
    echo "   2. 上传 CSV 文件"
    echo "   3. 选择 Baseline 列和数据列"
    echo "   4. 点击运行分析查看结果"
    echo ""
    echo "🔧 管理命令:"
    echo "   停止服务: ./kill.sh"
    echo "   重启 Nginx: nginx -s reload"
    echo "   查看后端日志: tail -f /tmp/backend_startup.log"
    echo ""
    echo "ℹ️  提示: 服务已脱离终端，关闭窗口不会影响运行"
    echo ""
    echo "========================================"
}

# 主流程
main() {
    check_dependencies
    start_backend
    start_nginx
    check_frontend
    test_nginx_proxy
    show_info
}

# 运行主流程
main
