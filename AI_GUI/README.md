# AI Chat GUI

基于 PyQt5 + QWebEngineView 的本地 AI 聊天应用，支持多会话管理、流式输出、Markdown 渲染和多 API 配置。

## 功能特性

- **多会话管理** — 创建、切换、重命名、删除聊天会话，历史自动保存
- **流式输出** — AI 回复实时逐字显示，支持中途停止
- **Markdown 渲染** — 支持 GFM 语法、代码高亮（highlight.js）、表格、引用块
- **代码复制** — 代码块右上角一键复制（clipboard.js）
- **多 API 支持** — 通过 OpenAI SDK 兼容接口接入 DeepSeek、X.AI、通义千问等
- **主题切换** — Dark / Light 双主题，字体大小可调
- **智能滚动** — 用户上滚时暂停自动滚动，回到底部自动恢复
- **思考指示器** — 等待首个 token 时显示动画提示

## 技术栈

| 层级 | 技术 |
|------|------|
| 框架 | PyQt5 + PyQtWebEngine |
| API 客户端 | OpenAI Python SDK（流式模式） |
| 前端渲染 | marked.js + highlight.js + clipboard.js |
| 数据存储 | JSON 文件（本地持久化） |

## 项目结构

```
AI_GUI/
├── src/
│   ├── __init__.py              # Python 包标识
│   ├── paths.py                 # 统一路径管理
│   ├── main_window.py           # 主窗口逻辑、流式处理、会话管理
│   ├── ui_layout.py             # Qt 布局定义（侧边栏、输入框、浏览器）
│   ├── api_client.py            # API 客户端（DeepSeek 兼容 OpenAI 接口）
│   ├── settings_dialog.py       # 设置对话框（主题 + API 配置）
│   ├── themes.py                # Qt QSS 样式（Dark / Light）
│   └── constants.py             # 全局常量和模板
├── assets/
│   ├── icon/                    # 应用图标
│   └── chat_template.html       # 聊天界面 HTML/CSS/JS
├── data/
│   ├── config.json              # API 配置（不纳入版本控制）
│   └── config.example.json      # 配置模板
├── node_modules/                # 前端依赖（vendored）
├── requirements.txt             # Python 依赖
├── package.json                 # 前端依赖声明
└── docs/
    └── architecture.xmind       # 架构设计图
```

## 安装

### 前置要求

- Python 3.8+
- Node.js（用于安装前端依赖）

### 步骤

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/PyQt5-master.git
cd PyQt5-master/Custom_code/localAI_GUI/AI_GUI

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 安装前端依赖
npm install
```

## 配置

首次运行前，复制配置模板并填入你的 API 信息：

```bash
cp data/config.example.json data/config.json
```

编辑 `data/config.json`：

```json
{
    "theme": "dark",
    "font_size": "medium",
    "items": [
        {
            "name": "deepseek",
            "model": "deepseek-chat",
            "api_key": "sk-your-api-key",
            "base_url": "https://api.deepseek.com"
        }
    ],
    "select": {
        "default": "deepseek"
    }
}
```

也可以通过应用内 **设置界面**（左下角齿轮图标）添加和切换 API 配置。

### 支持的 API

| 服务 | Base URL | 说明 |
|------|----------|------|
| DeepSeek | `https://api.deepseek.com` | deepseek-chat / deepseek-reasoner |
| X.AI (Grok) | `https://api.x.ai/v1` | grok-beta |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | qwen 系列 |
| LM Studio | `http://localhost:1234/v1` | 本地模型 |

## 运行

```bash
cd src
python main_window.py
```

## 使用

1. 启动后自动创建一个新会话
2. 在底部输入框输入消息，按 **Enter** 或点击 **Send** 发送
3. AI 回复会实时流式显示，点击 **Stop** 可中断
4. 左侧面板管理多个聊天会话
5. 点击左下角齿轮打开设置，切换主题或修改 API 配置

## 架构概览

```
┌─────────────────────────────────────────────────┐
│  Qt Widgets (sidebar, input, buttons)           │
│  ┌───────────────────────────────────────────┐  │
│  │  QWebEngineView (chat_template.html)      │  │
│  │  marked.js + highlight.js + clipboard.js  │  │
│  └───────────────────────────────────────────┘  │
│                    ↕ _post_message()             │
│  QTimer (50ms) ← Stream Iterator ← QThread      │
│                                    ↑             │
│                          OpenAI SDK (streaming)  │
└─────────────────────────────────────────────────┘
```

1. 用户输入 → `QuestAIResponse` QThread 调用 API
2. 流式响应存入 iterator
3. QTimer 每 50ms 批量拉取 chunks，通过 `runJavaScript()` 推送到 HTML
4. JS 端 `postMessage()` 分发消息，marked.js 渲染 Markdown

## 许可证

MIT License
