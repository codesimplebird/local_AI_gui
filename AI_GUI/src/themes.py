_QT_DARK = """
QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
}
QLineEdit {
    background-color: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 4px 10px;
}
QLineEdit:focus {
    border-color: #00d4ff;
}
QListWidget {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    outline: none;
}
QListWidget::item {
    background-color: #161b22;
    color: #c9d1d9;
    margin: 2px;
    padding: 10px;
    border-radius: 8px;
}
QListWidget::item:selected {
    background-color: rgba(0, 212, 255, 0.15);
    color: #00d4ff;
    border: 1px solid rgba(0, 212, 255, 0.3);
}
QListWidget::item:hover {
    background-color: #21262d;
}
QPushButton {
    border-radius: 10px;
    padding: 6px 16px;
}
QPushButton#sendButton:enabled {
    background-color: #238636;
    color: #ffffff;
    border: 1px solid #2ea043;
}
QPushButton#sendButton:enabled:hover {
    background-color: #2ea043;
}
QPushButton#sendButton:disabled {
    background-color: #21262d;
    color: #484f58;
    border: 1px solid #30363d;
}
QPushButton#newChatButton {
    background-color: rgba(0, 212, 255, 0.08);
    color: #00d4ff;
    border: 1px solid rgba(0, 212, 255, 0.2);
    font-weight: bold;
}
QPushButton#newChatButton:hover {
    background-color: rgba(0, 212, 255, 0.15);
}
QPushButton#settingsButton {
    background: transparent;
    border: none;
}
QLabel {
    background: transparent;
    color: #c9d1d9;
}
QLabel#chatTitle {
    color: #f0f6fc;
    font-weight: bold;
}
QLabel#chatHistoryLabel {
    color: #8b949e;
}
QMenu {
    background-color: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 20px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: rgba(0, 212, 255, 0.12);
}
QComboBox {
    background-color: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 4px 10px;
}
QComboBox:hover {
    border-color: #00d4ff;
}
QComboBox QAbstractItemView {
    background-color: #161b22;
    color: #c9d1d9;
    selection-background-color: rgba(0, 212, 255, 0.15);
    border: 1px solid #30363d;
    border-radius: 4px;
}
QTabWidget::pane {
    border: 1px solid #30363d;
    border-radius: 6px;
    background: #0d1117;
}
QTabBar::tab {
    background: #161b22;
    color: #8b949e;
    padding: 8px 20px;
    border: 1px solid #30363d;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #0d1117;
    color: #00d4ff;
    border-bottom: 2px solid #00d4ff;
}
QTabBar::tab:hover {
    color: #c9d1d9;
}
QMessageBox {
    background-color: #0d1117;
}
QMessageBox QLabel {
    color: #c9d1d9;
}
QMessageBox QPushButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 16px;
    min-width: 80px;
}
QMessageBox QPushButton:hover {
    background-color: #30363d;
}
QInputDialog {
    background-color: #0d1117;
}
QInputDialog QLineEdit {
    background-color: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 4px 10px;
}
"""

_QT_LIGHT = """
QWidget {
    background-color: #ffffff;
    color: #1f2328;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
}
QLineEdit {
    background-color: #f6f8fa;
    color: #1f2328;
    border: 1px solid #d0d7de;
    border-radius: 10px;
    padding: 4px 10px;
}
QLineEdit:focus {
    border-color: #0969da;
}
QListWidget {
    background-color: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    outline: none;
}
QListWidget::item {
    background-color: #f6f8fa;
    color: #1f2328;
    margin: 2px;
    padding: 10px;
    border-radius: 8px;
}
QListWidget::item:selected {
    background-color: #ddf4ff;
    color: #0969da;
    border: 1px solid #54aeff;
}
QListWidget::item:hover {
    background-color: #e6eaef;
}
QPushButton {
    border-radius: 10px;
    padding: 6px 16px;
}
QPushButton#sendButton:enabled {
    background-color: #1f883d;
    color: #ffffff;
    border: 1px solid #1f883d;
}
QPushButton#sendButton:enabled:hover {
    background-color: #1a7a35;
}
QPushButton#sendButton:disabled {
    background-color: #e6eaef;
    color: #8c959f;
    border: 1px solid #d0d7de;
}
QPushButton#newChatButton {
    background-color: #ddf4ff;
    color: #0969da;
    border: 1px solid #54aeff;
    font-weight: bold;
}
QPushButton#newChatButton:hover {
    background-color: #b6e3ff;
}
QPushButton#settingsButton {
    background: transparent;
    border: none;
}
QLabel {
    background: transparent;
    color: #1f2328;
}
QLabel#chatTitle {
    color: #1f2328;
    font-weight: bold;
}
QLabel#chatHistoryLabel {
    color: #656d76;
}
QMenu {
    background-color: #ffffff;
    color: #1f2328;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 20px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #f0f2f5;
}
QComboBox {
    background-color: #f6f8fa;
    color: #1f2328;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 4px 10px;
}
QComboBox:hover {
    border-color: #0969da;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1f2328;
    selection-background-color: #ddf4ff;
    border: 1px solid #d0d7de;
    border-radius: 4px;
}
QTabWidget::pane {
    border: 1px solid #d0d7de;
    border-radius: 6px;
    background: #ffffff;
}
QTabBar::tab {
    background: #f6f8fa;
    color: #656d76;
    padding: 8px 20px;
    border: 1px solid #d0d7de;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #ffffff;
    color: #0969da;
    border-bottom: 2px solid #0969da;
}
QTabBar::tab:hover {
    color: #1f2328;
}
QMessageBox {
    background-color: #ffffff;
}
QMessageBox QLabel {
    color: #1f2328;
}
QMessageBox QPushButton {
    background-color: #f6f8fa;
    color: #1f2328;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 6px 16px;
    min-width: 80px;
}
QMessageBox QPushButton:hover {
    background-color: #e6eaef;
}
QInputDialog {
    background-color: #ffffff;
}
QInputDialog QLineEdit {
    background-color: #f6f8fa;
    color: #1f2328;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 4px 10px;
}
"""
