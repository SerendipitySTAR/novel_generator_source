#!/bin/bash

# 自动小说生成器停止脚本
# Author: AI Assistant
# Description: 停止前后端服务

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

# 停止后端服务
stop_backend() {
    log_info "停止后端服务..."
    
    if [ -f "$PROJECT_ROOT/logs/backend.pid" ]; then
        BACKEND_PID=$(cat "$PROJECT_ROOT/logs/backend.pid")
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill $BACKEND_PID
            sleep 2
            if ps -p $BACKEND_PID > /dev/null 2>&1; then
                log_warning "强制终止后端服务..."
                kill -9 $BACKEND_PID
            fi
            log_success "后端服务已停止"
        else
            log_warning "后端服务进程不存在"
        fi
        rm -f "$PROJECT_ROOT/logs/backend.pid"
    else
        log_warning "后端服务PID文件不存在"
    fi
    
    # 检查端口并强制终止
    BACKEND_PORT=$(grep "^PORT=" "$PROJECT_ROOT/.env" | cut -d'=' -f2 | tr -d ' ')
    BACKEND_PORT=${BACKEND_PORT:-8002}
    
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null ; then
        log_info "强制终止占用端口 $BACKEND_PORT 的进程..."
        lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
    fi
}

# 停止前端服务
stop_frontend() {
    log_info "停止前端服务..."
    
    if [ -f "$PROJECT_ROOT/logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat "$PROJECT_ROOT/logs/frontend.pid")
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill $FRONTEND_PID
            sleep 2
            if ps -p $FRONTEND_PID > /dev/null 2>&1; then
                log_warning "强制终止前端服务..."
                kill -9 $FRONTEND_PID
            fi
            log_success "前端服务已停止"
        else
            log_warning "前端服务进程不存在"
        fi
        rm -f "$PROJECT_ROOT/logs/frontend.pid"
    else
        log_warning "前端服务PID文件不存在"
    fi
    
    # 检查端口并强制终止
    FRONTEND_PORT=5173
    
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null ; then
        log_info "强制终止占用端口 $FRONTEND_PORT 的进程..."
        lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
    fi
}

# 停止所有相关进程
stop_all_processes() {
    log_info "停止所有相关进程..."
    
    # 停止所有Python进程（包含run.py）
    pkill -f "python.*run.py" 2>/dev/null || true
    
    # 停止所有Node.js进程（包含vite）
    pkill -f "node.*vite" 2>/dev/null || true
    pkill -f "pnpm.*dev" 2>/dev/null || true
    
    log_success "所有相关进程已停止"
}

# 清理临时文件
cleanup() {
    log_info "清理临时文件..."
    
    # 清理PID文件
    rm -f "$PROJECT_ROOT/logs/backend.pid"
    rm -f "$PROJECT_ROOT/logs/frontend.pid"
    
    log_success "临时文件清理完成"
}

# 显示状态
show_status() {
    echo ""
    log_info "=== 服务状态 ==="
    
    # 检查后端端口
    BACKEND_PORT=$(grep "^PORT=" "$PROJECT_ROOT/.env" | cut -d'=' -f2 | tr -d ' ')
    BACKEND_PORT=${BACKEND_PORT:-8002}
    
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null ; then
        log_error "后端端口 $BACKEND_PORT 仍被占用"
    else
        log_success "后端端口 $BACKEND_PORT 已释放"
    fi
    
    # 检查前端端口
    FRONTEND_PORT=5173
    
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null ; then
        log_error "前端端口 $FRONTEND_PORT 仍被占用"
    else
        log_success "前端端口 $FRONTEND_PORT 已释放"
    fi
    
    echo ""
}

# 主函数
main() {
    echo ""
    log_info "=== 自动小说生成器停止脚本 ==="
    echo ""
    
    # 停止服务
    stop_backend
    stop_frontend
    
    # 停止所有相关进程
    stop_all_processes
    
    # 清理临时文件
    cleanup
    
    # 显示状态
    show_status
    
    log_success "=== 所有服务已停止！==="
    echo ""
}

# 执行主函数
main "$@"
