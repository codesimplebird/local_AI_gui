"""
API 客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.api_client import DeepSeekChat
from openai import (
    APIConnectionError,
    RateLimitError,
    APIStatusError,
    AuthenticationError,
)


class TestDeepSeekChat:
    """测试 DeepSeekChat 类"""

    @pytest.fixture
    def mock_config(self):
        """模拟 API 配置"""
        return [{
            "name": "test_api",
            "model": "deepseek-chat",
            "api_key": "test-key-123",
            "base_url": "https://api.deepseek.com"
        }]

    @pytest.fixture
    def mock_messages(self):
        """模拟消息历史"""
        return [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

    def test_init_with_config(self, mock_config):
        """测试初始化"""
        chat = DeepSeekChat(mock_config)
        assert chat.model == "deepseek-chat"
        assert chat.client is not None

    def test_init_with_default_base_url(self):
        """测试默认 base_url"""
        config = [{
            "name": "test",
            "model": "test-model",
            "api_key": "test-key"
        }]
        chat = DeepSeekChat(config)
        # 应该使用默认 URL
        assert chat.model == "test-model"

    @patch('src.api_client.OpenAI')
    def test_chat_success(self, mock_openai, mock_config, mock_messages):
        """测试成功发送消息"""
        # 模拟流式响应
        mock_stream = MagicMock()
        mock_openai.return_value.chat.completions.create.return_value = mock_stream

        chat = DeepSeekChat(mock_config)
        result = chat.chat(mock_messages, send_code=1)

        assert result == mock_stream
        mock_openai.return_value.chat.completions.create.assert_called_once()

    def test_chat_authentication_error(self, mock_config, mock_messages):
        """测试认证错误"""
        with patch('src.api_client.OpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.side_effect = (
                AuthenticationError(
                    "Invalid API key",
                    response=Mock(),
                    body={},
                )
            )

            chat = DeepSeekChat(mock_config)
            result = chat.chat(mock_messages, send_code=1)

            assert isinstance(result, str)
            assert "API Key" in result

    def test_chat_rate_limit_error(self, mock_config, mock_messages):
        """测试频率限制错误"""
        with patch('src.api_client.OpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.side_effect = (
                RateLimitError("Rate limit exceeded", response=Mock(), body={})
            )

            chat = DeepSeekChat(mock_config)
            result = chat.chat(mock_messages, send_code=1)

            assert isinstance(result, str)
            assert "频率超限" in result

    def test_chat_connection_error(self, mock_config, mock_messages):
        """测试连接错误"""
        with patch('src.api_client.OpenAI') as mock_openai:
            mock_openai.return_value.chat.completions.create.side_effect = (
                APIConnectionError(
                    message="Connection failed",
                    request=Mock(),
                )
            )

            chat = DeepSeekChat(mock_config)
            result = chat.chat(mock_messages, send_code=1)

            assert isinstance(result, str)
            assert "无法连接" in result

    def test_chat_api_status_error(self, mock_config, mock_messages):
        """测试 API 状态错误"""
        with patch('src.api_client.OpenAI') as mock_openai:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_error = APIStatusError(
                "Internal Server Error",
                response=mock_response,
                body={}
            )
            mock_openai.return_value.chat.completions.create.side_effect = mock_error

            chat = DeepSeekChat(mock_config)
            result = chat.chat(mock_messages, send_code=1)

            assert isinstance(result, str)
            assert "500" in result

    def test_chat_invalid_send_code(self, mock_config, mock_messages):
        """测试无效的 send_code"""
        chat = DeepSeekChat(mock_config)
        result = chat.chat(mock_messages, send_code=0)

        assert isinstance(result, str)
        assert "send_code" in result

    def test_chat_with_long_history(self, mock_config):
        """测试长对话历史"""
        # 构建包含多轮对话的消息历史
        messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        for i in range(20):  # 20轮对话
            messages.append({"role": "user", "content": f"Question {i}"})
            messages.append({"role": "assistant", "content": f"Answer {i}"})

        with patch('src.api_client.OpenAI') as mock_openai:
            mock_stream = MagicMock()
            mock_openai.return_value.chat.completions.create.return_value = mock_stream

            chat = DeepSeekChat(mock_config)
            result = chat.chat(messages, send_code=1)

            assert result == mock_stream
            # 验证调用参数
            call_args = mock_openai.return_value.chat.completions.create.call_args
            assert len(call_args.kwargs['messages']) == 41  # 1 system + 40 messages
