# Database Migrations

This directory contains SQL migration files for the AI 漫剧创作者工作台 database schema.

## Migration Files

Migrations are numbered sequentially and should be applied in order:

1. `001_initial_schema.sql` - Initial schema with users, projects, episodes, workflow_runs, and stage_tasks
2. `002_documents_assets_qa.sql` - Documents, assets, and QA reports tables
3. `003_iteration1_shots_reviews.sql` - Shots and review decisions tables
4. `004_performance_indexes.sql` - Performance indexes for workspace queries
5. `005_add_stage_task_metrics.sql` - Add metrics_jsonb column to stage_tasks
6. `006_qa_review_rerun.sql` - QA/Review/Rerun support: workflow_runs extensions and indexes
7. `007_fix_review_decision_length.sql` - Fix review_decisions.decision field length (VARCHAR(16) → VARCHAR(32))

## Applying Migrations

### Using Docker Compose

If you're using the Docker Compose setup from `infra/docker/docker-compose.yml`:

```bash
# Start PostgreSQL
cd infra/docker
docker-compose up -d postgres

# Apply migrations in order
docker exec -i docker-postgres-1 psql -U postgres -d thinking < ../migrations/001_initial_schema.sql
docker exec -i docker-postgres-1 psql -U postgres -d thinking < ../migrations/002_documents_assets_qa.sql
docker exec -i docker-postgres-1 psql -U postgres -d thinking < ../migrations/003_iteration1_shots_reviews.sql
docker exec -i docker-postgres-1 psql -U postgres -d thinking < ../migrations/004_performance_indexes.sql
docker exec -i docker-postgres-1 psql -U postgres -d thinking < ../migrations/005_add_stage_task_metrics.sql
docker exec -i docker-postgres-1 psql -U postgres -d thinking < ../migrations/006_qa_review_rerun.sql
docker exec -i docker-postgres-1 psql -U postgres -d thinking < ../migrations/007_fix_review_decision_length.sql
```

### Using Local PostgreSQL

If you have PostgreSQL installed locally:

```bash
# Apply migrations in order
psql -U postgres -d thinking -f infra/migrations/001_initial_schema.sql
psql -U postgres -d thinking -f infra/migrations/002_documents_assets_qa.sql
psql -U postgres -d thinking -f infra/migrations/003_iteration1_shots_reviews.sql
psql -U postgres -d thinking -f infra/migrations/004_performance_indexes.sql
psql -U postgres -d thinking -f infra/migrations/005_add_stage_task_metrics.sql
psql -U postgres -d thinking -f infra/migrations/006_qa_review_rerun.sql
psql -U postgres -d thinking -f infra/migrations/007_fix_review_decision_length.sql
```

### Using Python Script

You can also apply migrations programmatically using the database connection from the API:

```python
import asyncpg
import asyncio
from pathlib import Path

async def apply_migrations():
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='postgres',
        database='thinking'
    )
    
    migrations_dir = Path('infra/migrations')
    migration_files = sorted(migrations_dir.glob('*.sql'))
    
    for migration_file in migration_files:
        print(f"Applying {migration_file.name}...")
        sql = migration_file.read_text()
        await conn.execute(sql)
        print(f"✓ {migration_file.name} applied")
    
    await conn.close()

asyncio.run(apply_migrations())
```

## Migration 004: Performance Indexes

The latest migration adds three indexes to optimize workspace aggregation queries:

1. **idx_documents_episode_type_version**: Optimizes fetching the latest document version by episode and type (Requirement 8.2)
2. **idx_shots_episode_scene_shot**: Optimizes fetching shots ordered by scene and shot number (Requirement 8.3)
3. **idx_stage_tasks_workflow_stage_created**: Optimizes fetching stage tasks by workflow and stage type (Requirement 8.4)

These indexes use `IF NOT EXISTS` so they can be safely re-applied without errors.

## Migration 007: Fix review_decisions.decision Field Length

This migration fixes a bug where the `decision` field in `review_decisions` table was too short (VARCHAR(16)) to store the 'revision_required' decision type (18 characters).

### Changes

- Extended `decision` column from VARCHAR(16) to VARCHAR(32)
- Added comment documenting the fix

### Problem

The original schema defined:
```sql
decision VARCHAR(16) NOT NULL
```

But the application uses three decision types:
- 'approved' (8 chars) ✅
- 'rejected' (8 chars) ✅
- 'revision_required' (18 chars) ❌

### Solution

```sql
ALTER TABLE review_decisions
ALTER COLUMN decision TYPE VARCHAR(32);
```

### Testing

Run the test script to verify the fix:

```bash
cd infra/migrations
python test_007_migration.py
```

The test validates:
- Column length is at least 32 characters
- 'revision_required' can be inserted successfully
- All decision types can be stored

### Quick Apply

```bash
cd infra/migrations
bash apply_007_migration.sh
```

## Migration 006: QA / Review / Rerun Support

This migration adds support for the QA/Review/Rerun workflow:

### Workflow Runs Extensions

1. **parent_workflow_run_id**: Tracks parent-child relationships for reruns
2. **rerun_reason**: Records why a rerun was triggered (from review or manual)
3. **rerun_shot_ids_jsonb**: Stores which shots to rerun for partial reruns

### Performance Indexes

1. **idx_qa_reports_episode_created_at**: Optimizes QA report queries by episode (Requirement 10.5)
2. **idx_review_decisions_stage_task_created_at**: Optimizes review history queries (Requirement 12.1)
3. **idx_workflow_runs_episode_rerun_from_stage**: Optimizes rerun history queries (Requirement 15.4)
4. **idx_workflow_runs_parent_workflow_run_id**: Optimizes parent-child rerun queries
5. **idx_workflow_runs_rerun_shot_ids**: GIN index for efficient JSONB queries on shot IDs

### Testing the Migration

Run the test script to verify the migration was applied correctly:

```bash
cd infra/migrations
python test_006_migration.py
```

The test script validates:
- All new columns exist
- All indexes were created
- Foreign key constraints are in place

## Notes

- All migrations use `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS` to be idempotent
- Migrations can be safely re-applied without causing errors
- Always apply migrations in numerical order
- Test migrations on a development database before applying to production
