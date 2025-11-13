import sys
from typing import List, Optional, Dict, Any, Union
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QLineEdit, QMessageBox, QLabel, QFrame, QTextBrowser,
                             QVBoxLayout, QHBoxLayout, QSizePolicy, QDialog)
from PyQt6.QtGui import QCloseEvent, QShowEvent
import requests
from requests.exceptions import ConnectionError

from ui import *


class ChatWindow(QMainWindow, main_window.Ui_MainWindow):
    """
    Главное окно чата, отображающее сообщения и список пользователей.

    Attributes:
        window: Окно регистрации или авторизации
        main_user: Данные текущего пользователя
        wind: Окно профиля пользователя
        msb: Всплывающее окно для отображения ошибок
        chat_layout: Layout для отображения сообщений
        data: Данные, полученные с сервера
    """

    def __init__(self) -> None:
        """Инициализирует главное окно чата."""
        super().__init__()
        self.setupUi(self)
        self.initUI()

        self.update_timer: QTimer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(2000)

        self.window: Optional[Union[RegisterWidget, LoginWidget]] = None
        self.main_user: Optional[Dict[str, Union[str, int]]] = None
        self.wind: Optional[UserProfileModal] = None
        self.msb: QMessageBox = QMessageBox()
        self.msb.setWindowTitle('Ошибка')
        self.data: Dict[str, Any] = {}

    def initUI(self) -> None:
        """
        Инициализирует пользовательский интерфейс главного окна.

        Настраивает соединения сигналов с слотами и создает layout для сообщений.
        """
        self.message_btn.clicked.connect(self.send_message)
        self.my_btn.clicked.connect(self.show_my_profile)
        self.line_search.textChanged.connect(self.search_users)

        self.chat_layout = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(4)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.addStretch()

    def showEvent(self, event: QShowEvent) -> None:
        """
        Обрабатывает событие показа окна.

        Args:
            event: Событие показа окна
        """
        try:
            self.data = requests.get('http://127.0.0.1:5000/').json()
            self.loading_msg()
            self.loading_users()
        except ConnectionError:
            self.msb.setText('Связь с сервером не установлена!')
            self.msb.show()

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Обрабатывает событие закрытия окна.

        Args:
            event: Событие закрытия окна
        """
        self.update_timer.stop()
        if self.main_user:
            answer = requests.post('http://127.0.0.1:5000/change_state', json={'id': self.main_user['main_id']})

    def update_data(self) -> None:
        """Периодически обновляет сообщения и список пользователей"""
        if self.main_user:
            try:
                self.data = requests.get('http://127.0.0.1:5000/').json()
                self.loading_msg()
                self.loading_users()
            except ConnectionError:
                pass

    def send_message(self) -> None:
        """Отправляет сообщение в чат."""
        if self.message_line.text():
            data: Dict[str, str] = {
                'text': self.message_line.text(),
                'username': self.main_user['main_name']  # type: ignore
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

    def add_message_to_chat(self, text: str, is_my_message: bool = True, author: Optional[str] = None) -> None:
        """
        Добавляет сообщение в чат.

        Args:
            text: Текст сообщения
            is_my_message: Флаг, указывающий является ли сообщение своим
            author: Автор сообщения (если не свой)
        """
        max_width = int(self.scroll_chat.width() // 2)

        if is_my_message:
            author = self.main_user['main_name']  # type: ignore
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
        """Прокручивает чат до последнего сообщения."""
        scrollbar = self.scroll_chat.verticalScrollBar()
        QtCore.QTimer.singleShot(100, lambda: scrollbar.setValue(scrollbar.maximum()))

    def show_my_profile(self) -> None:
        """Отображает модальное окно с профилем текущего пользователя."""
        self.wind = UserProfileModal(
            self.main_user['main_name'],  # type: ignore
            self.main_user['main_id'],  # type: ignore
            self.main_user['main_descr'],  # type: ignore
            True
        )
        self.wind.setWindowTitle('Мой профиль')
        self.wind.show()

    def search_users(self) -> None:
        """Выполняет поиск пользователей по введенному тексту."""
        search_text = self.line_search.text().strip().lower()

        if search_text == "":
            self.loading_users()
        else:
            names = self.data.get('names', [])
            information = self.data.get('infos', [])
            ids = self.data['ids']
            states = self.data.get('states', [])

            grid_layout = self.scrollAreaWidgetContents_3.findChild(QtWidgets.QGridLayout, "gridLayout")
            if grid_layout:
                while grid_layout.count():
                    child = grid_layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

                visible_count = 0
                for i in range(len(names)):
                    if i < len(information) and i < len(ids) and i < len(states):
                        if str(names[i]) != str(self.main_user['main_name']):  # type: ignore
                            if search_text in names[i].lower():
                                self.add_profile(names[i], information[i], ids[i], states[i])

    def add_profile(self, name: str, info: str, id: int, state: bool) -> None:
        """
        Добавляет виджет профиля пользователя в список.

        Args:
            name: Имя пользователя
            info: Информация о пользователе
            id: ID пользователя
            state: Статус пользователя (online/offline)
        """
        profile = Profile(name, id, info, state, self.scrollAreaWidgetContents_3)
        grid_layout = self.scrollAreaWidgetContents_3.findChild(QtWidgets.QGridLayout, "gridLayout")

        if grid_layout is not None:
            current_count = grid_layout.count()
            row = current_count // 2
            col = current_count % 2

            grid_layout.addWidget(profile, row, col)
            grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def loading_msg(self) -> None:
        """Загружает и отображает сообщения из чата."""
        messages = self.data.get('messages', [])
        senders = self.data.get('sender_users', [])

        for i in reversed(range(self.chat_layout.count() - 1)):
            item = self.chat_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setParent(None)

        for i in range(len(messages)):
            if i < len(senders) and senders[i] == self.main_user['main_name']:  # type: ignore
                self.add_message_to_chat(messages[i], is_my_message=True)
            else:
                sender_name = senders[i] if i < len(senders) else "Неизвестный"
                self.add_message_to_chat(messages[i], is_my_message=False, author=sender_name)

    def loading_users(self) -> None:
        """Загружает и отображает список пользователей."""
        names = self.data.get('names', [])
        information = self.data.get('infos', [])
        ids: List[str] = self.data.get('ids', [])
        states = self.data.get('states', [])

        grid_layout = self.scrollAreaWidgetContents_3.findChild(QtWidgets.QGridLayout, "gridLayout")
        if grid_layout:
            while grid_layout.count():
                child = grid_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        for i in range(len(names)):
            if i < len(information) and i < len(ids) and i < len(states):
                if str(names[i]) != str(self.main_user['main_name']):
                    self.add_profile(names[i], information[i], ids[i], states[i])


class RegisterWidget(QWidget, register.Ui_Form):
    """
    Виджет регистрации нового пользователя.

    Attributes:
        msb: Всплывающее окно для отображения ошибок
    """

    def __init__(self) -> None:
        """Инициализирует виджет регистрации."""
        super().__init__()
        self.setupUi(self)
        self.initUI()

        self.msb: QMessageBox = QMessageBox(self)
        self.msb.setWindowTitle('Ошибка')

    def initUI(self) -> None:
        """Инициализирует пользовательский интерфейс виджета регистрации."""
        self.register_btn.clicked.connect(self.enter_in)

        self.password_line.setEchoMode(QLineEdit.EchoMode.Password)
        self.try_line.setEchoMode(QLineEdit.EchoMode.Password)

    def return_style(self) -> None:
        """Восстанавливает стандартные стили для всех полей ввода."""
        line_edits = self.findChildren(QLineEdit)
        labels = self.findChildren(QLabel)

        for line, lab in zip(line_edits, labels):
            line.setStyleSheet("border: .5px solid black;")
            lab.setStyleSheet("color: black;")

        self.description.setStyleSheet("border: .5px solid black;")

    def enter_in(self) -> None:
        """Обрабатывает попытку регистрации пользователя."""
        self.return_style()

        if self.name_line.text():
            if self.password_line.text():
                if self.description.toPlainText():
                    if self.try_line.text() and self.try_line.text() == self.password_line.text():
                        data: Dict[str, str] = {
                            "username": self.name_line.text(),
                            "password": self.password_line.text(),
                            "user_info": self.description.toPlainText(),
                        }

                        try:
                            answer: Dict[str, Union[bool, int, str]] = requests.post(
                                "http://127.0.0.1:5000/register",
                                json=data
                            ).json()

                            if answer['answer']:
                                window_chat.main_user = {
                                    'main_name': answer['main_name'],  # type: ignore
                                    'main_descr': answer['main_info'],  # type: ignore
                                    'main_id': answer['main_id']  # type: ignore
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


class LoginWidget(QWidget, login.Ui_Form):
    """
    Виджет авторизации пользователя.

    Attributes:
        msb: Всплывающее окно для отображения ошибок
    """

    def __init__(self) -> None:
        """Инициализирует виджет авторизации."""
        super().__init__()
        self.setupUi(self)
        self.initUI()

        self.msb: QMessageBox = QMessageBox(self)
        self.msb.setWindowTitle('Ошибка')

    def initUI(self) -> None:
        """Инициализирует пользовательский интерфейс виджета авторизации."""
        self.login_btn.clicked.connect(self.enter_in)

        self.password_line.setEchoMode(QLineEdit.EchoMode.Password)

    def return_style(self) -> None:
        """Восстанавливает стандартные стили для всех полей ввода."""
        line_edits = self.findChildren(QLineEdit)
        labels = self.findChildren(QLabel)

        for line, lab in zip(line_edits, labels):
            line.setStyleSheet("border: .5px solid black;")
            lab.setStyleSheet("color: black;")

    def enter_in(self) -> None:
        """Обрабатывает попытку авторизации пользователя."""
        self.return_style()

        if self.name_line.text():
            if self.password_line.text():
                data: Dict[str, str] = {
                    'username': self.name_line.text(),
                    'password': self.password_line.text()
                }

                try:
                    answer: Dict[str, Union[bool, int, str]] = requests.get(
                        "http://127.0.0.1:5000/login",
                        json=data
                    ).json()

                    if answer['answer']:
                        window_chat.main_user = {
                            'main_name': answer['main_name'],  # type: ignore
                            'main_descr': answer['main_info'],  # type: ignore
                            'main_id': answer['main_id']  # type: ignore
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


class ChoiceWidget(QWidget, choice.Ui_Form):
    """Виджет выбора между регистрацией и авторизацией."""

    def __init__(self) -> None:
        """Инициализирует виджет выбора."""
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self) -> None:
        """Инициализирует пользовательский интерфейс виджета выбора."""
        self.setFixedSize(400, 132)

        self.reg_btn.clicked.connect(self.click)
        self.log_btn.clicked.connect(self.click)

    def click(self) -> None:
        """Обрабатывает нажатие кнопки регистрации или авторизации."""
        if self.sender().objectName() == 'reg_btn':
            window_chat.window = RegisterWidget()
        else:
            window_chat.window = LoginWidget()

        window_chat.window.show()
        self.close()


class Profile(QWidget, profile.Ui_UserCard):
    """
    Виджет карточки пользователя в списке.

    Attributes:
        name: Имя пользователя
        id: ID пользователя
        info: Информация о пользователе
        state: Статус пользователя (online/offline)
        modal: Модальное окно с детальной информацией о пользователе
    """

    def __init__(self, name: str, id: int, info: str, state: bool, parent: Optional[QWidget] = None):
        """
        Инициализирует виджет карточки пользователя.

        Args:
            name: Имя пользователя
            id: ID пользователя
            info: Информация о пользователе
            state: Статус пользователя
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.setupUi(self)
        self.name = name
        self.id = id
        self.info = info
        self.state = state
        self.modal: Optional[UserProfileModal] = None
        self.initUI()

    def initUI(self) -> None:
        """Инициализирует пользовательский интерфейс карточки пользователя."""
        self.setFixedSize(304, 120)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

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
        """Открывает модальное окно с детальной информацией о пользователе."""
        self.modal = UserProfileModal(self.name, self.id, self.info, self.state)
        self.modal.show()


class UserProfileModal(QDialog, modal_profile.Ui_UserProfileModal):
    """
    Модальное окно с детальной информацией о пользователе.

    Attributes:
        name: Имя пользователя
        id: ID пользователя
        info: Информация о пользователе
        state: Статус пользователя (online/offline)
    """

    def __init__(self, name: str, id: int, info: str, state: bool):
        """
        Инициализирует модальное окно профиля пользователя.

        Args:
            name: Имя пользователя
            id: ID пользователя
            info: Информация о пользователе
            state: Статус пользователя
        """
        super().__init__()
        self.setupUi(self)
        self.name = name
        self.id = id
        self.info = info
        self.state = state
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle(f"Профиль {name}")
        self.initUI()

    def initUI(self) -> None:
        """Инициализирует пользовательский интерфейс модального окна."""
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
    """
    Виджет сообщения в чате.

    Attributes:
        is_my_message: Флаг, указывающий является ли сообщение своим
        max_width: Максимальная ширина сообщения
        author: Автор сообщения
        text: Текст сообщения
        author_label: Метка с именем автора (для чужих сообщений)
        text_browser: Виджет для отображения текста сообщения
    """

    def __init__(self, text: str, author: str, is_my_message: bool = True, max_width: int = 300):
        """
        Инициализирует виджет сообщения.

        Args:
            text: Текст сообщения
            author: Автор сообщения
            is_my_message: Флаг, указывающий является ли сообщение своим
            max_width: Максимальная ширина сообщения
        """
        super().__init__()
        self.is_my_message = is_my_message
        self.max_width = max_width
        self.author = author
        self.text = text
        self.author_label: Optional[QLabel] = None
        self.text_browser: Optional[QTextBrowser] = None
        self.initUI()

    def initUI(self) -> None:
        """Инициализирует пользовательский интерфейс виджета сообщения."""
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

    def set_message(self, text: str) -> None:
        """
        Устанавливает текст сообщения.

        Args:
            text: Текст сообщения
        """
        if self.text_browser:
            self.text_browser.setText(text)
            self.adjust_size()

    def adjust_size(self) -> None:
        """Настраивает размер виджета сообщения в соответствии с содержимым."""
        if not self.text_browser:
            return

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

if __name__ == '__main__':
    """
    Точка входа в приложение.

    Создает и отображает начальное окно выбора (регистрация/авторизация).
    """
    app = QApplication(sys.argv)
    window_chat: ChatWindow = ChatWindow()
    window_choice: ChoiceWidget = ChoiceWidget()
    window_choice.show()
    sys.exit(app.exec())
