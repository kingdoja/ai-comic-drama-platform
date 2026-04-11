-- Migration 007: Fix review_decisions.decision field length
-- Issue: VARCHAR(16) cannot store 'revision_required' (18 chars)
-- Solution: Extend to VARCHAR(32)

-- Extend decision field length
ALTER TABLE review_decisions 
ALTER COLUMN decision TYPE VARCHAR(32);

-- Add comment
COMMENT ON COLUMN review_decisions.decision IS 'Review decision: approved, rejected, revision_required (max 32 chars)';
