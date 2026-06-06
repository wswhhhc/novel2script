#!/usr/bin/env python3
"""
Novel2Script - 停止开发服务
跨平台 Python 脚本，通过端口查找并停止进程
"""
import sys
import subprocess
import platform


def get_pid_by_port(port):
    """通过端口号查找进程 PID"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                check=True,
            )
            pids = set()
            for line in result.stdout.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if parts:
                        pid = parts[-1]
                        if pid.isdigit():
                            pids.add(int(pid))
            return list(pids)
        else:
            # macOS/Linux
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return [int(pid) for pid in result.stdout.strip().split("\n") if pid]
            return []
    except Exception as e:
        print(f"查找端口 {port} 的进程时出错: {e}")
        return []


def kill_process(pid):
    """停止指定 PID 的进程"""
    try:
        if platform.system() == "Windows":
            subprocess.run(
                ["taskkill", "/F", "/PID", str(pid)],
                capture_output=True,
                check=True,
            )
        else:
            subprocess.run(["kill", "-9", str(pid)], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    print("正在停止 Novel2Script 开发服务...\n")

    # 停止后端服务 (8000 端口)
    backend_pids = get_pid_by_port(8000)
    if backend_pids:
        print(f"找到后端服务进程: {backend_pids}")
        for pid in backend_pids:
            if kill_process(pid):
                print(f"  ✓ 已停止进程 PID: {pid}")
            else:
                print(f"  ✗ 停止进程 PID: {pid} 失败")
    else:
        print("○ 后端服务未运行 (端口 8000)")

    # 停止前端服务 (5173 端口)
    frontend_pids = get_pid_by_port(5173)
    if frontend_pids:
        print(f"\n找到前端服务进程: {frontend_pids}")
        for pid in frontend_pids:
            if kill_process(pid):
                print(f"  ✓ 已停止进程 PID: {pid}")
            else:
                print(f"  ✗ 停止进程 PID: {pid} 失败")
    else:
        print("\n○ 前端服务未运行 (端口 5173)")

    print("\n所有服务已停止")


if __name__ == "__main__":
    main()
