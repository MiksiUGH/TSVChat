import sys
from PyQt6 import uic, QtCore, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLineEdit, QMessageBox
import requests
from requests.exceptions import ConnectionError


class ChatWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('desktop/ui_files/main_window.ui', self)
        self.initUI()
        self.window: None | RegisterWidget | LoginWidget = None

    def initUI(self) -> None:
        ...


class RegisterWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('desktop/ui_files/register.ui', self)
        self.initUI()

        msb: QMessageBox = QMessageBox(self)
        msb.setWindowTitle('Ошибка')

    def initUI(self) -> None:
        self.register_btn.clicked.connect(self.enter_in)

        self.password_line.setEchoMode(QLineEdit.EchoMode.Password)
        self.try_line.setEchoMode(QLineEdit.EchoMode.Password)

    def enter_in(self) -> None:
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
                            answer: dict[str, bool] = requests.post("http://127.0.0.1:5000/register", json=data)
                            if answer:
                                window_chat.show()
                                self.close()
                            else:
                                msb.setText('Ошибка со стороны сервера!')
                                msb.show()

                        except ConnectionError:
                            msb.setText('Сервер недоступен!')
                            msb.show()

                    else:
                        if self.try_line.text() != self.password_line.text():
                            msb.setText('Пароли не совпадают!')
                            msb.show()
                        else:
                            self.try_line.setStyleSheet("border: 1px solid red;")
                            self.label_4.setStyleSheet("color: red")
                else:
                    self.description.setStyleSheet("border: 1px solid red;")
                    self.label_2.setStyleSheet("color: red")
            else:
                self.password.setStyleSheet("border: 1px solid red;")
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
        ...


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
