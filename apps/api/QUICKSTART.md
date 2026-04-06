# 快速启动指南

## 前置要求

- Python 3.8+
- Docker & Docker Compose
- PostgreSQL 16（通过 Docker）

## 启动步骤

### 1. 启动数据库

```bash
# 进入 Docker 配置目录
cd ../../infra/docker

# 启动 PostgreSQL
docker-compose up -d postgres

# 验证数据库已启动
docker-compose ps
```

### 2. 设置 Python 环境

```bash
# 返回 API 目录
cd ../../apps/api

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件（如果需要）
# 默认配置应该可以直接使用
```

### 4. 运行数据库迁移

```bash
# 进入迁移目录
cd ../../infra/migrations

# 运行迁移
alembic upgrade head

# 返回 API 目录
cd ../../apps/api
```

### 5. 运行测试（可选）

```bash
# 运行所有测试
pytest tests/ -v

# 或只运行不需要数据库的测试
pytest tests/ -v -k "not database"
```

### 6. 启动 API 服务器

```bash
# 确保在 apps/api 目录且虚拟环境已激活
uvicorn app.main:app --reload --port 8000
```

### 7. 验证服务

打开浏览器访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 常见问题

### 问题 1：虚拟环境激活失败

**Windows PowerShell 报错**：
```
无法加载文件 .venv\Scripts\Activate.ps1，因为在此系统上禁止运行脚本
```

**解决方案**：
```powershell
# 以管理员身份运行 PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 问题 2：数据库连接失败

**错误**：`connection timeout expired`

**解决方案**：
```bash
# 检查数据库状态
cd infra/docker
docker-compose ps

# 如果未运行，启动数据库
docker-compose up -d postgres

# 查看数据库日志
docker-compose logs postgres
```

### 问题 3：端口被占用

**错误**：`Address already in use`

**解决方案**：
```bash
# 使用其他端口
uvicorn app.main:app --reload --port 8001

# 或查找并终止占用端口的进程（Windows）
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F
```

### 问题 4：Python 版本不兼容

**错误**：`TypeError: unsupported operand type(s) for |`

**解决方案**：
```bash
# 检查 Python 版本
python --version

# 必须是 Python 3.8 或更高版本
# 如果版本过低，请升级 Python
```

运行兼容性检查：
```bash
python scripts/check_python38_compat.py
```

## 开发工作流

### 修改代码后

API 服务器会自动重载（`--reload` 参数）。

### 修改数据库模型后

```bash
cd infra/migrations

# 创建新迁移
alembic revision --autogenerate -m "描述变更"

# 应用迁移
alembic upgrade head
```

### 运行测试

```bash
cd apps/api

# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/unit/test_document_service.py -v

# 运行特定测试
pytest tests/unit/test_document_service.py::test_validate_schema_brief_valid -v
```

## 停止服务

### 停止 API 服务器

在运行 uvicorn 的终端按 `Ctrl+C`

### 停止数据库

```bash
cd infra/docker
docker-compose down

# 如果要删除数据
docker-compose down -v
```

## 下一步

- 查看 API 文档：http://localhost:8000/docs
- 阅读技术文档：`docs/engineering/`
- 查看功能规格：`.kiro/specs/`
- 遇到问题查看：`TROUBLESHOOTING.md`

---

**最后更新**：2026-04-06
