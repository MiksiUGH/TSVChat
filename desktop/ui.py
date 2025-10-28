import sys
from PyQt6 import uic, QtCore, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                             QLineEdit, QMessageBox, QLabel)
import requests
from requests.exceptions import ConnectionError


class ChatWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('desktop/ui_files/main_window.ui', self)
        self.initUI()
        self.window: None | RegisterWidget | LoginWidget = None
        self.main_id: int | None = None

    def initUI(self) -> None:
        ...


class RegisterWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('desktop/ui_files/register.ui', self)
        self.initUI()

        self.msb: QMessageBox = QMessageBox(self)
        self.msb.setWindowTitle('Ошибка')

    def initUI(self) -> None:
        self.register_btn.clicked.connect(self.enter_in)

        self.password_line.setEchoMode(QLineEdit.EchoMode.Password)
        self.try_line.setEchoMode(QLineEdit.EchoMode.Password)

    def return_style(self) -> None:
        line_edits = self.findChildren(QLineEdit)
        labels = self.findChildren(QLabel)

        for line, lab in zip(line_edits, labels):
            line.setStyleSheet("border: .5px solid black;")
            lab.setStyleSheet("color: black;")

        self.description.setStyleSheet("border: .5px solid black;")

    def enter_in(self) -> None:
        self.return_style()

        if self.name_line.text():
            if self.password_line.text():
                if self.description.toPlainText():
                    if self.try_line.text() and self.try_line.text() == self.password_line.text():
                        data: dict[str, str] = {
                            "username": self.name_line.text(),
                            "password": self.password_line.text(),
                            "user_info": self.description.toPlainText(),
                        }

                        try:
                            answer: dict[str, bool | int] = requests.post("http://127.0.0.1:5000/register", json=data)
                            if answer['answer']:
                                window_chat.main_id = answer['main_id']
                                window_chat.show()
                                self.close()
                            else:
                                self.msb.setText('Ошибка со стороны сервера!')
                                self.msb.show()

                        except ConnectionError:
                            self.msb.setText('Сервер недоступен!')
                            self.msb.show()

                    else:
                        if not self.try_line.text():
                            self.try_line.setStyleSheet("border: 1px solid red;")
                            self.label_4.setStyleSheet("color: red")
                        else:
                            self.msb.setText('Пароли не совпадают!')
                            self.msb.show()
                else:
                    self.description.setStyleSheet("border: 1px solid red;")
                    self.label_2.setStyleSheet("color: red")
            else:
                self.password_line.setStyleSheet("border: 1px solid red;")
                self.label_3.setStyleSheet("color: red")
        else:
            self.name_line.setStyleSheet("border: 1px solid red;")
            self.label.setStyleSheet("color: red")


class LoginWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('desktop/ui_files/login.ui', self)
        self.initUI()

    def initUI(self) -> None:
        self.login_btn.clicked.connect(self.enter_in)

    def return_style(self) -> None:
        line_edits = self.findChildren(QLineEdit)
        labels = self.findChildren(QLabel)

        for line, lab in zip(line_edits, labels):
            line.setStyleSheet("border: .5px solid black;")
            lab.setStyleSheet("color: black;")

    def enter_in(self) -> None:
        self.return_style()


class ChoiceWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('desktop/ui_files/choice.ui', self)
        self.initUI()

    def initUI(self) -> None:
        self.setFixedSize(400, 132)

        self.reg_btn.clicked.connect(self.click)
        self.log_btn.clicked.connect(self.click)

    def click(self) -> None:
        if self.sender().objectName() == 'reg_btn':
            window_chat.window = RegisterWidget()
        else:
            window_chat.window = LoginWidget()

        window_chat.window.show()
        self.close()


if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

def excepthook(a, b, c) -> None:
    sys.__excepthook__(a, b, c)

if __name__ == '__main__':
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    window_chat: ChatWindow = ChatWindow()
    window_choice: ChoiceWidget = ChoiceWidget()
    window_choice.show()
    sys.exit(app.exec())
