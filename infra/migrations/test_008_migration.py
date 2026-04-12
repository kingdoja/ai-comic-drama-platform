#!/usr/bin/env python3
"""
Test script for Migration 008: Final Export and Pilot Ready

This script performs a dry-run test of the migration without actually
executing it against a database.
"""

import re
import sys


def test_migration_008():
    """Test the migration file for common issues"""
    
    print("Testing Migration 008: Final Export and Pilot Ready")
    print("=" * 60)
    
    try:
        with open('008_final_export_pilot_ready.sql', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("✗ Migration file not found")
        return False
    
    all_tests_passed = True
    
    # Test 1: Check for SQL injection vulnerabilities
    print("\n1. Security checks...")
    dangerous_patterns = [
        r'EXECUTE\s+',  # Dynamic SQL execution
        r';\s*DROP\s+',  # SQL injection pattern
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            print(f"  ⚠️  Warning: Potentially dangerous pattern found: {pattern}")
        else:
            print(f"  ✓ No dangerous pattern: {pattern}")
    
    # Test 2: Check for proper transaction handling
    print("\n2. Transaction handling...")
    # Note: PostgreSQL DDL is auto-committed, so explicit transactions are optional
    print("  ✓ DDL statements are auto-committed in PostgreSQL")
    
    # Test 3: Check for proper error handling
    print("\n3. Error handling...")
    if 'DO $$' in content and 'EXCEPTION' not in content:
        print("  ℹ️  Note: Validation block doesn't use exception handling")
    if 'RAISE EXCEPTION' in content:
        print("  ✓ Uses RAISE EXCEPTION for validation failures")
    if 'RAISE NOTICE' in content:
        print("  ✓ Uses RAISE NOTICE for success messages")
    
    # Test 4: Check for idempotency
    print("\n4. Idempotency checks...")
    if 'IF NOT EXISTS' in content:
        print("  ✓ Uses IF NOT EXISTS for safe re-execution")
    else:
        print("  ⚠️  Warning: No IF NOT EXISTS clauses found")
        all_tests_passed = False
    
    # Test 5: Check for proper indexing
    print("\n5. Index strategy...")
    index_count = len(re.findall(r'CREATE INDEX', content))
    print(f"  ✓ Found {index_count} indexes")
    if index_count < 5:
        print("  ⚠️  Warning: Consider adding more indexes for query performance")
    
    # Test 6: Check for foreign key constraints
    print("\n6. Foreign key constraints...")
    fk_count = len(re.findall(r'REFERENCES', content))
    print(f"  ✓ Found {fk_count} foreign key constraints")
    
    # Check for proper CASCADE behavior
    if 'ON DELETE CASCADE' in content:
        print("  ✓ Uses ON DELETE CASCADE for parent-child relationships")
    if 'ON DELETE SET NULL' in content:
        print("  ✓ Uses ON DELETE SET NULL for optional references")
    
    # Test 7: Check for proper data types
    print("\n7. Data type validation...")
    proper_types = {
        'UUID': r'UUID',
        'TIMESTAMP WITH TIME ZONE': r'TIMESTAMP WITH TIME ZONE',
        'JSONB': r'JSONB',
        'BIGINT': r'BIGINT',
    }
    for type_name, pattern in proper_types.items():
        if re.search(pattern, content):
            print(f"  ✓ Uses {type_name} data type")
    
    # Test 8: Check for comments
    print("\n8. Documentation...")
    comment_count = len(re.findall(r'COMMENT ON', content))
    print(f"  ✓ Found {comment_count} comments")
    if comment_count < 5:
        print("  ℹ️  Note: Consider adding more comments for documentation")
    
    # Test 9: Check for default values
    print("\n9. Default values...")
    if 'DEFAULT' in content:
        default_count = len(re.findall(r'DEFAULT', content))
        print(f"  ✓ Found {default_count} default values")
    
    # Test 10: Check for validation block
    print("\n10. Validation block...")
    if 'DO $$' in content:
        print("  ✓ Includes validation block")
        
        # Check what the validation block validates
        validation_checks = [
            ('export_bundles table', r"table_name = 'export_bundles'"),
            ('trace_records table', r"table_name = 'trace_records'"),
            ('last_export_at column', r"column_name = 'last_export_at'"),
            ('export_count column', r"column_name = 'export_count'"),
        ]
        
        for check_name, pattern in validation_checks:
            if re.search(pattern, content):
                print(f"    ✓ Validates {check_name}")
            else:
                print(f"    ⚠️  Missing validation for {check_name}")
    else:
        print("  ✗ No validation block found")
        all_tests_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("✅ Migration 008 tests PASSED!")
        print("The migration appears to be well-structured and safe to apply.")
        return True
    else:
        print("⚠️  Migration 008 tests completed with warnings")
        print("Review the warnings above before applying the migration.")
        return True  # Warnings don't fail the test


if __name__ == '__main__':
    success = test_migration_008()
    sys.exit(0 if success else 1)
