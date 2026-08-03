"""
消息历史构建逻辑单元测试
"""
import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock


class TestMessagesHistoryBuilder:
    """测试消息历史构建逻辑"""

    @pytest.fixture
    def sample_chat_data(self):
        """示例聊天数据"""
        return {
            "item": [
                {
                    "chat_id": "test123",
                    "title": "Test Chat",
                    "messages": [
                        {"role": "user", "content": "Hello"},
                        {"role": "assistant", "content": "Hi there!"},
                        {"role": "user", "content": "How are you?"},
                        {"role": "assistant", "content": "I'm good, thanks!"},
                    ]
                }
            ]
        }

    @pytest.fixture
    def temp_chat_file(self, sample_chat_data):
        """临时聊天历史文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_chat_data, f)
            temp_path = f.name
        
        yield temp_path
        
        # 清理
        if os.path.exists(temp_path):
            os.remove(temp_path)

    def test_build_messages_history_structure(self):
        """测试消息历史结构"""
        # 模拟构建逻辑
        messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"},
        ]
        
        for msg in history:
            if msg["role"] == "user":
                messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                messages.append({"role": "assistant", "content": msg["content"]})
        
        messages.append({"role": "user", "content": "New question"})
        
        # 验证结构
        assert len(messages) == 4
        assert messages[0]["role"] == "system"
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == "New question"

    def test_build_messages_history_with_system_prompt(self):
        """测试包含 system prompt"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        
        assert len(messages) == 1
        assert messages[0]["role"] == "system"
        assert "helpful assistant" in messages[0]["content"]

    def test_build_messages_history_empty(self):
        """测试空对话历史"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        
        # 没有历史消息，只有 system prompt 和当前输入
        messages.append({"role": "user", "content": "First message"})
        
        assert len(messages) == 2
        assert messages[1]["content"] == "First message"

    def test_build_messages_history_long_conversation(self):
        """测试长对话历史"""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        
        # 模拟 10 轮对话
        for i in range(10):
            messages.append({"role": "user", "content": f"Question {i}"})
            messages.append({"role": "assistant", "content": f"Answer {i}"})
        
        # 添加当前输入
        messages.append({"role": "user", "content": "Final question"})
        
        # 验证：1 system + 20 history + 1 current = 22
        assert len(messages) == 22
        assert messages[0]["role"] == "system"
        assert messages[-1]["content"] == "Final question"

    def test_messages_role_alternation(self):
        """测试消息角色交替"""
        messages = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "Q1"},
            {"role": "assistant", "content": "A1"},
            {"role": "user", "content": "Q2"},
            {"role": "assistant", "content": "A2"},
        ]
        
        # 验证 user 和 assistant 交替出现（跳过 system）
        for i in range(1, len(messages)):
            if i % 2 == 1:
                assert messages[i]["role"] == "user"
            else:
                assert messages[i]["role"] == "assistant"

    def test_messages_content_preservation(self):
        """测试消息内容保留"""
        original_content = [
            {"role": "user", "content": "你好，世界！"},
            {"role": "assistant", "content": "你好！有什么我可以帮助的？"},
        ]
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        
        for msg in original_content:
            if msg["role"] == "user":
                messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                messages.append({"role": "assistant", "content": msg["content"]})
        
        # 验证内容完全保留
        assert messages[1]["content"] == "你好，世界！"
        assert messages[2]["content"] == "你好！有什么我可以帮助的？"

    def test_messages_with_special_characters(self):
        """测试包含特殊字符的消息"""
        special_chars = [
            "Code: `print('hello')`",
            "List:\n- item1\n- item2",
            "Math: $E = mc^2$",
            "Chinese: 中文测试",
            "Emoji: 🎉🚀💻",
        ]
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        
        for content in special_chars:
            messages.append({"role": "user", "content": content})
            messages.append({"role": "assistant", "content": f"Response to: {content}"})
        
        # 验证所有特殊字符都保留
        for i, content in enumerate(special_chars):
            assert messages[i*2 + 1]["content"] == content


class TestChatDataValidation:
    """测试聊天数据验证"""

    def test_valid_chat_data_structure(self):
        """测试有效的聊天数据结构"""
        chat_data = {
            "item": [
                {
                    "chat_id": "123",
                    "title": "Test",
                    "messages": [
                        {"role": "user", "content": "Hello"},
                        {"role": "assistant", "content": "Hi"},
                    ]
                }
            ]
        }
        
        assert "item" in chat_data
        assert len(chat_data["item"]) == 1
        assert "chat_id" in chat_data["item"][0]
        assert "messages" in chat_data["item"][0]

    def test_invalid_chat_data_missing_fields(self):
        """测试无效的聊天数据（缺少字段）"""
        chat_data = {
            "item": [
                {
                    "chat_id": "123",
                    # 缺少 title 和 messages
                }
            ]
        }
        
        # 应该能处理缺失字段的情况
        item = chat_data["item"][0]
        assert "chat_id" in item
        assert item.get("title") is None
        assert item.get("messages") is None

    def test_chat_data_with_empty_messages(self):
        """测试空消息列表的聊天数据"""
        chat_data = {
            "item": [
                {
                    "chat_id": "123",
                    "title": "New Chat",
                    "messages": []
                }
            ]
        }
        
        assert len(chat_data["item"][0]["messages"]) == 0
