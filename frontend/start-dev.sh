#!/bin/bash

# 前端开发启动脚本

echo "🚀 启动徐AI新闻RAG系统前端开发服务器"
echo "================================================"

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未检测到 Node.js，请先安装 Node.js"
    echo "   下载地址: https://nodejs.org/"
    exit 1
fi

# 检查 npm 是否安装
if ! command -v npm &> /dev/null; then
    echo "❌ 错误: 未检测到 npm，请先安装 npm"
    exit 1
fi

echo "✅ Node.js 版本: $(node --version)"
echo "✅ npm 版本: $(npm --version)"
echo ""

# 检查依赖是否安装
if [ ! -d "node_modules" ]; then
    echo "📦 正在安装依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖已安装"
fi

echo ""
echo "🔧 当前配置:"
echo "   - 运行模式: 开发模式 (Mock数据)"
echo "   - 前端端口: 5173"
echo "   - Mock模式: 启用"
echo "   - API地址: http://localhost:3001/api (Mock)"
echo ""
echo "💡 提示:"
echo "   - 前端将使用模拟数据运行，无需后端服务"
echo "   - 默认登录账号: admin@example.com"
echo "   - 默认登录密码: admin123"
echo "   - 访问地址: http://localhost:5173"
echo ""
echo "🌟 启动开发服务器..."
echo "================================================"

# 启动开发服务器
npm run dev