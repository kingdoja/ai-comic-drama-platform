"""修复 test_review_service.py 中的 fixture 问题"""

from pathlib import Path

def fix_test_file():
    file_path = Path(__file__).parent.parent / "tests" / "unit" / "test_review_service.py"
    content = file_path.read_text(encoding='utf-8')
    
    # 修复错误的换行符
    content = content.replace('# Setup - use test fixtures`n        project_id = test_project.id`n        episode_id = test_episode.id',
                             '# Setup - use test fixtures\n        project_id = test_project.id\n        episode_id = test_episode.id')
    
    # 修复剩余的 Setup 部分
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 如果找到 "# Setup" 后面跟着 "project_id = uuid4()"
        if line.strip() == '# Setup' and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line == 'project_id = uuid4()':
                # 替换为使用 fixtures
                fixed_lines.append(line.replace('# Setup', '# Setup - use test fixtures'))
                fixed_lines.append(lines[i + 1].replace('project_id = uuid4()', 'project_id = test_project.id'))
                if i + 2 < len(lines) and lines[i + 2].strip() == 'episode_id = uuid4()':
                    fixed_lines.append(lines[i + 2].replace('episode_id = uuid4()', 'episode_id = test_episode.id'))
                    i += 3
                    continue
                i += 2
                continue
        
        fixed_lines.append(line)
        i += 1
    
    content = '\n'.join(fixed_lines)
    file_path.write_text(content, encoding='utf-8')
    print("✓ Fixed test_review_service.py")

if __name__ == "__main__":
    fix_test_file()
