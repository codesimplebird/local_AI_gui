import sys
from PyQt5.QtWidgets import (
    QWidget,
    QApplication,
    QPushButton,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QHBoxLayout,
    QShortcut,
    QListWidget,
    QListWidgetItem,
)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QIcon, QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView

from src.paths import icon_path


class CustomListWidgetItem(QListWidgetItem):
    def __init__(self, name, item_id):
        super().__init__(name)
        self.item_id = item_id
        self.name = name


class MyWindow_layout(QWidget):

    def __init__(self):
        super().__init__()

        self.resize(1000, 750)
        self.setWindowTitle("AI图形界面")
        app_icon = QIcon(icon_path("copilot_icon4.png"))
        self.setWindowIcon(app_icon)

        self.my_init()

    def my_init(self):

        input_main = QLineEdit()
        input_main.setFixedHeight(30)
        input_main.setPlaceholderText("input")
        input_main.setObjectName("inputField")

        note_input = QLabel("输入内容:")
        note_input.setFixedSize(80, 30)
        note_input.setFont(QFont("Microsoft YaHei", 10))

        layout_in_input = QHBoxLayout()
        layout_in_input.addWidget(note_input)
        layout_in_input.addWidget(input_main)

        btn_send = QPushButton("Send")
        btn_send.setFixedSize(100, 30)
        btn_send.setObjectName("sendButton")

        self.shortcut = QShortcut(QKeySequence("Enter"), self)
        self.shortcut.activated.connect(btn_send.click)

        settings_btn = QPushButton(self)
        settings_btn.setIcon(QIcon(icon_path("settings.png")))
        settings_btn.setFlat(True)
        settings_btn.setToolTip("设置")
        settings_btn.setObjectName("settingsButton")
        settings_btn.clicked.connect(self.settings)

        browser = QWebEngineView(self)

        title_Chat = QLabel("Chat")
        title_Chat.setFont(QFont("Microsoft YaHei", 14))
        title_Chat.setFixedSize(600, 30)
        title_Chat.setAlignment(Qt.AlignCenter)
        title_Chat.setObjectName("chatTitle")

        list_widget = QListWidget()
        list_widget.setFocusPolicy(Qt.NoFocus)
        list_widget.setObjectName("chatList")
        list_widget.setFont(QFont("Microsoft YaHei", 12))
        list_widget.setFixedWidth(200)
        list_widget.setToolTip("点击右键打开菜单")
        list_widget.setContextMenuPolicy(Qt.CustomContextMenu)

        btn_new_chat = QPushButton("New Chat")
        btn_new_chat.setFixedSize(150, 50)
        btn_new_chat.setObjectName("newChatButton")
        new_chat_font = QFont("Microsoft YaHei", 15)
        new_chat_font.setBold(True)
        btn_new_chat.setFont(new_chat_font)

        F = QFont("Microsoft YaHei", 10, QFont.Bold)
        note_chat = QLabel("\n Chat history")
        note_chat.setFont(F)
        note_chat.setObjectName("chatHistoryLabel")
        note_chat.setFixedSize(120, 60)

        left_layout = QVBoxLayout()
        left_layout.addWidget(btn_new_chat)
        left_layout.addWidget(note_chat)
        left_layout.addWidget(list_widget)

        right_up_layout = QVBoxLayout()
        right_up_layout.addWidget(title_Chat)
        right_up_layout.addWidget(browser)

        up_layout = QHBoxLayout()
        up_layout.setContentsMargins(0, 0, 0, 0)
        up_layout.setSpacing(1)
        up_layout.addLayout(left_layout)
        up_layout.addLayout(right_up_layout)

        down_layout = QHBoxLayout()
        down_layout.addWidget(settings_btn, alignment=Qt.AlignLeft)
        down_layout.addWidget(btn_send, alignment=Qt.AlignLeft)

        layout_out = QVBoxLayout()
        layout_out.addLayout(up_layout, 1)
        layout_out.addLayout(layout_in_input)
        layout_out.addLayout(down_layout)

        self.setLayout(layout_out)

        self.btn_new_chat = btn_new_chat
        self.list_widget = list_widget
        self.btn_send = btn_send
        self.settings_btn = settings_btn
        self.input_main = input_main
        self.browser = browser
        self.title_Chat = title_Chat

        self.input_main.setFocus()

    def settings(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)

    MW = MyWindow_layout()
    MW.list_widget.addItem("test")
    MW.list_widget.addItem("test")

    MW.show()

    app.exec_()
