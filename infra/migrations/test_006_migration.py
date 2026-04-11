"""
Test script for migration 006: QA / Review / Rerun
This script validates that the migration was applied correctly.
"""
import asyncio
import asyncpg
import os
from pathlib import Path


async def test_migration():
    """Test that migration 006 was applied correctly."""
    
    # Get database connection details from environment
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = int(os.getenv('DB_PORT', '5432'))
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_name = os.getenv('DB_NAME', 'thinking')
    
    print(f"Connecting to database: {db_host}:{db_port}/{db_name}")
    
    try:
        conn = await asyncpg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        
        print("✓ Connected to database")
        
        # Test 1: Check if parent_workflow_run_id column exists
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'workflow_runs' AND column_name = 'parent_workflow_run_id'
            )
        """)
        assert result, "❌ parent_workflow_run_id column not found"
        print("✓ parent_workflow_run_id column exists")
        
        # Test 2: Check if rerun_reason column exists
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'workflow_runs' AND column_name = 'rerun_reason'
            )
        """)
        assert result, "❌ rerun_reason column not found"
        print("✓ rerun_reason column exists")
        
        # Test 3: Check if rerun_shot_ids_jsonb column exists
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'workflow_runs' AND column_name = 'rerun_shot_ids_jsonb'
            )
        """)
        assert result, "❌ rerun_shot_ids_jsonb column not found"
        print("✓ rerun_shot_ids_jsonb column exists")
        
        # Test 4: Check if qa_reports index exists
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE indexname = 'idx_qa_reports_episode_created_at'
            )
        """)
        assert result, "❌ idx_qa_reports_episode_created_at index not found"
        print("✓ idx_qa_reports_episode_created_at index exists")
        
        # Test 5: Check if review_decisions index exists
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE indexname = 'idx_review_decisions_stage_task_created_at'
            )
        """)
        assert result, "❌ idx_review_decisions_stage_task_created_at index not found"
        print("✓ idx_review_decisions_stage_task_created_at index exists")
        
        # Test 6: Check if workflow_runs rerun index exists
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE indexname = 'idx_workflow_runs_episode_rerun_from_stage'
            )
        """)
        assert result, "❌ idx_workflow_runs_episode_rerun_from_stage index not found"
        print("✓ idx_workflow_runs_episode_rerun_from_stage index exists")
        
        # Test 7: Check if parent workflow run index exists
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE indexname = 'idx_workflow_runs_parent_workflow_run_id'
            )
        """)
        assert result, "❌ idx_workflow_runs_parent_workflow_run_id index not found"
        print("✓ idx_workflow_runs_parent_workflow_run_id index exists")
        
        # Test 8: Check if rerun_shot_ids GIN index exists
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE indexname = 'idx_workflow_runs_rerun_shot_ids'
            )
        """)
        assert result, "❌ idx_workflow_runs_rerun_shot_ids index not found"
        print("✓ idx_workflow_runs_rerun_shot_ids index exists")
        
        # Test 9: Verify foreign key constraint on parent_workflow_run_id
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.table_constraints tc
                JOIN information_schema.constraint_column_usage ccu
                    ON tc.constraint_name = ccu.constraint_name
                WHERE tc.table_name = 'workflow_runs'
                    AND tc.constraint_type = 'FOREIGN KEY'
                    AND ccu.column_name = 'parent_workflow_run_id'
            )
        """)
        assert result, "❌ Foreign key constraint on parent_workflow_run_id not found"
        print("✓ Foreign key constraint on parent_workflow_run_id exists")
        
        print("\n" + "="*60)
        print("✅ All migration 006 tests passed!")
        print("="*60)
        
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ Migration test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_migration())
