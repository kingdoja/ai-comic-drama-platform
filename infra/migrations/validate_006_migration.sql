-- Validation script for migration 006
-- Run this after applying the migration to verify it was successful

\echo '========================================='
\echo 'Validating Migration 006: QA/Review/Rerun'
\echo '========================================='
\echo ''

-- Check workflow_runs columns
\echo 'Checking workflow_runs table columns...'
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'workflow_runs' AND column_name = 'parent_workflow_run_id'
        ) THEN '✓ parent_workflow_run_id column exists'
        ELSE '✗ parent_workflow_run_id column MISSING'
    END AS check_result
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'workflow_runs' AND column_name = 'rerun_reason'
        ) THEN '✓ rerun_reason column exists'
        ELSE '✗ rerun_reason column MISSING'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'workflow_runs' AND column_name = 'rerun_shot_ids_jsonb'
        ) THEN '✓ rerun_shot_ids_jsonb column exists'
        ELSE '✗ rerun_shot_ids_jsonb column MISSING'
    END;

\echo ''
\echo 'Checking indexes...'

-- Check indexes
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM pg_indexes
            WHERE indexname = 'idx_qa_reports_episode_created_at'
        ) THEN '✓ idx_qa_reports_episode_created_at exists'
        ELSE '✗ idx_qa_reports_episode_created_at MISSING'
    END AS check_result
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM pg_indexes
            WHERE indexname = 'idx_review_decisions_stage_task_created_at'
        ) THEN '✓ idx_review_decisions_stage_task_created_at exists'
        ELSE '✗ idx_review_decisions_stage_task_created_at MISSING'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM pg_indexes
            WHERE indexname = 'idx_workflow_runs_episode_rerun_from_stage'
        ) THEN '✓ idx_workflow_runs_episode_rerun_from_stage exists'
        ELSE '✗ idx_workflow_runs_episode_rerun_from_stage MISSING'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM pg_indexes
            WHERE indexname = 'idx_workflow_runs_parent_workflow_run_id'
        ) THEN '✓ idx_workflow_runs_parent_workflow_run_id exists'
        ELSE '✗ idx_workflow_runs_parent_workflow_run_id MISSING'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM pg_indexes
            WHERE indexname = 'idx_workflow_runs_rerun_shot_ids'
        ) THEN '✓ idx_workflow_runs_rerun_shot_ids exists'
        ELSE '✗ idx_workflow_runs_rerun_shot_ids MISSING'
    END;

\echo ''
\echo 'Checking foreign key constraints...'

-- Check foreign key constraint
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
            WHERE tc.table_name = 'workflow_runs'
                AND tc.constraint_type = 'FOREIGN KEY'
                AND ccu.column_name = 'parent_workflow_run_id'
        ) THEN '✓ Foreign key constraint on parent_workflow_run_id exists'
        ELSE '✗ Foreign key constraint on parent_workflow_run_id MISSING'
    END AS check_result;

\echo ''
\echo '========================================='
\echo 'Validation Complete'
\echo '========================================='
