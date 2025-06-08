#!/bin/bash

# 自动小说生成器一键启动脚本
# Author: AI Assistant
# Description: 启动前后端服务

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

log_info "项目根目录: $PROJECT_ROOT"

# 创建日志目录
create_log_dir() {
    mkdir -p "$PROJECT_ROOT/logs"
}

# 启动后端服务
start_backend() {
    log_info "启动后端服务..."

    # 检查端口是否被占用
    BACKEND_PORT=$(grep "^PORT=" "$PROJECT_ROOT/.env" | cut -d'=' -f2 | tr -d ' ')
    BACKEND_PORT=${BACKEND_PORT:-8002}

    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "端口 $BACKEND_PORT 已被占用，尝试终止占用进程..."
        lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi

    log_info "在后台启动后端服务 (端口: $BACKEND_PORT)..."
    nohup python3 "$PROJECT_ROOT/backend/run.py" > "$PROJECT_ROOT/logs/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$PROJECT_ROOT/logs/backend.pid"

    # 等待后端启动
    sleep 3

    log_success "后端服务已启动 (PID: $BACKEND_PID)"
    log_info "后端API地址: http://localhost:$BACKEND_PORT"
    log_info "后端日志: $PROJECT_ROOT/logs/backend.log"
}

# 启动前端服务
start_frontend() {
    log_info "启动前端服务..."

    cd "$PROJECT_ROOT/frontend"

    # Vite默认端口是5173，不是3000
    FRONTEND_PORT=5173

    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "端口 $FRONTEND_PORT 已被占用，尝试终止占用进程..."
        lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi

    log_info "在后台启动前端服务 (端口: $FRONTEND_PORT)..."
    nohup npm run dev > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$PROJECT_ROOT/logs/frontend.pid"

    # 等待前端启动
    sleep 3

    log_success "前端服务已启动 (PID: $FRONTEND_PID)"
    log_info "前端访问地址: http://localhost:$FRONTEND_PORT"
    log_info "前端日志: $PROJECT_ROOT/logs/frontend.log"
}

# 显示服务状态
show_status() {
    echo ""
    log_info "=== 服务状态 ==="

    # 检查后端状态
    if [ -f "$PROJECT_ROOT/logs/backend.pid" ]; then
        BACKEND_PID=$(cat "$PROJECT_ROOT/logs/backend.pid")
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            log_success "后端服务运行中 (PID: $BACKEND_PID)"
        else
            log_error "后端服务未运行"
        fi
    else
        log_error "后端服务PID文件不存在"
    fi

    # 检查前端状态
    if [ -f "$PROJECT_ROOT/logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat "$PROJECT_ROOT/logs/frontend.pid")
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            log_success "前端服务运行中 (PID: $FRONTEND_PID)"
        else
            log_error "前端服务未运行"
        fi
    else
        log_error "前端服务PID文件不存在"
    fi

    echo ""
    log_info "=== 访问地址 ==="
    BACKEND_PORT=$(grep "^PORT=" "$PROJECT_ROOT/.env" | cut -d'=' -f2 | tr -d ' ')
    BACKEND_PORT=${BACKEND_PORT:-8002}
    log_info "后端API: http://localhost:$BACKEND_PORT"
    log_info "前端界面: http://localhost:5173"

    echo ""
    log_info "=== 日志文件 ==="
    log_info "后端日志: $PROJECT_ROOT/logs/backend.log"
    log_info "前端日志: $PROJECT_ROOT/logs/frontend.log"

    echo ""
    log_info "=== 停止服务 ==="
    log_info "运行 './stop.sh' 停止所有服务"
}

# 主函数
main() {
    echo ""
    log_info "=== 自动小说生成器一键启动脚本 ==="
    echo ""

    # 创建日志目录
    create_log_dir

    # 启动服务
    start_backend
    start_frontend

    # 显示状态
    show_status

    echo ""
    log_success "=== 启动完成！==="
    log_info "请等待几秒钟让服务完全启动，然后访问前端界面"
    echo ""
}

# 执行主函数
main "$@"
