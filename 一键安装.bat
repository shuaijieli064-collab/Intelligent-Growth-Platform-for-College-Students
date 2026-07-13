@echo off
chcp 65001 >nul
title 大学生智能成长平台 - 安装依赖

echo ================================================
echo   大学生智能成长平台 - 安装 Python 依赖
echo ================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python！请先安装 Python 3.12+
    echo 下载: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 安装依赖包...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if %errorlevel% neq 0 (
    pip install -r requirements.txt
)

echo.
echo ================================================
echo   安装完成！
echo   以后只需双击 启动.bat 即可运行
echo   首次启动时会自动初始化数据库
echo ================================================
pause
