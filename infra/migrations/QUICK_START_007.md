# Quick Start: Migration 007

## 快速应用迁移

```bash
cd infra/migrations
bash apply_007_migration.sh
```

## 或者手动应用

```bash
cd infra/migrations

# 应用迁移
psql -U postgres -d ai_comic_drama -f 007_fix_review_decision_length.sql

# 验证
python test_007_migration.py
```

## 问题

`review_decisions.decision` 字段 VARCHAR(16) 无法存储 'revision_required' (18 字符)

## 解决方案

扩展到 VARCHAR(32)

## 验证

```bash
python test_007_migration.py
```

应该看到：
```
✅ PASSED: decision column length is 32 (>= 32)
✅ PASSED: Successfully inserted 'revision_required'
✅ All tests passed!
```

## 完成！

迁移完成后，审核功能的"需要修订"决策将正常工作。
