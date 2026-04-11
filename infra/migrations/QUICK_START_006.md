# Quick Start: Migration 006

## TL;DR

```bash
# Apply the migration
psql -U postgres -d thinking -f infra/migrations/006_qa_review_rerun.sql

# Validate it worked
python infra/migrations/validate_sql_syntax.py
```

## What This Migration Does

Adds support for workflow reruns:
- Track parent-child rerun relationships
- Record why reruns were triggered
- Store which shots to rerun
- Optimize queries for QA reports, reviews, and reruns

## New Fields in workflow_runs

```python
# In your code, you can now use:
workflow_run.parent_workflow_run_id  # UUID or None
workflow_run.rerun_reason            # str or None
workflow_run.rerun_shot_ids_jsonb    # list or None
```

## Example Usage

### Creating a Rerun

```python
# Full workflow rerun
rerun = WorkflowRunModel(
    project_id=project_id,
    episode_id=episode_id,
    workflow_kind="text_workflow",
    rerun_from_stage="script",
    parent_workflow_run_id=original_run.id,
    rerun_reason="Review feedback: improve dialogue",
    status="pending"
)

# Partial shot rerun
rerun = WorkflowRunModel(
    project_id=project_id,
    episode_id=episode_id,
    workflow_kind="media_workflow",
    rerun_from_stage="image_render",
    parent_workflow_run_id=original_run.id,
    rerun_reason="Fix character expressions",
    rerun_shot_ids_jsonb=[shot1_id, shot2_id],
    status="pending"
)
```

### Querying Reruns

```python
# Get all reruns for an episode
reruns = await db.execute(
    select(WorkflowRunModel)
    .where(WorkflowRunModel.episode_id == episode_id)
    .where(WorkflowRunModel.parent_workflow_run_id.isnot(None))
    .order_by(WorkflowRunModel.created_at.desc())
)

# Get rerun history for a specific stage
reruns = await db.execute(
    select(WorkflowRunModel)
    .where(WorkflowRunModel.episode_id == episode_id)
    .where(WorkflowRunModel.rerun_from_stage == "image_render")
    .order_by(WorkflowRunModel.created_at.desc())
)
```

## Performance Benefits

The new indexes optimize these common queries:

1. **QA Reports by Episode** - Fast retrieval of all QA reports for an episode
2. **Review History** - Quick lookup of review decisions for a stage
3. **Rerun History** - Efficient queries for rerun tracking
4. **Parent-Child Relationships** - Fast traversal of rerun chains

## Troubleshooting

### Migration fails with "column already exists"

This is safe to ignore - the migration uses `IF NOT EXISTS` to be idempotent.

### Migration fails with permission error

Ensure your database user has `ALTER TABLE` and `CREATE INDEX` permissions:

```sql
GRANT ALTER, CREATE ON DATABASE thinking TO your_user;
```

### Need to check if migration was applied?

```bash
psql -U postgres -d thinking -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'workflow_runs' AND column_name IN ('parent_workflow_run_id', 'rerun_reason', 'rerun_shot_ids_jsonb');"
```

Should return 3 rows if the migration was applied.

## See Also

- `MIGRATION_006_SUMMARY.md` - Detailed migration documentation
- `README.md` - General migration guide
- `.kiro/specs/qa-review-rerun/design.md` - Feature design document
