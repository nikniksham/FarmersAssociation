import datetime
import os
import random
import time
import threading
from markupsafe import Markup
from flask import Flask, render_template, url_for, request
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_restful import abort, Api
from requests import put, delete, get, post
from werkzeug.utils import redirect
from data import db_session
from data.API.AdminAPI.AdminResource import CreateAdminResource, AdminResource, AdminListRecourse, UserResourceAdmin
from data.API.AuditlogAPI.AuditlogResource import AuditlogResource, AuditlogListRecourse
from data.API.ConfirmationCodeAPI.ConfirmationcodeResource import CodeForConfirmation
from data.API.ContentAPI.ContentResource import CreateContentResource, ContentResource, ContentListRecourse, \
    ContentListRecourseId
from data.API.FeedbackAPI.FeedbackResource import FeedbackResource, FeedbackListRecourse, CreateFeedbackResource
from data.API.NewspageAPI.NewspageResource import NewspageResource, NewspageListRecourse, CreateNewspageResource, \
    NewspageResourceUsual, NewspageListRecourseId, NewspageResourceLink
from data.API.PartnerAPI.PartnerResource import PartnerResource, PartnerResourceUsual, PartnerListRecourse, \
    CreatePartnerResource
from data.API.SmartpageAPI.SmartpageResource import CreateSmartpageResource, SmartpageResource, SmartpageListRecourse, \
    SmartpageRecourseUsual, SmartpageRecourseLink
from data.user import User
from data.auditlog import AuditLog
from data.content import Content
from data.feedback import Feedback
from data.newspage import Newspage
from data.partner import Partner
from data.smartpage import Smartpage
from main import PasswordManager, ManagerContainer, text_transform
from data.forms import NewspageForm, AdminForm, FeedbackForm, ContentForm, PartnerForm, SmartpageForm, DeleteForm
from werkzeug.utils import secure_filename
from PIL import Image

link_website = "http://127.0.0.1:8000/"
app = Flask(__name__)
let = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
app.config['SECRET_KEY'] = os.urandom(30)
app.config['UPLOAD_FOLDER'] = 'static/img/'
# app.config["DEBUG"] = False
# app.config["TESTING"] = False
api = Api(app)
api.add_resource(CreateAdminResource, "/api/admin/<string:email>/<string:password>")
api.add_resource(AdminResource, "/api/admin/<string:email>/<string:password>")
api.add_resource(UserResourceAdmin, "/api/admin/<string:email>/<string:password>/<int:user_id>")
api.add_resource(AdminListRecourse, "/api/admin/list/<string:email>/<string:password>")
api.add_resource(CreateSmartpageResource, "/api/smartpage/<string:email>/<string:password>")
api.add_resource(SmartpageResource, "/api/smartpage/<string:email>/<string:password>/<int:smartpage_id>")
api.add_resource(SmartpageRecourseUsual, "/api/smartpage/<int:smartpage_id>")
api.add_resource(SmartpageRecourseLink, "/api/smartpage/<string:link>")
api.add_resource(SmartpageListRecourse, "/api/smartpage")
api.add_resource(CreateContentResource, "/api/content/<string:email>/<string:password>")
api.add_resource(ContentResource, "/api/content/<string:email>/<string:password>/<int:content_id>")
api.add_resource(ContentListRecourse, "/api/content")
api.add_resource(ContentListRecourseId, "/api/content/<int:smartpage_id>")
api.add_resource(AuditlogResource, "/api/auditlog/<string:email>/<string:password>/<int:auditlog_id>")
api.add_resource(AuditlogListRecourse, "/api/auditlog/<string:email>/<string:password>")
api.add_resource(CreateNewspageResource, "/api/newspage/<string:email>/<string:password>")
api.add_resource(NewspageResource, "/api/newspage/<string:email>/<string:password>/<int:newspage_id>")
api.add_resource(NewspageResourceUsual, "/api/newspage/<int:newspage_id>")
api.add_resource(NewspageListRecourseId, "/api/newspage/<int:start_id>/<int:end_id>")
api.add_resource(NewspageListRecourse, "/api/newspage")
api.add_resource(NewspageResourceLink, "/api/newspage/<string:link>")
api.add_resource(CreatePartnerResource, "/api/partner/<string:email>/<string:password>")
api.add_resource(PartnerResource, "/api/partner/<string:email>/<string:password>/<int:partner_id>")
api.add_resource(PartnerResourceUsual, "/api/partner/<int:partner_id>")
api.add_resource(PartnerListRecourse, "/api/partner")
api.add_resource(FeedbackResource, "/api/feedback/<string:email>/<string:password>/<int:feedback_id>")
api.add_resource(FeedbackListRecourse, "/api/feedback/<string:email>/<string:password>")
api.add_resource(CreateFeedbackResource, "/api/feedback")
db_session.global_init("db/FarmersAssociation.sqlite")
login_manager = LoginManager()
login_manager.init_app(app)
code_helper = CodeForConfirmation()
password_manager = PasswordManager()
containerManager = ManagerContainer()


# Получение пользователя
@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


def create_random_name(name_len):
    return ''.join([random.choice(let) for i in range(name_len)])


def save_image_multithreading(filename, file):
    file.save(filename)
    image = Image.open(filename)
    if image.size[0] > 720 or image.size[1] > 480:
        image.thumbnail((720, 480))
    path, format = filename.split(".")
    if format != "png":
        image = image.convert('RGB')
    print(path, format)
    image.save(filename)


def save_image(filename, file):
    t1 = threading.Thread(target=save_image_multithreading, args=(os.path.join(app.config["UPLOAD_FOLDER"], filename), file))
    t1.start()
    t1.join()


def delete_img(filename):
    if filename not in ["", "standard.png"] and os.path.exists(f"{app.config['UPLOAD_FOLDER']}{filename}"):
        os.remove(f"{app.config['UPLOAD_FOLDER']}{filename}")


def create_new_image_name(logo=False):
    filelist, format = os.listdir(app.config['UPLOAD_FOLDER']), ".png" if logo else ".jpg"
    filename = create_random_name(50) + format
    while filename in filelist:
        filename = create_random_name(50) + format
    return filename


def allowed_file(filename):
    ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg']
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def main(port=8000):
    # print(code_helper.create_code("yuramorozov2711@gmail.com"))
    # print(code_helper.create_code("nikniksham@gmail.com"))
    # print(code_helper.create_code("kolya.toropof@gmail.com"))
    # code_helper.clear_codes()
    """session = db_session.create_session()
    session.execute("alter table smartpage add column 'link' VARCHAR")"""
    app.run(port=port)


def you_dont_have_permission():
    return redirect("/")


def page_not_found():
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
            return redirect("/admin")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/")
def website_main():
    smartpages = get(f"{link_website}api/smartpage").json()
    return render_template('main-page.html', title='Главная страница', smartpages=smartpages, is_admin=(not current_user.is_anonymous))


@app.route("/next")
def test_page():
    smartpages = get(f"{link_website}api/smartpage").json()
    return render_template('test_page.html', title='Наследник от главной страницы', smartpages=smartpages, is_admin=(not current_user.is_anonymous))


@app.route("/admin")
@login_required
def admin():
    smartpages = get(f"{link_website}api/smartpage").json()
    return render_template('admin-panel.html', title='админка', smartpages=smartpages, is_admin=(not current_user.is_anonymous))


@app.route("/admin-list-news")
@login_required
def admin_list_news():
    if current_user.status > 0:
        smartpages = get(f"{link_website}api/smartpage").json()
        newslist = get(f"{link_website}api/newspage").json()
        return render_template('admin-list-news.html', title='Новости', newslist=newslist, smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/admin-create-news", methods=['GET', 'POST'])
@login_required
def admin_create_news():
    if current_user.status > 0:
        form = NewspageForm()
        message, result, filenames, filename, preview_text = None, False, [], None, None
        if request.method == 'POST':
            cont = containerManager.get_container(f"news_{current_user.name}")
            img_list = list(request.files)
            for ind, name in enumerate(request.files):
                file = request.files[name]
                if file.filename != "":
                    if img_list[ind] in cont:
                        delete_img(cont[img_list[ind]])
                    if file and allowed_file(file.filename):
                        filename = secure_filename(create_new_image_name())
                        save_image(filename, file)
                        filenames.append(filename)
                else:
                    if img_list[ind] in cont:
                        filenames.append(cont[img_list[ind]])
            if len(filenames) == 0:
                filenames = ["standard.png"]
            containerManager.add_container(f"news_{current_user.name}", filenames, True)
            if form.submit.data:
                message = post(
                    f"{link_website}api/newspage/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}",
                    json={"heading": form.heading.data, "text": form.text.data, "tags": form.tags.data, "image": "//".join(filenames)}).json()
                if "success" in message:
                    result = True
                    containerManager.delete_container(f"news_{current_user.name}")
                message = " ".join(list(message.values()))
            elif form.preview.data:
                preview_text = Markup(text_transform(form.text.data, filenames, app.config["UPLOAD_FOLDER"]))
        else:
            filenames = containerManager.get_container(f"news_{current_user.name}").values()
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-news-form.html', title='Создание новости', message=message, preview_text=preview_text,
                               form=form, result=result, filenames=filenames, image_len=len(filenames) + 1, smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/admin-edit-news/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_news(id):
    if current_user.status > 0:
        form = NewspageForm()
        message, result, filenames, filename, preview_text = None, False, [], None, None
        news = get(
            f"{link_website}api/newspage/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
        if "message" not in list(news):
            if request.method == 'POST':
                cont = containerManager.get_container(f"news_{id}")
                img_list = list(request.files)
                for ind, name in enumerate(request.files):
                    file = request.files[name]
                    if file.filename != "":
                        if img_list[ind] in cont:
                            delete_img(cont[img_list[ind]])
                        if file and allowed_file(file.filename):
                            filename = secure_filename(create_new_image_name())
                            save_image(filename, file)
                            filenames.append(filename)
                    else:
                        if img_list[ind] in cont:
                            filenames.append(cont[img_list[ind]])
                if len(filenames) == 0:
                    filenames = ["standard.png"]
                containerManager.add_container(f"news_{id}", filenames)
                if form.submit.data:
                    message = put(
                        f"{link_website}api/newspage/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}",
                        json={"heading": form.heading.data, "text": form.text.data, "tags": form.tags.data, "image": "//".join(filenames)}).json()
                    if "success" in message:
                        result = True
                    message = " ".join(list(message.values()))
                elif form.preview.data:
                    preview_text = Markup(text_transform(form.text.data, filenames, app.config["UPLOAD_FOLDER"]))
            else:
                form.heading.data = news["heading"]
                form.text.data = news["text"]
                form.tags.data = news["tags"]
                filenames = news["image"].split("//")
                containerManager.add_container(f"news_{id}", filenames)
        else:
            message = "Новость не найдена"
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-news-form.html', title='Редактирование новости', message=message, result=result,
                               form=form, filenames=filenames, image_len=len(filenames) + 1, smartpages=smartpages,
                               is_admin=(not current_user.is_anonymous), preview_text=preview_text)
    return you_dont_have_permission()


@app.route("/admin-delete-news/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_news(id):
    if current_user.status > 0:
        form = DeleteForm()
        message, result, name = None, False, "новость не найдена"
        news = get(
            f"{link_website}api/newspage/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
        if "message" not in news:
            name = "новость " + news["heading"]
            if request.method == 'POST':
                message = delete(
                    f"{link_website}api/newspage/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
                if "success" in message:
                    result = True
                message = " ".join(list(message.values()))
                images = news["image"]
                for image in images.split("//"):
                    delete_img(image)
                containerManager.delete_container(f"news_{id}")
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-delete-form.html', title='Удаление новости', message=message, form=form,
                               result=result, name=name, smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/admin-list-admin")
@login_required
def admin_list_admin():
    if current_user.status > 0:
        adminlist = get(
            f"{link_website}api/admin/list/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}").json()
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-list-admin.html', title='Новости', adminlist=adminlist, smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/admin-create-admin", methods=['GET', 'POST'])
@login_required
def admin_create_admin():
    if current_user.status > 1:
        form = AdminForm()
        message, result = None, False
        if request.method == 'POST':
            if form.password.data == form.password_again.data:
                form.status.data = int(form.status.data)
                if form.status.data <= current_user.status:
                    message = post(
                        f"{link_website}api/admin/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}",
                        json={"name": form.name.data, "surname": form.surname.data, "email": form.email.data,
                              "password": form.password.data, "status": form.status.data}).json()
                    form.status.data = str(form.status.data)
                    if "success" in message:
                        result = True
                    message = " ".join(list(message.values()))
                else:
                    message = "Слишком высокий статус нового пользователя"
            else:
                message = "Пароли не совпадают"
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-admin-form.html', title='Создание админа', message=message, form=form,
                               result=result, flag=True, smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/admin-edit-admin/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_admin(id):
    if current_user.status > 1:
        form = AdminForm()
        admin = get(
            f"{link_website}api/admin/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
        form.stat = current_user.status
        message, result = None, False
        if "message" not in admin:
            if admin["status"] <= current_user.status:
                if request.method == 'POST':
                    form.status.data = int(form.status.data)
                    message = put(
                        f"{link_website}api/admin/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}",
                        json={"name": form.name.data, "surname": form.surname.data, "email": form.email.data,
                              "status": form.status.data}).json()
                    form.status.data = str(form.status.data)
                    if "success" in message:
                        result = True
                    message = " ".join(list(message.values()))
                else:
                    form.name.data = admin["name"]
                    form.surname.data = admin["surname"]
                    form.email.data = admin["email"]
                    form.status.data = str(admin["status"])
            else:
                message = "У вас недостаточно прав для этого"
        else:
            message = "Пользователь не найден"
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-admin-form.html', title='Редактирование админа', message=message, form=form,
                               result=result, flag=False, smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/admin-delete-admin/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_admin(id):
    if current_user.status > 1:
        form = DeleteForm()
        message, name, result = None, "пользователь не найден", False
        admin = get(
            f"{link_website}api/admin/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
        if "message" not in admin:
            name = "админа " + f"{admin['name']} {admin['surname']}"
            if admin["status"] < current_user.status:
                if request.method == 'POST':
                    message = delete(
                        f"{link_website}api/admin/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
                    if "success" in message:
                        result = True
                    message = " ".join(list(message.values()))
            else:
                message = "У вас недостаточно прав для этого"
        else:
            name = "пользователь не найден"
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-delete-form.html', title='Удаление админа', message=message, form=form,
                               result=result, name=name, smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/admin-list-smartpage/<int:page_id>")
@login_required
def admin_list_smartpage(page_id):
    if current_user.status > 0:
        smartpagelist, contentdict = get(f"{link_website}api/smartpage").json(), {}
        contentlist = get(f"{link_website}api/content").json()
        for page in smartpagelist:
            for content in contentlist:
                if page["id"] == content["smartpage_id"]:
                    if page["id"] in contentdict:
                        contentdict[page["id"]].append(content)
                    else:
                        contentdict[page["id"]] = [content]
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-list-smartpage.html', title='Страницы', smartpagelist=smartpagelist,
                               contentdict=contentdict, types={"News": "Новости", "Image": "Картинки", "Text": "Текст", "Partner": "Партнёры"},
                               smartpages=smartpages, is_admin=(not current_user.is_anonymous), page_id=page_id)
    return you_dont_have_permission()


@app.route("/admin-create-smartpage", methods=['GET', 'POST'])
@login_required
def admin_create_smartpage():
    if current_user.status > 0:
        form = SmartpageForm()
        message, result, filenames, filename = None, False, [], None
        if request.method == 'POST':
            for name in request.files:
                file = request.files[name]
                if file.filename != "":
                    if file and allowed_file(file.filename):
                        filename = secure_filename(create_new_image_name())
                        save_image(filename, file)
                        filenames.append(filename)
            if len(filenames) == 0:
                filenames = ["standard.png"]
            message = post(
                f"{link_website}api/smartpage/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}",
                json={"heading": form.heading.data, "image": "//".join(filenames)}).json()
            if "success" in message:
                result = True
            message = " ".join(list(message.values()))
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-smartpage-form.html', title='Создание страницы', message=message, form=form,
                               result=result, filenames=filenames, image_len=1, smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/admin-edit-smartpage/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_smartpage(id):
    if current_user.status > 0:
        form = SmartpageForm()
        smartpage = get(
            f"{link_website}api/smartpage/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
        message, result, filenames, filename = None, False, [], None
        if "message" not in smartpage:
            if request.method == 'POST':
                cont = containerManager.get_container(f"smartpage_{id}")
                img_list = list(request.files)
                for ind, name in enumerate(request.files):
                    file = request.files[name]
                    if file.filename != "":
                        if img_list[ind] in cont:
                            delete_img(cont[img_list[ind]])
                        if file and allowed_file(file.filename):
                            filename = secure_filename(create_new_image_name())
                            save_image(filename, file)
                            filenames.append(filename)
                    else:
                        if img_list[ind] in cont:
                            filenames.append(cont[img_list[ind]])
                if len(filenames) == 0:
                    filenames = ["standard.png"]
                containerManager.add_container(f"smartpage_{id}", filenames)
                message = put(
                    f"{link_website}api/smartpage/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}",
                    json={"heading": form.heading.data, "image": "//".join(filenames)}).json()
                if "success" in message:
                    result = True
                message = " ".join(list(message.values()))
            else:
                form.heading.data = smartpage["heading"]
                filenames = smartpage["image"].split("//")
                containerManager.add_container(f"smartpage_{id}", filenames)
        else:
            message = "Страница не найдена"
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-smartpage-form.html', title='Редактирование страницы', message=message, form=form,
                               result=result, flag=False, filenames=filenames, image_len=len(filenames) + 1,
                               smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/admin-delete-smartpage/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_smartpage(id):
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result = "", "страница не найдена", False
        smartpage = get(
            f"{link_website}api/smartpage/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
        if "message" not in smartpage:
            name = "страница " + smartpage['heading']
            if request.method == 'POST':
                message = delete(
                    f"{link_website}api/smartpage/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
                if "success" in message:
                    result = True
                message = " ".join(list(message.values()))
                images = smartpage["image"]
                for image in images.split("//"):
                    delete_img(image)
                containerManager.delete_container(f"smartpage_{id}")
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-delete-form.html', title='Удаление страницы', message=message, form=form,
                               result=result, name=name, smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/admin-create-content/<int:page_id>", methods=['GET', 'POST'])
@login_required
def admin_create_content(page_id):
    if current_user.status > 0:
        form = ContentForm()
        message, result, filenames, filename = None, False, [], None
        if request.method == 'POST':
            for name in request.files:
                file = request.files[name]
                if file.filename != "":
                    if file and allowed_file(file.filename):
                        filename = secure_filename(create_new_image_name())
                        save_image(filename, file)
                        filenames.append(filename)
            image = "" if len(filenames) == 0 else "//".join(filenames)
            message = post(
                f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}",
                json={"type": form.type.data, "text": form.text.data, "page_id": page_id,
                      "heading": form.heading.data, "image": image}).json()
            if "success" in message:
                result = True
            message = " ".join(list(message.values()))
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-content-form.html', title='Создание контента', message=message, form=form,
                               result=result, flag=True, filenames=filenames, image_len=1, smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/admin-edit-content-move-up/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_content_move_up(id):
    if current_user.status > 0:
        content = get(
            f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
        put(
            f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}",
            json={"position": content["position"] - 1})
        return redirect(f"/admin-list-smartpage/{content['smartpage_id']}")
    return you_dont_have_permission()


@app.route("/admin-edit-content-move-down/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_content_move_down(id):
    if current_user.status > 0:
        content = get(
            f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
        put(f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}",
            json={"position": content["position"] + 1}).json()
        return redirect(f"/admin-list-smartpage/{content['smartpage_id']}")
    return you_dont_have_permission()


@app.route("/admin-edit-content/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_content(id):
    if current_user.status > 0:
        form = ContentForm()
        content = get(
            f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
        message, result, filenames, filename = None, False, [], None
        if "message" not in content:
            if request.method == 'POST':
                cont = containerManager.get_container(f"content_{id}")
                img_list = list(request.files)
                for ind, name in enumerate(request.files):
                    file = request.files[name]
                    if file.filename != "":
                        if img_list[ind] in cont:
                            delete_img(cont[img_list[ind]])
                        if file and allowed_file(file.filename):
                            filename = secure_filename(create_new_image_name())
                            save_image(filename, file)
                            filenames.append(filename)
                    else:
                        if img_list[ind] in cont:
                            filenames.append(cont[img_list[ind]])
                image = "" if len(filenames) == 0 else "//".join(filenames)
                containerManager.add_container(f"content_{id}", filenames)
                message = put(
                    f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}",
                    json={"type": form.type.data, "text": form.text.data, "heading": form.heading.data, "image": image}).json()
                if "success" in message:
                    result = True
                message = " ".join(list(message.values()))
            else:
                form.type.data = content["type"]
                form.text.data = content["text"]
                form.heading.data = content["heading"]
                if content["image"]:
                    filenames = content["image"].split("//")
                containerManager.add_container(f"content_{id}", filenames)
        else:
            message = "Контент не найден"
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-content-form.html', title='Редактирование контента', message=message, form=form,
                               result=result, flag=False, filenames=filenames, image_len=len(filenames) + 1,
                               smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/admin-delete-content/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_content(id):
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result = "", "контент не найден", False
        content = get(
            f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
        if "message" not in content:
            name = "контент " + content['heading']
            if request.method == 'POST':
                message = delete(
                    f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
                if "success" in message:
                    result = True
                message = " ".join(list(message.values()))
                images = content["image"]
                for image in images.split("//"):
                    delete_img(image)
                containerManager.delete_container(f"content_{id}")
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-delete-form.html', title='Удаление контента', message=message, form=form,
                               result=result, name=name, smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/admin-list-partner")
@login_required
def admin_list_partner():
    if current_user.status > 0:
        partnerlist = get(f"{link_website}api/partner").json()
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-list-partner.html', title='Партнёры', partnerlist=partnerlist, smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/admin-create-partner", methods=['GET', 'POST'])
@login_required
def admin_create_partner():
    if current_user.status > 0:
        form = PartnerForm()
        message, result, filenames, filename = None, False, [], None
        if request.method == 'POST':
            for name in request.files:
                file = request.files[name]
                if file.filename != "":
                    if file and allowed_file(file.filename):
                        filename = secure_filename(create_new_image_name(True))
                        save_image(filename, file)
                        filenames.append(filename)
            if len(filenames) == 0:
                filenames = ["standard.png"]
            message = post(
                f"{link_website}api/partner/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}",
                json={"name": form.name.data, "image": "//".join(filenames), "text": form.text.data,
                      "link": form.link.data}).json()
            if "success" in message:
                result = True
            message = " ".join(list(message.values()))
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-partner-form.html', title='Создание партнёра', message=message, form=form,
                               result=result, flag=True, filenames=filenames, image_len=1, smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/admin-edit-partner/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_partner(id):
    if current_user.status > 0:
        form = PartnerForm()
        partner = get(
            f"{link_website}api/partner/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
        message, result, filenames, filename = None, False, [], None
        if "message" not in partner:
            if request.method == 'POST':
                cont = containerManager.get_container(f"partner_{id}")
                img_list = list(request.files)
                for ind, name in enumerate(request.files):
                    file = request.files[name]
                    if file.filename != "":
                        if img_list[ind] in cont:
                            delete_img(cont[img_list[ind]])
                        if file and allowed_file(file.filename):
                            filename = secure_filename(create_new_image_name(True))
                            save_image(filename, file)
                            filenames.append(filename)
                    else:
                        if img_list[ind] in cont:
                            filenames.append(cont[img_list[ind]])
                if len(filenames) == 0:
                    filenames = ["standard.png"]
                containerManager.add_container(f"partner_{id}", filenames)
                message = put(
                    f"{link_website}api/partner/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}",
                    json={"name": form.name.data, "text": form.text.data, "link": form.link.data, "image": "//".join(filenames)}).json()
                if "success" in message:
                    result = True
                message = " ".join(list(message.values()))
            else:
                form.name.data = partner["name"]
                form.text.data = partner["text"]
                form.link.data = partner["link"]
                filenames = partner["image"].split("//")
                containerManager.add_container(f"partner_{id}", filenames)
        else:
            message = "Партнёр не найден"
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-partner-form.html', title='Редактирование партнёра', message=message, form=form,
                               result=result, flag=False, filenames=filenames, image_len=len(filenames) + 1,
                               smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/admin-delete-partner/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_partner(id):
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result = "", "партнёр не найден", False
        partner = get(
            f"{link_website}api/partner/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
        if "message" not in partner:
            name = "страница " + partner['name']
            if request.method == 'POST':
                message = delete(
                    f"{link_website}api/partner/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
                if "success" in message:
                    result = True
                message = " ".join(list(message.values()))
                images = partner["image"]
                for image in images.split("//"):
                    delete_img(image)
                containerManager.delete_container(f"partner_{id}")
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-delete-form.html', title='Удаление партнёра', message=message, form=form,
                               result=result, name=name, smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/admin-list-auditlog")
@login_required
def admin_auditlog():
    auditlogs = get(
        f"{link_website}api/auditlog/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}").json()
    smartpages = get(f"{link_website}api/smartpage").json()
    return render_template('admin-list-auditlog.html', title='Журнал аудита', auditlogs=auditlogs, smartpages=smartpages, is_admin=(not current_user.is_anonymous))


@app.route("/admin-list-feedback")
@login_required
def admin_feedback():
    feedbacks = get(
        f"{link_website}api/feedback/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}").json()
    smartpages = get(f"{link_website}api/smartpage").json()
    return render_template('admin-feedback-list.html', title='Отзывы', feedbacks=feedbacks, smartpages=smartpages, is_admin=(not current_user.is_anonymous))


@app.route("/admin-delete-feedback/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_feedback(id):
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result = "", "отзыв не найден", False
        feedback = get(
            f"{link_website}api/feedback/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
        if "message" not in feedback:
            name = "отзыв " + feedback['heading']
            if request.method == 'POST':
                message = delete(
                    f"{link_website}api/feedback/{current_user.email}/{password_manager.get_password(current_user.email, current_user.status)}/{id}").json()
                if "success" in message:
                    result = True
                message = " ".join(list(message.values()))
                images = feedback["image"]
                for image in images.split("//"):
                    delete_img(image)
                # containerManager.delete_container(f"feedback_{id}")
        smartpages = get(f"{link_website}api/smartpage").json()
        return render_template('admin-delete-form.html', title='Удаление отзыва', message=message, form=form,
                               result=result, name=name, smartpages=smartpages, is_admin=(not current_user.is_anonymous))
    return you_dont_have_permission()


@app.route("/write-feedback/<string:code>", methods=['GET', 'POST'])
def write_feedback(code):
    form = FeedbackForm()
    message, result, filenames, preview_text = None, False, [], None
    if request.method == 'POST':
        img_list = list(request.files)
        cont = containerManager.get_container(f"feedback_{code}")
        for ind, name in enumerate(request.files):
            file = request.files[name]
            if file.filename != "":
                if img_list[ind] in cont:
                    delete_img(cont[img_list[ind]])
                if file and allowed_file(file.filename):
                    filename = secure_filename(create_new_image_name())
                    save_image(filename, file)
                    filenames.append(filename)
            else:
                if img_list[ind] in cont:
                    filenames.append(cont[img_list[ind]])
        containerManager.add_container(f"feedback_{code}", filenames, True)
        preview_text = Markup(text_transform(form.text.data, filenames, app.config["UPLOAD_FOLDER"]))
        if form.submit.data:
            message = post(f"{link_website}api/feedback",
                           json={"email": form.email.data, "fullname": form.fullname.data, "heading": form.heading.data,
                                 "image": "//".join(filenames), "text": form.text.data, "code": form.code.data}).json()
            if "success" in message:
                result = True
                message = "Спасибо за отзыв"
                containerManager.delete_container(f"feedback_{code}")
            else:
                message = " ".join(list(message.values()))
        elif form.getcode.data:
            code_helper.create_code(form.email.data)
        elif form.preview.data:
            preview_text = Markup(text_transform(form.text.data, filenames, app.config["UPLOAD_FOLDER"]))
    else:
        filenames = containerManager.get_container(f"feedback_{code}").values()
    page = get(f"{link_website}api/smartpage/5").json()
    content = get(f"{link_website}api/content/{page['id']}").json()
    newslist = get(f"{link_website}api/newspage/0/9").json()
    smartpages = get(f"{link_website}api/smartpage").json()
    return render_template('write-feedback.html', title="Отзыв", page=page, content=content, newslist=newslist,
                           smartpages=smartpages, is_admin=(not current_user.is_anonymous), result=result, flag=True,
                           message=message, form=form, preview_text=preview_text, filenames=filenames, image_len=len(filenames) + 1)


@app.route("/contacts")
def contacts():
    page = get(f"{link_website}api/smartpage/5").json()
    content = get(f"{link_website}api/content/{page['id']}").json()
    newslist = get(f"{link_website}api/newspage/0/9").json()
    smartpages = get(f"{link_website}api/smartpage").json()
    return render_template('contacts.html', title=page["heading"], page=page, content=content, newslist=newslist,
                           smartpages=smartpages, is_admin=(not current_user.is_anonymous), code=create_random_name(10))


@app.route("/agro_and_agro-tourism_sector")
def agro_and_agro_tourism_sector():
    page = get(f"{link_website}api/smartpage/1").json()
    content = get(f"{link_website}api/content/{page['id']}").json()
    newslist = get(f"{link_website}api/newspage/0/9").json()
    smartpages = get(f"{link_website}api/smartpage").json()
    return render_template('agro_and_agro_tourism_sector.html', title=page["heading"], page=page, content=content, newslist=newslist,
                           smartpages=smartpages, is_admin=(not current_user.is_anonymous))


@app.route("/partners")
def partners():
    page = get(f"{link_website}api/smartpage/2").json()
    content = get(f"{link_website}api/content/{page['id']}").json()
    newslist = get(f"{link_website}api/newspage/0/9").json()
    smartpages = get(f"{link_website}api/smartpage").json()
    return render_template('partners.html', title=page["heading"], page=page, content=content, newslist=newslist,
                           smartpages=smartpages, is_admin=(not current_user.is_anonymous))


@app.route("/all_news")
def all_news():
    page = get(f"{link_website}api/smartpage/3").json()
    content = get(f"{link_website}api/content/{page['id']}").json()
    newslist = get(f"{link_website}api/newspage/0/9").json()
    smartpages = get(f"{link_website}api/smartpage").json()
    return render_template('all_news.html', title=page["heading"], page=page, content=content, newslist=newslist,
                           smartpages=smartpages, is_admin=(not current_user.is_anonymous))


@app.route("/team")
def team():
    page = get(f"{link_website}api/smartpage/4").json()
    content = get(f"{link_website}api/content/{page['id']}").json()
    newslist = get(f"{link_website}api/newspage/0/9").json()
    smartpages = get(f"{link_website}api/smartpage").json()
    return render_template('team.html', title=page["heading"], page=page, content=content, newslist=newslist,
                           smartpages=smartpages, is_admin=(not current_user.is_anonymous))


@app.route("/page/<string:link>")
def page_by_link(link):
    containerManager.clear_container(app.config['UPLOAD_FOLDER'])
    smartpages = get(f"{link_website}api/smartpage").json()
    if link == smartpages[0]["link"]:
        return redirect("/agro_and_agro-tourism_sector")
    if link == smartpages[1]["link"]:
        return redirect("/partners")
    if link == smartpages[2]["link"]:
        return redirect("/all_news")
    if link == smartpages[3]["link"]:
        return redirect("/team")
    if link == smartpages[4]["link"]:
        return redirect("/contacts")
    page = get(f"{link_website}api/smartpage/{link}").json()
    content = get(f"{link_website}api/content/{page['id']}").json()
    newslist = get(f"{link_website}api/newspage/0/9").json()
    return render_template('generated-page.html', title=page["heading"], page=page, content=content, newslist=newslist,
                           smartpages=smartpages, is_admin=(not current_user.is_anonymous))


@app.route("/news-page/<string:link>")
def news_page(link):
    news = get(f"{link_website}api/news/{link}").json()
    if "message" in news:
        page_not_found()
    # Теперь какой-то рендер теймплейт


@app.route("/test", methods=['GET', 'POST'])
def test():
    smartpages = get(f"{link_website}api/smartpage").json()
    return render_template('partner.html', smartpages=smartpages, is_admin=(not current_user.is_anonymous))


if __name__ == '__main__':
    print("http://127.0.0.1:8000/admin")
    print("http://127.0.0.1:8000/login")
    print("http://127.0.0.1:8000/test")
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
        """
        <a>Агро и Агро-туристический сектор</a>
        <a>Партнёры</a>
        <a>Все новости</a>
        <a>Команда</a>
        <a>Контакты</a>"""

