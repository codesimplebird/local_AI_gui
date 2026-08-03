# 测试指南

## 运行测试

### 1. 安装测试依赖

```bash
# 使用项目的虚拟环境
cd AI_GUI

# 激活虚拟环境（Windows）
.venv(PyQt5)\Scripts\activate

# 或使用项目根目录的虚拟环境
cd ../../
.venv(PyQt5)\Scripts\activate

# 安装 pytest
pip install pytest

# 或安装所有测试依赖
pip install -r requirements-test.txt
```

### 2. 运行所有测试

```bash
cd AI_GUI
pytest
```

### 3. 运行特定测试文件

```bash
# 测试 API 客户端
pytest tests/test_api_client.py -v

# 测试消息历史
pytest tests/test_messages_history.py -v

# 测试 JSON 操作
pytest tests/test_json_operations.py -v
```

### 4. 运行特定测试用例

```bash
# 运行某个测试类
pytest tests/test_api_client.py::TestDeepSeekChat -v

# 运行某个测试方法
pytest tests/test_api_client.py::TestDeepSeekChat::test_chat_success -v
```

### 5. 查看详细输出

```bash
# 显示 print 输出
pytest -s

# 显示详细日志
pytest -v --log-cli-level=DEBUG

# 显示覆盖率报告（需要安装 pytest-cov）
pip install pytest-cov
pytest --cov=src --cov-report=html
```

## 测试覆盖范围

### ✅ 已实现的测试

#### 1. API 客户端测试 (`test_api_client.py`)
- ✅ 初始化配置
- ✅ 成功发送消息
- ✅ 认证错误处理
- ✅ 频率限制错误
- ✅ 连接错误处理
- ✅ API 状态错误
- ✅ 无效 send_code
- ✅ 长对话历史支持

#### 2. 消息历史测试 (`test_messages_history.py`)
- ✅ 消息历史结构验证
- ✅ System prompt 处理
- ✅ 空对话历史
- ✅ 长对话历史
- ✅ 消息角色交替
- ✅ 消息内容保留
- ✅ 特殊字符处理
- ✅ 聊天数据验证

#### 3. JSON 操作测试 (`test_json_operations.py`)
- ✅ JSON 读写
- ✅ 文件不存在处理
- ✅ 无效 JSON 处理
- ✅ 空数据处理
- ✅ Unicode 内容保留
- ✅ 大型聊天历史
- ✅ JSON 格式化
- ✅ 消息追加
- ✅ 配置管理

## 测试统计

- **测试文件**: 3 个
- **测试类**: 4 个
- **测试用例**: 25+ 个
- **覆盖模块**:
  - `src/api_client.py` ✅
  - 消息历史构建逻辑 ✅
  - JSON 文件操作 ✅

## 持续改进

### 待添加的测试

1. **UI 组件测试**
   - 使用 `pytest-qt` 测试 PyQt5 组件
   - 测试用户交互流程

2. **集成测试**
   - 完整的对话流程测试
   - 多轮对话上下文测试
   - 流式输出测试

3. **性能测试**
   - 大型聊天历史加载性能
   - JSON 读写性能
   - 内存使用测试

4. **边界测试**
   - 超长消息处理
   - 特殊字符边界
   - 并发访问测试

## 注意事项

1. **虚拟环境**: 确保在项目虚拟环境中运行测试
2. **依赖**: 需要先安装 `pytest` 和 `openai` 库
3. **Mock**: API 测试使用 mock，不需要真实 API key
4. **临时文件**: 测试使用临时文件，会自动清理
5. **隔离**: 每个测试用例相互独立，不影响真实数据

## 常见问题

### Q: 提示找不到模块？
```bash
# 确保在正确的目录
cd AI_GUI

# 设置 PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%cd%      # Windows
```

### Q: 测试失败？
```bash
# 查看详细错误信息
pytest -v --tb=long

# 运行单个测试调试
pytest tests/test_api_client.py::TestDeepSeekChat::test_chat_success -v -s
```

### Q: 如何添加新测试？
1. 在 `tests/` 目录创建 `test_*.py` 文件
2. 创建 `Test*` 类
3. 添加 `test_*` 方法
4. 使用 `@pytest.fixture` 准备测试数据
5. 使用 `assert` 验证结果

## 测试最佳实践

1. **独立性**: 每个测试独立运行，不依赖其他测试
2. **可重复**: 测试结果可重复，不使用随机数据
3. **隔离性**: 使用 mock 和临时文件，不影响真实数据
4. **覆盖率**: 尽量覆盖所有代码路径
5. **可读性**: 测试命名清晰，注释完整
6. **快速**: 测试运行速度快，使用 mock 替代慢操作
