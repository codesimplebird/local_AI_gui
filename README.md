# localAI_GUI

基于 PyQt5 + QWebEngineView 的本地 AI 聊天应用：多会话管理、流式输出、Markdown 渲染、多 API 接入。

## 项目位置

主项目代码位于 [`AI_GUI/`](AI_GUI/README.md)，包含：

- **多会话管理** — 创建 / 切换 / 重命名 / 删除会话，历史自动保存
- **流式输出** — 实时逐字显示，支持中途停止
- **Markdown 渲染** — marked.js + highlight.js + clipboard.js
- **多 API 支持** — 通过 OpenAI 兼容接口接入 DeepSeek、X.AI、通义千问、LM Studio 等
- **双主题** — Dark / Light，字体大小可调

## 快速开始

```bash
cd AI_GUI
pip install -r requirements.txt
npm install          # 安装前端依赖（marked / highlight.js / clipboard）
cp data/config.example.json data/config.json   # 填入你的 API Key
python src/main_window.py
```

详细文档见 [`AI_GUI/README.md`](AI_GUI/README.md)。
