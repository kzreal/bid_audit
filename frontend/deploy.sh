#!/bin/bash

# 投标文件审核系统部署脚本

set -e

echo "开始部署投标文件审核系统..."

# 检查环境
check_environment() {
    if ! command -v node &> /dev/null; then
        echo "错误: Node.js 未安装"
        exit 1
    fi

    if ! command -v npm &> /dev/null; then
        echo "错误: npm 未安装"
        exit 1
    fi

    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 16 ]; then
        echo "错误: 需要 Node.js 16 或更高版本"
        exit 1
    fi

    echo "✓ 环境检查通过"
}

# 安装依赖
install_dependencies() {
    echo "正在安装依赖..."
    npm install
    echo "✓ 依赖安装完成"
}

# 构建项目
build_project() {
    echo "正在构建项目..."
    npm run build
    echo "✓ 项目构建完成"
}

# 优化构建
optimize_build() {
    echo "正在优化构建..."

    # 压缩静态资源
    if command -v gzip &> /dev/null; then
        find dist/assets -type f -name "*.js" -o -name "*.css" | while read -r file; do
            gzip -f "$file"
        done
    fi

    # 清理不必要的文件
    rm -rf dist/assets/*.map

    echo "✓ 构建优化完成"
}

# 设置环境变量
setup_env() {
    if [ ! -f .env.production ]; then
        echo "创建生产环境配置..."
        cat > .env.production << EOF
VITE_APP_TITLE=投标文件审核系统
VITE_API_BASE_URL=https://prd-ai-studio.chint.com/api/proxy/api/v1
VITE_HIAGENT_API_KEY=your_production_api_key_here
VITE_HIAGENT_REVIEW_API_KEY=your_production_review_api_key_here
EOF
    fi

    echo "✓ 环境变量设置完成"
}

# 健康检查
health_check() {
    echo "正在运行健康检查..."

    # 检查构建输出
    if [ ! -d "dist" ]; then
        echo "错误: dist 目录不存在"
        exit 1
    fi

    # 检查关键文件
    if [ ! -f "dist/index.html" ]; then
        echo "错误: index.html 不存在"
        exit 1
    fi

    # 检查 JavaScript 文件（包括 .gz 压缩文件）
    JS_COUNT=$(find dist/assets -name "*.js" -o -name "*.js.gz" | wc -l)
    if [ "$JS_COUNT" -eq 0 ]; then
        echo "错误: JavaScript 文件不存在"
        exit 1
    fi

    echo "✓ 健康检查通过"
}

# 生成报告
generate_report() {
    echo "正在生成部署报告..."

    BUILD_TIME=$(date '+%Y-%m-%d %H:%M:%S')
    BUILD_SIZE=$(du -sh dist | cut -f1)
    ASSET_COUNT=$(find dist/assets -type f | wc -l)

    cat > deployment-report.txt << EOF
投标文件审核系统部署报告
==========================

部署时间: $BUILD_TIME
构建大小: $BUILD_SIZE
资源文件数: $ASSET_COUNT

文件列表:
$(find dist -type f -name "*" | sort)

部署成功!
EOF

    echo "✓ 部署报告已生成"
}

# 主流程
main() {
    check_environment
    setup_env
    install_dependencies
    build_project
    optimize_build
    health_check
    generate_report

    echo ""
    echo "🎉 部署完成!"
    echo "部署位置: ./dist/"
    echo "访问地址: file://$(pwd)/dist/index.html"
}

# 运行主函数
main "$@"