import sys

from PyQt6.QtWidgets import QApplication, QWidget, QListWidget

config = {
    "mac_os": {
        "path_split": "/",
        "windows_w": 750,
        "windows_h": 421,
        "view_box_move_w": 20,
        "view_box_move_h": 20,
        "view_box_w": 710,
        "view_box_h": 351,
    },
    "windows": {
        "path_split": "\\"
    },
    "ubuntu": {
        "path_split": "/"
    }
}


class RemoteFileTransporterClient:
    app: QApplication
    windows: QWidget
    view_box: QListWidget

    os: str

    def __init__(self, os: str):
        self.os = os

    def render(self):
        self.app = QApplication(sys.argv)
        self.windows = QWidget()
        self.windows.setFixedSize(config[self.os]["windows_w"], config[self.os]["windows_h"])
        self.windows.setWindowTitle("Remote File Transporter")

        self.view_box = QListWidget(self.windows)
        self.view_box.move(config[self.os]["view_box_move_w"], config[self.os]["view_box_move_h"])
        self.view_box.resize(config[self.os]["view_box_w"], config[self.os]["view_box_h"])
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
