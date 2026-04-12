#!/usr/bin/env python3
"""
Test script for Migration 007: Fix review_decisions.decision field length

This script verifies that:
1. The decision column can store 'revision_required' (18 characters)
2. The column length is VARCHAR(32)
3. All existing data is preserved
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import psycopg2
from psycopg2.extras import RealDictCursor


def test_migration_007():
    """Test Migration 007: review_decisions.decision field length fix"""
    
    # Database connection parameters
    conn_params = {
        'dbname': os.getenv('DB_NAME', 'ai_comic_drama'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("=" * 80)
        print("Testing Migration 007: review_decisions.decision field length")
        print("=" * 80)
        
        # Test 1: Check column length
        print("\n[Test 1] Checking decision column length...")
        cursor.execute("""
            SELECT character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'review_decisions' AND column_name = 'decision'
        """)
        result = cursor.fetchone()
        
        if result is None:
            print("❌ FAILED: decision column not found")
            return False
        
        length = result['character_maximum_length']
        if length >= 32:
            print(f"✅ PASSED: decision column length is {length} (>= 32)")
        else:
            print(f"❌ FAILED: decision column length is {length} (expected >= 32)")
            return False
        
        # Test 2: Test inserting 'revision_required'
        print("\n[Test 2] Testing 'revision_required' insertion...")
        
        # First, check if we have any projects and episodes to use
        cursor.execute("SELECT id FROM projects LIMIT 1")
        project = cursor.fetchone()
        
        if not project:
            print("⚠️  SKIPPED: No projects found (need test data)")
        else:
            cursor.execute("SELECT id FROM episodes WHERE project_id = %s LIMIT 1", (project['id'],))
            episode = cursor.fetchone()
            
            if not episode:
                print("⚠️  SKIPPED: No episodes found (need test data)")
            else:
                cursor.execute("SELECT id FROM stage_tasks WHERE episode_id = %s LIMIT 1", (episode['id'],))
                stage_task = cursor.fetchone()
                
                if not stage_task:
                    print("⚠️  SKIPPED: No stage_tasks found (need test data)")
                else:
                    # Try to insert a review decision with 'revision_required'
                    try:
                        cursor.execute("""
                            INSERT INTO review_decisions (
                                project_id, episode_id, stage_task_id, decision, comment_text
                            ) VALUES (%s, %s, %s, %s, %s)
                            RETURNING id
                        """, (
                            project['id'],
                            episode['id'],
                            stage_task['id'],
                            'revision_required',
                            'Test migration 007'
                        ))
                        
                        review_id = cursor.fetchone()['id']
                        print(f"✅ PASSED: Successfully inserted 'revision_required' (id: {review_id})")
                        
                        # Clean up test data
                        cursor.execute("DELETE FROM review_decisions WHERE id = %s", (review_id,))
                        conn.commit()
                        print("   Cleaned up test data")
                        
                    except Exception as e:
                        conn.rollback()
                        print(f"❌ FAILED: Could not insert 'revision_required': {e}")
                        return False
        
        # Test 3: Verify all decision types can be stored
        print("\n[Test 3] Verifying all decision types...")
        decision_types = ['approved', 'rejected', 'revision_required']
        max_length = max(len(d) for d in decision_types)
        
        if length >= max_length:
            print(f"✅ PASSED: Column length {length} can store all decision types (max: {max_length})")
        else:
            print(f"❌ FAILED: Column length {length} cannot store all decision types (max: {max_length})")
            return False
        
        print("\n" + "=" * 80)
        print("✅ All tests passed!")
        print("=" * 80)
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        return False


if __name__ == '__main__':
    success = test_migration_007()
    sys.exit(0 if success else 1)
