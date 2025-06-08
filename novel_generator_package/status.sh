#!/bin/bash

# 自动小说生成器状态检查脚本
# Author: AI Assistant
# Description: 检查前后端服务状态

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

# 检查后端状态
check_backend() {
    log_info "检查后端服务状态..."
    
    # 从配置文件读取端口
    BACKEND_PORT=$(grep "^PORT=" "$PROJECT_ROOT/.env" | cut -d'=' -f2 | tr -d ' ')
    BACKEND_PORT=${BACKEND_PORT:-8002}
    
    # 检查PID文件
    if [ -f "$PROJECT_ROOT/logs/backend.pid" ]; then
        BACKEND_PID=$(cat "$PROJECT_ROOT/logs/backend.pid")
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            log_success "后端进程运行中 (PID: $BACKEND_PID)"
        else
            log_error "后端PID文件存在但进程未运行"
        fi
    else
        log_warning "后端PID文件不存在"
    fi
    
    # 检查端口
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null ; then
        log_success "后端端口 $BACKEND_PORT 正在监听"
        
        # 检查API健康状态
        if curl -s "http://localhost:$BACKEND_PORT/api/health" > /dev/null 2>&1; then
            log_success "后端API响应正常"
        else
            log_warning "后端API无响应或健康检查失败"
        fi
    else
        log_error "后端端口 $BACKEND_PORT 未在监听"
    fi
    
    echo ""
}

# 检查前端状态
check_frontend() {
    log_info "检查前端服务状态..."
    
    FRONTEND_PORT=5173
    
    # 检查PID文件
    if [ -f "$PROJECT_ROOT/logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat "$PROJECT_ROOT/logs/frontend.pid")
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            log_success "前端进程运行中 (PID: $FRONTEND_PID)"
        else
            log_error "前端PID文件存在但进程未运行"
        fi
    else
        log_warning "前端PID文件不存在"
    fi
    
    # 检查端口
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null ; then
        log_success "前端端口 $FRONTEND_PORT 正在监听"
        
        # 检查前端页面
        if curl -s "http://localhost:$FRONTEND_PORT" > /dev/null 2>&1; then
            log_success "前端页面响应正常"
        else
            log_warning "前端页面无响应"
        fi
    else
        log_error "前端端口 $FRONTEND_PORT 未在监听"
    fi
    
    echo ""
}

# 检查环境依赖
check_dependencies() {
    log_info "检查环境依赖..."
    
    # 检查Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        log_success "Python3: $PYTHON_VERSION"
    else
        log_error "Python3 未安装"
    fi
    
    # 检查Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        log_success "Node.js: $NODE_VERSION"
    else
        log_error "Node.js 未安装"
    fi
    
    # 检查pnpm
    if command -v pnpm &> /dev/null; then
        PNPM_VERSION=$(pnpm --version)
        log_success "pnpm: $PNPM_VERSION"
    else
        log_error "pnpm 未安装"
    fi
    
    # 检查虚拟环境
    if [ -d "$PROJECT_ROOT/venv" ]; then
        log_success "Python虚拟环境存在"
    else
        log_warning "Python虚拟环境不存在"
    fi
    
    echo ""
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."
    
    if [ -f "$PROJECT_ROOT/.env" ]; then
        log_success ".env 配置文件存在"
        
        # 检查关键配置
        if grep -q "^OPENAI_API_KEY=" "$PROJECT_ROOT/.env"; then
            log_success "OPENAI_API_KEY 已配置"
        else
            log_warning "OPENAI_API_KEY 未配置"
        fi
        
        if grep -q "^OPENAI_API_BASE=" "$PROJECT_ROOT/.env"; then
            API_BASE=$(grep "^OPENAI_API_BASE=" "$PROJECT_ROOT/.env" | cut -d'=' -f2)
            log_success "OPENAI_API_BASE: $API_BASE"
        else
            log_warning "OPENAI_API_BASE 未配置"
        fi
    else
        log_error ".env 配置文件不存在"
    fi
    
    echo ""
}

# 检查日志文件
check_logs() {
    log_info "检查日志文件..."
    
    if [ -f "$PROJECT_ROOT/logs/backend.log" ]; then
        BACKEND_LOG_SIZE=$(du -h "$PROJECT_ROOT/logs/backend.log" | cut -f1)
        log_success "后端日志文件存在 (大小: $BACKEND_LOG_SIZE)"
        
        # 检查最近的错误
        if tail -n 20 "$PROJECT_ROOT/logs/backend.log" | grep -i "error\|exception\|failed" > /dev/null; then
            log_warning "后端日志中发现错误信息"
        fi
    else
        log_warning "后端日志文件不存在"
    fi
    
    if [ -f "$PROJECT_ROOT/logs/frontend.log" ]; then
        FRONTEND_LOG_SIZE=$(du -h "$PROJECT_ROOT/logs/frontend.log" | cut -f1)
        log_success "前端日志文件存在 (大小: $FRONTEND_LOG_SIZE)"
        
        # 检查最近的错误
        if tail -n 20 "$PROJECT_ROOT/logs/frontend.log" | grep -i "error\|exception\|failed" > /dev/null; then
            log_warning "前端日志中发现错误信息"
        fi
    else
        log_warning "前端日志文件不存在"
    fi
    
    echo ""
}

# 显示访问信息
show_access_info() {
    log_info "=== 访问信息 ==="
    
    BACKEND_PORT=$(grep "^PORT=" "$PROJECT_ROOT/.env" | cut -d'=' -f2 | tr -d ' ')
    BACKEND_PORT=${BACKEND_PORT:-8002}
    
    echo -e "${BLUE}后端API:${NC} http://localhost:$BACKEND_PORT"
    echo -e "${BLUE}前端界面:${NC} http://localhost:5173"
    echo -e "${BLUE}API文档:${NC} http://localhost:$BACKEND_PORT/docs"
    
    echo ""
}

# 显示操作提示
show_operations() {
    log_info "=== 操作提示 ==="
    
    echo -e "${BLUE}启动服务:${NC} ./start.sh"
    echo -e "${BLUE}停止服务:${NC} ./stop.sh"
    echo -e "${BLUE}查看状态:${NC} ./status.sh"
    echo -e "${BLUE}查看后端日志:${NC} tail -f logs/backend.log"
    echo -e "${BLUE}查看前端日志:${NC} tail -f logs/frontend.log"
    
    echo ""
}

# 主函数
main() {
    echo ""
    log_info "=== 自动小说生成器状态检查 ==="
    echo ""
    
    # 检查各项状态
    check_dependencies
    check_config
    check_backend
    check_frontend
    check_logs
    
    # 显示访问信息
    show_access_info
    
    # 显示操作提示
    show_operations
}

# 执行主函数
main "$@"
