import sys
from PyQt6 import uic, QtCore, QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
import requests


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

    def initUI(self) -> None:
        ...


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