import sys
import json

from PyQt5.QtWidgets import (
    QDialog,
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QComboBox,
    QLabel,
    QTabWidget,
)

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from src.paths import icon_path, CONFIG_PATH


class Settings_mode(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Settings")
        app_icon = QIcon(icon_path("settings4.png"))
        self.setWindowIcon(app_icon)
        self.setGeometry(800, 400, 420, 420)

        # ── load config ──
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self._data = json.load(f)

        # ═══════════════ Tab 1: Theme ═══════════════
        tab_theme = QWidget()
        tab_theme_layout = QVBoxLayout()

        lbl_theme = QLabel("Theme")
        lbl_theme.setStyleSheet("font-weight:bold;font-size:14px;margin-top:10px;")
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["dark", "light"])
        self.combo_theme.setCurrentText(self._data.get("theme", "dark"))

        lbl_font = QLabel("Font Size")
        lbl_font.setStyleSheet("font-weight:bold;font-size:14px;margin-top:14px;")
        self.combo_font = QComboBox()
        self.combo_font.addItems(["small", "medium", "large"])
        self.combo_font.setCurrentText(self._data.get("font_size", "medium"))

        tab_theme_layout.addWidget(lbl_theme)
        tab_theme_layout.addWidget(self.combo_theme)
        tab_theme_layout.addWidget(lbl_font)
        tab_theme_layout.addWidget(self.combo_font)
        tab_theme_layout.addStretch()
        tab_theme.setLayout(tab_theme_layout)

        # ═══════════════ Tab 2: API ═══════════════
        tab_api = QWidget()
        tab_api_layout = QVBoxLayout()

        lbl_select = QLabel("Configuration")
        lbl_select.setStyleSheet("font-weight:bold;font-size:14px;margin-top:10px;")
        self.combo_box = QComboBox()
        self.combo_box.addItem("-- New --")
        for item in self._data.get("items", []):
            self.combo_box.addItem(item["name"])
        self.combo_box.setCurrentText(self._data.get("select", {}).get("default", ""))

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Config name")
        self.input_model = QLineEdit()
        self.input_model.setPlaceholderText("Model")
        self.input_key = QLineEdit()
        self.input_key.setPlaceholderText("API Key")
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("Base URL")

        tab_api_layout.addWidget(lbl_select)
        tab_api_layout.addWidget(self.combo_box)
        tab_api_layout.addWidget(QLabel("Name"))
        tab_api_layout.addWidget(self.input_name)
        tab_api_layout.addWidget(QLabel("Model"))
        tab_api_layout.addWidget(self.input_model)
        tab_api_layout.addWidget(QLabel("API Key"))
        tab_api_layout.addWidget(self.input_key)
        tab_api_layout.addWidget(QLabel("Base URL"))
        tab_api_layout.addWidget(self.input_url)
        tab_api.setLayout(tab_api_layout)

        # ═══════════════ Tabs + Buttons ═══════════════
        self.tabs = QTabWidget()
        self.tabs.addTab(tab_theme, "Theme")
        self.tabs.addTab(tab_api, "API")

        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)

        root = QVBoxLayout()
        root.addWidget(self.tabs)
        root.addLayout(btn_layout)
        self.setLayout(root)

        self.combo_box.currentIndexChanged.connect(self._on_api_select)
        self._on_api_select(self.combo_box.currentIndex())

    def _on_api_select(self, index):
        if index <= 0:
            self.input_name.clear()
            self.input_model.clear()
            self.input_key.clear()
            self.input_url.clear()
            return
        items = self._data.get("items", [])
        if index - 1 < len(items):
            item = items[index - 1]
            self.input_name.setText(item.get("name", ""))
            self.input_model.setText(item.get("model", ""))
            self.input_key.setText(item.get("api_key", ""))
            self.input_url.setText(item.get("base_url", ""))

    def get_input(self) -> dict:
        return {
            "name": self.input_name.text(),
            "model": self.input_model.text(),
            "api_key": self.input_key.text(),
            "base_url": self.input_url.text(),
            "theme": self.combo_theme.currentText(),
            "font_size": self.combo_font.currentText(),
        }


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(700, 400, 300, 200)

        layout = QVBoxLayout()
        self.show_dialog_button = QPushButton("Show Input Dialog")
        self.show_dialog_button.clicked.connect(self.show_input_dialog)
        layout.addWidget(self.show_dialog_button)
        self.setLayout(layout)

    def show_input_dialog(self):
        setting = Settings_mode()
        if setting.exec_() == Settings_mode.Accepted:
            input_info = setting.get_input()
            print("Input text:", input_info)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
