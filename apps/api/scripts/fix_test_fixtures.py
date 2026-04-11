"""
修复测试文件中的 fixture 依赖问题

将所有使用 uuid4() 创建 project_id 和 episode_id 的地方
替换为使用 test_project 和 test_episode fixtures
"""

import re
from pathlib import Path

def fix_test_file(file_path: Path):
    """修复单个测试文件"""
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    
    # 1. 修改测试方法签名，添加 test_project, test_episode fixtures
    content = re.sub(
        r'def (test_\w+)\(self, test_session\):',
        r'def \1(self, test_session, test_project, test_episode):',
        content
    )
    
    # 2. 替换 project_id = uuid4() 为 project_id = test_project.id
    content = re.sub(
        r'project_id = uuid4\(\)',
        r'project_id = test_project.id',
        content
    )
    
    # 3. 替换 episode_id = uuid4() 为 episode_id = test_episode.id
    content = re.sub(
        r'episode_id = uuid4\(\)',
        r'episode_id = test_episode.id',
        content
    )
    
    # 4. 更新 Setup 注释
    content = re.sub(
        r'# Setup\n',
        r'# Setup - use test fixtures\n',
        content
    )
    
    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        print(f"✓ Fixed {file_path.name}")
        return True
    else:
        print(f"- No changes needed for {file_path.name}")
        return False

def main():
    """修复所有测试文件"""
    test_dir = Path(__file__).parent.parent / "tests" / "unit"
    
    files_to_fix = [
        "test_review_service.py",
        "test_qa_stage.py",
    ]
    
    fixed_count = 0
    for filename in files_to_fix:
        file_path = test_dir / filename
        if file_path.exists():
            if fix_test_fixture(file_path):
                fixed_count += 1
        else:
            print(f"✗ File not found: {filename}")
    
    print(f"\n修复完成: {fixed_count} 个文件已更新")

if __name__ == "__main__":
    main()
