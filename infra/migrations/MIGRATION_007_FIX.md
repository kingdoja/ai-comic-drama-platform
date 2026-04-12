# Migration 007: Fix review_decisions.decision Field Length

## 问题描述

在 Iteration 5 (QA/Review/Rerun) 实现过程中发现，`review_decisions` 表的 `decision` 字段长度不足：

- **当前定义**: `VARCHAR(16)`
- **实际需要**: 至少 18 个字符（用于存储 'revision_required'）

### 影响

当用户提交审核决策为 "需要修订" (revision_required) 时，数据库会报错：

```
ERROR: value too long for type character varying(16)
```

### 决策类型

系统支持三种审核决策：

| 决策类型 | 英文值 | 字符数 | 状态 |
|---------|--------|--------|------|
| 批准 | approved | 8 | ✅ 可存储 |
| 拒绝 | rejected | 8 | ✅ 可存储 |
| 需要修订 | revision_required | 18 | ❌ 无法存储 |

## 解决方案

### 1. 数据库迁移

扩展 `decision` 字段长度到 `VARCHAR(32)`：

```sql
ALTER TABLE review_decisions
ALTER COLUMN decision TYPE VARCHAR(32);
```

### 2. 应用迁移

#### 方法 A: 使用快速脚本（推荐）

```bash
cd infra/migrations
bash apply_007_migration.sh
```

#### 方法 B: 手动应用

```bash
cd infra/migrations

# 应用迁移
psql -U postgres -d ai_comic_drama -f 007_fix_review_decision_length.sql

# 运行测试
python test_007_migration.py
```

#### 方法 C: 使用 Docker

```bash
cd infra/docker
docker-compose up -d postgres

cd ../migrations
docker exec -i docker-postgres-1 psql -U postgres -d ai_comic_drama < 007_fix_review_decision_length.sql
```

### 3. 验证修复

运行测试脚本验证：

```bash
python test_007_migration.py
```

预期输出：

```
================================================================================
Testing Migration 007: review_decisions.decision field length
================================================================================

[Test 1] Checking decision column length...
✅ PASSED: decision column length is 32 (>= 32)

[Test 2] Testing 'revision_required' insertion...
✅ PASSED: Successfully inserted 'revision_required' (id: ...)
   Cleaned up test data

[Test 3] Verifying all decision types...
✅ PASSED: Column length 32 can store all decision types (max: 18)

================================================================================
✅ All tests passed!
================================================================================
```

## 代码更新

### 数据库模型

Python 模型已经正确定义为 `String(32)`，无需修改：

```python
# apps/api/app/db/models.py
class ReviewDecisionModel(Base):
    __tablename__ = "review_decisions"
    
    decision: Mapped[str] = mapped_column(String(32))  # ✅ 已经是 32
```

### API Schema

Pydantic schema 无需修改，使用 Enum 验证：

```python
# apps/api/app/schemas/review.py
class ReviewDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUIRED = "revision_required"
```

## 回滚

如果需要回滚（不推荐，因为会导致功能不可用）：

```sql
-- 警告：这会导致 'revision_required' 无法存储
ALTER TABLE review_decisions
ALTER COLUMN decision TYPE VARCHAR(16);
```

## 相关文件

- **迁移文件**: `infra/migrations/007_fix_review_decision_length.sql`
- **测试脚本**: `infra/migrations/test_007_migration.py`
- **应用脚本**: `infra/migrations/apply_007_migration.sh`
- **数据库模型**: `apps/api/app/db/models.py`
- **API Schema**: `apps/api/app/schemas/review.py`

## 时间线

- **发现时间**: 2026-04-11
- **优先级**: 中（有 workaround，但影响用户体验）
- **修复时间**: 2026-04-12
- **迁移编号**: 007

## 注意事项

1. **向后兼容**: 此迁移完全向后兼容，不会影响现有数据
2. **性能影响**: 字段长度增加对性能影响可忽略不计
3. **数据迁移**: 无需迁移现有数据，只是扩展字段长度
4. **应用重启**: 应用迁移后无需重启应用

## 验收标准

- [x] `decision` 字段长度为 VARCHAR(32)
- [x] 可以成功插入 'revision_required'
- [x] 所有三种决策类型都可以正常存储
- [x] 测试脚本全部通过
- [x] 文档已更新

---

**状态**: ✅ 已修复  
**迁移编号**: 007  
**创建日期**: 2026-04-12
