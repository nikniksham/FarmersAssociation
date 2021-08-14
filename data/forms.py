from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired


class StartForm(FlaskForm):
    submit = SubmitField("Готово")


class NewspageForm(StartForm):
    heading = StringField('Заголовок', validators=[DataRequired()])
    text = TextAreaField('Статья', validators=[DataRequired()])
    tags = StringField('Тэги', validators=[DataRequired()])
    preview = SubmitField("Предпросмотр")


class AdminForm(StartForm):
    stat = 0
    name = StringField('Имя', validators=[DataRequired("Пожалуйста введите имя")])
    surname = StringField('Фамилия', validators=[DataRequired("Напишите вашу фамилию")])
    email = StringField('Почта', validators=[DataRequired("Сюда надо написать почту")])
    password = PasswordField('Пароль', validators=[DataRequired("Введите пароль")])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired("Введите пароль повторно")])
    password_current = PasswordField('Ваш пароль', validators=[DataRequired("Введите текущий пароль")])
    status = SelectField("Права доступа",
                         choices=[(i, ["Без прав", "Модератор", "Админ", "Владелец"][i]) for i in range(min(4, stat))])


class ContentForm(StartForm):
    type = SelectField('Тип', choices=[("News", "Новостной"), ("Text", "Текстовый"),
                                       ("Image", "С картинками"), ("Partner", "Партнёры"), ("Map", "Карта")])
    heading = StringField('Название', validators=[DataRequired()])
    # animation_type = StringField('Тип анимации', validators=[DataRequired()])
    text = StringField('Текст')


class FeedbackForm(StartForm):
    fullname = StringField('ФИО', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired()])
    heading = StringField('Заголовок', validators=[DataRequired()])
    text = TextAreaField('Текст', validators=[DataRequired()])
    code = StringField('Код подверждения')
    getcode = SubmitField("Получить код")
    preview = SubmitField("Предпросмотр")


class SmartpageForm(StartForm):
    heading = StringField('Заголовок', validators=[DataRequired()])


class PartnerForm(StartForm):
    name = StringField('Название', validators=[DataRequired()])
    text = StringField('О партнёре', validators=[DataRequired()])
    address = StringField("Адрес", validators=[DataRequired()])
    occupation = StringField("Роды деятельности (через запятую)", validators=[DataRequired()])
    link = StringField('Ссылка', validators=[DataRequired()])


class DeleteForm(FlaskForm):
    submit = SubmitField("Подтвердить")


class AddressForm(StartForm):
    address = StringField('Адрес', validators=[DataRequired()])


class EmailForm(StartForm):
    email = StringField('Электронная почта', validators=[DataRequired()])


class PhoneForm(StartForm):
    number = StringField('Номер телефона', validators=[DataRequired()])


class SocialmediaForm(StartForm):
    link = StringField('Ссылка на соцсеть', validators=[DataRequired()])


class WorkerForm(StartForm):
    name = StringField('ФИО', validators=[DataRequired()])
    profession = StringField('Должность', validators=[DataRequired()])
    phone = StringField("Телефон", validators=[DataRequired()])
    email = StringField("Почта", validators=[DataRequired()])


class SeoForm(StartForm):
    title = StringField("Название сайта", validators=[DataRequired()])
    description = TextAreaField("Краткое описание сайта", validators=[DataRequired()])
    tags = StringField("Тэги сайта (через запятую)", validators=[DataRequired()])
    set_logo = SubmitField("Сохранить новую иконку сайта")
    set_logo_sm = SubmitField("Сохранить новую иконку для ссылкок")
