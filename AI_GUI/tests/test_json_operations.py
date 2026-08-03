"""
JSON 文件读写单元测试
"""
import pytest
import json
import os
import tempfile
from pathlib import Path


class TestJSONOperations:
    """测试 JSON 文件操作"""

    @pytest.fixture
    def temp_dir(self):
        """临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_chat_data(self):
        """示例聊天数据"""
        return {
            "item": [
                {
                    "chat_id": "test123",
                    "user_id": "user123",
                    "title": "Test Chat",
                    "timestamp": "2024-01-01T12:00:00Z",
                    "messages": [
                        {"role": "user", "content": "Hello"},
                        {"role": "assistant", "content": "Hi there!"},
                    ],
                    "metadata": {
                        "platform": "web",
                        "language": "zh-CN"
                    }
                }
            ]
        }

    def test_write_and_read_json(self, temp_dir, sample_chat_data):
        """测试 JSON 写入和读取"""
        file_path = os.path.join(temp_dir, "test_chat.json")
        
        # 写入
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(sample_chat_data, f, ensure_ascii=False, indent=4)
        
        # 读取
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 验证
        assert data == sample_chat_data
        assert len(data["item"]) == 1
        assert data["item"][0]["chat_id"] == "test123"

    def test_read_nonexistent_file(self, temp_dir):
        """测试读取不存在的文件"""
        file_path = os.path.join(temp_dir, "nonexistent.json")
        
        with pytest.raises(FileNotFoundError):
            with open(file_path, "r", encoding="utf-8") as f:
                json.load(f)

    def test_read_invalid_json(self, temp_dir):
        """测试读取无效的 JSON"""
        file_path = os.path.join(temp_dir, "invalid.json")
        
        # 写入无效的 JSON
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("{invalid json content}")
        
        # 应该抛出 JSONDecodeError
        with pytest.raises(json.JSONDecodeError):
            with open(file_path, "r", encoding="utf-8") as f:
                json.load(f)

    def test_write_empty_chat_data(self, temp_dir):
        """测试写入空的聊天数据"""
        file_path = os.path.join(temp_dir, "empty_chat.json")
        empty_data = {"item": []}
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(empty_data, f, ensure_ascii=False, indent=4)
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert data == empty_data
        assert len(data["item"]) == 0

    def test_unicode_content_preservation(self, temp_dir):
        """测试 Unicode 内容保留"""
        unicode_data = {
            "item": [
                {
                    "chat_id": "unicode_test",
                    "title": "中文标题",
                    "messages": [
                        {"role": "user", "content": "你好，世界！"},
                        {"role": "assistant", "content": "こんにちは世界！"},
                    ]
                }
            ]
        }
        
        file_path = os.path.join(temp_dir, "unicode_chat.json")
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(unicode_data, f, ensure_ascii=False, indent=4)
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert data["item"][0]["title"] == "中文标题"
        assert data["item"][0]["messages"][0]["content"] == "你好，世界！"

    def test_large_chat_history(self, temp_dir):
        """测试大型聊天历史"""
        large_data = {"item": []}
        
        # 创建 100 个会话
        for i in range(100):
            chat = {
                "chat_id": f"chat_{i}",
                "title": f"Chat {i}",
                "messages": []
            }
            
            # 每个会话 50 条消息
            for j in range(25):
                chat["messages"].append({"role": "user", "content": f"Q{j}"})
                chat["messages"].append({"role": "assistant", "content": f"A{j}"})
            
            large_data["item"].append(chat)
        
        file_path = os.path.join(temp_dir, "large_chat.json")
        
        # 写入
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(large_data, f, ensure_ascii=False, indent=4)
        
        # 读取
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 验证
        assert len(data["item"]) == 100
        assert len(data["item"][0]["messages"]) == 50
        assert data["item"][50]["chat_id"] == "chat_50"

    def test_json_indentation_formatting(self, temp_dir):
        """测试 JSON 缩进格式"""
        data = {"item": [{"chat_id": "123", "title": "Test"}]}
        file_path = os.path.join(temp_dir, "formatted.json")
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        # 读取原始内容
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 验证格式（应该包含缩进）
        assert "    " in content  # 4 空格缩进
        assert "\\n" not in content  # 不应该有转义的换行符

    def test_append_messages(self, temp_dir):
        """测试追加消息"""
        file_path = os.path.join(temp_dir, "append_test.json")
        data = {
            "item": [
                {
                    "chat_id": "test123",
                    "title": "Test",
                    "messages": [
                        {"role": "user", "content": "Message 1"},
                    ]
                }
            ]
        }
        
        # 首次写入
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        # 读取并追加
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        data["item"][0]["messages"].extend([
            {"role": "assistant", "content": "Response 1"},
            {"role": "user", "content": "Message 2"},
        ])
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        # 验证
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert len(data["item"][0]["messages"]) == 3
        assert data["item"][0]["messages"][1]["content"] == "Response 1"

    def test_concurrent_write_simulation(self, temp_dir):
        """模拟并发写入（应该加锁）"""
        file_path = os.path.join(temp_dir, "concurrent_test.json")
        data = {"item": []}
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        # 模拟多次写入
        for i in range(10):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            data["item"].append({"chat_id": f"chat_{i}", "title": f"Chat {i}", "messages": []})
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert len(data["item"]) == 10


class TestConfigFileOperations:
    """测试配置文件操作"""

    @pytest.fixture
    def sample_config(self):
        """示例配置"""
        return {
            "theme": "dark",
            "font_size": "medium",
            "items": [
                {
                    "name": "deepseek",
                    "model": "deepseek-chat",
                    "api_key": "sk-test123",
                    "base_url": "https://api.deepseek.com"
                }
            ],
            "select": {
                "default": "deepseek"
            }
        }

    def test_config_read_write(self, temp_dir, sample_config):
        """测试配置文件读写"""
        file_path = os.path.join(temp_dir, "config.json")
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(sample_config, f, ensure_ascii=False, indent=4)
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert data["theme"] == "dark"
        assert len(data["items"]) == 1
        assert data["select"]["default"] == "deepseek"

    def test_config_with_multiple_apis(self, temp_dir):
        """测试多 API 配置"""
        config = {
            "theme": "light",
            "items": [
                {"name": "api1", "model": "model1", "api_key": "key1", "base_url": "url1"},
                {"name": "api2", "model": "model2", "api_key": "key2", "base_url": "url2"},
            ],
            "select": {"default": "api1"}
        }
        
        file_path = os.path.join(temp_dir, "multi_config.json")
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert len(data["items"]) == 2
        assert data["select"]["default"] == "api1"
