@echo off
chcp 65001 > nul
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║         IEEE Xplore 文献爬虫 - 快速启动                  ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 请选择操作：
echo.
echo   1. 安装依赖包
echo   2. 运行爬虫（开始爬取）
echo   3. 分析结果（查看统计）
echo   4. 查看使用说明
echo   5. 退出
echo.
set /p choice=请输入选项 (1-5): 

if "%choice%"=="1" (
    echo.
    echo 正在安装依赖包...
    pip install -r requirements.txt
    pip install pandas openpyxl
    echo.
    echo ✓ 安装完成！
    pause
    goto :start
)

if "%choice%"=="2" (
    echo.
    echo 🚀 正在启动爬虫...
    echo ⚠️  预计耗时约2小时，可随时按 Ctrl+C 中断
    echo.
    python ieee_crawler.py
    pause
    goto :start
)

if "%choice%"=="3" (
    echo.
    echo 📊 正在分析结果...
    echo.
    python analyze_results.py
    pause
    goto :start
)

if "%choice%"=="4" (
    echo.
    start README_爬虫使用说明.md
    goto :start
)

if "%choice%"=="5" (
    echo.
    echo 👋 再见！
    exit
)

echo ❌ 无效选项！
pause
:start
cls
%~nx0


