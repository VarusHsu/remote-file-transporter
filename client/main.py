import json
import sys
import time
from threading import Thread

import requests
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QListWidget, QPushButton, QLabel, QLineEdit

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
        "setting_button_w": 70,
        "setting_windows_w": 500,
        "setting_windows_h": 314,
        "save_button_move_w": 20,
        "save_button_move_h": 280,
        "save_button_w": 80,
        "cancel_button_move_w": 400,
        "cancel_button_move_h": 280,
        "cancel_button_w": 80,
        "server_ip_label_move_w": 20,
        "server_ip_label_move_h": 20,
        "download_dir_label_move_w": 20,
        "download_dir_label_move_h": 50,
        "server_ip_line_edit_w": 260,
        "server_ip_line_edit_move_w": 135,
        "server_ip_line_edit_move_h": 17,
        "download_dir_line_edit_w": 260,
        "download_dir_line_edit_move_w": 135,
        "download_dir_line_edit_move_h": 47,
        "connect_button_w": 70,
        "connect_button_move_w": 20,
        "connect_button_move_h": 385,
    },
    "windows": {
        "path_split": "\\"
    },
    "ubuntu": {
        "path_split": "/"
    }
}


class RerenderNotifySignal(QObject):
    rerender_view_box = pyqtSignal(list)
    pass


class UpdateDataNotifySignal(QObject):
    update_download_dir = pyqtSignal(str)
    update_cur_server_dir = pyqtSignal(str)
    update_server_address = pyqtSignal(str)
    pass


class SettingWindows:
    # widget
    windows: QWidget
    save_button: QPushButton
    cancel_button: QPushButton
    server_ip_label: QLabel
    download_dir_label: QLabel
    server_ip_line_edit: QLineEdit
    download_dir_line_edit: QLineEdit

    # config
    os: str
    language: str
    server_address: str

    # signals
    update_data_notify_signal: UpdateDataNotifySignal
    rerender_notify_signal: RerenderNotifySignal

    def __init__(self, os: str, language: str, server_address: str, download_dir: str,
                 update_data_notify_signal: UpdateDataNotifySignal, rerender_notify_signal: RerenderNotifySignal):
        self.os = os
        self.language = language
        self.update_data_notify_signal = update_data_notify_signal
        self.rerender_notify_signal = rerender_notify_signal

    def save_button_on_click(self):
        self.windows.close()
        self.update_data_notify_signal.update_download_dir.emit(self.download_dir_line_edit.text())
        self.update_data_notify_signal.update_server_address.emit(self.server_ip_line_edit.text())
        self.update_data_notify_signal.update_cur_server_dir.emit("")
        pass

    def cancel_button_on_click(self):
        self.windows.close()

    def render(self):
        self.windows = QWidget()
        self.windows.setWindowTitle(i18n.i18n["Setting"][self.language])
        self.windows.setFixedSize(config[self.os]["setting_windows_w"], config[self.os]["setting_windows_h"])

        self.save_button = QPushButton(self.windows)
        self.save_button.setText(i18n.i18n["Save"][self.language])
        self.save_button.move(config[self.os]["save_button_move_w"], config[self.os]["save_button_move_h"])
        self.save_button.setFixedWidth(config[self.os]["save_button_w"])
        self.save_button.clicked.connect(self.save_button_on_click)

        self.cancel_button = QPushButton(self.windows)
        self.cancel_button.setText(i18n.i18n["Cancel"][self.language])
        self.cancel_button.move(config[self.os]["cancel_button_move_w"], config[self.os]["cancel_button_move_h"])
        self.cancel_button.setFixedWidth(config[self.os]["cancel_button_w"])
        self.cancel_button.clicked.connect(self.cancel_button_on_click)

        self.server_ip_label = QLabel(self.windows)
        self.server_ip_label.setText(i18n.i18n["ServerAddress"][self.language])
        self.server_ip_label.move(config[self.os]["server_ip_label_move_w"], config[self.os]["server_ip_label_move_h"])

        self.download_dir_label = QLabel(self.windows)
        self.download_dir_label.setText(i18n.i18n["DownloadTo"][self.language])
        self.download_dir_label.move(config[self.os]["download_dir_label_move_w"],
                                     config[self.os]["download_dir_label_move_h"])

        self.server_ip_line_edit = QLineEdit(self.windows)
        self.server_ip_line_edit.setFixedWidth(config[self.os]["server_ip_line_edit_w"])
        self.server_ip_line_edit.move(config[self.os]["server_ip_line_edit_move_w"],
                                      config[self.os]["server_ip_line_edit_move_h"])

        self.download_dir_line_edit = QLineEdit(self.windows)
        self.download_dir_line_edit.setFixedWidth(config[self.os]["download_dir_line_edit_w"])
        self.download_dir_line_edit.move(config[self.os]["download_dir_line_edit_move_w"],
                                         config[self.os]["download_dir_line_edit_move_h"])

        self.windows.show()
        pass


class RemoteFileTransporterClient:
    # widgets
    app: QApplication
    windows: QWidget
    view_box: QListWidget
    setting_button: QPushButton
    connect_button: QPushButton
    setting_window: SettingWindows

    # configs
    os: str
    language: str
    server_address: str
    download_dir: str
    cur_server_dir: str

    # signals
    update_data_notify_signal: UpdateDataNotifySignal
    rerender_notify_signal: RerenderNotifySignal

    def __init__(self, os: str):
        self.os = os
        # self.language = "ja_jp"
        # self.language = "en_us"
        self.language = "zh_cn"
        self.server_address = ""
        self.download_dir = ""
        self.cur_server_dir = ""

        self.update_data_notify_signal = UpdateDataNotifySignal()
        self.rerender_notify_signal = RerenderNotifySignal()

    def setting_button_on_click(self):
        self.setting_window = SettingWindows(self.os, self.language, self.server_address, self.download_dir,
                                             self.update_data_notify_signal, self.rerender_notify_signal)
        self.setting_window.render()

    def connect_button_on_click(self):
        if self.server_address == "":
            # todo
            pass
        self.rerender_notify_signal.rerender_view_box.emit([i18n.i18n["Loading"][self.language]])
        thread: Thread = Thread(target=self.connect_button_on_click_task)
        thread.start()

    def update_download_dir_signal_on_receive(self, path: str):
        self.download_dir = path

    def update_server_address_signal_on_receive(self, address: str):
        self.server_address = address

    def update_cur_server_dir_signal_on_receive(self, path: str):
        self.cur_server_dir = path

    def rerender_view_box_signal_on_receive(self, items: list[str]):
        print("rerender")
        print(items)
        self.view_box.clear()
        for item in items:
            self.view_box.addItem(item)
        self.view_box.show()

    def get_home_dir_from_remote(self, address: str):
        url = "http://" + self.server_address + ":50422" + "/get_user_dir"
        try:
            rsp = requests.get(url)
        except Exception as e:
            self.rerender_notify_signal.rerender_view_box.emit([i18n.i18n["ConnectError"][self.language]])
        else:
            if rsp.status_code != 200:
                self.rerender_notify_signal.rerender_view_box.emit([i18n.i18n["ServerError"][self.language],
                                                                    f"Status Code:{rsp.status_code}"])
            else:
                context = json.loads(rsp.content)
                url = "http://" + self.server_address + ":50422" + f"/download?path={context['response']}"

                self.get_walk_dir_from_remote(url=url)

    def get_walk_dir_from_remote(self, url: str):
        try:
            rsp = requests.get(url)
        except Exception as e:
            self.rerender_notify_signal.rerender_view_box.emit([i18n.i18n["ConnectError"][self.language]])
        else:
            if rsp.status_code != 200:
                self.rerender_notify_signal.rerender_view_box.emit([i18n.i18n["ServerError"][self.language],
                                                                    f"Status Code:{rsp.status_code}"])
                print(rsp.content)
            else:
                response = json.loads(rsp.content)
                response = json.loads(response["response"])
                self.rerender_notify_signal.rerender_view_box.emit(response["items"])
        pass

    def connect_button_on_click_task(self):
        if self.cur_server_dir == "":
            url = "http://" + self.server_address + ":50422" + "/get_user_dir"
            try:
                rsp = requests.get(url)
            except Exception as e:
                self.rerender_notify_signal.rerender_view_box.emit([i18n.i18n["ConnectError"][self.language]])
            else:
                if rsp.status_code != 200:
                    self.rerender_notify_signal.rerender_view_box.emit([i18n.i18n["ServerError"][self.language],
                                                                        f"Status Code:{rsp.status_code}"])
                else:
                    context = json.loads(rsp.content)
                    self.cur_server_dir = context["response"]
        url = "http://" + self.server_address + ":50422" + f"/download?path={self.cur_server_dir}"
        self.get_walk_dir_from_remote(url=url)

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
        self.setting_button.setFixedWidth(config[self.os]["setting_button_w"])
        self.setting_button.clicked.connect(self.setting_button_on_click)

        self.connect_button = QPushButton(self.windows)
        self.connect_button.move(config[self.os]["connect_button_move_w"], config[self.os]["connect_button_move_h"])
        self.connect_button.setText(i18n.i18n["Connect"][self.language])
        self.connect_button.setFixedWidth(config[self.os]["connect_button_w"])
        self.connect_button.clicked.connect(self.connect_button_on_click)

        self.rerender_notify_signal.rerender_view_box.connect(self.rerender_view_box_signal_on_receive)
        self.update_data_notify_signal.update_server_address.connect(self.update_server_address_signal_on_receive)
        self.update_data_notify_signal.update_download_dir.connect(self.update_download_dir_signal_on_receive)
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
