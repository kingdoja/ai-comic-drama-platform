# 故障排查指南

## 常见问题

### 1. TypeError: 'ABCMeta' object is not subscriptable

**错误信息**：
```
TypeError: 'ABCMeta' object is not subscriptable
```

**原因**：
Python 3.8 不支持在类型注解中直接使用 `collections.abc.Generator`。

**解决方案**：
使用 `typing.Generator` 替代：

```python
# ❌ 错误
from collections.abc import Generator
def get_db() -> Generator[Session, None, None]:
    ...

# ✅ 正确
from typing import Generator
def get_db() -> Generator[Session, None, None]:
    ...
```

**已修复**：`apps/api/app/db/session.py`

---

### 2. TypeError: unsupported operand type(s) for |

**错误信息**：
```
TypeError: unsupported operand type(s) for |: 'ModelMetaclass' and 'NoneType'
```

**原因**：
Python 3.8 不支持使用 `X | Y` 语法表示联合类型（这是 Python 3.10+ 的特性）。

**解决方案**：
使用 `Optional[X]` 或 `Union[X, Y]` 替代：

```python
# ❌ 错误（Python 3.10+）
def func() -> str | None:
    ...

def func2() -> int | str:
    ...

# ✅ 正确（Python 3.8+）
from typing import Optional, Union

def func() -> Optional[str]:
    ...

def func2() -> Union[int, str]:
    ...
```

**已修复**：`apps/api/app/services/store.py`

**检查工具**：运行 `python scripts/check_python38_compat.py` 检查兼容性问题

---

### 3. 数据库连接超时

**错误信息**：
```
psycopg.errors.ConnectionTimeout: connection timeout expired
```

**原因**：
PostgreSQL 数据库未启动或无法连接。

**解决方案**：

1. 启动 PostgreSQL：
```bash
cd infra/docker
docker-compose up -d postgres
```

2. 检查数据库状态：
```bash
docker-compose ps
```

3. 查看数据库日志：
```bash
docker-compose logs postgres
```

4. 验证连接：
```bash
docker exec -it thinking-postgres-1 psql -U postgres -d thinking
```

---

### 3. 模块导入错误

**错误信息**：
```
ModuleNotFoundError: No module named 'app'
INFO:     Stopping reloader process [22276]
```

**原因**：
在错误的目录运行 uvicorn 命令。uvicorn 必须在 `apps/api` 目录下运行，因为 `app` 模块在该目录下。

**解决方案**：

1. **确保在正确的目录运行**：
```bash
# ❌ 错误 - 在项目根目录
D:\ai应用项目\thinking> uvicorn app.main:app --reload --port 8000

# ✅ 正确 - 在 apps/api 目录
cd apps/api
uvicorn app.main:app --reload --port 8000
```

2. 验证当前目录：
```bash
# Windows PowerShell
pwd
# 应该显示：...\thinking\apps\api

# 检查 app 目录是否存在
dir app
```

3. 如果虚拟环境未激活，先激活：
```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate
```

4. 确保依赖已安装：
```bash
pip install -r requirements.txt
```

---

### 4. Alembic 迁移错误

**错误信息**：
```
sqlalchemy.exc.ProgrammingError: relation "xxx" does not exist
```

**原因**：
数据库迁移未执行。

**解决方案**：

1. 进入迁移目录：
```bash
cd infra/migrations
```

2. 运行迁移：
```bash
alembic upgrade head
```

3. 检查迁移状态：
```bash
alembic current
```

---

### 5. 端口已被占用

**错误信息**：
```
OSError: [WinError 10048] 通常每个套接字地址(协议/网络地址/端口)只允许使用一次
```

**原因**：
端口 8000 已被其他进程占用。

**解决方案**：

1. 查找占用端口的进程（Windows）：
```powershell
netstat -ano | findstr :8000
```

2. 终止进程：
```powershell
taskkill /PID <进程ID> /F
```

3. 或使用其他端口：
```bash
uvicorn app.main:app --reload --port 8001
```

---

### 6. 测试失败

**错误信息**：
```
FAILED tests/test_xxx.py::test_xxx
```

**解决方案**：

1. 确保测试数据库可用：
```bash
# 检查 .env 文件中的 TEST_DATABASE_URL
cat apps/api/.env
```

2. 运行单个测试：
```bash
pytest tests/test_xxx.py::test_xxx -v
```

3. 查看详细输出：
```bash
pytest tests/ -v -s
```

4. 跳过数据库测试：
```bash
pytest tests/ -v -k "not database"
```

---

### 7. Python 版本不兼容

**错误信息**：
```
SyntaxError: invalid syntax
```

**原因**：
Python 版本低于 3.8。

**解决方案**：

1. 检查 Python 版本：
```bash
python --version
```

2. 升级到 Python 3.8+：
- Windows: 从 [python.org](https://www.python.org/downloads/) 下载
- Linux: `sudo apt install python3.8`
- Mac: `brew install python@3.8`

3. 重新创建虚拟环境：
```bash
python3.8 -m venv .venv
```

---

### 8. 依赖安装失败

**错误信息**：
```
ERROR: Could not find a version that satisfies the requirement xxx
```

**解决方案**：

1. 升级 pip：
```bash
python -m pip install --upgrade pip
```

2. 清除缓存：
```bash
pip cache purge
```

3. 使用国内镜像（可选）：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

### 9. Docker 容器无法启动

**错误信息**：
```
Error response from daemon: driver failed programming external connectivity
```

**解决方案**：

1. 检查端口冲突：
```bash
docker-compose ps
netstat -ano | findstr :5432
```

2. 停止所有容器：
```bash
docker-compose down
```

3. 清理并重启：
```bash
docker-compose down -v
docker-compose up -d
```

---

### 10. 环境变量未加载

**错误信息**：
```
KeyError: 'DATABASE_URL'
```

**原因**：
`.env` 文件不存在或未正确加载。

**解决方案**：

1. 复制示例配置：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件填写正确的配置：
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/thinking
```

3. 确保 `python-dotenv` 已安装：
```bash
pip install python-dotenv
```

---

## 调试技巧

### 1. 启用详细日志

在 `app/main.py` 中添加：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. 使用 Python 调试器

```python
import pdb; pdb.set_trace()
```

### 3. 检查数据库连接

```python
from app.db.session import engine
with engine.connect() as conn:
    result = conn.execute("SELECT 1")
    print(result.fetchone())
```

### 4. 查看 SQLAlchemy 查询

在 `app/db/session.py` 中：

```python
engine = create_engine(
    settings.database_url,
    future=True,
    echo=True  # 打印所有 SQL 查询
)
```

---

## 获取帮助

如果以上方法都无法解决问题：

1. 查看完整错误堆栈
2. 检查相关日志文件
3. 搜索错误信息
4. 查看项目文档：`docs/engineering/`

---

**最后更新**：2026-04-06
