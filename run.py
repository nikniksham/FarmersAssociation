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
    NewspageResourceUsual, NewspageListRecourseId, NewspageResourceLink, set_path
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
set_path(app.config["UPLOAD_FOLDER"])


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
    if format not in ["png", "gif"]:
        image = image.convert('RGB')
    print(filename)
    image.save(filename)


def save_image(filename, file):
    t1 = threading.Thread(target=save_image_multithreading, args=(os.path.join(app.config["UPLOAD_FOLDER"], filename), file))
    t1.start()
    t1.join()


def save_images(cont_name, files, r_img=True):
    filenames, img_list, cont = [], list(files), containerManager.get_container(cont_name)
    for ind, name in enumerate(files):
        file = files[name]
        if file.filename != "":
            if file and allowed_file(file.filename):
                filename = secure_filename(create_new_image_name())
                save_image(filename, file)
                filenames.append(filename)
        else:
            if img_list[ind] in cont:
                filenames.append(cont[img_list[ind]])
    if r_img and len(filenames) == 0:
        filenames = ["standard.png"]
    for key in cont.keys():
        if key not in img_list:
            delete_img(cont[key])
    containerManager.add_container(cont_name, filenames, True)
    return filenames


def get_standard_params():
    return {"smartpages": get(f"{link_website}api/smartpage").json(), "is_admin": (not current_user.is_anonymous)}


def get_special_params():
    return {"news": get(f"{link_website}api/newspage/0/9").json(), "partner": get(f"{link_website}api/partner").json()}


def delete_img(filename):
    if filename not in ["", "standard.png"] and os.path.exists(f"{app.config['UPLOAD_FOLDER']}{filename}"):
        os.remove(f"{app.config['UPLOAD_FOLDER']}{filename}")


def create_new_image_name(logo=False, gif=False):
    filelist, format = os.listdir(app.config['UPLOAD_FOLDER']), ".gif" if gif else (".png" if logo else ".jpg")
    print(format, gif)
    filename = create_random_name(50) + format
    while filename in filelist:
        filename = create_random_name(50) + format
    return filename


def allowed_file(filename):
    ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg', 'gif']
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def main(port=8000):
    # print(code_helper.create_code("yuramorozov2711@gmail.com"))
    # print(code_helper.create_code("nikniksham@gmail.com"))
    # print(code_helper.create_code("kolya.toropof@gmail.com"))
    # code_helper.clear_codes()
    """session = db_session.create_session()
    session.execute("alter table partner add column 'logo' VARCHAR")"""
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
            password_manager.add_user(form.email.data, form.password.data)
            login_user(user, remember=True)
            return redirect("/admin")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/")
def website_main():
    return render_template('main-page.html', title='Главная страница', params=get_standard_params())


@app.route("/admin")
@login_required
def admin():
    return render_template('admin-panel.html', title='админка', params=get_standard_params())


@app.route("/admin-list-news")
@login_required
def admin_list_news():
    if current_user.status > 0:
        newslist = get(f"{link_website}api/newspage").json()
        return render_template('admin-list-news.html', title='Новости', newslist=newslist, params=get_standard_params())
    return you_dont_have_permission()


@app.route("/admin-create-news", methods=['GET', 'POST'])
@login_required
def admin_create_news():
    if current_user.status > 0:
        form = NewspageForm()
        message, result, preview_text = None, False, None
        if request.method == 'POST':
            filenames = save_images(f"news_{current_user.email}", request.files)
            if form.submit.data:
                message = post(
                    f"{link_website}api/newspage/{current_user.email}/{password_manager.get_password(current_user.email)}",
                    json={"heading": form.heading.data, "text": form.text.data, "image": "//".join(filenames)}).json()
                if "success" in message:
                    result = True
                    containerManager.delete_container(f"news_{current_user.email}")
                message = " ".join(list(message.values()))
            elif form.preview.data:
                preview_text = Markup(text_transform(form.text.data, filenames, app.config["UPLOAD_FOLDER"]))
        else:
            filenames = containerManager.get_container(f"news_{current_user.email}").values()
        return render_template('admin-news-form.html', title='Создание новости', message=message, preview_text=preview_text,
                               form=form, result=result, filenames=filenames, image_len=len(filenames) + 1, params=get_standard_params())
    return you_dont_have_permission()


@app.route("/admin-edit-news/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_news(id):
    if current_user.status > 0:
        form = NewspageForm()
        message, result, filenames, filename, preview_text = None, False, [], None, None
        news = get(
            f"{link_website}api/newspage/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
        if "message" not in list(news):
            if request.method == 'POST':
                filenames = save_images(f"news_{id}", request.files)
                if form.submit.data:
                    message = put(
                        f"{link_website}api/newspage/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}",
                        json={"heading": form.heading.data, "text": form.text.data, "image": "//".join(filenames)}).json()
                    if "success" in message:
                        result = True
                    message = " ".join(list(message.values()))
                elif form.preview.data:
                    preview_text = Markup(text_transform(form.text.data, filenames, app.config["UPLOAD_FOLDER"]))
            else:
                form.heading.data = news["heading"]
                form.text.data = news["text"]
                if containerManager.get_container(f"news_{id}") == {}:
                    filenames = news["image"].split("//")
                else:
                    filenames = containerManager.get_container(f"news_{id}").values()
                containerManager.add_container(f"news_{id}", filenames)
        else:
            message = "Новость не найдена"
        return render_template('admin-news-form.html', title='Редактирование новости', message=message, result=result,
                               form=form, filenames=filenames, image_len=len(filenames) + 1,
                               params=get_standard_params(), preview_text=preview_text)
    return you_dont_have_permission()


@app.route("/admin-delete-news/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_news(id):
    if current_user.status > 0:
        form = DeleteForm()
        message, result, name = None, False, "новость не найдена"
        news = get(
            f"{link_website}api/newspage/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
        if "message" not in news:
            name = "новость " + news["heading"]
            if request.method == 'POST':
                message = delete(
                    f"{link_website}api/newspage/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
                if "success" in message:
                    result = True
                message = " ".join(list(message.values()))
                images = news["image"]
                for image in images.split("//"):
                    delete_img(image)
                containerManager.delete_container(f"news_{id}")
        return render_template('admin-delete-form.html', title='Удаление новости', message=message, form=form,
                               result=result, name=name, params=get_standard_params(), link_back="/admin-list-news")
    return you_dont_have_permission()


@app.route("/admin-list-admin")
@login_required
def admin_list_admin():
    if current_user.status > 0:
        adminlist = get(
            f"{link_website}api/admin/list/{current_user.email}/{password_manager.get_password(current_user.email)}").json()
        return render_template('admin-list-admin.html', title='Новости', adminlist=adminlist, params=get_standard_params(),
                               status=current_user.status, current_id=current_user.id, flag=(current_user.status > 0))
    return you_dont_have_permission()


@app.route("/admin-change-password/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_change_password(id):
    if current_user.status > 1:
        form = AdminForm()
        if current_user.id == id:
            admin = get(f"{link_website}api/admin/{current_user.email}/{password_manager.get_password(current_user.email)}").json()
        else:
            admin = get(f"{link_website}api/admin/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
        message, result, name = None, False, ""
        if "message" not in admin:
            name = f'{admin["name"]} {admin["surname"]}'
            if request.method == 'POST':
                if form.password.data == form.password_again.data:
                    if id == current_user.id:
                        message = put(f"{link_website}api/admin/{current_user.email}/{form.password_current.data}",
                                      json={"password": form.password.data}).json()
                    else:
                        message = put(f"{link_website}api/admin/{current_user.email}/{form.password_current.data}/{id}",
                                      json={"password": form.password.data}).json()
                    if "success" in message:
                        password_manager.add_user(admin["email"], form.password.data)
                        result = True
                    message = " ".join(list(message.values()))
                else:
                    message = "Новые пароли не совпадают"
        else:
            message = list(admin.values())[0]
        return render_template('admin-change-password.html', title=f'Изменение пароля админу {name}', message=message,
                               form=form, result=result, params=get_standard_params())
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
                message = post(
                    f"{link_website}api/admin/{current_user.email}/{password_manager.get_password(current_user.email)}",
                    json={"name": form.name.data, "surname": form.surname.data, "email": form.email.data,
                          "password": form.password.data, "status": form.status.data}).json()
                form.status.data = str(form.status.data)
                if "success" in message:
                    result = True
                message = " ".join(list(message.values()))
            else:
                message = "Пароли не совпадают"
        return render_template('admin-admin-form.html', title='Создание админа', message=message, form=form,
                               result=result, flag=True, params=get_standard_params(),
                               roles=["Без прав", "Модератор", "Админ", "Владелец"][:current_user.status])
    return you_dont_have_permission()


@app.route("/admin-edit-admin/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_admin(id):
    if current_user.status > 1:
        form = AdminForm()
        admin = get(
            f"{link_website}api/admin/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
        form.stat = current_user.status
        message, result, admin_status = None, False, 0
        if "message" not in admin:
            admin_status = admin["status"]
            if request.method == 'POST':
                message = put(
                    f"{link_website}api/admin/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}",
                    json={"name": form.name.data, "surname": form.surname.data, "email": form.email.data,
                          "status": int(form.status.data)}).json()
                if "success" in message:
                    admin_status = int(form.status.data)
                    result = True
                message = " ".join(list(message.values()))
            else:
                print(admin)
                admin_status = admin["status"]
                form.name.data = admin["name"]
                form.surname.data = admin["surname"]
                form.email.data = admin["email"]
                form.status.data = str(admin["status"])
        else:
            message = list(admin.values())[0]
        return render_template('admin-admin-form.html', title='Редактирование админа', message=message, form=form,
                               result=result, flag=False, params=get_standard_params(), admin_status=admin_status,
                               roles=["Без прав", "Модератор", "Админ", "Владелец"][:current_user.status])
    return you_dont_have_permission()


@app.route("/admin-delete-admin/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_admin(id):
    if current_user.status > 1:
        form = DeleteForm()
        message, name, result = None, "пользователь не найден", False
        admin = get(
            f"{link_website}api/admin/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
        if "message" not in admin:
            name = "админа " + f"{admin['name']} {admin['surname']}"
            if admin["status"] < current_user.status:
                if request.method == 'POST':
                    message = delete(
                        f"{link_website}api/admin/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
                    if "success" in message:
                        result = True
                    message = " ".join(list(message.values()))
            else:
                message = "У вас недостаточно прав для этого"
        else:
            name = "пользователь не найден"
        return render_template('admin-delete-form.html', title='Удаление админа', message=message, form=form,
                               result=result, name=name, params=get_standard_params(), link_back="/admin-list-admin")
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
        return render_template('admin-list-smartpage.html', title='Страницы', smartpagelist=smartpagelist,
                               contentdict=contentdict, types={"News": "Новости", "Image": "Картинки", "Text": "Текст", "Partner": "Партнёры"},
                               params=get_standard_params(), page_id=page_id)
    return you_dont_have_permission()


@app.route("/admin-create-smartpage", methods=['GET', 'POST'])
@login_required
def admin_create_smartpage():
    if current_user.status > 0:
        form = SmartpageForm()
        message, result, filenames = None, False, []
        if request.method == 'POST':
            filenames = save_images(f"smartpage_{current_user.email}", request.files)
            message = post(
                f"{link_website}api/smartpage/{current_user.email}/{password_manager.get_password(current_user.email)}",
                json={"heading": form.heading.data, "image": "//".join(filenames)}).json()
            if "success" in message:
                result = True
            message = " ".join(list(message.values()))
        return render_template('admin-smartpage-form.html', title='Создание страницы', message=message, form=form,
                               result=result, filenames=filenames, image_len=1, params=get_standard_params())
    return you_dont_have_permission()


@app.route("/admin-edit-smartpage/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_smartpage(id):
    if current_user.status > 0:
        form = SmartpageForm()
        smartpage = get(
            f"{link_website}api/smartpage/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
        message, result, filenames, filename = None, False, [], None
        if "message" not in smartpage:
            if request.method == 'POST':
                filenames = save_images(f"smartpage_{id}", request.files)
                message = put(
                    f"{link_website}api/smartpage/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}",
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
        return render_template('admin-smartpage-form.html', title='Редактирование страницы', message=message, form=form,
                               result=result, flag=False, filenames=filenames, image_len=len(filenames) + 1,
                               params=get_standard_params())
    return you_dont_have_permission()


@app.route("/admin-delete-smartpage/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_smartpage(id):
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result = "", "страница не найдена", False
        smartpage = get(
            f"{link_website}api/smartpage/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
        if "message" not in smartpage:
            name = "страница " + smartpage['heading']
            if request.method == 'POST':
                message = delete(
                    f"{link_website}api/smartpage/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
                if "success" in message:
                    result = True
                message = " ".join(list(message.values()))
                images = smartpage["image"]
                for image in images.split("//"):
                    delete_img(image)
                containerManager.delete_container(f"smartpage_{id}")
        return render_template('admin-delete-form.html', title='Удаление страницы', message=message, form=form,
                               result=result, name=name, params=get_standard_params(), link_back="/admin-list-smartpage/0")
    return you_dont_have_permission()


@app.route("/admin-create-content/<int:page_id>", methods=['GET', 'POST'])
@login_required
def admin_create_content(page_id):
    if current_user.status > 0:
        form = ContentForm()
        message, result, filenames, filename = None, False, [], None
        if request.method == 'POST':
            filenames = save_images(f"content_{current_user.email}", request.files, False)
            image = "" if len(filenames) == 0 else "//".join(filenames)
            message = post(
                f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email)}",
                json={"type": form.type.data, "text": form.text.data, "page_id": page_id,
                      "heading": form.heading.data, "image": image}).json()
            if "success" in message:
                result = True
            message = " ".join(list(message.values()))
        return render_template('admin-content-form.html', title='Создание контента', message=message, form=form,
                               result=result, flag=True, filenames=filenames, image_len=1, params=get_standard_params(),
                               page_id=page_id)
    return you_dont_have_permission()


@app.route("/admin-edit-content-move-up/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_content_move_up(id):
    if current_user.status > 0:
        content = get(
            f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
        put(
            f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}",
            json={"position": content["position"] - 1})
        return redirect(f"/admin-list-smartpage/{content['smartpage_id']}")
    return you_dont_have_permission()


@app.route("/admin-edit-content-move-down/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_content_move_down(id):
    if current_user.status > 0:
        content = get(
            f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
        put(f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}",
            json={"position": content["position"] + 1}).json()
        return redirect(f"/admin-list-smartpage/{content['smartpage_id']}")
    return you_dont_have_permission()


@app.route("/admin-edit-content/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_content(id):
    if current_user.status > 0:
        form = ContentForm()
        content = get(
            f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
        message, result, filenames, filename, page_id = None, False, [], None, 0
        if "message" not in content:
            if request.method == 'POST':
                filenames = save_images(f"content_{id}", request.files, False)
                image = "" if len(filenames) == 0 else "//".join(filenames)
                message = put(
                    f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}",
                    json={"type": form.type.data, "text": form.text.data, "heading": form.heading.data, "image": image}).json()
                if "success" in message:
                    result = True
                message = " ".join(list(message.values()))
            else:
                form.type.data = content["type"]
                form.text.data = content["text"]
                form.heading.data = content["heading"]
                page_id = content["smartpage_id"]
                if content["image"]:
                    filenames = content["image"].split("//")
                containerManager.add_container(f"content_{id}", filenames)
        else:
            message = "Контент не найден"
        return render_template('admin-content-form.html', title='Редактирование контента', message=message, form=form,
                               result=result, flag=False, filenames=filenames, image_len=len(filenames) + 1,
                               params=get_standard_params(), page_id=page_id)
    return you_dont_have_permission()


@app.route("/admin-delete-content/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_content(id):
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result, page_id = "", "контент не найден", False, 0
        content = get(
            f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
        if "message" not in content:
            page_id = content["smartpage_id"]
            name = "контент " + content['heading']
            if request.method == 'POST':
                message = delete(
                    f"{link_website}api/content/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
                if "success" in message:
                    result = True
                message = " ".join(list(message.values()))
                images = content["image"]
                for image in images.split("//"):
                    delete_img(image)
                containerManager.delete_container(f"content_{id}")
        return render_template('admin-delete-form.html', title='Удаление контента', message=message, form=form,
                               result=result, name=name, params=get_standard_params(),
                               link_back=f"/admin-list-smartpage/{page_id}")
    return you_dont_have_permission()


@app.route("/admin-list-partner")
@login_required
def admin_list_partner():
    if current_user.status > 0:
        partnerlist = get(f"{link_website}api/partner").json()
        return render_template('admin-list-partner.html', title='Партнёры', partnerlist=partnerlist, params=get_standard_params())
    return you_dont_have_permission()


@app.route("/admin-create-partner", methods=['GET', 'POST'])
@login_required
def admin_create_partner():
    if current_user.status > 0:
        form = PartnerForm()
        message, result, filenames1, filenames2 = None, False, [], []
        if request.method == 'POST':
            img_list = list(request.files)
            for ind, name in enumerate(request.files):
                file = request.files[name]
                if file.filename != "":
                    if file and allowed_file(file.filename):
                        if img_list[ind] in ["icon", "iconInput"]:
                            filename = secure_filename(create_new_image_name(True))
                            save_image(filename, file)
                            filenames1.append(filename)
                        else:
                            filename = secure_filename(create_new_image_name())
                            save_image(filename, file)
                            filenames2.append(filename)
            if len(filenames1) == 0:
                filenames1 = ["standard.png"]
            if len(filenames2) == 0:
                filenames2 = ["standard.png"]
            message = post(
                f"{link_website}api/partner/{current_user.email}/{password_manager.get_password(current_user.email)}",
                json={"name": form.name.data, "logo": "//".join(filenames1), "image": "//".join(filenames2),
                      "text": form.text.data, "link": form.link.data}).json()
            if "success" in message:
                result = True
            message = " ".join(list(message.values()))
        return render_template('admin-partner-form.html', title='Создание партнёра', message=message, form=form,
                               result=result, flag=True, filenames1=filenames1, filenames2=filenames2, image_len=len(filenames2),
                               params=get_standard_params())
    return you_dont_have_permission()


@app.route("/admin-edit-partner/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_partner(id):
    if current_user.status > 0:
        form = PartnerForm()
        partner = get(
            f"{link_website}api/partner/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
        message, result, filenames1, filenames2 = None, False, [], []
        if "message" not in partner:
            if request.method == 'POST':
                cont1 = containerManager.get_container(f"partner_logo_{id}")
                cont2 = containerManager.get_container(f"partner_image_{id}")
                img_list = list(request.files)
                for ind, name in enumerate(request.files):
                    file = request.files[name]
                    if file.filename != "":
                        if file and allowed_file(file.filename):
                            if img_list[ind] in ["icon", "iconInput"]:
                                filename = secure_filename(create_new_image_name(True))
                                save_image(filename, file)
                                filenames1.append(filename)
                            else:
                                filename = secure_filename(create_new_image_name())
                                save_image(filename, file)
                                filenames2.append(filename)
                    else:
                        if img_list[ind] in ["icon", "iconInput"]:
                            if "image1" in cont1:
                                filenames1.append(cont1["image1"])
                        else:
                            if img_list[ind] in cont2:
                                filenames2.append(cont2[img_list[ind]])

                if len(filenames1) == 0:
                    filenames1 = ["standard.png"]
                if len(filenames2) == 0:
                    filenames1 = ["standard.png"]
                for key in cont1.keys():
                    if key not in img_list:
                        delete_img(cont1[key])
                for key in cont2.keys():
                    if key not in img_list:
                        delete_img(cont2[key])
                containerManager.add_container(f"partner_logo_{id}", filenames1)
                containerManager.add_container(f"partner_image_{id}", filenames2)
                message = put(
                    f"{link_website}api/partner/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}",
                    json={"name": form.name.data, "logo": "//".join(filenames1), "image": "//".join(filenames2),
                          "text": form.text.data, "link": form.link.data}).json()
                if "success" in message:
                    result = True
                message = " ".join(list(message.values()))
            else:
                form.name.data = partner["name"]
                form.text.data = partner["text"]
                form.link.data = partner["link"]
                filenames1 = partner["logo"].split("//") if containerManager.get_container(f"partner_logo_{id}") == {} \
                    else list(containerManager.get_container(f"partner_logo_{id}").values())
                filenames2 = partner["image"].split("//") if containerManager.get_container(f"partner_image_{id}") == {} \
                    else list(containerManager.get_container(f"partner_image_{id}").values())
                containerManager.add_container(f"partner_logo_{id}", filenames1)
                containerManager.add_container(f"partner_image_{id}", filenames2)
        else:
            message = "Партнёр не найден"
        return render_template('admin-partner-form.html', title='Редактирование партнёра', message=message, form=form,
                               result=result, flag=False, filenames1=filenames1, filenames2=filenames2,
                               image_len=len(filenames2) + 1, params=get_standard_params())
    return you_dont_have_permission()


@app.route("/admin-delete-partner/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_partner(id):
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result = "", "партнёр не найден", False
        partner = get(
            f"{link_website}api/partner/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
        if "message" not in partner:
            name = "страница " + partner['name']
            if request.method == 'POST':
                message = delete(
                    f"{link_website}api/partner/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
                if "success" in message:
                    result = True
                message = " ".join(list(message.values()))
                images = partner["image"]
                for image in images.split("//"):
                    delete_img(image)
                containerManager.delete_container(f"partner_{id}")
        return render_template('admin-delete-form.html', title='Удаление партнёра', message=message, form=form,
                               result=result, name=name, params=get_standard_params(), link_back="/admin-list-partner")
    return you_dont_have_permission()


@app.route("/admin-list-auditlog")
@login_required
def admin_auditlog():
    auditlogs = get(
        f"{link_website}api/auditlog/{current_user.email}/{password_manager.get_password(current_user.email)}").json()
    return render_template('admin-list-auditlog.html', title='Журнал аудита', auditlogs=auditlogs, params=get_standard_params())


@app.route("/admin-list-feedback")
@login_required
def admin_feedback():
    feedbacks = get(
        f"{link_website}api/feedback/{current_user.email}/{password_manager.get_password(current_user.email)}").json()
    return render_template('admin-feedback-list.html', title='Отзывы', feedbacks=feedbacks, params=get_standard_params())


@app.route("/admin-delete-feedback/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_feedback(id):
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result = "", "отзыв не найден", False
        feedback = get(
            f"{link_website}api/feedback/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
        if "message" not in feedback:
            name = "отзыв " + feedback['heading']
            if request.method == 'POST':
                message = delete(
                    f"{link_website}api/feedback/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
                if "success" in message:
                    result = True
                message = " ".join(list(message.values()))
                images = feedback["image"]
                for image in images.split("//"):
                    delete_img(image)
                # containerManager.delete_container(f"feedback_{id}")
        return render_template('admin-delete-form.html', title='Удаление отзыва', message=message, form=form,
                               result=result, name=name, params=get_standard_params(), link_back="/admin-list-feedback")
    return you_dont_have_permission()


@app.route("/write-feedback/<int:id>", methods=['GET', 'POST'])
@login_required
def write_feedback(id):
    feedback = get(f"{link_website}api/feedback/{current_user.email}/{password_manager.get_password(current_user.email)}/{id}").json()
    print(feedback)
    if "message" not in feedback:
        return page_not_found()
    return render_template('news.html', title=feedback["heading"], params=get_standard_params(), feedback=feedback)


@app.route("/write-feedback/<string:code>", methods=['GET', 'POST'])
def write_feedback(code):
    form = FeedbackForm()
    message, result, filenames, preview_text = None, False, [], None
    if request.method == 'POST':
        filenames = save_images(f"feedback_{code}", request.files)
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
    return render_template('write-feedback.html', title="Отзыв", page=page, content=content,
                           params=get_standard_params(), result=result, flag=True, message=message, form=form,
                           preview_text=preview_text, filenames=filenames, image_len=len(filenames) + 1,
                           special_params=get_special_params())


@app.route("/contacts")
def contacts():
    page = get(f"{link_website}api/smartpage/5").json()
    content = get(f"{link_website}api/content/{page['id']}").json()
    return render_template('contacts.html', title=page["heading"], page=page, content=content,
                           params=get_standard_params(), code=create_random_name(10), special_params=get_special_params())


@app.route("/agro_and_agro-tourism_sector")
def agro_and_agro_tourism_sector():
    page = get(f"{link_website}api/smartpage/1").json()
    content = get(f"{link_website}api/content/{page['id']}").json()
    return render_template('agro_and_agro_tourism_sector.html', title=page["heading"], page=page, content=content,
                           params=get_standard_params(), special_params=get_special_params())


@app.route("/partners")
def partners():
    page = get(f"{link_website}api/smartpage/2").json()
    content = get(f"{link_website}api/content/{page['id']}").json()
    return render_template('partners.html', title=page["heading"], page=page, content=content,
                           params=get_standard_params(), special_params=get_special_params())


@app.route("/all_news")
def all_news():
    page = get(f"{link_website}api/smartpage/3").json()
    content = get(f"{link_website}api/content/{page['id']}").json()
    return render_template('all_news.html', title=page["heading"], page=page, content=content,
                           params=get_standard_params(), special_params=get_special_params())


@app.route("/team")
def team():
    page = get(f"{link_website}api/smartpage/4").json()
    content = get(f"{link_website}api/content/{page['id']}").json()
    return render_template('team.html', title=page["heading"], page=page, content=content, params=get_standard_params(),
                           special_params=get_special_params())


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
    return render_template('generated-page.html', title=page["heading"], page=page, content=content,
                           params=get_standard_params(), special_params=get_special_params())


@app.route("/news-page/<string:link>")
def news_page(link):
    news = get(f"{link_website}api/newspage/{link}").json()
    if "message" in news:
        return page_not_found()
    print(news)
    return render_template('news.html', title=news["heading"], params=get_standard_params(), news=news)


@app.route("/test", methods=['GET', 'POST'])
def test():
    return render_template('partner.html', params=get_standard_params())


@app.route('/logout')
@login_required
def logout():
    password_manager.delete_user(current_user.email)
    logout_user()
    return redirect("/")


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

