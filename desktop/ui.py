import sys
from typing import List
from PyQt6 import uic, QtCore, QtWidgets
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                             QLineEdit, QMessageBox, QLabel, QFrame, QTextBrowser,
                             QVBoxLayout, QHBoxLayout, QSizePolicy, QDialog)
from PyQt6.QtGui import QTextDocument
import requests
from requests.exceptions import ConnectionError


class ChatWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('desktop/ui_files/main_window.ui', self)
        self.initUI()

        self.window: None | RegisterWidget | LoginWidget = None
        self.main_user: dict[str, str | int] | None = None
        self.wind: Profile | None = None
        self.msb: QMessageBox = QMessageBox()
        self.msb.setWindowTitle('Ошибка')

    def initUI(self) -> None:
        self.message_btn.clicked.connect(self.send_message)
        self.my_btn.clicked.connect(self.show_my_profile)
        self.line_search.textChanged.connect(self.search_users)

        self.chat_layout = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(4)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.addStretch()

    def showEvent(self, event) -> None:
        try:
            self.data = requests.get('http://127.0.0.1:5000/').json()
            self.loading()
        except ConnectionError:
            self.msb.setText('Связь с сервером не установлена!')
            self.msb.show()

    def closeEvent(self, event) -> None:
        answer = requests.post('http://127.0.0.1:5000/change_state', json={'id': self.main_user['main_id']})

    def send_message(self) -> None:
        if self.message_line.text():
            data: dict[str, str] = {
                'text': self.message_line.text(),
                'username': self.main_user['main_name']
            }

            try:
                answer = requests.post('http://127.0.0.1:5000/send_message', json=data).json()
                if not answer['answer']:
                    self.msb.setText('Ошибка отправки!')
                    self.msb.show()
                else:
                    self.add_message_to_chat(self.message_line.text(), is_my_message=True)
                    self.message_line.clear()
            except ConnectionError:
                self.msb.setText('Ошибка отправки!')
                self.msb.show()

    def add_message_to_chat(self, text, is_my_message=True, author=None):
        max_width = int(self.scroll_chat.width() // 2)

        # Определяем автора
        if is_my_message:
            author = self.main_user['main_name']
        elif author is None:
            author = "Другой пользователь"

        message_widget = ChatMessage(text, author, is_my_message, max_width)

        message_container = QWidget()
        message_container_layout = QHBoxLayout(message_container)
        message_container_layout.setContentsMargins(0, 0, 0, 0)

        if is_my_message:
            message_container_layout.addStretch()
            message_container_layout.addWidget(message_widget)
        else:
            message_container_layout.addWidget(message_widget)
            message_container_layout.addStretch()

        self.chat_layout.insertWidget(self.chat_layout.count() - 1, message_container)
        self.scroll_to_bottom()

    def scroll_to_bottom(self) -> None:
        scrollbar = self.scroll_chat.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def show_my_profile(self) -> None:
        self.wind: UserProfileModal = UserProfileModal(
            self.main_user['main_name'],
            self.main_user['main_id'],
            self.main_user['main_descr'],
            True
        )
        self.wind.setWindowTitle('Мой профиль')
        self.wind.show()

    def search_users(self) -> None:
        ...

    def add_profile(self, name, info, id, state) -> None:
        # Создаем карточку профиля
        profile = Profile(name, id, info, state, self.scrollAreaWidgetContents_3)

        # Получаем gridLayout
        grid_layout = self.scrollAreaWidgetContents_3.findChild(QtWidgets.QGridLayout, "gridLayout")

        if grid_layout:
            # Находим следующую свободную позицию в сетке
            row = grid_layout.rowCount()
            col = grid_layout.columnCount()

            # Расчет позиции для 2 карточек в строке
            current_row = row
            current_col = col % 2  # 0 или 1 для двух колонок

            # Если это первая карточка в строке, увеличиваем счетчик строк
            if current_col == 0 and col > 0:
                current_row += 1

            # Добавляем карточку в сетку
            grid_layout.addWidget(profile, current_row, current_col)

            # Обновляем layout
            grid_layout.update()

    def loading(self):
        messages = self.data.get('messages', [])
        senders = self.data.get('sender_users', [])

        for i in reversed(range(self.chat_layout.count() - 1)):
            item = self.chat_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)

        for i in range(len(messages)):
            if i < len(senders) and senders[i] == self.main_user['main_name']:
                self.add_message_to_chat(messages[i], is_my_message=True)
            else:
                sender_name = senders[i] if i < len(senders) else "Неизвестный"
                self.add_message_to_chat(messages[i], is_my_message=False, author=sender_name)

        names = self.data.get('names', [])
        information = self.data.get('infos', [])
        ids: List[str] = self.data['ids']
        states = self.data.get('states', [])

        grid_layout = self.scrollAreaWidgetContents_3.findChild(QtWidgets.QGridLayout, "gridLayout")
        if grid_layout:
            for i in reversed(range(grid_layout.count())):
                item = grid_layout.itemAt(i)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.setParent(None)

        for i in range(len(names)):
            if i < len(information) and i < len(ids) and i < len(states):
                if str(names[i]) != str(self.main_user['main_name']):
                    self.add_profile(names[i], information[i], ids[i], states[i])


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
                            answer: dict[str, bool | int] = requests.post(
                                "http://127.0.0.1:5000/register",
                                json=data
                            ).json()

                            if answer['answer']:
                                window_chat.main_user = {
                                    'main_name': answer['main_name'],
                                    'main_descr': answer['main_info'],
                                    'main_id': answer['main_id']
                                }
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

        self.msb: QMessageBox = QMessageBox(self)
        self.msb.setWindowTitle('Ошибка')

    def initUI(self) -> None:
        self.login_btn.clicked.connect(self.enter_in)

        self.password_line.setEchoMode(QLineEdit.EchoMode.Password)

    def return_style(self) -> None:
        line_edits = self.findChildren(QLineEdit)
        labels = self.findChildren(QLabel)

        for line, lab in zip(line_edits, labels):
            line.setStyleSheet("border: .5px solid black;")
            lab.setStyleSheet("color: black;")

    def enter_in(self) -> None:
        self.return_style()

        if self.name_line.text():
            if self.password_line.text():
                data: dict[str, str] = {
                    'username': self.name_line.text(),
                    'password': self.password_line.text()
                }

                try:
                    answer: dict[str, bool | int] = requests.get(
                        "http://127.0.0.1:5000/login",
                        json=data
                    ).json()

                    if answer['answer']:
                        window_chat.main_user = {
                            'main_name': answer['main_name'],
                            'main_descr': answer['main_info'],
                            'main_id': answer['main_id']
                        }
                        window_chat.show()
                        self.close()
                    else:
                        self.msb.setText('Неверное имя пользователя или пароль!')
                        self.msb.show()
                except ConnectionError:
                    self.msb.setText('Сервер недоступен!')
                    self.msb.show()

            else:
                self.password_line.setStyleSheet("border: 1px solid red;")
                self.label_2.setStyleSheet("color: red")
        else:
            self.name_line.setStyleSheet("border: 1px solid red;")
            self.label.setStyleSheet("color: red")


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


class Profile(QWidget):
    def __init__(self, name, id, info, state, parent=None):
        super().__init__(parent)
        uic.loadUi('desktop/ui_files/profile.ui', self)
        self.name = name
        self.id = id
        self.info = info
        self.state = state
        self.initUI()

    def initUI(self) -> None:
        self.nameLabel.setText(self.name)
        self.idLabel.setText(f"ID: {self.id}")

        if len(self.info) > 50:
            self.infoLabel.setText(self.info[:47] + "...")
        else:
            self.infoLabel.setText(self.info)

        if self.state:
            self.statusLabel.setText("● В сети")
            self.statusLabel.setStyleSheet("font-size: 11px; color: #28a745;")
        else:
            self.statusLabel.setText("○ Не в сети")
            self.statusLabel.setStyleSheet("font-size: 11px; color: #dc3545;")

        self.detailsBtn.clicked.connect(self.open_details)

    def open_details(self) -> None:
        self.modal = UserProfileModal(self.name, self.id, self.info, self.state)
        self.modal.show()


class UserProfileModal(QDialog):
    def __init__(self, name, id, info, state, parent=None):
        super().__init__(parent)
        uic.loadUi('desktop/ui_files/modal_profile.ui', self)
        self.name = name
        self.id = id
        self.info = info
        self.state = state
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle(f"Профиль {name}")
        self.initUI()

    def initUI(self) -> None:
        self.modalNameLabel.setText(self.name)
        self.modalIdLabel.setText(f"ID: {self.id}")
        self.infoTextEdit.setText(self.info)

        if self.state:
            self.modalStatusLabel.setText("● В сети")
            self.modalStatusLabel.setStyleSheet("font-size: 14px; color: #28a745; font-weight: bold;")
        else:
            self.modalStatusLabel.setText("○ Не в сети")
            self.modalStatusLabel.setStyleSheet("font-size: 14px; color: #dc3545; font-weight: bold;")

        self.modalCloseBtn.clicked.connect(self.close)
        self.setFixedSize(400, 350)


class ChatMessage(QWidget):
    def __init__(self, text, author, is_my_message=True, max_width=300, parent=None):
        super().__init__(parent)
        self.is_my_message = is_my_message
        self.max_width = max_width
        self.author = author
        self.text = text
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        if not self.is_my_message:
            self.author_label = QLabel(self.author)
            self.author_label.setStyleSheet("""
                QLabel {
                    color: #666;
                    font-size: 11px;
                    padding: 0px 5px;
                }
            """)
            self.author_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(self.author_label)

        self.text_browser = QTextBrowser()
        self.text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_browser.setFrameShape(QFrame.Shape.NoFrame)
        self.text_browser.setReadOnly(True)

        if self.is_my_message:
            self.text_browser.setStyleSheet("""
                QTextBrowser {
                    background-color: #0084ff;
                    color: white;
                    border-radius: 12px;
                    padding: 8px 12px;
                    margin: 0px;
                }
            """)
        else:
            self.text_browser.setStyleSheet("""
                QTextBrowser {
                    background-color: grey;
                    color: black;
                    border-radius: 12px;
                    padding: 8px 12px;
                    margin: 0px;
                }
            """)

        layout.addWidget(self.text_browser)
        self.set_message(self.text)

    def set_message(self, text):
        self.text_browser.setText(text)
        self.adjust_size()

    def adjust_size(self):
        doc = self.text_browser.document()
        doc.setTextWidth(self.max_width)

        ideal_width = min(doc.idealWidth() + 25, self.max_width)
        text_height = int(doc.size().height()) + 20

        self.text_browser.setFixedSize(int(ideal_width), text_height)

        if self.is_my_message:
            self.setFixedSize(int(ideal_width) + 10, text_height)
        else:
            author_height = 15
            self.setFixedSize(int(ideal_width) + 10, text_height + author_height)


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
