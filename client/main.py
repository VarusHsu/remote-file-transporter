import json
import sys
import os
from threading import Thread

import requests
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QWidget, QListWidget, QPushButton, QLabel, QLineEdit, QFileDialog

import i18n
from config import config


class RerenderNotifySignal(QObject):
    rerender_view_box = pyqtSignal(list)
    rerender_view_box_files = pyqtSignal(list)
    pass


class UpdateDataNotifySignal(QObject):
    update_download_dir = pyqtSignal(str)
    update_cur_server_dir = pyqtSignal(str)
    update_server_address = pyqtSignal(str)
    pass


class ViewBox(QListWidget):
    rightClicked = pyqtSignal()

    def mousePressEvent(self, e) -> None:
        super().mousePressEvent(e)
        if e.button() == Qt.MouseButton.RightButton:
            self.rightClicked.emit()


class SettingWindows:
    # widget
    windows: QWidget
    save_button: QPushButton
    cancel_button: QPushButton
    server_ip_label: QLabel
    download_dir_label: QLabel
    server_ip_line_edit: QLineEdit
    download_dir_line_edit: QLineEdit
    select_button: QPushButton
    select_dir_filedialog: QFileDialog

    # config
    os: str
    language: str
    server_address: str
    download_dir: str

    # signals
    update_data_notify_signal: UpdateDataNotifySignal
    rerender_notify_signal: RerenderNotifySignal

    def __init__(self, os: str, language: str, server_address: str, download_dir: str,
                 update_data_notify_signal: UpdateDataNotifySignal, rerender_notify_signal: RerenderNotifySignal):
        self.os = os
        self.language = language
        self.update_data_notify_signal = update_data_notify_signal
        self.rerender_notify_signal = rerender_notify_signal
        self.download_dir = download_dir
        self.server_address = server_address

    def save_button_on_click(self):
        self.windows.close()
        self.update_data_notify_signal.update_download_dir.emit(self.download_dir_line_edit.text())
        self.update_data_notify_signal.update_server_address.emit(self.server_ip_line_edit.text())
        self.update_data_notify_signal.update_cur_server_dir.emit("")
        self.download_dir = self.download_dir_line_edit.text()
        self.server_address = self.server_ip_line_edit.text()
        self.set_cache()
        pass

    def cancel_button_on_click(self):
        self.windows.close()

    def select_button_on_click(self):
        self.select_dir_filedialog = QFileDialog(self.windows)
        self.select_dir_filedialog.setWindowTitle(i18n.i18n["DownloadTo"][self.language])
        self.select_dir_filedialog.setFileMode(QFileDialog.FileMode.Directory)
        directory = self.select_dir_filedialog.getExistingDirectory()
        if directory != "":
            self.download_dir = directory
            self.download_dir_line_edit.setText(directory)
        self.select_dir_filedialog.close()
        pass

    @staticmethod
    def get_user_home_path() -> str:
        return os.path.expanduser("~")

    def set_cache(self):
        file = os.path.join(self.get_user_home_path(), ".rft_cache")
        with open(file, "w") as f:
            f.write(self.server_address + "\n")
            f.write(self.download_dir + "\n")
        pass

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
        self.server_ip_line_edit.setText(self.server_address)

        self.download_dir_line_edit = QLineEdit(self.windows)
        self.download_dir_line_edit.setFixedWidth(config[self.os]["download_dir_line_edit_w"])
        self.download_dir_line_edit.move(config[self.os]["download_dir_line_edit_move_w"],
                                         config[self.os]["download_dir_line_edit_move_h"])
        self.download_dir_line_edit.setText(self.download_dir)

        self.select_button = QPushButton(self.windows)
        self.select_button.setText(i18n.i18n["Select"][self.language])
        self.select_button.move(config[self.os]["select_button_move_w"], config[self.os]["select_button_move_h"])
        self.select_button.setFixedWidth(config[self.os]["select_button_w"])
        self.select_button.clicked.connect(self.select_button_on_click)

        self.windows.show()
        pass


class RemoteFileTransporterClient:
    # widgets
    app: QApplication
    windows: QWidget
    view_box: ViewBox
    setting_button: QPushButton
    connect_button: QPushButton
    setting_window: SettingWindows

    # configs
    cur_server_path: str
    cur_server_walked: list
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
        self.get_cache()
        self.cur_server_dir = ""
        self.cur_server_walked = []

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

    def view_box_on_double_click(self):
        if len(self.cur_server_walked) == 0:
            return
        clicked_text = self.view_box.currentItem().text()
        item = None
        for file in self.cur_server_walked:
            if clicked_text == file["name"]:
                item = file
                break
        if item is None:
            return
        if item["type"] == "dir":
            if item["name"] == ".":
                return
            elif item["name"] == "..":
                if self.cur_server_dir == "/":
                    return
                else:
                    if self.cur_server_dir.rfind("/") == 0:
                        path = "/"
                    else:
                        path = self.cur_server_dir[0:self.cur_server_dir.rfind("/")]
                    print(path)
            else:
                path = self.cur_server_dir + f"/{item['name']}"
            url = "http://" + self.server_address + ":50422" + f"/visit?path={path}"
            self.cur_server_dir = path
            print(url)
            self.get_walk_dir_from_remote(url)
        else:
            pass

    def view_box_on_right_click(self):
        pass

    def update_download_dir_signal_on_receive(self, path: str):
        self.download_dir = path

    def update_server_address_signal_on_receive(self, address: str):
        self.server_address = address

    def update_cur_server_dir_signal_on_receive(self, path: str):
        self.cur_server_dir = path

    def rerender_view_box_signal_on_receive(self, items: list):
        self.view_box.clear()
        for item in items:
            self.view_box.addItem(item)

    def rerender_view_box_dir_signal_on_receive(self, items: list):
        self.view_box.clear()
        for item in items:
            self.view_box.addItem(item["name"])
        i = 0
        font = QFont()
        font.setBold(True)
        for item in items:
            if item["type"] == "dir":
                self.view_box.item(i).setFont(font)
            i += 1

    def get_home_dir_from_remote(self):
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
                url = "http://" + self.server_address + ":50422" + f"/visit?path={context['response']}"

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

                res = [{"name": ".", "type": "dir"}, {"name": "..", "type": "dir"}] + response[
                    "items"]
                self.cur_server_walked = res
                self.rerender_notify_signal.rerender_view_box_files.emit(res)
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
        url = "http://" + self.server_address + ":50422" + f"/visit?path={self.cur_server_dir}"
        self.get_walk_dir_from_remote(url=url)

    @staticmethod
    def get_user_home_path() -> str:
        return os.path.expanduser("~")

    def get_default_download_path(self) -> str:
        return os.path.join(self.get_user_home_path(), "Downloads")

    def get_cache(self) -> bool:
        file = os.path.join(self.get_user_home_path(), ".rft_cache")
        if not os.path.exists(file):
            self.download_dir = self.get_default_download_path()
            self.server_address = ""
            return False
        with open(file) as f:
            self.server_address = f.readline()[0:-1]
            self.download_dir = f.readline()[0:-1]
            return True

    def render(self):
        self.app = QApplication(sys.argv)
        self.windows = QWidget()
        self.windows.setFixedSize(config[self.os]["windows_w"], config[self.os]["windows_h"])
        self.windows.setWindowTitle(i18n.i18n["Remote File Transporter"][self.language])

        self.view_box = ViewBox(self.windows)
        self.view_box.move(config[self.os]["view_box_move_w"], config[self.os]["view_box_move_h"])
        self.view_box.resize(config[self.os]["view_box_w"], config[self.os]["view_box_h"])
        self.view_box.addItem(i18n.i18n["Welcome"][self.language])
        self.view_box.doubleClicked.connect(self.view_box_on_double_click)
        self.view_box.rightClicked.connect(self.view_box_on_right_click)

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
        self.rerender_notify_signal.rerender_view_box_files.connect(self.rerender_view_box_dir_signal_on_receive)
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
