from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField , SelectField
from wtforms.validators import DataRequired
import psycopg2.extras
try:
    conn = psycopg2.connect("dbname='Catalog' user='postgres'" \
                            " host='localhost' password='nike1234'")
except psycopg2.Error as err:
    print("Connection error: {}".format(err))


class LoginForm(FlaskForm):
    login = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    login = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    checkPassword = PasswordField('СoniformPassword', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class SeriesForm(FlaskForm):
    cursor = conn.cursor()
    cursor.execute('select id,Название From Сериал')
    seriesName = cursor.fetchall()

    Series = SelectField('Cериалы',choices =  seriesName,coerce=int)
    submit = SubmitField('Done')

class ActorForm(FlaskForm):
    cursor = conn.cursor()
    cursor.execute('select id,ФИО_актёра From Актёр_серии ')
    seriesName = cursor.fetchall()

    Series = SelectField('Cериалы',choices =  seriesName,coerce=int)
    submit = SubmitField('Done')
