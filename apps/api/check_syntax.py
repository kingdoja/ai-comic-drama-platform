#!/usr/bin/env python
"""Check for Python 3.10+ syntax in codebase."""
import ast
import sys
from pathlib import Path

def check_file(filepath):
    """Check if file uses Python 3.10+ union syntax."""
    try:
        content = filepath.read_text(encoding='utf-8')
        # Check for | in type hints (simple regex check)
        lines = content.split('\n')
        issues = []
        for i, line in enumerate(lines, 1):
            # Skip comments and strings
            if '#' in line:
                line = line[:line.index('#')]
            # Look for type union syntax
            if ' | ' in line and ('->' in line or ':' in line):
                # Check if it's in a type annotation context
                if 'def ' in line or ':' in line:
                    issues.append((i, line.strip()))
        return issues
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

def main():
    app_dir = Path('app')
    issues_found = False
    
    for py_file in app_dir.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
        
        issues = check_file(py_file)
        if issues:
            issues_found = True
            print(f"\n{py_file}:")
            for line_no, line in issues:
                print(f"  Line {line_no}: {line}")
    
    if not issues_found:
        print("No Python 3.10+ syntax issues found!")
    else:
        print("\nFound files with potential Python 3.10+ syntax.")
        sys.exit(1)

if __name__ == '__main__':
    main()
