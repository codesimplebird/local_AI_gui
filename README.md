# localAI_GUI

本地 AI 聊天桌面应用，基于 **PyQt5 + QWebEngineView** 构建。支持多会话管理、流式输出、Markdown 渲染，并通过 OpenAI 兼容接口接入 DeepSeek、X.AI、通义千问、LM Studio 等任意模型服务。

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-green) ![License](https://img.shields.io/badge/License-MIT-orange)

## 功能特性

- **多会话管理** — 创建 / 切换 / 重命名 / 删除会话，聊天历史自动本地保存
- **流式输出** — AI 回复实时逐字显示，支持中途 Stop 中断
- **思考指示器** — 等待首个 token 时显示动画提示（支持 reasoning 模型）
- **Markdown 渲染** — GFM 语法、代码高亮（highlight.js）、表格、引用块
- **一键复制** — 代码块右上角 COPY 按钮
- **多 API 接入** — 任意 OpenAI 兼容服务：DeepSeek、X.AI (Grok)、通义千问、LM Studio 等
- **双主题** — Dark / Light 主题切换，字体大小可调
- **智能滚动** — 用户上翻暂停自动滚动，回到底部自动恢复
- **健壮性** — 原子化 JSON 写入（防写坏文件）、内存缓存、线程安全、断网/鉴权/限流错误友好提示

## 项目结构

```
localAI_GUI/
├── AI_GUI/                      # 主应用
│   ├── src/
│   │   ├── main_window.py       # 主窗口逻辑：流式处理、会话管理、线程控制
│   │   ├── ui_layout.py         # Qt 布局（侧边栏 / 输入框 / WebView）
│   │   ├── api_client.py        # OpenAI 兼容 API 客户端（流式）
│   │   ├── settings_dialog.py   # 设置对话框（主题 + API 配置，Key 密码输入）
│   │   ├── themes.py            # Qt QSS 样式（Dark / Light）
│   │   ├── paths.py             # 统一路径管理
│   │   └── constants.py         # 全局常量
│   ├── assets/
│   │   ├── icon/                # 应用图标
│   │   └── chat_template.html   # 聊天界面 HTML/CSS/JS（marked + hljs + clipboard）
│   ├── data/
│   │   ├── config.json          # API 配置（含密钥，gitignore，不入库）
│   │   └── config.example.json  # 配置模板
│   ├── tests/                   # pytest 单元测试（30 个用例）
│   ├── docs/                    # 架构文档
│   ├── requirements.txt         # Python 依赖
│   └── package.json             # 前端依赖声明（npm install）
├── README.md                    # 本文档
└── .gitignore
```

## 安装

### 前置要求

- Python 3.8+
- Node.js（安装前端渲染依赖）

### 步骤

```bash
# 1. 进入项目目录
cd AI_GUI

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 安装前端依赖（marked.js / highlight.js / clipboard.js）
npm install

# 4. 初始化配置
cp data/config.example.json data/config.json
```

## 配置

编辑 `data/config.json`，填入你的 API 信息：

```json
{
    "theme": "dark",
    "font_size": "medium",
    "items": [
        {
            "name": "deepseek",
            "model": "deepseek-chat",
            "api_key": "sk-xxx",
            "base_url": "https://api.deepseek.com"
        }
    ],
    "select": {
        "default": "deepseek"
    }
}
```

也可以通过应用内**设置界面**（左下角齿轮）添加、切换 API 配置，API Key 采用密码输入框，仅保存在本地文件。

### 支持的 API（任意 OpenAI 兼容服务）

| 服务 | Base URL | 模型示例 |
|------|----------|----------|
| DeepSeek | `https://api.deepseek.com` | deepseek-chat / deepseek-reasoner |
| X.AI (Grok) | `https://api.x.ai/v1` | grok-beta |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | qwen 系列 |
| LM Studio | `http://localhost:1234/v1` | 本地任意模型 |

> 注意：`data/config.json` 包含密钥，已被 .gitignore 排除，请勿提交到仓库。

## 运行

```bash
cd AI_GUI
python src/main_window.py
```

## 使用

1. 启动后自动创建新会话
2. 底部输入框输入消息，按 **Enter** 或点击 **Send** 发送
3. AI 回复流式显示，点击 **Stop** 可中断
4. 左侧列表管理多个会话；右键会话可**重命名 / 删除**
5. 左下角齿轮打开设置：切换主题、字号、添加 API

## 运行测试

```bash
cd AI_GUI
python -m pytest tests -q
```

## 架构概览

```
┌────────────────────────────────────────────────────┐
│  Qt Widgets（侧边栏 / 输入框 / 按钮）              │
│  ┌────────────────────────────────────────────┐   │
│  │  QWebEngineView（chat_template.html）      │   │
│  │  marked.js + highlight.js + clipboard.js   │   │
│  └────────────────────────────────────────────┘   │
│                    ↕ runJavaScript 消息桥            │
│  QTimer(50ms) ← 流迭代器 ← QThread（QuestAIResponse）│
│                                     ↑                 │
│                          OpenAI SDK（stream）         │
└────────────────────────────────────────────────────┘
```

- 用户输入 → `QuestAIResponse` QThread 发起流式请求
- QTimer 每 50ms 批量拉取 chunks，`runJavaScript()` 推送到 HTML
- JS 端 `postMessage()` 分发渲染，流结束自动代码高亮 + 保存历史

## 许可证

MIT License
