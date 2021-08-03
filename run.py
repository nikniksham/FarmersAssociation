import datetime
import os
import time
from flask import Flask, render_template, url_for, request
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_restful import abort, Api
from requests import put, delete, get, post
from werkzeug.utils import redirect
from data import db_session
from data.API.AdminAPI.AdminResource import CreateAdminResource, AdminResource, AdminListRecourse, UserResourceAdmin
from data.API.AuditlogAPI.AuditlogResource import AuditlogResource, AuditlogListRecourse
from data.API.ConfirmationCodeAPI.ConfirmationcodeResource import CodeForConfirmation
from data.API.ContentAPI.ContentResource import CreateContentResource, ContentResource, ContentListRecourse
from data.API.FeedbackAPI.FeedbackResource import FeedbackResource, FeedbackListRecourse, CreateFeedbackResource
from data.API.NewspageAPI.NewspageResource import NewspageResource, NewspageListRecourse, CreateNewspageResource, \
    NewspageResourceUsual
from data.API.PartnerAPI.PartnerResource import PartnerResource, PartnerResourceUsual, PartnerListRecourse, \
    CreatePartnerResource
from data.API.SmartpageAPI.SmartpageResource import CreateSmartpageResource, SmartpageResource, SmartpageListRecourse
from data.user import User
from data.auditlog import AuditLog
from data.content import Content
from data.feedback import Feedback
from data.newspage import Newspage
from data.partner import Partner
from data.smartpage import Smartpage
from main import PasswordManager
from data.forms import NewspageForm, AdminForm, FeedbackForm, ContentForm, PartnerForm, SmartpageForm, DeleteForm

link_website = "http://127.0.0.1:8000/"
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(30)
# app.config["DEBUG"] = False
# app.config["TESTING"] = False
api = Api(app)
api.add_resource(CreateAdminResource, "/api/admin/<string:email>/<string:password>")
api.add_resource(AdminResource, "/api/admin/<string:email>/<string:password>")
api.add_resource(UserResourceAdmin, "/api/admin/<string:email>/<string:password>/<int:user_id>")
api.add_resource(AdminListRecourse, "/api/admin/list/<string:email>/<string:password>")
api.add_resource(CreateSmartpageResource, "/api/smartpage/<string:email>/<string:password>")
api.add_resource(SmartpageResource, "/api/smartpage/<string:email>/<string:password>/<int:smartpage_id>")
api.add_resource(SmartpageListRecourse, "/api/smartpage")
api.add_resource(CreateContentResource, "/api/content/<string:email>/<string:password>")
api.add_resource(ContentResource, "/api/content/<string:email>/<string:password>/<int:content_id>")
api.add_resource(ContentListRecourse, "/api/content")
api.add_resource(AuditlogResource, "/api/auditlog/<string:email>/<string:password>/<int:auditlog_id>")
api.add_resource(AuditlogListRecourse, "/api/auditlog/<string:email>/<string:password>")
api.add_resource(CreateNewspageResource, "/api/newspage/<string:email>/<string:password>")
api.add_resource(NewspageResource, "/api/newspage/<string:email>/<string:password>/<int:newspage_id>")
api.add_resource(NewspageResourceUsual, "/api/newspage/<int:newspage_id>")
api.add_resource(NewspageListRecourse, "/api/newspage")
api.add_resource(CreatePartnerResource, "/api/partner/<string:email>/<string:password>")
api.add_resource(PartnerResource, "/api/partner/<string:email>/<string:password>/<int:partner_id>")
api.add_resource(PartnerResourceUsual, "/api/partner/<int:partner_id>")
api.add_resource(PartnerListRecourse, "/api/partner")
api.add_resource(FeedbackResource, "/api/feedback/<string:email>/<string:password>/<int:feedback_id>")
api.add_resource(FeedbackListRecourse, "/api/feedback/<string:email>/<string:password>")
api.add_resource(CreateFeedbackResource, "/api/feedback/<string:code>")
db_session.global_init("db/FarmersAssociation.sqlite")
login_manager = LoginManager()
login_manager.init_app(app)
code_helper = CodeForConfirmation()
password_manager = PasswordManager()


# Получение пользователя
@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


def main(port=8000):
    # print(code_helper.create_code("yuramorozov2711@gmail.com"))
    # print(code_helper.create_code("nikniksham@gmail.com"))
    # print(code_helper.create_code("kolya.toropof@gmail.com"))
    # code_helper.clear_codes()
    """session = db_session.create_session()
    session.execute("alter table feedback add column 'heading' 'varchar'")"""
    app.run(port=port)


def you_dont_have_permission():
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_anonymous:
        return redirect("/")
    form = AdminForm()
    if request.method == 'POST':
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        session.close()
        if user and user.check_password(form.password.data):
            password_manager.add_user(form.email.data, form.password.data, user.status)
            login_user(user, remember=True)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/")
def website_main():
    return render_template('main-page.html', title='Главная страница')


@app.route("/next")
def test_page():
    return render_template('test_page.html', title='Наследник от главной страницы')


@app.route("/admin")
@login_required
def admin():
    return render_template('admin-panel.html', title='админка')


@app.route("/admin-list-news")
@login_required
def admin_list_news():
    newslist = get(f"{link_website}api/newspage").json()
    return render_template('admin-list-news.html', title='Новости', newslist=newslist)


@app.route("/admin-create-news", methods=['GET', 'POST'])
@login_required
def admin_create_news():
    if current_user.status > 0:
        message = ""
        form = NewspageForm()
        if request.method == 'POST':
            message = post(
                f"{link_website}api/newspage/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}",
                json={"heading": form.heading.data, "text": form.text.data, "tags": form.tags.data}).json()

        return render_template('admin-news-form.html', title='Создание новости', message=message, form=form)
    return you_dont_have_permission()


@app.route("/admin-edit-news/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_news(id):
    form = NewspageForm()
    if current_user.status > 0:
        message = ""
        if request.method == 'POST':
            message = put(
                f"{link_website}api/newspage/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}",
                json={"heading": form.heading.data, "text": form.text.data, "tags": form.tags.data}).json()
        else:
            news = get(f"{link_website}api/newspage/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
            if "message" not in list(news):
                form.heading.data = news["heading"]
                form.text.data = news["text"]
                form.tags.data = news["tags"]
            else:
                message = "Новость не найдена"
        return render_template('admin-news-form.html', title='Редактирование новости', message=message, form=form)
    return you_dont_have_permission()


@app.route("/admin-delete-news/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_news(id):
    form = DeleteForm()
    if current_user.status > 0:
        message, name = "", "новость не найдена"
        news = get(
            f"{link_website}api/newspage/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
        if "message" not in news:
            name = "новость " + news["heading"]
        if request.method == 'POST':
            message = delete(
                f"{link_website}api/newspage/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
        return render_template('admin-delete-form.html', title='Удаление новости', message=message, form=form,
                               name=name)
    return you_dont_have_permission()


@app.route("/admin-list-admin")
@login_required
def admin_list_admin():
    adminlist = get(
        f"{link_website}api/admin/list/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}").json()
    return render_template('admin-list-admin.html', title='Новости', adminlist=adminlist)


@app.route("/admin-create-admin", methods=['GET', 'POST'])
@login_required
def admin_create_admin():
    form = AdminForm()
    if current_user.status > 1:
        message = ""
        if request.method == 'POST':
            if form.password.data == form.password_again.data:
                form.status.data = int(form.status.data)
                if form.status.data < current_user.status:
                    message = post(
                        f"{link_website}api/admin/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}",
                        json={"name": form.name.data, "surname": form.surname.data, "email": form.email.data,
                              "password": form.password.data, "status": form.status.data}).json()
                    form.status.data = str(form.status.data)
                else:
                    message = "Слишком высокий статус нового пользователя"
            else:
                message = "Пароли не совпадают"
        return render_template('admin-admin-form.html', title='Создание админа', message=message, form=form, flag=True)
    return you_dont_have_permission()


@app.route("/admin-edit-admin/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_admin(id):
    form = AdminForm()
    admin = get(
        f"{link_website}api/admin/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
    if current_user.status > 1:
        message = ""
        if "message" not in admin:
            if admin["status"] < current_user.status:
                if request.method == 'POST':
                    form.status.data = int(form.status.data)
                    message = put(
                        f"{link_website}api/admin/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}",
                        json={"name": form.name.data, "surname": form.surname.data, "email": form.email.data, "status": form.status.data}).json()
                    form.status.data = str(form.status.data)
                else:
                    form.name.data = admin["name"]
                    form.surname.data = admin["surname"]
                    form.email.data = admin["email"]
                    form.status.data = str(admin["status"])
            else:
                message = "У вас недостаточно прав для этого"
        else:
            message = "Пользователь не найден"
        return render_template('admin-admin-form.html', title='Редактирование админа', message=message, form=form, flag=False)
    return you_dont_have_permission()


@app.route("/admin-delete-admin/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_admin(id):
    form = DeleteForm()
    if current_user.status > 0:
        message, name = "", "пользователь не найден"
        admin = get(
            f"{link_website}api/admin/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
        if "message" not in admin:
            name = "админа " + f"{admin['name']} {admin['surname']}"
        if request.method == 'POST':
            message = delete(
                f"{link_website}api/admin/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
        return render_template('admin-delete-form.html', title='Удаление админа', message=message, form=form,
                               name=name)
    return you_dont_have_permission()


@app.route("/admin-content")
@login_required
def admin_content():
    content = get(f"{link_website}/api/content").json()
    return render_template('admin-panel-content.html', title='контент', content=content)


@app.route("/admin-feedback")
@login_required
def admin_feedback():
    feedback = get(f"{link_website}/api/feedback/<string:email>/<string:password>").json()
    return render_template('admin-panel-feedback.html', title='контент', feedback=feedback)


@app.route("/admin-newspage")
@login_required
def admin_newspage():
    newspage = get(f"{link_website}/api/feedback/<string:email>/<string:password>").json()
    return render_template('admin-panel-newspage.html', title='контент', newspage=newspage)


@app.route("/admin-partner")
@login_required
def admin_partner():
    partner = get(f"{link_website}/api/partner/<string:email>/<string:password>").json()
    return render_template('admin-panel-partner.html', title='контент', partner=partner)


@app.route("/admin-smartpage")
@login_required
def admin_smartpage():
    smartpage = get(f"{link_website}/api/smartpage/<string:email>/<string:password>").json()
    return render_template('admin-panel-smartpage.html', title='контент', smartpage=smartpage)


if __name__ == '__main__':
    print("http://127.0.0.1:8000/admin")
    print("http://127.0.0.1:8000/admin-create-news")
    print("http://127.0.0.1:8000/login")
    main()
    create_new_db = False
    if create_new_db:
        db_session.global_init("db/FarmersAssociation.sqlite")
        session = db_session.create_session()
        admin = User()
        session.add(admin)
        session.add(AuditLog())
        session.add(Feedback())
        session.commit()
        session = db_session.create_session()
        session.add(Newspage())
        session.add(Partner())
        session.add(Smartpage())
        session.commit()
        session = db_session.create_session()
        session.add(Content())
        session.commit()
        print('Успех!')
