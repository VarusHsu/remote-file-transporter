import sys

from PyQt6.QtWidgets import QApplication, QWidget, QListWidget, QPushButton

import i18n

config = {
    "mac_os": {
        "path_split": "/",
        "windows_w": 750,
        "windows_h": 421,
        "view_box_move_w": 20,
        "view_box_move_h": 20,
        "view_box_w": 710,
        "view_box_h": 360,
        "setting_button_move_w": 658,
        "setting_button_move_h": 385,
        "setting_windows_w": 500,
        "setting_windows_h": 314,
    },
    "windows": {
        "path_split": "\\"
    },
    "ubuntu": {
        "path_split": "/"
    }
}


class SettingWindows:
    windows: QWidget

    os: str
    language: str

    def __init__(self, os: str, language: str):
        self.os = os

    def render(self):
        self.windows = QWidget()
        self.windows.setWindowTitle(i18n.i18n["Setting"][[self.language]])
        pass


class RemoteFileTransporterClient:
    app: QApplication
    windows: QWidget
    view_box: QListWidget
    setting_button: QPushButton
    setting_window: SettingWindows

    os: str
    language:str

    def __init__(self, os: str):
        self.os = os
        self.language = "ja_jp"

    def setting_button_on_click(self):
        self.setting_window = SettingWindows(self.os, self.language)
        self.setting_window.render()

    def render(self):
        self.app = QApplication(sys.argv)
        self.windows = QWidget()
        self.windows.setFixedSize(config[self.os]["windows_w"], config[self.os]["windows_h"])
        self.windows.setWindowTitle(i18n.i18n["Remote File Transporter"][self.language])

        self.view_box = QListWidget(self.windows)
        self.view_box.move(config[self.os]["view_box_move_w"], config[self.os]["view_box_move_h"])
        self.view_box.resize(config[self.os]["view_box_w"], config[self.os]["view_box_h"])
        self.view_box.addItem(i18n.i18n["Welcome"][self.language])

        self.setting_button = QPushButton(self.windows)
        self.setting_button.move(config[self.os]["setting_button_move_w"], config[self.os]["setting_button_move_h"])
        self.setting_button.setText(i18n.i18n["Setting"][self.language])

        self.windows.show()
        sys.exit(self.app.exec())

    pass


def main():
    if len(sys.argv) != 2:
        print("example usage: python3 main.py mac_os")
        return
    elif sys.argv[1] not in ["mac_os", "windows", "ubuntu"]:
        print("only suppose operating systems: [mac_os, windows, ubuntu]")
    else:
        client: RemoteFileTransporterClient = RemoteFileTransporterClient(sys.argv[1])
        client.render()


if __name__ == "__main__":
    main()
