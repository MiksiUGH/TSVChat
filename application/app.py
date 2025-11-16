import flask
from typing import Tuple, Any, Dict, List, Optional
from sqlalchemy import select, Select
import datetime

from application.models import User, UserMessage, UserProfile, MAIN_SESSION, Base, ENGINE

app: flask.Flask = flask.Flask(__name__)
"""Экземпляр Flask-приложения."""

with app.app_context():
    Base.metadata.create_all(bind=ENGINE)
"""Создание таблиц в БД"""


@app.route('/register', methods=['POST'])
def registration() -> Tuple[flask.Response, int]:
    """
    Регистрирует нового пользователя в системе.

    Returns:
        Tuple[flask.Response, int]: JSON-ответ с данными пользователя и HTTP-статус

    Example JSON request:
        {
            "username": "john_doe",
            "user_info": "Информация о пользователе",
            "password": "secret_password"
        }
    """
    data: Dict[str, Any] = flask.request.json
    username: str = data.get('username', '')
    user_info: str = data.get('user_info', '')
    user_password: str = data.get('password', '')

    with MAIN_SESSION() as session:
        new_user: User = User(username=username)
        new_user_profile: UserProfile = UserProfile(
            user_info=user_info,
            user_password=user_password,
            user=new_user,
            user_state=True
        )
        session.add(new_user)
        session.add(new_user_profile)
        session.commit()

        selected: Select = select(User.id).order_by(User.id.desc())
        user_id: int = session.scalars(selected).first()

        return flask.jsonify({
            'answer': True,
            'main_id': user_id,
            'main_name': username,
            'main_info': user_info,
        }), 200


@app.route('/login', methods=['GET'])
def login() -> Tuple[flask.Response, int]:
    """
    Аутентифицирует пользователя в системе.

    Returns:
        Tuple[flask.Response, int]: JSON-ответ с результатом аутентификации и HTTP-статус

    Example JSON request:
        {
            "username": "john_doe",
            "password": "secret_password"
        }
    """
    data: Dict[str, Any] = flask.request.json
    username: str = data.get('username', '')
    password: str = data.get('password', '')

    result: Dict[str, Any] = {'answer': False, 'main_id': 0}

    with MAIN_SESSION() as session:
        user: Optional[User] = session.scalar(
            select(User).where(User.username == username)
        )

        if user:
            user_profile: Optional[UserProfile] = session.scalar(
                select(UserProfile).where(UserProfile.user_id == user.id)
            )

            if user_profile and user_profile.user_password == password:
                result.update({
                    'answer': True,
                    'main_id': user_profile.user_id,
                    'main_name': username,
                    'main_info': user_profile.user_info
                })
                user_profile.user_state = True
                session.commit()

    return flask.jsonify(result), 200


@app.route('/', methods=['GET'])
def index() -> Tuple[flask.Response, int]:
    """
    Возвращает основную информацию о всех пользователях и сообщениях.

    Returns:
        Tuple[flask.Response, int]: JSON-ответ с данными системы и HTTP-статус
    """
    with MAIN_SESSION() as session:
        users_name: List[str] = session.scalars(select(User.username)).all()
        users_info: List[str] = session.scalars(select(UserProfile.user_info)).all()
        users_id: List[int] = session.scalars(select(User.id)).all()
        users_messages: List[str] = session.scalars(select(UserMessage.message)).all()
        sender_users: List[str] = session.scalars(select(UserMessage.user_name)).all()
        users_state: List[bool] = session.scalars(select(UserProfile.user_state)).all()

        return flask.jsonify({
            'names': users_name,
            'infos': users_info,
            'messages': users_messages,
            'ids': users_id,
            'sender_users': sender_users,
            'states': users_state
        }), 200


@app.route('/send_message', methods=['POST'])
def send_message() -> Tuple[flask.Response, int]:
    """
    Отправляет новое сообщение от имени пользователя.

    Returns:
        Tuple[flask.Response, int]: JSON-ответ с результатом операции и HTTP-статус

    Example JSON request:
        {
            "text": "Текст сообщения",
            "username": "john_doe"
        }
    """
    data: Dict[str, Any] = flask.request.json
    new_message: UserMessage = UserMessage(
        date=str(datetime.datetime.now()),
        message=data.get('text', ''),
        user_name=data.get('username', '')
    )

    with MAIN_SESSION() as session:
        session.add(new_message)
        session.commit()
        return flask.jsonify({'answer': True}), 200


@app.route('/change_state', methods=['POST'])
def change_state() -> Tuple[flask.Response, int]:
    """
    Изменяет состояние пользователя на неактивное.

    Returns:
        Tuple[flask.Response, int]: Пустой ответ и HTTP-статус

    Example JSON request:
        {
            "id": 1
        }
    """
    user_id: int = flask.request.json['id']

    with MAIN_SESSION() as session:
        profile: Optional[UserProfile] = session.scalar(
            select(UserProfile).where(UserProfile.id == user_id)
        )
        if profile:
            profile.user_state = False
            session.commit()

    return flask.Response('', status=200), 200


if __name__ == '__main__':
    app.run(debug=True)
