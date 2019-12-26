# - *- coding: utf-8 -*-
import psycopg2.extras
from flask import render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash
from flask_login import LoginManager, UserMixin, logout_user, login_required, login_user, current_user

from app import app
from app.forms import LoginForm, RegistrationForm, CommentForm

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return "%d/%s/%s/%s/%d" % (self.id)


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


try:
    conn = psycopg2.connect("dbname='d13els2dc8llov' user='kmtxbmyrifiiei'" \
                            " host='ec2-176-34-183-20.eu-west-1.compute.amazonaws.com' password='7327af8b47965e5de01691bad9f107792912b7ec3a826662e0cd250d9c75bb1c'")
except psycopg2.Error as err:
    print("Connection error: {}".format(err))


@app.route('/')
def start():
   return redirect(url_for("series"))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из профиля')
    return redirect(url_for('index'))


@app.route('/account')
def account():
    if current_user.is_authenticated:
        cursor = conn.cursor()
        cursor.execute('SELECT Комментарий,Название FROM Комментарий_сериала Inner join Сериал On Комментарий_сериала.idSerial = Сериал.id Where login = %s', (current_user.id,))
        conn.commit()
        comments = cursor.fetchall()
        return render_template('account.html', title="Личный Кабинет", user=user,comments = comments)
    else:
        flash('Вы ещё не вошли в свой аккаунт')
        return redirect(url_for('index'))


@app.route('/index')
def index():
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(id) FROM Пользователь')
    conn.commit()
    countUsers = cursor.fetchone()
    cursor.execute('SELECT COUNT(id) FROM Сериал')
    conn.commit()
    countSerial = cursor.fetchone()
    return render_template('index.html', title='Справочник', user=user,countUsers = countUsers[0],countSerial = countSerial[0])


@app.route('/login', methods=['GET', 'POST'])
def login():
    global username
    if current_user.is_authenticated:
        flash('Вы уже авторизированны')
        return redirect(url_for('account'))
    form = LoginForm()
    if form.validate_on_submit():
        cursor = conn.cursor()
        cursor.execute('select pwdHash,login from Пользователь where  login = %s', (form.login.data,))
        conn.commit()
        record = cursor.fetchone()
        cursor.close()
        if record and check_password_hash(record[0], form.password.data):
            username = record[1]
            user_id = User(username)
            login_user(user_id, remember=form.remember_me.data)
            flash('Вы успешно вошли!')
            return redirect(url_for('account'))
        else:
            flash('Неверный логин или пароль')
    return render_template('login.html', title='Login', form=form, user=user)


@app.route('/reg', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        flash('Вы уже зарегистрированы')
        return redirect(url_for('account'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data == form.checkPassword.data:
            cursor = conn.cursor()
            cursor.execute('select login from Пользователь where  login = %s', (form.login.data,))
            conn.commit()
            record = cursor.fetchall()
            if not record:
                cursor = conn.cursor()
                hash = generate_password_hash(format(form.password.data))
                cursor.execute('INSERT INTO Пользователь (login,pwdHash) VALUES (%s,%s)', (form.login.data, hash,))
                conn.commit()
                cursor.close()
                flash('Вы успешно зарегистрировались!')
            else:
                flash('Аккаунт с данным логином уже существует')
        else:
            flash('Пароли не совпадают')
    return render_template('reg.html', title='Registration', form=form, user=user)


@app.route('/series', methods=['GET', 'POST'])
def series():
    return render_template('series.html', title='Series', user=user)


@app.route('/series/<idSerial>', methods=['GET', 'POST'])
def seriesId(idSerial):
    cursor = conn.cursor()
    cursor.execute('select Название From Сериал where id = %s', (idSerial,))
    conn.commit()
    title = cursor.fetchone()
    if title == None:
        flash("Данного сериала не существует")
        return redirect(url_for('index'))
    cursor.execute('select Название_жанра From Жанр_сериала where  idSerial = %s', (idSerial,))
    conn.commit()
    genre = cursor.fetchone()

    img = []
    for i in range(1, 5):
        filename = 'img/' + str(idSerial) + '/' + str(i) + '.jpg'
        img.append(filename)

    cursor.execute('select Описание From Описание_сериала where idAbout = %s', (idSerial,))
    conn.commit()
    about = cursor.fetchone()
    form = CommentForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        cursor.execute('select login  From Рейтинг_пользователя where login = %s and idSerial = %s',
                       (current_user.id, idSerial,))
        conn.commit()
        record = cursor.fetchone()
        if not record and  form.raiting.data != '1':
             cursor.execute('INSERT INTO Рейтинг_пользователя(idSerial,login,Оценка)  VALUES (%s,%s,%s)',(idSerial, current_user.id, int(form.raiting.data) - 1,))
             conn.commit()
        else:
            if form.newComment.data == '' or form.newComment.data == '-1' :
                flash("Вы уже проголосовали")
        if form.newComment.data != '' and form.newComment.data != '-1':
            cursor.execute('INSERT INTO Комментарий_сериала(idSerial,login,Комментарий) VALUES (%s,%s,%s)',
                           (idSerial, current_user.id, form.newComment.data,))
            conn.commit()

    cursor.execute('select avg(Оценка) From Рейтинг_пользователя where idSerial = %s', (idSerial,))
    conn.commit()
    userRaiting = cursor.fetchone()
    if userRaiting[0] != None:
        userRaiting = round(userRaiting[0],2)
    cursor.execute('select Оценка From Рейтинг_пользователя where login = %s and idSerial = %s', (current_user.id,idSerial,))
    conn.commit()
    userNote= cursor.fetchone()
    if userNote != None :
        userNote = round(userNote[0],2)

    cursor.execute('select ФИО_актёра From Актёр_сериала where idSerial = %s', (idSerial,))
    conn.commit()
    nameActors = cursor.fetchall()


    cursor.execute('select login,Комментарий  from Комментарий_сериала where  idSerial = %s', (idSerial,))
    conn.commit()
    comments = cursor.fetchall()
    return render_template('baseSerial.html', title=title[0], user=user, img=img, about=about[0], genre=genre[0],
                           comments=comments, form=form, userRaiting=userRaiting,userNote = userNote,
                           nameActors=nameActors)
