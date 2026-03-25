@echo off
REM 工业质量统计工具启动脚本 (Windows)
REM 使用方法: iqs.bat [命令] [参数]
REM 示例: iqs.bat report --file data.csv --column diameter --lsl 24.5 --usl 25.5

set SCRIPT_DIR=%~dp0
set PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%
python "%SCRIPT_DIR%cli/main.py" %*
