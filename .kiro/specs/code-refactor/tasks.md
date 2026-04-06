# 代码重构实施任务

## 任务列表

- [ ] 1. 创建新目录结构
  - 创建 agents/、services/、tests/、utils/、docs/ 目录
  - 添加所有必要的 __init__.py 文件
  - _Requirements: 2.1_

- [ ] 2. 移动和重组 Agent 文件
  - [ ] 2.1 移动 base_agent.py 到 agents/
    - 移动文件
    - 更新 agents/__init__.py 导出
    - _Requirements: 1.2, 2.2_
  
  - [ ] 2.2 移动所有 Agent 实现到 agents/
    - 移动 brief_agent.py
    - 移动 story_bible_agent.py
    - 移动 character_agent.py
    - 移动 script_agent.py
    - 移动 storyboard_agent.py
    - 更新 agents/__init__.py
    - _Requirements: 1.2, 2.2_
  
  - [ ] 2.3 更新 Agent 文件中的导入路径
    - 更新 base_agent 导入
    - 更新 services 导入（llm_service、validator）
    - 使用相对导入或包导入
    - _Requirements: 3.1, 3.2_

- [ ] 3. 移动和重组服务文件
  - [ ] 3.1 移动服务文件到 services/
    - 移动 llm_service.py
    - 移动 mock_llm_service.py
    - 移动 validator.py
    - _Requirements: 1.4, 2.4_
  
  - [ ] 3.2 创建 services/__init__.py
    - 导出所有服务类
    - 提供统一的导入接口
    - _Requirements: 2.4_
  
  - [ ] 3.3 更新服务文件中的导入路径
    - 更新内部依赖导入
    - _Requirements: 3.1_

- [ ] 4. 移动和重组测试文件
  - [ ] 4.1 移动所有测试文件到 tests/
    - 移动 test_brief_real_llm.py → test_brief_agent.py
    - 移动 test_story_bible_real_llm.py → test_story_bible_agent.py
    - 移动 test_character_real_llm.py → test_character_agent.py
    - 移动 test_script_real_llm.py → test_script_agent.py
    - 移动 test_storyboard_agent.py
    - 移动 test_llm_connection.py
    - 移动 test_validator.py
    - 移动 test_proxy_fix.py
    - _Requirements: 1.3, 2.3_
  
  - [ ] 4.2 更新测试文件中的导入路径
    - 更新 Agent 导入：`from agents.brief_agent import BriefAgent`
    - 更新服务导入：`from services.llm_service import LLMServiceFactory`
    - 更新 base_agent 导入
    - _Requirements: 3.1, 3.2_
  
  - [ ] 4.3 更新测试文件中的路径引用
    - 更新 .env 文件路径（向上一级）
    - 更新 sys.path 设置
    - _Requirements: 3.2_

- [ ] 5. 移动工具和文档文件
  - [ ] 5.1 移动工具文件到 utils/
    - 移动 setup_llm.py
    - 创建 utils/__init__.py
    - _Requirements: 2.5_
  
  - [ ] 5.2 移动文档到 docs/
    - 移动 README_LLM.md → docs/LLM.md
    - 移动 README_VALIDATOR.md → docs/VALIDATOR.md
    - 移动 LLM_INTEGRATION_SUMMARY.md → docs/INTEGRATION_SUMMARY.md
    - _Requirements: 4.3_

- [ ] 6. 更新配置和根文件
  - [ ] 6.1 更新 README.md
    - 添加新目录结构说明
    - 更新快速开始指南
    - 添加导入示例
    - _Requirements: 4.1, 4.2_
  
  - [ ] 6.2 保留配置文件在根目录
    - 保持 .env、.env.example、requirements.txt 在根目录
    - 确保配置文件路径引用正确
    - _Requirements: 1.5_

- [ ] 7. 验证和测试
  - [ ] 7.1 运行所有测试
    - 运行 test_brief_agent.py
    - 运行 test_story_bible_agent.py
    - 运行 test_character_agent.py
    - 运行 test_script_agent.py
    - 运行 test_llm_connection.py
    - 运行 test_validator.py
    - _Requirements: 3.2, 3.3_
  
  - [ ] 7.2 验证 Agent 功能
    - 测试 Brief Agent 端到端
    - 测试 Story Bible Agent 端到端
    - 测试 Character Agent 端到端
    - 测试 Script Agent 端到端
    - _Requirements: 3.3_
  
  - [ ] 7.3 验证导入路径
    - 检查所有 import 语句
    - 确认没有导入错误
    - _Requirements: 3.1, 3.2_

- [ ] 8. 清理和文档
  - [ ] 8.1 删除旧文件（如果有备份）
    - 确认所有文件已正确移动
    - 删除任何临时文件
    - _Requirements: 2.1_
  
  - [ ] 8.2 创建迁移文档
    - 记录文件移动映射
    - 说明导入路径变化
    - 提供迁移指南
    - _Requirements: 4.3, 4.4_
  
  - [ ] 8.3 更新项目文档
    - 更新 PROJECT_SUMMARY.md
    - 更新相关文档中的路径引用
    - _Requirements: 4.1_

- [ ] 9. 提交到 Git
  - 提交所有更改
  - 使用清晰的 commit message
  - 推送到 GitHub
  - _Requirements: All_

## 注意事项

1. **备份：** 在开始重构前，确保代码已提交到 Git
2. **增量测试：** 每移动一批文件后立即测试
3. **导入路径：** 优先使用包导入（from agents.xxx）而非相对导入
4. **文件重命名：** 测试文件统一命名为 test_<agent>_agent.py
5. **文档同步：** 确保所有文档中的路径引用同步更新
