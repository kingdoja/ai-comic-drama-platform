# Quick Start: Migration 008

## TL;DR

```bash
# Validate the migration
cd infra/migrations
python validate_008_migration.py

# Apply the migration
python apply_migrations.py

# Or apply directly with psql
psql -U your_user -d your_database -f 008_final_export_pilot_ready.sql
```

## What This Migration Does

Creates two new tables for Final Export functionality:

1. **export_bundles** - Tracks all export operations and results
2. **trace_records** - Records data lineage and processing flow

Plus adds export tracking fields to the `episodes` table.

## Before You Run

✅ Backup your database (recommended)
✅ Ensure you have applied all previous migrations (001-007)
✅ Verify database connection

## Apply Migration

### Method 1: Python Script (Recommended)

```bash
cd infra/migrations
python apply_migrations.py
```

This will:
- Check which migrations have been applied
- Apply any pending migrations in order
- Validate the results

### Method 2: Direct SQL

```bash
psql -U your_user -d your_database -f infra/migrations/008_final_export_pilot_ready.sql
```

## Verify Success

Run the validation script:

```bash
python validate_008_migration.py
```

Expected output:
```
✅ Migration 008 validation PASSED!
```

Or check manually:

```sql
-- Check if tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('export_bundles', 'trace_records');

-- Check if episodes columns exist
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'episodes' 
AND column_name IN ('last_export_at', 'export_count');
```

## Troubleshooting

### Error: "relation already exists"

The tables already exist. This is safe to ignore if you're re-running the migration.

### Error: "permission denied"

Ensure your database user has CREATE TABLE and ALTER TABLE permissions.

### Error: "foreign key constraint"

Ensure all previous migrations (001-007) have been applied successfully.

## What's Next?

After applying this migration:

1. Update `app/db/models.py` with new models
2. Create repositories for export bundles and trace records
3. Implement Export Service
4. Implement Trace Service

See `MIGRATION_008_SUMMARY.md` for detailed information.
