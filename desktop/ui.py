import sys
from PyQt6 import uic, QtCore, QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
import requests


class ChatWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('desktop/ui_files/...', self)
        self.initUI()

    def initUI(self) -> None:
        ...


class RegisterWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('desktop/ui_files/...', self)
        self.initUI()

    def initUI(self) -> None:
        ...


class LoginWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('desktop/ui_files/...', self)
        self.initUI()

    def initUI(self) -> None:
        ...


class ChoiceWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('desktop/ui_files/...', self)
        self.initUI()

    def initUI(self) -> None:
        ...


if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

def excepthook(a, b, c) -> None:
    sys.__excepthook__(a, b, c)

if __name__ == '__main__':
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())