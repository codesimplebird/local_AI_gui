import sys
import os

# ── suppress libpng iCCP warnings ──
class _LibPNGFilter:
    def __init__(self, stream):
        self._stream = stream
    def write(self, data):
        if 'iCCP' not in data and 'libpng warning' not in data:
            self._stream.write(data)
    def flush(self):
        self._stream.flush()

sys.stderr = _LibPNGFilter(sys.stderr)

# add project root to sys.path for src.* imports
_proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _proj_root not in sys.path:
    sys.path.insert(0, _proj_root)

import json
import time
import html
import logging
import os
import threading
import tempfile
from copy import deepcopy

from PyQt5.QtWidgets import QApplication, QMessageBox, QMenu, QInputDialog

from PyQt5.QtCore import pyqtSignal, QThread, QUrl, QTimer


from src.api_client import DeepSeekChat

from src.settings_dialog import Settings_mode

from src.ui_layout import MyWindow_layout, CustomListWidgetItem

from src.themes import _QT_DARK, _QT_LIGHT
from src.constants import test_code, item_info_template
from src.paths import PROJECT_ROOT, CONFIG_PATH, CHAT_HISTORY_PATH, CHAT_TEMPLATE_PATH

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QuestAIResponse(QThread):
    """
    AI 响应线程，处理流式 API 调用
    """
    data_fetched = pyqtSignal(object)

    def __init__(self, messages_history, AI_sever_config):
        super().__init__()
        self.messages_history = messages_history
        self.AIchat = DeepSeekChat(AI_sever_config)
        self.running = True

    def run(self):
        logger.info(f"Starting AI response thread with {len(self.messages_history)} messages")
        AI_response_data = self.AIchat.chat(
            messages_history=self.messages_history, send_code=test_code
        )

        self.data_fetched.emit(AI_response_data)


class MyWindow_Stream(MyWindow_layout):

    def __init__(self):

        super().__init__()

        self.chat_info_path = CHAT_HISTORY_PATH
        self.config_path = CONFIG_PATH
        self.marked_html_path = CHAT_TEMPLATE_PATH
        self.ensure_chat_info_file()

        # ── 内存缓存 + 线程锁，避免频繁全量读写 JSON ──
        self._chat_cache = None
        self._chat_lock = threading.Lock()
        self._finishing = False  # 防止 finish_stream 重入

        self.load_local_html_file(self.marked_html_path)
        self.browser.loadFinished.connect(self._apply_theme_from_config)

        self.response_string = ""
        self.input_content = ""
        self.streaming = False

        self.cut_text = lambda text: text[:10] + "..." if len(text) > 9 else text

        self.btn_send.clicked.connect(self.send_content)
        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.btn_send.setEnabled(False)

        self.input_main.textChanged.connect(self.checkLineEditState)

        self.list_item_init()

        self.list_widget.itemClicked.connect(self.list_item_click)
        self.list_widget.customContextMenuRequested.connect(self.show_rightMouse_menu)

        self.btn_new_chat.clicked.connect(self.setNew_chat)

        self.setNew_chat()
        self.AI_sever_config = self.init_config()
        self.stream = None
        self.pending_chunks = []
        self.thinking_active = False
        self.stream_done = False
        self.chunk_batch_size = 6

    def init_config(self):
        """
        初始化 API 配置
        
        Returns:
            list: API 配置列表
        """
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {self.config_path}")
            QMessageBox.warning(
                self, 
                "配置文件缺失", 
                f"未找到配置文件，请先配置API信息。\n\n文件路径: {self.config_path}"
            )
            self.settings()
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Config file JSON decode error: {e}")
            QMessageBox.critical(
                self, 
                "配置文件错误", 
                f"配置文件格式错误，请检查 JSON 格式。\n\n错误信息: {str(e)}"
            )
            self.settings()
            return []
        except Exception as e:
            logger.error(f"Unexpected error loading config: {e}")
            QMessageBox.critical(self, "错误", f"加载配置时发生错误: {str(e)}")
            return []

        item_data = [
            item
            for item in data.get("items", [])
            if item["name"] == data.get("select", {}).get("default")
        ]
        
        if not item_data:
            logger.warning("No matching API config found")
            QMessageBox.information(
                self, 
                "配置缺失", 
                "未找到默认的API配置，请先添加API配置。"
            )
            self.settings()
            return []
            
        logger.info(f"Loaded API config: {item_data[0]['name']}")
        return item_data

    def _apply_theme_from_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            theme = data.get("theme", "dark")
            font_size = data.get("font_size", "medium")
        except (FileNotFoundError, json.JSONDecodeError):
            theme = "dark"
            font_size = "medium"
        self._apply_qt_theme(theme)
        self._post_message("set_theme", {"theme": theme})
        self._post_message("set_font_size", {"size": font_size})

    def _apply_qt_theme(self, theme: str):
        qss = _QT_DARK if theme == "dark" else _QT_LIGHT
        QApplication.instance().setStyleSheet(qss)

    def setNew_chat(self):
        """
        Create a new chat and add it to the list.
        The new chat will have a unique id and the current time.
        If a new chat already exists, select it.
        """
        if "New Chat" not in [
            self.list_widget.item(i).text() for i in range(self.list_widget.count())
        ]:

            # clear the chat on the page
            self._post_message("clear")

            json_data = self.json_read()

            # create a new chat item with the current time
            time_id = str(int(time.time() * 1000))
            new_data = deepcopy(item_info_template)
            new_data[0]["chat_id"] = f"{time_id}"
            new_data[0]["timestamp"] = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.localtime()
            )
            json_data["item"].extend(new_data)

            # add the new item to the list_widget
            item_new = CustomListWidgetItem("New Chat", time_id)
            self.list_widget.insertItem(0, item_new)
            self.list_widget.setCurrentItem(item_new)

            # write the json data back to the file (原子写入 + 更新缓存)
            self._atomic_write_json(self.chat_info_path, json_data)
        else:
            # select the new item if it already exists
            self.list_widget.setCurrentItem(
                [
                    self.list_widget.item(i)
                    for i in range(self.list_widget.count())
                    if self.list_widget.item(i).text() == "New Chat"
                ][0]
            )
            self._post_message("clear")

    def send_content(self):
        # ── Stop mode: abort streaming ──
        if self.streaming:
            self.stop_stream()
            return

        if not self.CheckSelectedItem():
            QMessageBox.information(self, "提示", "select a chat")
            return

        if not self.AI_sever_config or any(
            value in (None, "", [], {}, (), set())
            for value in self.AI_sever_config[0].values()
        ):
            QMessageBox.information(self, "提示", "请补充AI配置")
            return
            
        self.input_content = self.input_main.text()
        if self.input_content.strip() == "":
            return

        # 显示用户消息
        self.type_text(self.input_content)
        self.input_main.setText("")

        # 构建完整的对话历史
        messages_history = self._build_messages_history()
        logger.info(f"Built messages history with {len(messages_history)} messages")

        # 更新 UI 状态
        self.streaming = True
        self.btn_send.setText("⏹ Stop")
        self.input_main.setReadOnly(True)
        self.list_widget.setEnabled(False)

        # 启动 AI 响应线程
        self.QuestAIResponse = QuestAIResponse(
            messages_history=messages_history, AI_sever_config=self.AI_sever_config
        )
        self.QuestAIResponse.data_fetched.connect(self.AI_response)
        self.QuestAIResponse.start()

    def stop_stream(self):
        if self.stream is not None:
            try:
                self.stream.close()
            except Exception:
                pass
        self.stream = None
        self.timer.stop()
        self.finish_stream()

    def CheckSelectedItem(self) -> bool:
        if self.list_widget.currentItem() is None:
            return False
        else:
            return True

    def _build_messages_history(self) -> list:
        """
        构建完整的对话历史，包含 system prompt 和所有历史消息
        
        Returns:
            list: 格式化的消息历史列表
        """
        # 添加 system prompt
        messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        
        # 获取当前选中的会话
        current_item = self.list_widget.currentItem()
        if current_item is None:
            return messages
            
        # 读取聊天历史
        data = self.json_read()
        selected_item_info = next(
            (
                item
                for item in data["item"]
                if item["chat_id"] == current_item.item_id
            ),
            None,
        )
        
        if selected_item_info is None:
            logger.warning("No chat info found for current item")
            return messages
            
        # 添加历史消息
        for msg in selected_item_info.get("messages", []):
            if msg["role"] == "user":
                messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                messages.append({"role": "assistant", "content": msg["content"]})
                
        # 添加当前用户输入
        messages.append({"role": "user", "content": self.input_content})
        
        logger.info(f"Built message history with {len(messages)} messages")
        return messages

    def list_item_click(self, item):
        # update item
        # self.list_widget.clear()
        # self.list_item_init()
        self.Reload_chat(item)

    # json file read
    def json_read(self) -> dict:
        """
        读取聊天历史 JSON 文件（带内存缓存）
        首次调用从磁盘加载，后续直接返回缓存。
        写操作会同步更新缓存。

        Returns:
            dict: 聊天历史数据
        """
        if self._chat_cache is not None:
            return self._chat_cache
        try:
            with open(self.chat_info_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._chat_cache = data
            return data
        except FileNotFoundError:
            logger.warning(f"Chat history file not found, creating new one")
            self.ensure_chat_info_file()
            self._chat_cache = {"item": []}
            return self._chat_cache
        except json.JSONDecodeError as e:
            logger.error(f"Chat history JSON decode error: {e}")
            QMessageBox.critical(
                self,
                "聊天记录错误",
                f"聊天记录文件格式错误。\n\n错误信息: {str(e)}"
            )
            self._chat_cache = {"item": []}
            return self._chat_cache
        except Exception as e:
            logger.error(f"Error reading chat history: {e}")
            QMessageBox.critical(self, "错误", f"读取聊天记录时发生错误: {str(e)}")
            self._chat_cache = {"item": []}
            return self._chat_cache

    def _atomic_write_json(self, path: str, data: dict) -> None:
        """
        原子写入 JSON：先写临时文件，再 rename，避免写一半崩溃导致数据损坏。
        同时更新内存缓存（如果是聊天历史文件）。
        """
        with self._chat_lock:
            # 写临时文件再 rename，保证原子性
            dir_name = os.path.dirname(path)
            fd, tmp_path = tempfile.mkstemp(
                dir=dir_name, suffix=".tmp", prefix=".chat_"
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                os.replace(tmp_path, path)
            except Exception:
                # 清理临时文件
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise

            # 同步更新内存缓存
            if path == self.chat_info_path:
                self._chat_cache = deepcopy(data)

    def Reload_chat(self, item) -> None:
        self._post_message("clear")

        # this is for test
        current_Qtwigetlist_item = self.list_widget.currentItem()

        data = self.json_read()

        selected_item_info = next(
            (
                item
                for item in data["item"]
                if item["chat_id"] == current_Qtwigetlist_item.item_id
            ),
            None,
        )

        if selected_item_info is None:
            pass

        else:
            # decode msg
            for obj in selected_item_info["messages"]:
                if obj["role"] == "user":
                    content = obj["content"].replace("\n", "\\n")
                    content = html.escape(content, quote=True)
                    self._post_message("user_msg", {"content": content})

                elif obj["role"] == "assistant":
                    content = obj["content"]
                    self._post_message("reload_ai", {"content": content})
            self.title_Chat.setText(selected_item_info["title"])

        self._post_message("add_copy_btn")

    # add user send and AI response to json file
    def json_write_Chat(self) -> None:
        """
        将用户消息和 AI 响应保存到 JSON 文件
        """
        try:
            # extract current selectedItems from list_widget
            current_item = self.list_widget.currentItem()
            if current_item is None:
                logger.error("No item selected when trying to save chat")
                return
                
            data = self.json_read()

            selected_item = next(
                (item for item in data["item"] if item["chat_id"] == current_item.item_id),
                None,
            )

            if selected_item is None:
                logger.error(f"Chat item not found: {current_item.item_id}")
                QMessageBox.information(self, "错误", "未找到当前选中的聊天记录")
                return

            if (
                selected_item["title"].strip() == "New Chat"
                or selected_item["title"].strip() == ""
            ):
                new_title = self.cut_text(self.input_content.strip())
                current_item.setText(new_title)
                selected_item["title"] = self.input_content.strip()
                logger.info(f"Updated chat title to: {new_title}")

            plus_MSG = [
                {
                    "role": "user",
                    "content": self.input_content,
                },
                {
                    "role": "assistant",
                    "content": self.response_string,
                },
            ]
            selected_item["messages"].extend(plus_MSG)

            self._atomic_write_json(self.chat_info_path, data)

            logger.info(f"Saved chat history, total messages: {len(selected_item['messages'])}")
            
            # clear the response string and input string
            self.response_string = ""
            self.input_content = ""
            
        except Exception as e:
            logger.error(f"Error saving chat history: {e}")
            QMessageBox.critical(self, "错误", f"保存聊天记录时发生错误: {str(e)}")

    def list_item_init(self) -> None:

        item = self.json_read()["item"]
        # cut text 5 characters

        for i in range(len(item) - 1, -1, -1):

            self.list_widget.addItem(
                CustomListWidgetItem(
                    self.cut_text(
                        item[i]["title"]
                        if item[i]["title"].strip() != ""
                        else "New Chat"
                    ),
                    item[i]["chat_id"],
                )
            )

    def show_rightMouse_menu(self, pos) -> None:
        item = self.list_widget.itemAt(pos)
        if not item:
            return

        menu = QMenu()

        export_action = menu.addAction("rename")
        delete_action = menu.addAction("delete")
        # 呼出位置
        action = menu.exec_(self.list_widget.mapToGlobal(pos))

        if action == delete_action:
            self.list_widget.takeItem(self.list_widget.row(item))

            self.item_delete(item.item_id)
        elif action == export_action:
            text, ok = QInputDialog.getText(None, "输入弹窗", "请输入文本:")
            if ok:
                item.name = text
                item.setText(text)

                data = self.json_read()
                for i in range(len(data["item"])):
                    if data["item"][i]["chat_id"] == item.item_id:
                        data["item"][i]["title"] = text

                self._atomic_write_json(self.chat_info_path, data)

    def item_delete(self, item_id) -> None:
        data = self.json_read()
        item = next(
            (item for item in data["item"] if item["chat_id"] == item_id),
            None,
        )
        if item is None:
            return
        data["item"].remove(item)
        self._atomic_write_json(self.chat_info_path, data)

    # add user send text to html

    # accept AI response from js
    def AI_response(self, answer) -> None:
        if type(answer) == str:
            self.streaming = False
            QMessageBox.information(self, "错误", answer)
            self.btn_send.setText("Send")
            self.btn_send.setEnabled(False)
            self.list_widget.setEnabled(True)
            self.input_main.setReadOnly(False)
            self.input_main.setFocus()
            return
        self.stream = answer
        self.stream_done = False
        self.pending_chunks = []

        # timer容易出现断连,触发错误
        try:
            self.timer.timeout.disconnect(self.run_js)
        except TypeError:
            pass
        self.timer.timeout.connect(self.run_js)
        self.timer.start()

    # type each token of AI response to html
    def run_js(self) -> None:
        """
        处理流式响应的每个 chunk
        reasoning_content 只用于显示思考动画，不写入 response_string
        """
        if self.stream is None:
            self.finish_stream()
            return

        try:
            for _ in range(self.chunk_batch_size):
                chunk = next(self.stream)
                delta = chunk.choices[0].delta
                content = delta.content
                reasoning = getattr(delta, 'reasoning_content', None)

                if reasoning is not None:
                    # 思考内容只触发动画，不保存为正式回复
                    if not self.thinking_active:
                        self.thinking_active = True
                        self._post_message("thinking")
                        logger.debug("Thinking indicator activated")
                elif content is not None:
                    self.thinking_active = False
                    self.pending_chunks.append(content)
                    self.response_string += content
        except StopIteration:
            logger.info("Stream completed (StopIteration)")
            self.stream_done = True
        except TypeError as e:
            logger.warning(f"Stream TypeError: {e}")
            self.stream_done = True
        except Exception as e:
            logger.error(f"Stream error: {e}")
            self.stream_done = True
            self.response_string += f"\n\n[Stream error: {e}]"

        if self.pending_chunks:
            merged_content = "".join(self.pending_chunks)
            self.pending_chunks = []
            self._post_message("ai_stream", {"text": merged_content, "done": 0})

        if self.stream_done:
            self.finish_stream()

    def finish_stream(self) -> None:
        # 防止重入：stop_stream 和 run_js 可能同时触发
        if self._finishing:
            return
        self._finishing = True

        self.timer.stop()
        try:
            self.timer.timeout.disconnect(self.run_js)
        except TypeError:
            pass
        self.thinking_active = False
        was_streaming = self.streaming
        self._post_message("ai_stream", {"text": "", "done": 1})
        self._post_message("add_copy_btn")
        self.stream = None
        self.pending_chunks = []
        self.stream_done = False
        self.streaming = False
        if was_streaming and self.response_string:
            self.json_write_Chat()
        self.list_widget.setEnabled(True)
        self.input_main.setReadOnly(False)
        self.input_main.setFocus()
        self.btn_send.setText("Send")
        self.btn_send.setEnabled(False)

        self._finishing = False

    def type_text(self, input_content):
        content = input_content.replace("\n", "\\n")
        content = html.escape(content, quote=True)
        self._post_message("user_msg", {"content": content})

    def _post_message(self, msg_type: str, payload=None):
        """统一发送消息到 JS postMessage 分发器"""
        code = json.dumps({"type": msg_type, "payload": payload}, ensure_ascii=False)
        self.browser.page().runJavaScript(f"postMessage({code})")

    def load_local_html_file(self, file_path):
        self.browser.setUrl(QUrl.fromLocalFile(file_path))

    def ensure_chat_info_file(self) -> None:
        if os.path.exists(self.chat_info_path):
            return
        self._atomic_write_json(self.chat_info_path, {"item": []})

    #
    def settings(self):
        """show setting dialog and save changes to config.json"""

        settings = Settings_mode()
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        setExt = settings.exec_()
        if setExt == Settings_mode.Accepted:
            info = settings.get_input()
            theme = info.pop("theme", "dark")
            font_size = info.pop("font_size", "medium")

            # ── always apply theme/font ──
            data["theme"] = theme
            data["font_size"] = font_size

            # ── API config: only validate if user filled in the name field ──
            if info.get("name", "").strip():
                if any(
                    value in (None, "", [], {}, (), set())
                    for value in info.values()
                ):
                    QMessageBox.warning(self, "Warning", "Please fill in all API fields")
                    return  # 不再递归调用，避免栈溢出
                if info["name"] in [
                    item["name"] for item in data["items"]
                ]:
                    data["select"]["default"] = info["name"]
                else:
                    data["items"].append(info)
                    data["select"]["default"] = info["name"]

            self._atomic_write_json(self.config_path, data)
            self._apply_qt_theme(theme)
            self._post_message("set_theme", {"theme": theme})
            self._post_message("set_font_size", {"size": font_size})
        elif setExt == Settings_mode.Rejected:
            pass

    def checkLineEditState(self):
        if self.streaming:
            return
        if self.input_main.text().strip() == "":
            self.btn_send.setEnabled(False)
        else:
            self.btn_send.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MW = MyWindow_Stream()
    MW.show()

    app.exec_()
