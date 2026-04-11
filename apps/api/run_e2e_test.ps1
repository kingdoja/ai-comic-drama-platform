# E2E 测试运行脚本
# 用法: .\run_e2e_test.ps1

Write-Host "=== 运行 E2E 全流程测试 ===" -ForegroundColor Green

# 设置 PYTHONPATH
$env:PYTHONPATH = "."

# 检查虚拟环境
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "错误: 虚拟环境不存在，请先创建虚拟环境" -ForegroundColor Red
    exit 1
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

# 检查数据库连接
Write-Host "检查数据库连接..." -ForegroundColor Yellow
# TODO: 添加数据库连接检查

# 运行测试
Write-Host "运行测试..." -ForegroundColor Yellow
python -m pytest tests/e2e/test_full_workflow.py -v -s

# 显示结果
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=== 测试通过 ===" -ForegroundColor Green
} else {
    Write-Host "`n=== 测试失败 ===" -ForegroundColor Red
}

exit $LASTEXITCODE
