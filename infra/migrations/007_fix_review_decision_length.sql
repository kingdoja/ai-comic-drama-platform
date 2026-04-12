-- Migration 007: Fix review_decisions.decision field length
-- Problem: VARCHAR(16) cannot store 'revision_required' (18 characters)
-- Solution: Extend field to VARCHAR(32) to accommodate all decision types

-- ============================================================================
-- Extend decision field length
-- ============================================================================

ALTER TABLE review_decisions
ALTER COLUMN decision TYPE VARCHAR(32);

-- Add comment to document the fix
COMMENT ON COLUMN review_decisions.decision IS 'Review decision: approved, rejected, or revision_required (extended to VARCHAR(32) in migration 007)';

-- ============================================================================
-- Verification
-- ============================================================================

DO $$
DECLARE
    decision_length INTEGER;
BEGIN
    -- Check the new column length
    SELECT character_maximum_length INTO decision_length
    FROM information_schema.columns
    WHERE table_name = 'review_decisions' AND column_name = 'decision';
    
    IF decision_length < 32 THEN
        RAISE EXCEPTION 'Migration failed: decision column length is %, expected 32', decision_length;
    END IF;
    
    RAISE NOTICE 'Migration 007 completed successfully: decision field extended to VARCHAR(32)';
END $$;
