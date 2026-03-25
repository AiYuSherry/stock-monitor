#!/bin/bash
# Stock Monitor - Start Script
# 股票监测程序 - 启动脚本

# Get script directory / 获取脚本目录
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Log files / 日志文件
LOG_FILE="$DIR/stock_monitor.log"
PID_FILE="$DIR/stock_monitor.pid"

# Check if already running / 检查是否已在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "$(date): Program already running / 程序已在运行 (PID: $OLD_PID)" >> "$LOG_FILE"
        exit 0
    fi
fi

# Check and install dependencies / 检查并安装依赖
echo "$(date): Checking dependencies / 检查依赖..." >> "$LOG_FILE"
pip3 install schedule requests --quiet 2>/dev/null

# Start program / 启动程序
echo "$(date): Starting Stock Monitor / 启动股票监测程序..." >> "$LOG_FILE"
nohup python3 "$DIR/stock_monitor.py" >> "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"
echo "$(date): Program started / 程序已启动 (PID: $NEW_PID)" >> "$LOG_FILE"
echo "✅ Stock Monitor started / 股票监测程序已启动 (PID: $NEW_PID)"
