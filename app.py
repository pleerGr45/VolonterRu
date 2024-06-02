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
    password = Column(String(32), nullable=False)
    user_name = Column(String(32), nullable=False)
    user_last_name = Column(String(32), nullable=False)
    user_father_name = Column(String(32), nullable=True, default="")
    user_city = Column(String(32), nullable=True, default="")
    user_address = Column(String, nullable=True, default="")
    user_tags = Column(String, nullable=True, default="")
    user_birthdate = Column(String)
    date_creation = Column(String)
    user_phone = Column(String, nullable=True)
    user_email = Column(String, nullable=False)
    user_org = Column(String(32), nullable=True)
    status = Column(String, default="Волонтёр")
    admin_access = Column(Boolean, default=False)
    org_access_UUID = Column(Integer, default=False)
    user_verificated_hours = Column(Integer, default=0)
    user_good_actions = Column(Integer, default=0)
    user_v_coins = Column(Integer, default=0)

# Создание модели ORG
class Org(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True)
    org_name = Column(String(32), nullable=False, unique=True)
    org_description = Column(String, nullable=True)
    org_address = Column(String, nullable=False)
    org_city = Column(String, nullable=False)
    org_phone = Column(String, nullable=False)
    org_email = Column(String, nullable=False)
    org_owner = Column(String(32), nullable=False)
    posts = Column(String, nullable=False, default='')

class App(Base):
    __tablename__ = 'app'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)
    user_message = Column(String, nullable=True)
    date_create = Column(String, nullable=False)

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

session.query(Auth).filter_by(id=1).update({Auth.admin_access: True})
session.commit()

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

# ------------ Обработка пути '/login' ------------ 
@app.route("/login", methods=['GET', 'POST'])
def login_page():
    # Если пользователь уже авторизован
    if current_user.is_authenticated:
        # Перенаправление на /profile
        return redirect(url_for('profile_page'))
    
    # Если POST запрос
    if request.method == 'POST':
        # Получение получение пользователя по логину
        user = session.query(Auth).filter_by(user_email=request.form['email']).first()

        # Проверка на существование пользователя, на сходство паролей
        if user and check_password_hash(user.password, request.form['pass']):
            # Логининг пользователя
            user_login = UserLogin().create(user)
            login_user(user_login, remember=bool(request.form.get('remainme')))
            # Отправка сообщения пользователю об успехе
            flash('Произошёл успешный вход', 'success')
            # Перенаправление на главную страницу /
            return redirect(url_for('profile_page'))

        # Отправка сообщения пользователю об ошибке
        flash('Неверная пара логина и пароля', 'error')

    # Возврат шаблона login_page.html
    return render_template("login_page.html")

# ------------ Обработка пути '/register' ------------ 
@app.route("/register", methods=['GET', 'POST'])
def register_page():
    # Если POST запрос
    if request.method == 'POST':

        # Получение данных из формы
        name = request.form['name']
        last_name = request.form['last_name']
        father_name = request.form['father_name']
        email = request.form['email']
        phone = request.form['phone']
        city = request.form['city']
        address = request.form['address']
        password = request.form['pass']
        password_repeat = request.form['pass_repeat']

        # Проверка почты
        if not check_email(email): 
            # Провекрка пароля
            if password == password_repeat:
                # Генерация скрытого пароля
                pass_hash = generate_password_hash(password)
                # Отправка в базу данных
                datedb = datetime.now(pytz.timezone('Europe/Moscow'))
                session.add(Auth(
                        password=pass_hash,
                        user_name=name,
                        user_last_name=last_name,
                        user_father_name=father_name,
                        user_phone=phone,
                        user_email=email,
                        user_city=city,
                        user_address=address,
                        date_creation=date_format(datedb)
                    )
                )
                session.commit()
                # Отправка сообщения пользователю об успехе
                flash('Вы успешно зарегистрированы', 'success')
                # Перевод пользователя в разел /login
                return redirect(url_for('login_page'))
            else:
                # Отправка сообщения пользователю о том, что пароли не совпадают
                flash('Пароли не совпадают', 'error')
        else:
            # Отправка сообщения пользователю о том, что почта уже занята
            flash('Аккаунт с такой электронной почтой уже существует', 'warning')


    # Возврат шаблона register_page.html
    return render_template("register_page.html")

# ------------ Обработка пути '/org' ------------ 
@app.route("/org", methods=['GET', 'POST'])
@login_required
def org_page():
    orgs = session.query(Org).all()
    return render_template("org_page.html", orgs=orgs)

# ------------ Обработка пути '/org/create' ------------ 
@app.route("/org/create", methods=['GET', 'POST'])
@login_required
def org_create_page():
    user_metadata = session.query(Auth).filter_by(
            id=current_user.get_id()).first()
    
    if user_metadata.status == 'Организатор':
        if request.method == 'POST':
            name = request.form['name']
            address = request.form['address']
            city = request.form['city']
            phone = request.form['phone']
            email = request.form['email']
            description = request.form['description']

            session.add(Org(
                org_name=name,
                org_address=address,
                org_city=city,
                org_phone=phone,
                org_email=email,
                org_description=description,
                org_owner = user_metadata.id
            ))

            session.commit()

            flash('Организация успешно создана', 'success')
            return redirect(url_for('org_manage_page'))
        return render_template("org_create_page.html")
    else:
        flash('Вы не являетесь организатором', 'error')
        return redirect('/')

# ------------ Обработка пути '/org/manage' ------------ 
@app.route("/org/manage", methods=['GET', 'POST'])
@login_required
def org_manage_page():
    user_metadata = session.query(Auth).filter_by(
            id=current_user.get_id()).first()
    if user_metadata.status == 'Организатор':
        org = session.query(Org).filter_by(org_owner=user_metadata.id).first()
        if org:
            if request.method == 'POST':
                name = request.form['name']
                address = request.form['address']
                city = request.form['city']
                phone = request.form['phone']
                email = request.form['email']
                description = request.form['description']
                org.org_name = name
                org.org_address = address
                org.org_city = city
                org.org_phone = phone
                org.org_email = email
                org.org_description = description
                session.commit()

                flash('Организация успешно изменена', 'success')
            
            return render_template("org_manage_page.html", org=org, org_owner_email=user_metadata.user_email)
        else:
            flash('Вы не создали организацию', 'warning')
            return redirect('/org/create')
    else:
        flash('Вы не являетесь организатором', 'error')
        return redirect('/')

# ------------ Обработка пути '/org/manage' ------------ 
@app.route("/org/manage/create_post", methods=['GET', 'POST'])
@login_required
def org_manage_create_post_page():
    user_metadata = session.query(Auth).filter_by(
            id=current_user.get_id()).first()
    if user_metadata.status == 'Организатор':
        org = session.query(Org).filter_by(org_owner=user_metadata.id).first()
        if org:
            if request.method == 'POST':
                title = request.form['title']
                address = request.form['address']
                city = request.form['city']
                date = request.form['date']
                verificated_time = request.form['verificated_time']
                v_coins = request.form['v_coins']
                description = request.form['description']

                org.posts += f'{title},{address},{city},{date},{verificated_time},{v_coins},{description}|'

                session.commit()

                flash('Пост успешно создан', 'success')
                return redirect(url_for('org_manage_page'))
            
            return render_template("org_manage_create_post_page.html", org=org, org_owner_email=user_metadata.user_email)
        else:
            flash('Вы не создали организацию', 'warning')
            return redirect('/org/create')
    else:
        flash('Вы не являетесь организатором', 'error')
        return redirect('/')

@app.route("/org/manage/delete_post/<int:id>", methods=['GET', 'POST'])
@login_required
def org_manage_delete_post_page(id: int):
    user_metadata = session.query(Auth).filter_by(
            id=current_user.get_id()).first()
    if user_metadata.status == 'Организатор':
        org = session.query(Org).filter_by(org_owner=user_metadata.id).first()
        if org:
            posts = org.posts
            spl_posts = posts.split('|')
            
            org.posts = org.posts.replace(spl_posts[id]+'|', '')
            session.commit()

            return redirect(url_for('org_manage_page'))
        else:
            flash('Вы не создали организацию', 'warning')
            return redirect('/org/create')
    else:
        flash('Вы не являетесь организатором', 'error')
        return redirect('/')

# ------------ Обработка пути '/org/delete' ------------ 
@app.route("/org/delete", methods=['GET', 'POST'])
@login_required
def org_delete_page():
    user_metadata = session.query(Auth).filter_by(
        id=current_user.get_id()).first()
    
    if user_metadata.status == 'Организатор':
        org = session.query(Org).filter_by(org_owner=user_metadata.id).first()
        if org:
            session.delete(org)
            session.commit()
            flash('Организация успешно удалена', 'success')
        else:
            flash('Вы не создали организацию', 'warning')
            return redirect('/org/create')
    else:
        flash('Вы не являетесь организатором', 'error')

    return redirect('/org')

# ------------ Обработка пути '/org/main/<org_id>' ------------ 
@app.route("/org/main/<org_id>", methods=['GET', 'POST'])
@login_required
def org_main_page(org_id):
    org = session.query(Org).filter_by(id=org_id).first()

    post_list = org.posts.split('|')
    posts = []

    for el in post_list:
        if el:
            posts.append(el.split(','))

    return render_template("org_main_page.html", org=org, posts = posts)

# ------------ Обработка пути '/bonus' ------------ 
@app.route("/bonus")
def bonus_page():
    return render_template("bonus_page.html")


# ------------ Обработка пути '/app' ------------ 
@app.route("/app", methods=['GET', 'POST'])
@login_required
def app_page():
    if request.method == 'POST':
        user_metadata = session.query(Auth).filter_by(
            id=current_user.get_id()).first()
        
        if not session.query(App).filter_by(user_id=user_metadata.id).first():
            user_message = request.form['user_message']

            session.add(App(
                user_id=user_metadata.id,
                user_message=user_message, 
                date_create=date_format(datetime.now(pytz.timezone('Europe/Moscow')))
            ))
            session.commit()
            flash('Заявление успешно отправлено', 'success')
        else:
            flash('Вы уже оставляли заявку', 'warning')
        return redirect(url_for('profile_page'))
    return render_template("app_page.html")

# ------------ Обработка пути '/logout' ------------ 
@app.route("/logout")
@login_required
def logout_page():
    # Выход из системы
    logout_user()
    # Отправка сообщения пользователю об выходе из аккаунта
    flash('Произошёл выход из аккаунта', 'info')
    # Перенаправление на /login
    return redirect(url_for('login_page'))

# ------------ Обработка пути '/profile' ------------ 
@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile_page():
    # Получение данных о пользователе
    user_metadata = session.query(Auth).filter_by(
        id=current_user.get_id()).first()

    # Если POST запрос
    if request.method == 'POST':
        # Получение данных с формы и перезапись в БД
        user_metadata.user_name = request.form['user_name']
        user_metadata.user_last_name = request.form['user_last_name']
        user_metadata.user_father_name = request.form['user_father_name']
        user_metadata.user_city = request.form['user_city']
        user_metadata.user_address = request.form['user_address']
        user_metadata.user_tags = request.form['user_tags']
        user_metadata.user_email = request.form['user_email']
        user_metadata.user_phone = request.form['user_phone']
        user_metadata.user_birthdate = request.form['user_birthdate']
        user_metadata.date_creation = request.form['date_creation']
        user_metadata.status = request.form['status']
        user_metadata.user_email = request.form['user_email']
        session.commit()

    # Возврат шаблона profile_page.html
    return render_template("profile_page.html", profile=user_metadata)

@app.route("/superior/check_app", methods=['GET', 'POST'])
@login_required
def superior_check_app_page():
    # Получение данных о пользователе
    user_metadata = session.query(Auth).filter_by(
        id=current_user.get_id()).first()
    
    if user_metadata.admin_access:
        apps = session.query(App).all()
        app_list = []

        for app in apps:
            user = session.query(Auth).filter_by(id=app.user_id).first()
            app_list.append([
                app.id,
                user.user_email,
                user.user_name,
                user.user_last_name,
                user.user_city,
                app.user_message,
                app.date_create
            ])

        return render_template("superior_check_app_page.html", app_list = app_list)
    
    return abort(404) 

@app.route("/superior/confirm_app/<app_id>", methods=['GET', 'POST'])
@login_required
def superior_confirm_app_page(app_id):
    # Получение данных о пользователе
    user_metadata = session.query(Auth).filter_by(
        id=current_user.get_id()).first()
    
    if user_metadata.admin_access:
        app_rights = session.query(App).filter_by(id=app_id).first()
        
        user = session.query(Auth).filter_by(id=app_rights.user_id).first()
        user.status = 'Организатор'
        
        session.delete(app_rights)
        
        session.commit()

        return redirect(url_for('superior_check_app_page'))
    
    return abort(404) 

#######################################################################################
#        ___     ___    ___        _____                                              #
#       |   |   |   |  |   |      |__|__|  \  /  |   |  | /  |  |   |  /|  |  /|      #
#       |___|   |   |  |   |         |      \/   |---|  |<   |__|   | / |  | / |      #
#      |     |  |___|  |   |         |      /    |   |  | \      |  |/  |  |/  |      #
#                                                                                     #
#######################################################################################

# Функция проверки существования логина
def check_email(email: str) -> bool:
    """
    Функция check_email
    Проверяет наличие данного логина в БД
    Возвращает:
      True - если в пользователь с такой почтой (user_email: str) уже существет.
      False - если почта свободна
    Пояснение:
      Так как email у авторизованного пользователя уникален, нужна функция, которая проверяет уникальность почты
    """
    return True if session.query(Auth).filter_by(user_email=email).first() else False

# Функция форматирования даты
def date_format(date) -> str:
    """
    Метод date_format
    Возвращает время в формате: гг-мм-дд
    Добавляет ноль перед числом месяца или дня, если это число < 10
    """
    return "{}-{:02}-{:02}".format(date.year, date.month, date.day)


app.run(debug=True)
