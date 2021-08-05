from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, SelectField
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
    status = SelectField("Права доступа",
                         choices=[(i, ["Без прав", "Модератор", "Админ", "Владелец"][i]) for i in range(stat)])
    submit = SubmitField("Готово")


class ContentForm(StartForm):
    type = SelectField('Тип', choices=[("News", "Новостной"), ("Text", "Текстовой"),
                                       ("Image", "С картинками"), ("Partners", "Партнёры")])
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


class DeleteForm(FlaskForm):
    submit = SubmitField("Подтвердить")
