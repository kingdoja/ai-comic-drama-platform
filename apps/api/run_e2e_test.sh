#!/bin/bash
# E2E 测试运行脚本
# 用法: ./run_e2e_test.sh

echo "=== 运行 E2E 全流程测试 ==="

# 设置 PYTHONPATH
export PYTHONPATH="."

# 检查虚拟环境
if [ ! -f ".venv/bin/activate" ]; then
    echo "错误: 虚拟环境不存在，请先创建虚拟环境"
    exit 1
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source .venv/bin/activate

# 检查数据库连接
echo "检查数据库连接..."
# TODO: 添加数据库连接检查

# 运行测试
echo "运行测试..."
python -m pytest tests/e2e/test_full_workflow.py -v -s

# 显示结果
if [ $? -eq 0 ]; then
    echo -e "\n=== 测试通过 ==="
else
    echo -e "\n=== 测试失败 ==="
fi

exit $?
