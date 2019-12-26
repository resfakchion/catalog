from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField,TextAreaField
from wtforms.validators import DataRequired
import psycopg2.extras
seriesName = ''

try:
    conn = psycopg2.connect("dbname='d13els2dc8llov' user='kmtxbmyrifiiei'" \
                            " host='ec2-176-34-183-20.eu-west-1.compute.amazonaws.com' password='7327af8b47965e5de01691bad9f107792912b7ec3a826662e0cd250d9c75bb1c'")
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


'''class RaitingForm(FlaskForm):
    raiting = SelectField('Ваша оценка', choices=[('1', '1'), ('2', '2'), ('3', '3'),('4', '4'),('5', '5'),('6', '6'),('7', '7'),('8', '8'),('9', '9'),('10', '10')], coerce=int)
    submit = SubmitField('Оценить')
'''

class SeriesForm(FlaskForm):
    cursor = conn.cursor()
    cursor.execute('select id,Название From Сериал')
    seriesName = cursor.fetchall()
    Series = SelectField('Cериалы', choices=seriesName, coerce=int)
    submit = SubmitField('Done')


class CommentForm(FlaskForm):
    raiting = SelectField('Ваша оценка',choices=[('1',"-"), ('2', "1"), ('3', "2"), ('4', "3"), ('5', "4"), ('6', "5"), ('7', "6"), ('8', "7"),('9', "8"), ('10', "9"), ('11', "10")])
    newComment = TextAreaField('Оставить ваш комментарий',validators=[DataRequired()])
    submit = SubmitField('Отправить')
