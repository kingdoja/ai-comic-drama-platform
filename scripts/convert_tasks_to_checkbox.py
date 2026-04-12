#!/usr/bin/env python3
"""
Convert tasks.md from header format to checkbox format with phase grouping.
"""

import re
import sys

def convert_tasks_to_checkbox(input_file, output_file):
    """Convert tasks from header format (###) to checkbox format (- [ ]) with phase parents."""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    converted_lines = []
    
    i = 0
    current_phase = None
    phase_tasks = []
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a phase header (## 阶段 X:)
        phase_match = re.match(r'^## (阶段 \d+: .+)$', line)
        
        if phase_match:
            # Save previous phase if exists
            if current_phase and phase_tasks:
                converted_lines.append(f'- [ ] {current_phase}')
                for task_line in phase_tasks:
                    converted_lines.append(f'  {task_line}')
                converted_lines.append('')
                phase_tasks = []
            
            current_phase = phase_match.group(1)
            i += 1
            
            # Skip empty line after phase header
            if i < len(lines) and lines[i].strip() == '':
                i += 1
            continue
        
        # Check if this is a task header (### 任务 X.Y:)
        task_match = re.match(r'^### (任务 \d+\.\d+: .+)$', line)
        
        if task_match:
            task_title = task_match.group(1)
            
            # Start collecting task content
            task_content = []
            i += 1
            
            # Skip empty line after header
            if i < len(lines) and lines[i].strip() == '':
                i += 1
            
            # Collect content until next task or section
            while i < len(lines):
                next_line = lines[i]
                
                # Stop at next task or major section
                if (re.match(r'^### 任务 \d+\.\d+:', next_line) or 
                    re.match(r'^## ', next_line)):
                    break
                
                task_content.append(next_line)
                i += 1
            
            # Format as nested checkbox task
            if current_phase:
                phase_tasks.append(f'- [ ] {task_title}')
                # Add indented content (double indent for nested task)
                for content_line in task_content:
                    if content_line.strip():
                        phase_tasks.append(f'  {content_line}')
                    else:
                        phase_tasks.append('')
                phase_tasks.append('')
            else:
                # No phase, add as top-level task
                converted_lines.append(f'- [ ] {task_title}')
                for content_line in task_content:
                    if content_line.strip():
                        converted_lines.append(f'  {content_line}')
                    else:
                        converted_lines.append('')
                converted_lines.append('')
        else:
            # For non-task, non-phase lines
            if current_phase and phase_tasks:
                # We hit a non-task line, save current phase
                converted_lines.append(f'- [ ] {current_phase}')
                for task_line in phase_tasks:
                    converted_lines.append(f'  {task_line}')
                converted_lines.append('')
                current_phase = None
                phase_tasks = []
            
            # Keep non-task lines as-is
            converted_lines.append(line)
            i += 1
    
    # Save last phase if exists
    if current_phase and phase_tasks:
        converted_lines.append(f'- [ ] {current_phase}')
        for task_line in phase_tasks:
            converted_lines.append(f'  {task_line}')
        converted_lines.append('')
    
    # Write converted content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(converted_lines))
    
    print(f"✅ Converted {input_file} to {output_file}")
    print(f"   Total lines: {len(converted_lines)}")
    
    # Count phases and tasks
    phase_count = len([l for l in converted_lines if re.match(r'^- \[ \] 阶段 \d+:', l)])
    task_count = len([l for l in converted_lines if re.match(r'^  - \[ \] 任务 \d+\.\d+:', l)])
    print(f"   Phases: {phase_count}")
    print(f"   Tasks: {task_count}")

if __name__ == '__main__':
    input_file = '.kiro/specs/final-export-pilot-ready/tasks_backup.md'
    output_file = '.kiro/specs/final-export-pilot-ready/tasks.md'
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    convert_tasks_to_checkbox(input_file, output_file)
