# - *- coding: utf-8 -*-
import os
import psycopg2
import psycopg2.extras
from flask import render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash

from app import app
from app.forms import LoginForm, RegistrationForm, SeriesForm, ActorForm

user = {'login': 'none', 'password': 'none'}
try:
    conn = psycopg2.connect("dbname='Catalog' user='postgres'" \
                            " host='localhost' password='nike1234'")
except psycopg2.Error as err:
    print("Connection error: {}".format(err))


@app.route('/')
@app.route('/logout')
def logout():
    user['login'] = 'none'
    user['password'] = 'none'
    return redirect(url_for('index'))


@app.route('/account')
def account():
    if user['login'] != 'none':

        return render_template('account.html', title="Личный Кабинет", user=user)
    else:
        return redirect(url_for('index'))


@app.route('/index')
def index():
    return render_template('index.html', title='Справочник', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global user
    form = LoginForm()
    if form.validate_on_submit():
        cursor = conn.cursor()
        cursor.execute('select pwdHash,login from Пользователь where  login = %s', (form.login.data,))
        conn.commit()
        record = cursor.fetchall()
        cursor.close()
        if record and check_password_hash(record[0][0], form.password.data):
            user['login'] = record[0][1]
            user['password'] = record[0][0]
            flash('Вы успешно вошли!')
            return redirect(url_for('account'))
        else:
            flash('Неверный логин или пароль')
    return render_template('login.html', title='Login', form=form, user=user)


@app.route('/reg', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit and form.password.data != None and form.password.data != '':
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
    form = SeriesForm()
    if form.validate_on_submit:
        k = 0;
        return render_template('series.html', title='Series', form=form, user=user)
