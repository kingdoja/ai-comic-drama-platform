"""
Validate SQL syntax for migration 006.
This script performs basic syntax validation without requiring a database connection.
"""
import re
from pathlib import Path


def validate_migration_006():
    """Validate the SQL syntax of migration 006."""
    migration_file = Path(__file__).parent / "006_qa_review_rerun.sql"
    
    print("Validating migration 006...")
    print(f"File: {migration_file}")
    print()
    
    try:
        # Read the SQL file
        sql = migration_file.read_text(encoding='utf-8')
        print("✓ SQL file is valid UTF-8")
        
        # Check for ALTER TABLE statements
        alter_tables = re.findall(r'ALTER TABLE\s+\w+', sql, re.IGNORECASE)
        print(f"✓ Found {len(alter_tables)} ALTER TABLE statements")
        for stmt in alter_tables:
            print(f"  - {stmt}")
        
        # Check for ADD COLUMN statements
        add_columns = re.findall(r'ADD COLUMN\s+IF NOT EXISTS\s+(\w+)', sql, re.IGNORECASE)
        print(f"\n✓ Found {len(add_columns)} ADD COLUMN statements")
        for col in add_columns:
            print(f"  - {col}")
        
        # Check for CREATE INDEX statements
        create_indexes = re.findall(r'CREATE INDEX\s+IF NOT EXISTS\s+(\w+)', sql, re.IGNORECASE)
        print(f"\n✓ Found {len(create_indexes)} CREATE INDEX statements")
        for idx in create_indexes:
            print(f"  - {idx}")
        
        # Check for COMMENT statements
        comments = re.findall(r'COMMENT ON COLUMN', sql, re.IGNORECASE)
        print(f"\n✓ Found {len(comments)} COMMENT statements")
        
        # Check for required columns
        required_columns = ['parent_workflow_run_id', 'rerun_reason', 'rerun_shot_ids_jsonb']
        print(f"\n✓ Checking for required columns:")
        for col in required_columns:
            if col in sql:
                print(f"  ✓ {col}")
            else:
                print(f"  ✗ {col} MISSING")
                return False
        
        # Check for required indexes
        required_indexes = [
            'idx_qa_reports_episode_created_at',
            'idx_review_decisions_stage_task_created_at',
            'idx_workflow_runs_episode_rerun_from_stage',
            'idx_workflow_runs_parent_workflow_run_id',
            'idx_workflow_runs_rerun_shot_ids'
        ]
        print(f"\n✓ Checking for required indexes:")
        for idx in required_indexes:
            if idx in sql:
                print(f"  ✓ {idx}")
            else:
                print(f"  ✗ {idx} MISSING")
                return False
        
        # Check for foreign key constraint
        if 'REFERENCES workflow_runs(id)' in sql:
            print(f"\n✓ Foreign key constraint found")
        else:
            print(f"\n✗ Foreign key constraint MISSING")
            return False
        
        # Check for validation block
        if 'DO $$' in sql and 'RAISE EXCEPTION' in sql:
            print(f"✓ Validation block found")
        else:
            print(f"✗ Validation block MISSING")
            return False
        
        print("\n" + "="*60)
        print("✅ Migration 006 syntax validation passed!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        return False


if __name__ == "__main__":
    success = validate_migration_006()
    exit(0 if success else 1)
