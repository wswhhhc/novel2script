#!/usr/bin/env bash
# Novel2Script - 停止开发服务
# macOS/Linux Bash 脚本

set -e

echo -e "\033[36m正在停止 Novel2Script 开发服务...\033[0m"

# 停止后端服务（uvicorn）
backend_pid=$(pgrep -f "uvicorn.*app.main:app" || true)
if [ -n "$backend_pid" ]; then
    echo -e "\033[33m停止后端服务 (PID: $backend_pid)...\033[0m"
    kill -TERM "$backend_pid" 2>/dev/null || kill -KILL "$backend_pid" 2>/dev/null || true
    echo -e "\033[32m✓ 后端服务已停止\033[0m"
else
    echo -e "\033[90m○ 后端服务未运行\033[0m"
fi

# 停止前端服务（vite dev server）
frontend_pid=$(pgrep -f "vite.*--port 5173" || pgrep -f "npm run dev" || true)
if [ -n "$frontend_pid" ]; then
    echo -e "\033[33m停止前端服务 (PID: $frontend_pid)...\033[0m"
    kill -TERM "$frontend_pid" 2>/dev/null || kill -KILL "$frontend_pid" 2>/dev/null || true
    echo -e "\033[32m✓ 前端服务已停止\033[0m"
else
    echo -e "\033[90m○ 前端服务未运行\033[0m"
fi

echo -e "\n\033[36m所有服务已停止\033[0m"
