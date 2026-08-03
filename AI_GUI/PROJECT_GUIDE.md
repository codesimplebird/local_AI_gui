# AI Chat GUI — 项目技术指南

> 本文档面向 **AI 编码助手** 和 **首次接触本项目的开发者**。
> 目标：无需阅读全部源码即可理解项目结构、数据流、关键设计点和修改入口。
> 所有引用均附带源码行号，可在 IDE 中 Ctrl+Click 跳转。

---

## 目录

1. [项目一句话概述](#1-项目一句话概述)
2. [阅读路线图](#2-阅读路线图)
3. [完整文件结构](#3-完整文件结构)
4. [架构总览](#4-架构总览)
5. [核心数据流 — 从输入到渲染](#5-核心数据流--从输入到渲染)
6. [逐文件详解](#6-逐文件详解)
7. [前后端通信协议（`_post_message` 消息表）](#7-前后端通信协议_post_message-消息表)
8. [JSON 数据格式](#8-json-数据格式)
9. [状态变量字典](#9-状态变量字典)
10. [关键设计决策与陷阱](#10-关键设计决策与陷阱)
11. [扩展 / 修改指引](#11-扩展--修改指引)

---

## 1. 项目一句话概述

基于 **PyQt5 + QWebEngineView** 的本地 AI 聊天桌面应用。Qt Widgets 负责侧边栏/输入/设置，QWebEngineView 内嵌 HTML 页面负责消息渲染（marked.js + highlight.js），通过 OpenAI Python SDK 以流式方式调用兼容 API（DeepSeek / X.AI / 通义千问 / LM Studio），JSON 文件持久化聊天历史和配置。

---

## 2. 阅读路线图

| 时间预算 | 阅读顺序 | 关注点 |
|----------|----------|--------|
| **10 分钟** | [main_window.py](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L722-L727) → 入口 → [__init__](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L76-L119) → [send_content](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L232-L272) → [run_js](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L581-L624) | 入口、信号槽连接、一次发送的完整链路 |
| **30 分钟** | 加上 [api_client.py](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/api_client.py) → [ui_layout.py](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/ui_layout.py) → [chat_template.html](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L389-L426)（`postMessage` 函数） | API 调用、UI 构建、前后端消息协议 |
| **2 小时** | 全部 src/ 文件 + [constants.py](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/constants.py) + [paths.py](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/paths.py) + [settings_dialog.py](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/settings_dialog.py) + [themes.py](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/themes.py) | 配置、路径、主题、设置对话框、数据持久化细节 |
| **半天** | 加上 [tests/](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/tests/) + [chat_template.html](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html) 全文 CSS/JS | 测试覆盖、前端渲染细节、CSS 变量体系 |

---

## 3. 完整文件结构

```
AI_GUI/
├── src/                              # Python 后端源码
│   ├── __init__.py                   # 包标识（空文件）
│   ├── main_window.py                # ★ 核心：主窗口、流式处理、会话管理、JSON 持久化
│   ├── ui_layout.py                  # ★ Qt 布局定义：侧边栏、输入框、浏览器、按钮
│   ├── api_client.py                 # ★ OpenAI SDK 封装：流式请求 + 错误处理
│   ├── settings_dialog.py            # 设置对话框（主题 + API 配置 Tab）
│   ├── themes.py                     # Qt QSS 样式：_QT_DARK / _QT_LIGHT 两个主题字符串
│   ├── constants.py                  # 全局常量：send_code、新会话模板
│   └── paths.py                      # 统一路径管理：PROJECT_ROOT / CONFIG_PATH 等
├── assets/                           # 静态资源
│   ├── icon/                         # 应用图标（copilot_icon4.png / settings.png 等）
│   └── chat_template.html            # ★ 前端页面：Markdown 渲染 + 流式显示 + 主题
├── data/
│   ├── config.example.json           # API 配置模板（纳入版本控制）
│   ├── config.json                   # 实际配置（不纳入版本控制，运行时生成）
│   └── chat_history.json             # 聊天历史（不纳入版本控制，运行时生成）
├── node_modules/                     # 前端依赖（marked / highlight.js / clipboard）
│   ├── marked/marked.min.js
│   ├── highlight.min.js
│   ├── clipboard.min.js
│   └── styles/atom-one-dark.css
├── tests/                            # pytest 单元测试
│   ├── __init__.py
│   ├── test_api_client.py            # API 客户端测试（mock OpenAI SDK）
│   ├── test_messages_history.py      # 消息历史构建逻辑测试
│   └── test_json_operations.py       # JSON 读写测试
├── docs/
│   └── architecture.xmind            # 架构设计思维导图
├── requirements.txt                  # Python 依赖：PyQt5 / PyQtWebEngine / openai
├── requirements-test.txt             # 测试依赖
├── package.json                      # 前端依赖声明（marked / highlight.js / clipboard）
├── pytest.ini                        # pytest 配置
└── README.md                         # 用户手册（安装、配置、运行）
```

> ★ 标记为核心文件，建议优先阅读。

---

## 4. 架构总览

```
┌──────────────────────────────────────────────────────────────────┐
│                        MyWindow_Stream                            │
│                     (main_window.py:74)                           │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    MyWindow_layout                         │  │
│  │                    (ui_layout.py:29)                       │  │
│  │  ┌──────────────┐  ┌────────────────────────────────────┐  │  │
│  │  │  QListWidget  │  │      QWebEngineView (browser)      │  │  │
│  │  │  (侧边栏会话)  │  │   ← load chat_template.html        │  │  │
│  │  │              │  │   marked.js + highlight.js          │  │  │
│  │  └──────────────┘  │   + clipboard.js                    │  │  │
│  │                    └────────────────────────────────────┘  │  │
│  │  [input_main]  [btn_send]  [settings_btn]  [btn_new_chat]   │  │
│  └────────────────────────────────────────────────────────────┘  │
│         │                ▲                      │                │
│         │ signal/slot    │ runJavaScript()      │ click          │
│         ▼                │ postMessage()        ▼                │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐    │
│  │  QTimer     │  │ QuestAIResponse│  │ Settings_mode        │    │
│  │  (50ms tick)│  │   (QThread)    │  │ (settings_dialog.py) │    │
│  │  → run_js() │  │   → DeepSeekChat│  └──────────────────────┘    │
│  └──────┬──────┘  └───────┬────────┘                            │
│         │ batch chunks    │ data_fetched signal                  │
│         │                 ▼                                      │
│         │         ┌──────────────┐                               │
│         └─────────│ stream iter  │◄── OpenAI SDK (stream=True)    │
│                   │ (pending)    │    API Server (DeepSeek etc.)  │
│                   └──────────────┘                               │
│                                                                  │
│  json_read() / _atomic_write_json()  ←→  data/chat_history.json │
│  init_config() / settings()          ←→  data/config.json        │
└──────────────────────────────────────────────────────────────────┘
```

### 类继承关系

```
QWidget
  └── MyWindow_layout (ui_layout.py:29)          # 纯 UI 布局，无业务逻辑
        └── MyWindow_Stream (main_window.py:74)  # 业务逻辑：流式处理、会话管理
              ├── QuestAIResponse (main_window.py:53)  # QThread 内部类
              └── 使用 DeepSeekChat (api_client.py:13)

QDialog
  └── Settings_mode (settings_dialog.py:23)      # 设置对话框

QListWidgetItem
  └── CustomListWidgetItem (ui_layout.py:22)     # 侧边栏项，携带 item_id
```

### 关键对象在 `__init__` 中创建的顺序

[main_window.py:76-119](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L76-L119)：

1. 调用父类 `MyWindow_layout.__init__()` → 创建所有 Qt 控件
2. 设置路径常量 → `ensure_chat_info_file()` 确保历史文件存在
3. 初始化缓存/锁：`_chat_cache`, `_chat_lock`, `_finishing`
4. `load_local_html_file()` 加载 chat_template.html 到 browser
5. `browser.loadFinished` 连接 `_apply_theme_from_config`（页面加载完后应用主题）
6. 初始化流式状态变量：`response_string`, `input_content`, `streaming`
7. 信号槽连接：`btn_send.clicked` → `send_content`，QTimer 50ms
8. `input_main.textChanged` → `checkLineEditState`（控制发送按钮可用状态）
9. `list_item_init()` 从 JSON 加载已有会话到侧边栏
10. 侧边栏信号：`itemClicked` → `list_item_click`，右键菜单 → `show_rightMouse_menu`
11. `btn_new_chat.clicked` → `setNew_chat`
12. **自动创建一个 New Chat**：`self.setNew_chat()`
13. 加载 API 配置：`self.AI_sever_config = self.init_config()`
14. 初始化剩余流式状态：`stream`, `pending_chunks`, `thinking_active`, `stream_done`, `chunk_batch_size=6`

---

## 5. 核心数据流 — 从输入到渲染

### 5.1 发送消息完整链路

```
用户输入 → 按 Enter / 点 Send
    │
    ▼
[btn_send.clicked] → send_content()                    [main_window.py:232]
    │
    ├─ if streaming: stop_stream()  (点 Stop 按钮)
    ├─ 检查：选中会话？API 配置完整？输入非空？
    ├─ type_text() → _post_message("user_msg") → JS 渲染用户消息
    ├─ input_main 清空
    ├─ _build_messages_history()                       [main_window.py:290]
    │     ├─ 先加 system prompt
    │     ├─ 从 JSON 缓存读取当前会话的历史消息
    │     └─ 追加本次用户输入
    ├─ UI 状态更新：streaming=True, 按钮变 Stop, 输入框只读, 侧边栏禁用
    └─ 创建 QuestAIResponse(QThread) → start()
          │
          ▼
    QuestAIResponse.run()                              [main_window.py:65]
          │
          └─ DeepSeekChat.chat() → OpenAI SDK stream   [api_client.py:22]
                │ (在子线程中阻塞等待 API 响应)
                ▼
          data_fetched.emit(stream_or_error_str)
          │
          ▼ (Qt 信号自动回到主线程)
    AI_response(answer)                                [main_window.py:558]
          │
          ├─ 如果 answer 是 str → 错误弹窗，恢复 UI
          └─ 如果 answer 是 stream iterator →
               self.stream = answer
               QTimer.start(50ms) → 每 tick 调 run_js()
                    │
                    ▼
              run_js() (每 50ms 调用)                   [main_window.py:581]
                    │
                    ├─ for _ in range(6): 每次批量消费 6 个 chunk
                    │     chunk = next(self.stream)
                    │     ├─ reasoning_content → 只触发 thinking 动画
                    │     └─ content → 加入 pending_chunks + response_string
                    ├─ pending_chunks 合并 → _post_message("ai_stream", ...)
                    └─ StopIteration → stream_done=True → finish_stream()
                    │
                    ▼
              JS: postMessage() → receive_text()        [chat_template.html:306]
                    │
                    ├─ 节流渲染（120ms 间隔）
                    ├─ marked.parse() → HTML
                    └─ bubble.innerHTML = 渲染结果
                    │
                    ▼
              finish_stream()                           [main_window.py:626]
                    ├─ _finishing 重入保护
                    ├─ timer.stop(), 断开信号
                    ├─ _post_message("ai_stream", done=1) → JS 最终渲染+代码高亮
                    ├─ _post_message("add_copy_btn")
                    ├─ json_write_Chat() → 原子写入 JSON + 更新缓存
                    └─ 恢复 UI 状态：按钮 Send, 输入框可写, 侧边栏启用
```

### 5.2 切换会话链路

```
点击侧边栏项 → list_item_click(item)                   [main_window.py:335]
    │
    ▼
Reload_chat(item)                                      [main_window.py:405]
    ├─ _post_message("clear") → JS 清空页面
    ├─ json_read() → 从缓存读取数据
    ├─ 找到对应 chat_id 的会话
    ├─ 遍历 messages:
    │     user 消息 → html.escape + 换行转义 → _post_message("user_msg")
    │     assistant 消息 → 直接 Markdown → _post_message("reload_ai")
    ├─ title_Chat 显示会话标题
    └─ _post_message("add_copy_btn")
```

### 5.3 新建会话链路

```
点 New Chat 按钮 → setNew_chat()                       [main_window.py:190]
    │
    ├─ 如果已有 "New Chat" 项 → 直接选中它 + 清空页面
    └─ 否则：
         ├─ _post_message("clear")
         ├─ json_read() 读取当前缓存
         ├─ 生成毫秒时间戳 time_id 作为 chat_id
         ├─ deepcopy(item_info_template) 创建新会话模板
         ├─ 插入 list_widget 第 0 位并选中
         └─ _atomic_write_json() 原子写入 + 更新缓存
```

---

## 6. 逐文件详解

### 6.1 [src/paths.py](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/paths.py) — 路径常量

**职责**：集中管理所有文件路径，避免硬编码。

| 常量 | 值 | 说明 |
|------|-----|------|
| `PROJECT_ROOT` | `AI_GUI/` 目录的绝对路径 | 基于 `__file__` 向上两级推导 |
| `ASSETS_DIR` | `PROJECT_ROOT/assets` | 静态资源目录 |
| `DATA_DIR` | `PROJECT_ROOT/data` | 数据目录 |
| `ICON_DIR` | `ASSETS_DIR/icon` | 图标目录 |
| `CONFIG_PATH` | `DATA_DIR/config.json` | API 配置文件 |
| `CHAT_HISTORY_PATH` | `DATA_DIR/chat_history.json` | 聊天历史文件 |
| `CHAT_TEMPLATE_PATH` | `ASSETS_DIR/chat_template.html` | 前端 HTML |

| 函数 | 行号 | 说明 |
|------|------|------|
| `icon_path(filename)` | [L16-L17](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/paths.py#L16-L17) | 返回图标文件的完整路径 |

> **注意**：`PROJECT_ROOT` 是通过 `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` 推导的，即 `src/` 的上一级。如果移动 `src/` 目录位置需同步修改。

---

### 6.2 [src/constants.py](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/constants.py) — 全局常量

| 常量 | 行号 | 值/类型 | 说明 |
|------|------|---------|------|
| `test_code` | [L2](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/constants.py#L2) | `1` | **命名遗留问题**：实际是生产用的 send_code（1=流式请求），不是测试代码。`QuestAIResponse.run()` 将其传给 `DeepSeekChat.chat()` |
| `item_info_template` | [L4-L17](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/constants.py#L4-L17) | `list[dict]` | 新会话模板。`setNew_chat()` 用 `deepcopy` 复制后修改 `chat_id`/`timestamp` |

`item_info_template` 结构：
```python
[{
    "chat_id": "1234567890",       # 会被毫秒时间戳替换
    "user_id": "user123",          # 当前未使用
    "title": "New Chat",           # 首条消息后自动改名
    "timestamp": "2023-10-01T...", # 会被当前时间替换
    "messages": [],                # 消息列表，追加 {role, content}
    "metadata": { ... }            # 平台/语言/UA，当前仅存储未使用
}]
```

---

### 6.3 [src/themes.py](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/themes.py) — Qt 样式

| 变量 | 行号 | 说明 |
|------|------|------|
| `_QT_DARK` | [L1-L160](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/themes.py#L1-L160) | 暗色主题 QSS，GitHub Dark 风格配色（#0d1117 背景 / #00d4ff 强调色） |
| `_QT_LIGHT` | [L162-L321](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/themes.py#L162-L321) | 亮色主题 QSS，GitHub Light 风格配色（#ffffff 背景 / #0969da 强调色） |

应用方式：`QApplication.instance().setStyleSheet(qss)` — 全局应用，影响所有子控件。

**QSS 通过 objectName 选择器定制特定控件**：
- `#sendButton` / `#sendButton:enabled` / `#sendButton:disabled` — 发送按钮
- `#newChatButton` — 新建聊天按钮
- `#settingsButton` — 设置按钮（透明无边框）
- `#chatTitle` — 聊天标题 Label
- `#chatHistoryLabel` — "Chat history" 标签
- `#inputField` — 输入框
- `#chatList` — 会话列表

---

### 6.4 [src/ui_layout.py](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/ui_layout.py) — UI 布局

**职责**：纯 UI 构建，不包含业务逻辑。`MyWindow_layout` 是父类，`MyWindow_Stream` 继承后添加业务逻辑。

#### CustomListWidgetItem — [L22-L26](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/ui_layout.py#L22-L26)

```python
class CustomListWidgetItem(QListWidgetItem):
    def __init__(self, name, item_id):
        self.item_id = item_id   # 对应 JSON 中的 chat_id，关键关联字段
        self.name = name         # 显示名称（可被重命名修改）
```

> `item_id` 是连接 Qt 列表项和 JSON 数据的桥梁。`list_item_click`、`json_write_Chat`、`item_delete` 等都通过 `currentItem.item_id` 查找对应会话。

#### MyWindow_layout — [L29-L137](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/ui_layout.py#L29-L137)

创建的控件实例变量（子类通过 `self.xxx` 访问）：

| 变量名 | 类型 | objectName | 说明 |
|--------|------|------------|------|
| `self.input_main` | QLineEdit | `inputField` | 消息输入框，固定高度 30px |
| `self.btn_send` | QPushButton | `sendButton` | 发送/停止按钮，固定 100×30 |
| `self.settings_btn` | QPushButton | `settingsButton` | 齿轮图标按钮，flat=True |
| `self.browser` | QWebEngineView | — | 内嵌浏览器，加载 chat_template.html |
| `self.title_Chat` | QLabel | `chatTitle` | 当前会话标题，居中显示 |
| `self.list_widget` | QListWidget | `chatList` | 会话列表，固定宽 200px，自定义右键菜单 |
| `self.btn_new_chat` | QPushButton | `newChatButton` | 新建聊天按钮，150×50，粗体 |

布局结构：
```
QVBoxLayout (layout_out)
├── QHBoxLayout (up_layout, stretch=1)
│   ├── QVBoxLayout (left_layout)
│   │   ├── btn_new_chat
│   │   ├── note_chat ("Chat history" 标签)
│   │   └── list_widget
│   └── QVBoxLayout (right_up_layout)
│       ├── title_Chat
│       └── browser
├── QHBoxLayout (layout_in_input)
│   ├── note_input ("输入内容:")
│   └── input_main
└── QHBoxLayout (down_layout)
    ├── settings_btn (左对齐)
    └── btn_send (左对齐)
```

快捷键：`Enter` 键触发 `btn_send.click`（[L60-L61](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/ui_layout.py#L60-L61)）。

`self.settings()` 在父类中定义为空方法（[L135-L136](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/ui_layout.py#L135-L136)），子类覆盖实现。

---

### 6.5 [src/api_client.py](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/api_client.py) — API 客户端

#### DeepSeekChat — [L13-L74](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/api_client.py#L13-L74)

**注意**：类名虽叫 `DeepSeekChat`，但实际通过 `base_url` 参数支持所有 OpenAI 兼容接口（DeepSeek / X.AI / 通义千问 / LM Studio 等）。

```python
class DeepSeekChat:
    def __init__(self, AI_sever_config):
        config = AI_sever_config[0]           # 取列表第一个（当前选中的配置）
        self.client = OpenAI(
            api_key=config["api_key"],
            base_url=config.get("base_url", "https://api.deepseek.com"),
        )
        self.model = config.get("model", "deepseek-chat")
```

> `AI_sever_config` 是一个 **list**（不是 dict），由 `init_config()` 返回，始终取 `[0]`。这是因为筛选逻辑 `[item for item in ... if ...]` 返回列表。

#### chat() 方法 — [L22-L74](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/api_client.py#L22-L74)

| 参数 | 类型 | 说明 |
|------|------|------|
| `messages_history` | `list[dict]` | 完整消息历史，格式 `[{"role": "system"/"user"/"assistant", "content": "..."}]` |
| `send_code` | `int` | `1`=流式请求（唯一有效值），其他值返回错误字符串 |

**返回值**：
- 成功 → OpenAI Stream 迭代器（可 `next()` 逐个取 chunk）
- 失败 → **错误信息字符串**（以 `"error:"` 开头，中文提示）

**错误处理映射**：

| 异常类型 | 返回消息 |
|----------|----------|
| `AuthenticationError` | "error:API Key 无效或已过期..." |
| `RateLimitError` | "error:API 请求频率超限..." |
| `APIConnectionError` | "error:无法连接到 API 服务器..." |
| `APIStatusError` | "error:API 返回错误 (状态码 {e.status_code})" |
| 其他 Exception | "error:{类型名}: {消息}" |

**调用参数**：`temperature=0.7`, `stream=True`, `timeout=30`

> **重要**：此方法在 QThread 子线程中执行（`QuestAIResponse.run()`），网络IO阻塞不会卡住UI。返回的 stream 迭代器在主线程通过 QTimer 消费。

---

### 6.6 [src/settings_dialog.py](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/settings_dialog.py) — 设置对话框

#### Settings_mode — [L23-L137](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/settings_dialog.py#L23-L137)

基于 QDialog 的模态对话框，包含两个 Tab：

**Tab 1: Theme**（[L37-L57](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/settings_dialog.py#L37-L57)）
- `combo_theme`: dark / light 下拉框
- `combo_font`: small / medium / large 下拉框

**Tab 2: API**（[L60-L90](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/settings_dialog.py#L60-L90)）
- `combo_box`: 选择已有配置或 "-- New --" 创建新配置
- `input_name` / `input_model` / `input_key` / `input_url`: 四个 QLineEdit

**关键行为**：
- 构造函数直接打开 `CONFIG_PATH` 读取配置（[L33-L34](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/settings_dialog.py#L33-L34)）— 如果文件不存在会抛异常
- `combo_box.currentIndexChanged` 连接 `_on_api_select`（[L111](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/settings_dialog.py#L111)），切换选项时自动填充表单
- `get_input()` 返回 dict，包含 name/model/api_key/base_url/theme/font_size

**注意**：文件底部有一个独立的 `MainWindow` 类（[L140-L156](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/settings_dialog.py#L140-L156)），是开发测试用的入口，不参与主程序运行。

---

### 6.7 [src/main_window.py](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py) — 核心逻辑

这是项目最大、最重要的文件，包含两个类和程序入口。

#### 文件开头特殊处理 — [L4-L19](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L4-L19)

1. **`_LibPNGFilter`**（[L5-L12](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L5-L12)）：过滤 stderr 中的 libpng iCCP 警告（QWebEngineView 加载图片时常见的无关警告），通过替换 `sys.stderr` 实现。
2. **sys.path 修改**（[L17-L19](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L17-L19)）：将项目根目录（`AI_GUI/`）加入 `sys.path`，使得 `from src.xxx import yyy` 在 `cd src/` 目录运行时也能工作。

#### QuestAIResponse(QThread) — [L53-L71](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L53-L71)

| 成员 | 类型 | 说明 |
|------|------|------|
| `data_fetched` | `pyqtSignal(object)` | 信号：API 返回 stream 或错误字符串时发射 |
| `self.messages_history` | list | 构造时传入的消息历史 |
| `self.AIchat` | DeepSeekChat | API 客户端实例，在构造函数创建 |
| `self.running` | bool | 定义了但**未被检查**，stop 功能不依赖此标志 |

`run()` 方法（[L65-L71](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L65-L71)）：
1. 调用 `self.AIchat.chat(messages_history, send_code=test_code)`
2. 通过 `data_fetched.emit()` 将结果发送到主线程

> **已知限制**：此线程无法被安全提前终止。`stop_stream()` 关闭的是 stream 迭代器（在主线程），但 QThread 内的 `chat()` 调用仍在等待 API 响应。由于 OpenAI SDK 的 HTTP 请求无法从外部线程取消，这是一个固有限制。但 stream 关闭后 `run_js` 不再消费数据，用户体验上已经"停止"了。

#### MyWindow_Stream(MyWindow_layout) — [L74-L727](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L74-L727)

核心方法按功能分组：

**初始化与配置**：
| 方法 | 行号 | 说明 |
|------|------|------|
| `__init__()` | [L76-L119](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L76-L119) | 完整初始化，见上文"创建顺序" |
| `init_config()` | [L121-L171](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L121-L171) | 读取 config.json，筛选 `select.default` 对应的 API 配置项，返回 list |
| `_apply_theme_from_config()` | [L173-L184](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L173-L184) | 页面加载完成后读取配置，应用 Qt 主题 + JS 主题 + 字体大小 |
| `_apply_qt_theme()` | [L186-L188](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L186-L188) | 根据 theme 字符串设置全局 QSS |

**会话管理**：
| 方法 | 行号 | 说明 |
|------|------|------|
| `setNew_chat()` | [L190-L230](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L190-L230) | 创建新会话；已有 "New Chat" 则直接选中 |
| `list_item_init()` | [L497-L513](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L497-L513) | 启动时从 JSON 加载已有会话到侧边栏（倒序遍历，最新在前） |
| `list_item_click()` | [L335-L339](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L335-L339) | 点击会话项 → Reload_chat |
| `Reload_chat()` | [L405-L438](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L405-L438) | 重新加载指定会话的所有消息到页面 |
| `show_rightMouse_menu()` | [L515-L542](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L515-L542) | 右键菜单：rename / delete |
| `item_delete()` | [L544-L553](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L544-L553) | 删除指定 chat_id 的会话 |

**消息发送与流式处理**：
| 方法 | 行号 | 说明 |
|------|------|------|
| `send_content()` | [L232-L272](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L232-L272) | 发送按钮回调：校验→渲染用户消息→构建历史→启动线程 |
| `_build_messages_history()` | [L290-L333](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L290-L333) | 构建 system prompt + 历史消息 + 当前输入 |
| `stop_stream()` | [L274-L282](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L274-L282) | 停止流式：关闭 stream 迭代器 + timer + finish_stream |
| `AI_response()` | [L558-L578](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L558-L578) | 线程完成回调：错误弹窗或启动 QTimer 消费 stream |
| `run_js()` | [L581-L624](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L581-L624) | QTimer 回调：批量消费 chunk → 推送 JS → 检测流结束 |
| `finish_stream()` | [L626-L653](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L626-L653) | 流结束清理：停止 timer、最终渲染、保存 JSON、恢复 UI |
| `type_text()` | [L655-L658](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L655-L658) | 转义用户文本并发送到 JS 渲染 |

**数据持久化**：
| 方法 | 行号 | 说明 |
|------|------|------|
| `json_read()` | [L342-L376](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L342-L376) | 读取聊天历史（带内存缓存，首次从磁盘加载） |
| `_atomic_write_json()` | [L378-L403](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L378-L403) | 原子写入：临时文件 + os.replace + 线程锁 + 缓存同步 |
| `json_write_Chat()` | [L441-L495](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L441-L495) | 保存一轮对话（user+assistant），自动更新 "New Chat" 标题 |
| `ensure_chat_info_file()` | [L668-L671](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L668-L671) | 确保聊天历史文件存在 |

**设置与工具**：
| 方法 | 行号 | 说明 |
|------|------|------|
| `settings()` | [L674-L711](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L674-L711) | 打开设置对话框，保存后应用主题/写入配置 |
| `checkLineEditState()` | [L713-L719](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L713-L719) | 输入框内容变化时启用/禁用发送按钮 |
| `_post_message()` | [L660-L663](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L660-L663) | Python→JS 通信桥梁，通过 runJavaScript 调用 |
| `load_local_html_file()` | [L665-L666](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L665-L666) | 加载本地 HTML 文件到 browser |
| `CheckSelectedItem()` | [L284-L288](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L284-L288) | 检查是否选中了会话 |

**程序入口** — [L722-L727](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L722-L727)：
```python
if __name__ == "__main__":
    app = QApplication(sys.argv)
    MW = MyWindow_Stream()
    MW.show()
    app.exec_()
```

---

### 6.8 [assets/chat_template.html](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html) — 前端页面

单文件 HTML，包含 CSS + JS，无外部框架。

#### 外部依赖（[L8-L11](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L8-L11)）

| 脚本/样式 | 来源 | 用途 |
|-----------|------|------|
| `atom-one-dark.css` | highlight.js | 代码块暗色语法高亮 |
| `marked.min.js` | node_modules | Markdown → HTML 解析 |
| `highlight.min.js` | node_modules | 代码语法高亮 |
| `clipboard.min.js` | node_modules | 代码块一键复制 |

> 依赖通过 `npm install` 安装到 `node_modules/`（见 [package.json](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/package.json)）。

#### CSS 变量体系（[L16-L81](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L16-L81)）

通过 `data-theme` 属性切换：
- `:root, [data-theme="dark"]` — 暗色（默认）
- `[data-theme="light"]` — 亮色

关键 CSS 变量：
- `--bg` / `--surface` / `--border` — 背景/面板/边框
- `--ai-accent` / `--user-accent` — AI/用户消息强调色
- `--code-bg` / `--code-color` / `--pre-bg` — 代码块样式
- `--scroll-thumb` — 滚动条颜色

#### DOM 结构
```html
<body>
    <div id="container"></div>      <!-- 消息列表容器 -->
    <div id="scroll_point"></div>   <!-- 滚动锚点（scrollIntoView） -->
    <script>...</script>
</body>
```

消息行动态创建结构：
```html
<div class="msg-row">
    <div class="msg-label ai"><span class="dot"></span>AI</div>
    <div class="msg-bubble ai">渲染后的 HTML 内容</div>
</div>
```

#### 核心 JS 函数

| 函数 | 行号 | 说明 |
|------|------|------|
| `isNearBottom()` | [L252-L256](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L252-L256) | 判断是否滚动到底部 60px 以内 |
| `safeScrollToBottom()` | [L266-L270](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L266-L270) | 用户未上滚时自动滚动到底部（智能滚动） |
| `makeMsgRow(role, label)` | [L272-L281](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L272-L281) | 创建消息行 DOM 并添加到 container |
| `processStreamingText(bubble, text, shouldHighlight)` | [L285-L298](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L285-L298) | marked.parse → innerHTML → 可选代码高亮 |
| `receive_text(text, if_end)` | [L306-L338](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L306-L338) | 流式文本接收：120ms 节流渲染，结束时最终渲染+高亮 |
| `user_text(content)` | [L340-L344](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L340-L344) | 添加用户消息气泡，预创建 AI 气泡 |
| `reload_ai_info(text)` | [L347-L352](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L347-L352) | 历史 AI 消息加载（直接渲染完整内容） |
| `clear_chat()` | [L355-L359](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L355-L359) | 清空所有消息 |
| `addCopyButton()` | [L361-L375](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L361-L375) | 为每个 pre > code 添加 COPY 按钮 |
| `showThinking()` / `hideThinking()` | [L378-L390](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L378-L390) | 思考动画指示器（三个脉冲点） |
| `setTheme(theme)` | [L392-L394](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L392-L394) | 切换 data-theme 属性 |
| `setFontSize(size)` | [L397-L401](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L397-L401) | 设置根字体大小 (small=13px/medium=15px/large=17px) |
| **`postMessage(msg)`** | [L402-L439](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L402-L439) | **消息分发中心**，Python 端 `_post_message()` 的接收方 |

**渲染节流参数**：
- `RENDER_THROTTLE_MS = 120`（[L304](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L304)）— 流式期间最少渲染间隔
- 流式期间光标追加 `'|'` 字符作为打字指示（[L335](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L335)），最终渲染时不带

**智能滚动逻辑**（[L249-L270](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L249-L270)）：
- `window.scroll` 事件检测用户是否上滚
- 阈值 `SCROLL_THRESHOLD = 60`（距底部 60px 以内视为"在底部"）
- 只有在底部时新消息才自动滚到底部，否则保持用户阅读位置

---

## 7. 前后端通信协议（`_post_message` 消息表）

Python 端通过 [_post_message(msg_type, payload)](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L660-L663) 调用 JS：
```python
code = json.dumps({"type": msg_type, "payload": payload}, ensure_ascii=False)
self.browser.page().runJavaScript(f"postMessage({code})")
```

JS 端由 [postMessage(msg)](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L400-L437) switch-case 分发：

| type | payload | 调用方 | JS 行为 |
|------|---------|--------|---------|
| `user_msg` | `{"content": "<转义后的文本>"}` | `type_text()`, `Reload_chat()` | 创建用户气泡，预创建 AI 气泡，隐藏思考动画 |
| `ai_stream` | `{"text": "<chunk文本>", "done": 0/1}` | `run_js()`, `finish_stream()` | `done=0`：追加文本+节流渲染；`done=1`：最终渲染+代码高亮+复制按钮 |
| `thinking` | 无（payload 被忽略） | `run_js()` 收到 reasoning_content | 显示三个脉冲点的思考动画 |
| `clear` | 无 | `setNew_chat()`, `Reload_chat()` | 清空 container，重置 currentAiBubble，隐藏思考动画 |
| `add_copy_btn` | 无 | `Reload_chat()`, `finish_stream()` | 为所有 pre>code 添加 COPY 按钮 |
| `reload_ai` | `{"content": "<Markdown文本>"}` | `Reload_chat()` | 完整渲染一条历史 AI 消息（直接渲染，不追加光标） |
| `set_theme` | `{"theme": "dark"/"light"}` | `_apply_theme_from_config()`, `settings()` | 设置 `data-theme` 属性切换 CSS 变量 |
| `set_font_size` | `{"size": "small"/"medium"/"large"}` | `_apply_theme_from_config()`, `settings()` | 设置 `html.style.fontSize` |

> **注意**：用户消息内容在发送到 JS 前会经过 `html.escape()` 处理（[type_text L656-L657](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L656-L657)），换行符替换为 `\\n`。AI 回复内容直接以 Markdown 格式发送到 JS，由 marked 处理。

---

## 8. JSON 数据格式

### 8.1 config.json

路径：[data/config.json](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/data/config.json)（运行时生成，模板为 [config.example.json](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/data/config.example.json)）

```json
{
    "theme": "dark",              // "dark" | "light"
    "font_size": "medium",        // "small" | "medium" | "large"
    "items": [
        {
            "name": "deepseek",          // 配置名称（唯一标识）
            "model": "deepseek-chat",    // 模型名
            "api_key": "sk-xxx",         // API 密钥
            "base_url": "https://api.deepseek.com"  // API 端点
        }
    ],
    "select": {
        "default": "deepseek"    // 当前选中的配置 name
    }
}
```

**读取逻辑**（[init_config L154-L158](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L154-L158)）：筛选 `items` 中 `name == select.default` 的项，返回 list。

**写入逻辑**（[settings L691-L706](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L691-L706)）：
- 如果 `name` 已存在 → 仅切换 `select.default`
- 如果 `name` 不存在 → 追加到 `items` 并设为默认

### 8.2 chat_history.json

路径：`data/chat_history.json`（运行时生成）

```json
{
    "item": [
        {
            "chat_id": "1719283746501",     // 毫秒时间戳字符串
            "user_id": "user123",           // 预留字段，当前未使用
            "title": "你好，请介绍一下Python", // 首条用户消息（cut_text 截断显示）
            "timestamp": "2024-06-24T18:30:00Z",
            "messages": [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "你好！有什么可以帮助你的？"},
                {"role": "user", "content": "介绍Python"},
                {"role": "assistant", "content": "Python是一种..."}
            ],
            "metadata": {
                "platform": "web",
                "language": "zh-CN",
                "user_agent": "Mozilla/5.0..."
            }
        }
    ]
}
```

**标题自动生成**（[json_write_Chat L464-L471](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L464-L471)）：
- 如果 title 是 "New Chat" 或空，自动用用户首条消息（`cut_text` 截取前10字符+`...`）作为列表显示名
- JSON 中存储完整的 `input_content` 作为 title

---

## 9. 状态变量字典

[MyWindow_Stream.__init__](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L76-L119) 中定义的所有实例状态：

| 变量 | 类型 | 初始值 | 说明 |
|------|------|--------|------|
| `chat_info_path` | str | CHAT_HISTORY_PATH | 聊天历史文件路径 |
| `config_path` | str | CONFIG_PATH | 配置文件路径 |
| `marked_html_path` | str | CHAT_TEMPLATE_PATH | HTML 模板路径 |
| `_chat_cache` | dict/None | None | 聊天历史内存缓存，None 表示未加载 |
| `_chat_lock` | threading.Lock | 新锁 | JSON 写入线程锁 |
| `_finishing` | bool | False | finish_stream 重入保护标志 |
| `response_string` | str | "" | 累积的 AI 正式回复文本（不含 reasoning） |
| `input_content` | str | "" | 当前用户输入内容（发送前缓存） |
| `streaming` | bool | False | 是否正在流式输出（控制按钮/输入框状态） |
| `cut_text` | lambda | — | 标题截断函数：>9字符则前10字符+"..." |
| `timer` | QTimer | 50ms | 流式消费定时器 |
| `AI_sever_config` | list | init_config() 返回值 | 当前选中的 API 配置 list（取 [0]） |
| `stream` | iterator/None | None | OpenAI stream 迭代器 |
| `pending_chunks` | list | [] | 待推送 JS 的 chunk 缓冲区 |
| `thinking_active` | bool | False | 思考动画是否激活 |
| `stream_done` | bool | False | 流是否已结束（StopIteration） |
| `chunk_batch_size` | int | 6 | 每次 QTimer tick 消费的 chunk 数量 |

**父类 MyWindow_layout 中创建的控件**（见 [ui_layout.py 详解](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/ui_layout.py#L29-L137)）：
`input_main`, `btn_send`, `settings_btn`, `browser`, `title_Chat`, `list_widget`, `btn_new_chat`, `shortcut`

---

## 10. 关键设计决策与陷阱

### 10.1 为什么用 QTimer 而不是直接在 QThread 中操作 UI？

Qt 要求 UI 操作只能在主线程。`QuestAIResponse`（QThread）通过 `data_fetched` 信号将 stream 迭代器传回主线程后，不能直接在子线程 `next(stream)`（否则跨线程操作 OpenAI 内部可能不安全），但也不能在主线程阻塞等待（会卡死UI）。

解决方案：QTimer(50ms) 在主线程定时触发，每次批量消费 6 个 chunk，推送到 JS 后立即返回。这样既不阻塞 UI，又能实时显示。

### 10.2 为什么用 QWebEngineView 而不是纯 Qt Widget？

Markdown 渲染（含代码高亮、表格、GFM 语法）用 Qt Widget 实现非常复杂且效果差。嵌入 HTML 页面可以直接用成熟的 JS 库（marked + highlight.js），开发效率和渲染质量都更高。

代价是进程重（QWebEngineView 基于 Chromium），前后端通信需要通过 `runJavaScript` + `postMessage` 桥接。

### 10.3 reasoning_content 的处理

某些模型（如 deepseek-reasoner）会先返回 `reasoning_content`（思考过程），再返回 `content`（正式回复）。当前实现：
- reasoning_content 只触发 thinking 动画（三个脉冲点）
- **不保存** reasoning_content 到 `response_string` 和聊天历史
- content 开始后 thinking 动画消失，正式文本开始渲染

这意味着思考过程对用户是瞬时可见（动画期间）但不持久化。如需保存思考过程，需修改 [run_js L597-L602](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L597-L602) 和 `json_write_Chat` 的消息格式。

### 10.4 原子写入机制

[ _atomic_write_json() ](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L378-L403)使用 tempfile + os.replace 模式：
1. 在目标目录创建临时文件 `.chat_xxx.tmp`
2. 写入完整 JSON 数据
3. `os.replace(tmp, target)` 原子替换（Windows/Linux 均支持）
4. 同步更新 `_chat_cache`（deepcopy 避免引用问题）
5. `threading.Lock` 保护并发写入

### 10.5 已知命名/拼写问题（修改时注意）

| 当前名称 | 应为 | 位置 |
|----------|------|------|
| `AI_sever_config` | `AI_server_config` | 多处（sever→server拼写错误） |
| `test_code` | `send_code` 或 `STREAM_MODE` | [constants.py:2](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/constants.py#L2)（实际是生产常量，不是测试代码） |
| `setNew_chat` | `set_new_chat` | [main_window.py:190](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L190)（命名风格不一致） |
| `CheckSelectedItem` | `check_selected_item` | [main_window.py:284](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L284)（首字母大写不统一） |
| `Reload_chat` | `reload_chat` | [main_window.py:405](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L405) |

### 10.6 线程模型

- **主线程**：Qt 事件循环、所有 UI 操作、QTimer tick、JSON 读写
- **QuestAIResponse 子线程**：仅执行 `DeepSeekChat.chat()` 阻塞等待 API 响应
- **QWebEngine 渲染进程**：Chromium 子进程，独立于 Python，JS 执行不阻塞主线程

跨线程数据流：子线程 → `data_fetched.emit()` → 主线程槽函数 → QTimer 消费 stream → `runJavaScript()` → Chromium 进程。

---

## 11. 扩展 / 修改指引

### 添加新的 API 服务商

无需修改代码，只需在设置界面或 `config.json` 中添加：
```json
{"name": "服务名", "model": "模型名", "api_key": "key", "base_url": "https://xxx/v1"}
```
只要该服务兼容 OpenAI Chat Completions API 格式即可。

### 修改流式参数

- **消费速度**：`self.chunk_batch_size = 6`（[L119](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L119)）— 每次 tick 消费的 chunk 数；`self.timer.setInterval(50)`（[L101](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L101)）— tick 间隔
- **API 参数**：[api_client.py:42-48](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/api_client.py#L42-L48)（temperature, timeout 等）
- **前端渲染节流**：[chat_template.html:304](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html#L304) `RENDER_THROTTLE_MS`

### 添加新的消息类型

1. 在 Python 端调用 `self._post_message("new_type", payload)`
2. 在 JS 端 `postMessage()` switch 中添加 `case 'new_type':` 处理
3. 如果需要双向通信，需额外实现 `QWebChannel`（当前仅 Python→JS 单向）

### 修改 system prompt

[main_window.py:298-299](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L298-L299)：
```python
messages = [{"role": "system", "content": "You are a helpful assistant."}]
```

### 添加新主题

1. 在 [themes.py](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/themes.py) 中添加 `_QT_XXX` QSS 字符串
2. 在 [settings_dialog.py:43](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/settings_dialog.py#L43) 的 `combo_theme` 中添加选项
3. 在 [chat_template.html](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/assets/chat_template.html) 中添加 `[data-theme="xxx"]` CSS 变量集

### 修改消息保存格式

`json_write_Chat()` 中 `plus_MSG` 的结构（[L473-L482](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/src/main_window.py#L473-L482)）决定了保存格式。同时需要修改 `_build_messages_history()` 的读取逻辑以匹配。

### 修改前端依赖版本

编辑 [package.json](file:///c:/Users/14834/OneDrive/Desktop/python_Stu_s/PyQt5-master/Custom_code/localAI_GUI/AI_GUI/package.json) 后重新 `npm install`。注意：marked v14+ 中 `highlight` 和 `sanitize` 选项已废弃，当前代码仍使用旧 API，升级时需适配。

---

> **文档维护提示**：修改源码后请同步更新本文档中的行号引用。在 IDE 中可通过 Ctrl+Click 点击行号链接快速定位验证。
