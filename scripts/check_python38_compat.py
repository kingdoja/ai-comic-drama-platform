#!/usr/bin/env python3
"""
检查 Python 3.8 兼容性问题

常见问题：
1. 使用 X | Y 而不是 Union[X, Y] 或 Optional[X]
2. 使用 collections.abc.Generator 而不是 typing.Generator
3. 使用 dict[str, int] 而不是 Dict[str, int]
4. 使用 list[str] 而不是 List[str]
"""

import re
import sys
from pathlib import Path


def check_union_syntax(file_path: Path) -> list:
    """检查是否使用了 | 联合类型语法"""
    issues = []
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查类型注解中的 | 语法
            if re.search(r':\s*\w+\s*\|\s*\w+', line) or re.search(r'->\s*\w+\s*\|\s*\w+', line):
                issues.append({
                    'file': str(file_path),
                    'line': i,
                    'issue': 'Union type with | operator (Python 3.10+)',
                    'suggestion': 'Use Optional[X] or Union[X, Y] instead',
                    'code': line.strip()
                })
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return issues


def check_collections_abc(file_path: Path) -> list:
    """检查是否使用了 collections.abc 用于类型注解"""
    issues = []
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if 'from collections.abc import' in line and any(
                t in line for t in ['Generator', 'Iterator', 'Iterable', 'Callable']
            ):
                issues.append({
                    'file': str(file_path),
                    'line': i,
                    'issue': 'Using collections.abc for type hints',
                    'suggestion': 'Import from typing instead',
                    'code': line.strip()
                })
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return issues


def check_builtin_generics(file_path: Path) -> list:
    """检查是否使用了内置泛型（dict, list, set, tuple）"""
    issues = []
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查 dict[...], list[...], set[...], tuple[...]
            if re.search(r'\b(dict|list|set|tuple)\[', line):
                # 排除字符串和注释
                if not line.strip().startswith('#') and not line.strip().startswith('"'):
                    issues.append({
                        'file': str(file_path),
                        'line': i,
                        'issue': 'Using builtin generic types (Python 3.9+)',
                        'suggestion': 'Use Dict, List, Set, Tuple from typing',
                        'code': line.strip()
                    })
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return issues


def main():
    """主函数"""
    # 检查 apps/api 目录
    api_dir = Path(__file__).parent.parent / 'apps' / 'api' / 'app'
    
    if not api_dir.exists():
        print(f"Directory not found: {api_dir}")
        return 1
    
    all_issues = []
    
    # 遍历所有 Python 文件
    for py_file in api_dir.rglob('*.py'):
        issues = []
        issues.extend(check_union_syntax(py_file))
        issues.extend(check_collections_abc(py_file))
        issues.extend(check_builtin_generics(py_file))
        all_issues.extend(issues)
    
    # 输出结果
    if all_issues:
        print(f"\n❌ Found {len(all_issues)} Python 3.8 compatibility issues:\n")
        
        for issue in all_issues:
            print(f"📁 {issue['file']}:{issue['line']}")
            print(f"   Issue: {issue['issue']}")
            print(f"   Suggestion: {issue['suggestion']}")
            print(f"   Code: {issue['code']}")
            print()
        
        return 1
    else:
        print("\n✅ No Python 3.8 compatibility issues found!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
