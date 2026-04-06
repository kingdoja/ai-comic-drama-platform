# Database Migrations

This directory contains SQL migration files for the AI 漫剧创作者工作台 database schema.

## Migration Files

Migrations are numbered sequentially and should be applied in order:

1. `001_initial_schema.sql` - Initial schema with users, projects, episodes, workflow_runs, and stage_tasks
2. `002_documents_assets_qa.sql` - Documents, assets, and QA reports tables
3. `003_iteration1_shots_reviews.sql` - Shots and review decisions tables
4. `004_performance_indexes.sql` - Performance indexes for workspace queries

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
```

### Using Local PostgreSQL

If you have PostgreSQL installed locally:

```bash
# Apply migrations in order
psql -U postgres -d thinking -f infra/migrations/001_initial_schema.sql
psql -U postgres -d thinking -f infra/migrations/002_documents_assets_qa.sql
psql -U postgres -d thinking -f infra/migrations/003_iteration1_shots_reviews.sql
psql -U postgres -d thinking -f infra/migrations/004_performance_indexes.sql
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

## Notes

- All migrations use `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS` to be idempotent
- Migrations can be safely re-applied without causing errors
- Always apply migrations in numerical order
- Test migrations on a development database before applying to production
