# Migration 006: QA / Review / Rerun Support

## Overview

This migration adds database support for the QA/Review/Rerun workflow introduced in Iteration 5. It extends the `workflow_runs` table with rerun tracking capabilities and adds performance indexes for efficient querying.

## Changes Made

### 1. WorkflowRun Table Extensions

Added three new columns to the `workflow_runs` table:

| Column | Type | Description | Requirement |
|--------|------|-------------|-------------|
| `parent_workflow_run_id` | UUID | References the parent WorkflowRun if this is a rerun | 7.1, 7.2 |
| `rerun_reason` | TEXT | Records why the rerun was triggered (from review or manual) | 7.1, 7.2 |
| `rerun_shot_ids_jsonb` | JSONB | Stores which shots to rerun for partial reruns | 8.1 |

**Foreign Key Constraint:**
- `parent_workflow_run_id` references `workflow_runs(id)` with `ON DELETE SET NULL`

### 2. Performance Indexes

Created five new indexes to optimize query performance:

| Index Name | Table | Columns | Purpose | Requirement |
|------------|-------|---------|---------|-------------|
| `idx_qa_reports_episode_created_at` | qa_reports | (episode_id, created_at DESC) | Optimize QA report queries by episode | 10.5 |
| `idx_review_decisions_stage_task_created_at` | review_decisions | (stage_task_id, created_at DESC) | Optimize review history queries | 12.1 |
| `idx_workflow_runs_episode_rerun_from_stage` | workflow_runs | (episode_id, rerun_from_stage) | Optimize rerun history queries | 15.4 |
| `idx_workflow_runs_parent_workflow_run_id` | workflow_runs | (parent_workflow_run_id) | Optimize parent-child rerun queries | - |
| `idx_workflow_runs_rerun_shot_ids` | workflow_runs | GIN(rerun_shot_ids_jsonb) | Efficient JSONB queries on shot IDs | - |

**Note:** Indexes with WHERE clauses are partial indexes that only index rows where the condition is true, saving space and improving performance.

## How to Apply

### Using Docker Compose

```bash
cd infra/docker
docker-compose up -d postgres
docker exec -i docker-postgres-1 psql -U postgres -d thinking < ../migrations/006_qa_review_rerun.sql
```

### Using Local PostgreSQL

```bash
psql -U postgres -d thinking -f infra/migrations/006_qa_review_rerun.sql
```

### Using Python Script

```bash
cd infra/migrations
python apply_migrations.py
```

## Validation

### Syntax Validation (No Database Required)

```bash
cd infra/migrations
python validate_sql_syntax.py
```

This validates:
- SQL file encoding
- Required columns exist in the migration
- Required indexes exist in the migration
- Foreign key constraints are defined
- Validation block is present

### Database Validation (Requires Database Connection)

```bash
# Using SQL script
psql -U postgres -d thinking -f infra/migrations/validate_006_migration.sql

# Using Python script
cd infra/migrations
python test_006_migration.py
```

This validates:
- All columns were created
- All indexes were created
- Foreign key constraints are in place

## Impact on Existing Data

This migration is **non-destructive**:
- No existing data is modified
- No columns are dropped
- No tables are dropped
- All changes use `IF NOT EXISTS` to be idempotent

The migration can be safely applied to databases with existing data.

## Rollback

If you need to rollback this migration:

```sql
-- Remove indexes
DROP INDEX IF EXISTS idx_qa_reports_episode_created_at;
DROP INDEX IF EXISTS idx_review_decisions_stage_task_created_at;
DROP INDEX IF EXISTS idx_workflow_runs_episode_rerun_from_stage;
DROP INDEX IF EXISTS idx_workflow_runs_parent_workflow_run_id;
DROP INDEX IF EXISTS idx_workflow_runs_rerun_shot_ids;

-- Remove columns (WARNING: This will delete data in these columns)
ALTER TABLE workflow_runs DROP COLUMN IF EXISTS parent_workflow_run_id;
ALTER TABLE workflow_runs DROP COLUMN IF EXISTS rerun_reason;
ALTER TABLE workflow_runs DROP COLUMN IF EXISTS rerun_shot_ids_jsonb;
```

**⚠️ Warning:** Dropping columns will permanently delete any data stored in them. Only rollback if you're certain no rerun data needs to be preserved.

## Related Files

- **Migration Script:** `006_qa_review_rerun.sql`
- **Validation Scripts:**
  - `validate_sql_syntax.py` - Syntax validation
  - `validate_006_migration.sql` - SQL validation
  - `test_006_migration.py` - Python validation
- **Documentation:**
  - `README.md` - Updated with migration 006 information
  - `.kiro/specs/qa-review-rerun/design.md` - Design document
  - `.kiro/specs/qa-review-rerun/requirements.md` - Requirements document

## Next Steps

After applying this migration:

1. Verify the migration was successful using the validation scripts
2. Update your application code to use the new fields
3. Test the rerun functionality with the new database schema
4. Monitor query performance with the new indexes

## Questions?

If you encounter any issues:

1. Check the validation output for specific errors
2. Review the migration script for syntax errors
3. Ensure your database user has sufficient permissions
4. Check PostgreSQL logs for detailed error messages
