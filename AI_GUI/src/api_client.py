from openai import (
    OpenAI,
    APIConnectionError,
    RateLimitError,
    APIStatusError,
    AuthenticationError,
)
import logging

logger = logging.getLogger(__name__)


class DeepSeekChat:
    def __init__(self, AI_sever_config):
        config = AI_sever_config[0]
        self.client = OpenAI(
            api_key=config["api_key"],
            base_url=config.get("base_url", "https://api.deepseek.com"),
        )
        self.model = config.get("model", "deepseek-chat")

    def chat(self, messages_history, send_code=1):
        """
        发送聊天请求，支持多轮对话上下文
        
        Args:
            messages_history: 完整的消息历史列表，格式为:
                [
                    {"role": "system", "content": "..."},
                    {"role": "user", "content": "..."},
                    {"role": "assistant", "content": "..."},
                    ...
                ]
            send_code: 1 = stream request, else normal request
            
        Returns:
            stream iterator 或错误信息字符串
        """
        if 1 == send_code:
            try:
                logger.info(f"Sending chat request with {len(messages_history)} messages")
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages_history,
                    temperature=0.7,
                    stream=True,
                    timeout=30,  # 增加超时时间到30秒
                )
                logger.info("Successfully received stream response")
                return completion
            except AuthenticationError as e:
                error_msg = "error:API Key 无效或已过期，请检查设置"
                logger.error(f"AuthenticationError: {e}")
                return error_msg
            except RateLimitError as e:
                error_msg = "error:API 请求频率超限，请稍后重试"
                logger.error(f"RateLimitError: {e}")
                return error_msg
            except APIConnectionError as e:
                error_msg = "error:无法连接到 API 服务器，请检查网络或 Base URL"
                logger.error(f"APIConnectionError: {e}")
                return error_msg
            except APIStatusError as e:
                error_msg = f"error:API 返回错误 (状态码 {e.status_code})"
                logger.error(f"APIStatusError: {e.status_code} - {e.message}")
                return error_msg
            except Exception as e:
                error_msg = f"error:{type(e).__name__}: {e}"
                logger.error(f"Unexpected error: {error_msg}")
                return error_msg
        else:
            error_msg = "error:send_code 配置错误"
            logger.error(error_msg)
            return error_msg
