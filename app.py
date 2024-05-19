# Иморты
from flask import Flask, render_template, request, redirect, flash, url_for, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import NotFound, InternalServerError
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from os import remove

# Импорты для работы с датой и временем
from datetime import datetime
import pytz

# Импорт модулей для работы с БД
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

# Создание flask приложения
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4AUfadnhDc\n\xec]/'

# Настройка Менеджера логинов
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message = 'Для доступа необходимо осуществить вход в систему'

# Настройка базы данных
engine = create_engine('sqlite:///database.db')
Base = declarative_base()

# Создание модели AUTH
class Auth(Base):
    __tablename__ = 'authorized_users'
    id = Column(Integer, primary_key=True)
    login = Column(String(32), nullable=False, unique=True)
    password = Column(String(32), nullable=False)
    user_name = Column(String(32), nullable=False)
    user_last_name = Column(String(32), nullable=True)
    user_city = Column(String(32), nullable=True)
    user_tags = Column(String, nullable=True)
    user_birthdate = Column(String)
    date_creation = Column(String)
    user_phone = Column(String)
    user_email = Column(String)
    user_org = Column(String(32), nullable=True)
    status = Column(String, default="Волонтёр")
    admin_access = Column(Boolean, default=False)
    user_verificated_hours = Column(Integer, default=0)
    user_good_actions = Column(Integer, default=0)
    user_v_coins = Column(Integer, default=0)

# Создание базы данных
Base.metadata.create_all(engine)
# Создание сессий
session = sessionmaker(bind=engine)()
session.rollback()

# Создание класса пользователя
class UserLogin():
    def fromDB(self, user_id):
        self.__id = user_id
        return self

    def create(self, user):
        self.__id = user.id
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymoys(self):
        return False

    def get_id(self):
        return self.__id

# Обработчик загрузок пользователей
@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id)

#######################################################################################
#                        ___    ___           ___         _____                       #
#               |\  /|  |___|  |___|  |   |  |___|  \  /    |    |    |               #
#               | \/ |  |   |  |      | | |  |       \/     |    |__  |               # 
#               |    |  |   |  |      |_|_|  |       /      |    |__| |               #
#                                                                                     #
#######################################################################################

# ------------ Обработка пути '/' ------------ 
@app.route("/", methods=['GET', 'POST'])
def home_page():
    return render_template("home_page.html")

@app.route("/login", methods=['GET', 'POST'])
def login_page():
    return render_template("login_page.html")

@app.route("/register", methods=['GET', 'POST'])
def register_page():
    # Если POST запрос
    if request.method == 'POST':

        # Получение данных из формы
        login = request.form['login']
        name = request.form['name']
        password = request.form['pass']
        password_repeat = request.form['pass_repeat']

        # Проверка на соответствие введённых данных
        if len(login) > 4 and len(login) <= 32 and len(name) > 4 and len(name) <= 32\
                and len(password) > 5 and len(password) <= 32 and password == password_repeat:
            # Проверка логина
            if not check_login(login):
                # Генерация скрытого пароля
                pass_hash = generate_password_hash(password)
                # Отправка в базу данных
                datedb = datetime.now(pytz.timezone('Europe/Moscow'))
                session.add(Auth(login=login, password=pass_hash, user_name=name, date_creation=date_format(datedb)))
                session.commit()
                # Отправка сообщения пользователю об успехе
                flash('Вы успешно зарегистрированы', 'success')
                # Перевод пользователя в разел /login
                return redirect(url_for('login_page'))
            else:
                # Отправка сообщения пользователю о том, что логин уже занят
                flash('Такой логин уже существует', 'warning')
        else:
            # Отправка сообщения пользователю о том, что пароли не совпадают
            flash('Пароли не совпадают', 'error')

    # Возврат шаблона register_page.html
    return render_template("register_page.html")

app.run(debug=True)