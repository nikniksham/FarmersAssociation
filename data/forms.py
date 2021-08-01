from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class StartForm(FlaskForm):
    submit = SubmitField("Готово")


class NewspageForm(StartForm):
    heading = StringField('Заголовок', validators=[DataRequired()])
    text = TextAreaField('Статья', validators=[DataRequired()])
    tags = StringField('Тэги', validators=[DataRequired()])


class AdminForm(StartForm):
    stat = 3
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    status = SelectField("Права доступа", choices=[(i, ["Модератор", "Админ", "Владелец"][i]) for i in range(stat - 1)])


class ContentForm(StartForm):
    type = SelectField('Тип', choices=[(1, "Новостной"), (2, "Текстовой"), (3, "С картинками")])
    # animation_type = StringField('Тип анимации', validators=[DataRequired()])
    text = StringField('Текст', validators=[DataRequired()])
    tags = StringField('Тэги', validators=[DataRequired()])


class FeedbackForm(StartForm):
    fullname = StringField('ФИО', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired()])
    heading = StringField('Заголовок', validators=[DataRequired()])
    text = StringField('Текст', validators=[DataRequired()])
    code = StringField('Код подверждения', validators=[DataRequired()])


class SmartpageForm(StartForm):
    heading = StringField('Заголовок', validators=[DataRequired()])


class PartnerForm(StartForm):
    name = StringField('Название', validators=[DataRequired()])
    text = StringField('О партнёре', validators=[DataRequired()])
    link = StringField('Ссылка', validators=[DataRequired()])



"""class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    nickname = StringField('Никнейм', validators=[DataRequired()])
    submit = SubmitField('Зарегестрироваться')


class LoginForm(FlaskForm):
    email = StringField('Почта или Nickname', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class TextForm(FlaskForm):
    header = StringField('Заголовок', validators=[DataRequired()])
    body = TextAreaField('Содержание', validators=[DataRequired()])
    position = SelectField("Местонахождение",
                           choices=[('1', 'Вверху сайта'), ('2', 'В слайдере'), ('3', 'Внизу сайта'), ('4', 'Адреса')])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField("Готово")


class DeleteForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField("Готово")


class CreateCoachForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired()])
    description = TextAreaField("Описание (не более 250 символов)", validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField("Готово")


class CreateInfoForm(FlaskForm):
    header = StringField("Заголовок", validators=[DataRequired()])
    description = TextAreaField("Описание", validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField("Готово")


class CreateScheduleForm(FlaskForm):
    coach = SelectField("Тренер", choices=[(t, t) for t in coach_name])
    name = SelectField("Направление", choices=[('POLE SPORT', 'POLE SPORT'), ('Растяжка', 'Растяжка'),
                                               ('Воздушные полотна', 'Воздушные полотна'),
                                               ('Воздушное кольцо', 'Воздушное кольцо')])
    time = StringField("Время", validators=[DataRequired()])
    day = SelectField('День недели',
                      choices=[('пн', 'Понедельник'), ('вт', 'Вторник'), ('ср', 'Среда'), ('чт', 'Четверг'),
                               ('пт', 'Пятница'), ('сб', 'Суббота'), ('вс', 'Воскресение')])
    hall = SelectField("Зал", choices=[('1', 'Карла Маркса 21'), ('2', 'Преображенская 9')])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField("Готово")
"""