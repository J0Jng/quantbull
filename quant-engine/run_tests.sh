#!/bin/bash
# Quant Engine 测试运行脚本 (Bash)

echo "========================================"
echo "Quant Engine 测试套件"
echo "========================================"
echo ""

# 检查是否安装了 pytest
echo "检查依赖..."
if ! python -m pytest --version &> /dev/null; then
    echo "✗ pytest 未安装，正在安装..."
    pip install pytest pytest-asyncio
else
    echo "✓ pytest 已安装"
fi

echo ""
echo "运行测试..."
echo ""

# 运行测试
python -m pytest tests/ -v --tb=short

# 检查测试结果
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✓ 所有测试通过！"
    echo "========================================"
else
    echo ""
    echo "========================================"
    echo "✗ 部分测试失败"
    echo "========================================"
    exit 1
fi
