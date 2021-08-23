import os
import random
import threading
import moviepy.editor as mp
from markupsafe import Markup
from flask import Flask, render_template, request
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_restful import Api
from requests import put, get, post
from werkzeug.utils import redirect
from data import db_session
from data.API.AdminAPI.AdminResource import CreateAdminResource, AdminResource, UserResourceAdmin
from data.API.ConfirmationCodeAPI.ConfirmationcodeResource import CodeForConfirmation
from data.API.AuditlogAPI.AuditlogResource import AuditlogResource
from data.API.ContentAPI.ContentResource import CreateContentResource, ContentResource, ContentListRecourse, \
    ContentListRecourseId
from data.API.FeedbackAPI.FeedbackResource import FeedbackResource, CreateFeedbackResource, FeedbackTransportImage
from data.API.NewspageAPI.NewspageResource import NewspageResource, NewspageListRecourse, CreateNewspageResource, \
    NewspageResourceUsual, NewspageListRecourseId, NewspageResourceLink, NewspageListRecourseTags
from data.API.PartnerAPI.PartnerResource import PartnerResource, PartnerResourceUsual, PartnerListRecourse, \
    CreatePartnerResource
from data.API.SmartpageAPI.SmartpageResource import CreateSmartpageResource, SmartpageResource, SmartpageListRecourse, \
    SmartpageRecourseUsual, SmartpageRecourseLink
from data.API.AddressAPI.AddressResource import AddressListRecourse, AdminResourceAddress
from data.API.EmailAPI.EmailResource import EmailListRecourse, AdminResourceEmail, CreateEmailResource
from data.API.PhoneAPI.PhoneResource import PhoneListRecourse, AdminResourcePhone, CreatePhoneResource
from data.API.SocialmediaAPI.SocialmediaResource import SocialmediaListRecourse, AdminResourceSocialmedia, \
    CreateSocialmediaResource
from data.API.WorkerAPI.WorkerResource import WorkerResourceUsual, WorkerResource, WorkerListRecourse, \
    CreateWorkerResource
from data.API.MemberAPI.MemberResource import MemberResourceUsual, MemberResource, MemberListRecourse, \
    CreateMemberResource
from data.API.TextAPI.TextResource import TextListRecourse, CreateTextResource, AdminResourceText
from data.API.SeoAPI.SeoResource import SeoGetRecourse, AdminResourceSeo
from data.user import User
from main import ManagerContainer, text_transform, get_coord, PasswordManager, write_log
from data.forms import NewspageForm, AdminForm, FeedbackForm, ContentForm, PartnerForm, SmartpageForm, DeleteForm, \
    StartForm, PhoneForm, AddressForm, EmailForm, SocialmediaForm, WorkerForm, SeoForm, TextForm, MemberForm
from werkzeug.utils import secure_filename
from PIL import Image
import config
import shutil

load_new_footer_params, load_new_params, load_seo_params = True, True, True
link_website = "http://127.0.0.1:8000/"
link_website_heroku = "https://farmersassociation.herokuapp.com/"
link_web = "https://фермермо.рф"
link_web_2 = "https://xn--e1aaubkic1a.xn--p1ai/"
# link_website = link_website_heroku
let = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
application = Flask(__name__)
application.config.from_object(config)
api = Api(application)
password_manager = PasswordManager()
# Подключаем api

# AdminApi
api.add_resource(CreateAdminResource, "/api/admin/create")
api.add_resource(AdminResource, "/api/admin")
api.add_resource(UserResourceAdmin, "/api/admin/<int:user_id>")

# NewsApi
api.add_resource(CreateNewspageResource, "/api/newspage")
api.add_resource(NewspageResource, "/api/newspage/<int:newspage_id>")
api.add_resource(NewspageResourceUsual, "/api/newspage/<int:newspage_id>")
api.add_resource(NewspageListRecourseId, "/api/newspage/<int:start_id>/<int:end_id>")
api.add_resource(NewspageListRecourse, "/api/newspage")
api.add_resource(NewspageResourceLink, "/api/newspage/<string:link>")
api.add_resource(NewspageListRecourseTags, "/api/newspage/<int:start_id>/<int:end_id>/<string:text>")

# SmartpageApi
api.add_resource(CreateSmartpageResource, "/api/smartpage")
api.add_resource(SmartpageResource, "/api/smartpage/<int:smartpage_id>")
api.add_resource(SmartpageRecourseUsual, "/api/smartpage/<int:smartpage_id>")
api.add_resource(SmartpageRecourseLink, "/api/smartpage/<string:link>")
api.add_resource(SmartpageListRecourse, "/api/smartpage")

# ContentApi
api.add_resource(CreateContentResource, "/api/content")
api.add_resource(ContentResource, "/api/content/<int:content_id>")
api.add_resource(ContentListRecourse, "/api/content")
api.add_resource(ContentListRecourseId, "/api/content/<int:smartpage_id>")

# WorkerApi
api.add_resource(WorkerResource, "/api/worker/<int:worker_id>")
api.add_resource(WorkerResourceUsual, "/api/worker/<int:worker_id>")
api.add_resource(WorkerListRecourse, "/api/worker")
api.add_resource(CreateWorkerResource, "/api/worker")

# PartnerApi
api.add_resource(CreatePartnerResource, "/api/partner")
api.add_resource(PartnerResource, "/api/partner/<int:partner_id>")
api.add_resource(PartnerResourceUsual, "/api/partner/<int:partner_id>")
api.add_resource(PartnerListRecourse, "/api/partner")

# MemberApi
api.add_resource(MemberResource, "/api/member/<int:member_id>")
api.add_resource(MemberResourceUsual, "/api/member/<int:member_id>")
api.add_resource(MemberListRecourse, "/api/member")
api.add_resource(CreateMemberResource, "/api/member")

# AuditlogApi
api.add_resource(AuditlogResource, "/api/auditlog")

# FeedbackApi
api.add_resource(FeedbackResource, "/api/feedback")
api.add_resource(FeedbackTransportImage, "/api/feedback/<int:feedback_id>/<string:code>")
api.add_resource(CreateFeedbackResource, "/api/feedback")

# AddressApi
api.add_resource(AdminResourceAddress, "/api/address/<int:address_id>")
api.add_resource(AddressListRecourse, "/api/address")

# EmailApi
api.add_resource(AdminResourceEmail, "/api/email/<int:email_id>")
api.add_resource(CreateEmailResource, "/api/email")
api.add_resource(EmailListRecourse, "/api/email")

# PhoneApi
api.add_resource(AdminResourcePhone, "/api/phone/<int:phone_id>")
api.add_resource(CreatePhoneResource, "/api/phone")
api.add_resource(PhoneListRecourse, "/api/phone")

# SocialmediaApi
api.add_resource(AdminResourceSocialmedia, "/api/socialmedia/<int:socialmedia_id>")
api.add_resource(CreateSocialmediaResource, "/api/socialmedia")
api.add_resource(SocialmediaListRecourse, "/api/socialmedia")
db_session.global_init("db/FarmersAssociation.sqlite")

# SeoApi
api.add_resource(AdminResourceSeo, "/api/seo/<int:seo_id>")
api.add_resource(SeoGetRecourse, "/api/seo/<int:seo_id>")

# TextApi
api.add_resource(TextListRecourse, "/api/text")
api.add_resource(CreateTextResource, "/api/text")
api.add_resource(AdminResourceText, "/api/text/<int:text_id>")

login_manager = LoginManager()
login_manager.init_app(application)
code_helper = CodeForConfirmation()
containerManager = ManagerContainer()
formatting_text_instruction = \
    ["<br> новая строка - Указывается в месте переноса на новую строку",
     "<p></p> Текст между тэгов будет курсивным", "<b></b> Текст между тэгов будет жирным",
     "<h></h> Текст между тэгов будет заголовочным и по середине экрана",
     "<a href></a> Текст между тэгов будет подчёркнутым и содержать в себе ссылку, написанную на месте href",
     "<image id> Вставляет на этом месте картинку из поля загрузки картинок (нумерация изображений идёт с 1)"]
formatting_text_instruction_usual = \
    ["<image id> Вставляет на этом месте картинку из поля загрузки картинок (нумерация изображений идёт с 1)"]
special_params = {}


def set_map_params():
    partners, provinces, occupations = special_params["partner"], [], []
    for partner in partners:
        if partner['province'] not in provinces:
            provinces.append(partner['province'])
        for ocup in partner['occupation'].split("//"):
            ocup = ocup.strip().capitalize()
            if ocup not in occupations:
                occupations.append(ocup)
    special_params["provinces"] = provinces
    special_params["occupations"] = occupations


def set_footer_params():
    special_params["numbers"] = get(f"{link_website}api/phone").json()
    special_params["socials"] = get(f"{link_website}api/socialmedia").json()
    special_params["emails"] = get(f"{link_website}api/email").json()
    special_params["address"] = get(f"{link_website}api/address").json()
    special_params["link"] = link_website
    special_params['our_coord'] = get_coord(special_params["address"][0]["place"])["success"][0]


def set_seo_params():
    seoparams = get(f"{link_website}api/seo/1").json()
    special_params["seo"] = {"icon": "logo.png", "link_icon": "logo-sm.png", "title": seoparams['title'],
                             "description": seoparams["description"], "tags": seoparams["tags"].split(", ")}


def set_other_params():
    special_params["news"] = get(f"{link_website}api/newspage/0/9").json()
    partners = get(f"{link_website}api/partner").json()
    for ind, partner in enumerate(partners):
        partners[ind]["ratio"] = get_ratio(partner['logo'].split("//")[0])
    special_params['partner'] = partners
    special_params["smartpages"] = get(f"{link_website}api/smartpage").json()
    special_params["worker"] = get(f"{link_website}api/worker").json()
    special_params["text"] = get(f"{link_website}api/text").json()
    special_params["member"] = get(f"{link_website}api/member").json()
    set_map_params()


def crop_center(img):
    img_width, img_height, min_size = img.size[0], img.size[1], min(img.size)
    return img.crop(((img_width - min_size) // 2, (img_height - min_size) // 2,
                     (img_width + min_size) // 2, (img_height + min_size) // 2))


def get_image_name(link):
    link = link.split("//")
    images = {"vk.com": "vk.png", "t.me": "telegram.png", "instagram.com": "instagram.png",
              "facebook.com": "facebook.png", "twitter.com": "twitter.png"}
    if len(link) > 1:
        for key in images.keys():
            if key in link[1]:
                return f"socialmedia/{images[key]}"
    return "socialmedia/socialmedia.png"


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


def create_random_name(name_len):
    return ''.join([random.choice(let) for i in range(name_len)])


def convert_video_to_gif_multithreading(gif, path):
    gif.write_gif(path, fps=10, verbose=False, logger=None)
    gif.close()


def give_me_gif_filenames(filename, cont, path="static/img/"):
    if os.path.exists(path+filename):
        video = mp.VideoFileClip(path+filename)
        duration, filenames = video.duration, []
        count = int(duration // 7 if duration > 7 else 1)
        for i in range(count):
            filename = f"{create_random_name(50)}.gif"
            filenames.append(filename)
            gif = video.subclip(7 * i, duration if (i + 1) * 7 > duration else (i + 1) * 7)
            t1 = threading.Thread(target=convert_video_to_gif_multithreading, args=(gif, f"{path}{cont}/{filename}"))
            t1.start()
            t1.join()
        video.close()
        return filenames
    return []


def save_image_multithreading(filename, file):
    path = "/".join(filename.split("/")[:-1])
    if not os.path.exists(path):
        os.makedirs(path)
    file.save(filename)
    image = Image.open(filename)
    if image.size[0] > 1280 or image.size[1] > 720:
        image.thumbnail((1280, 720))
    split_name = filename.split('.')
    path, format = '.'.join(split_name[:-1]), split_name[-1]
    if format not in ["png", "gif"]:
        image = image.convert('RGB')
    if format != "gif":
        image.save(filename)


def save_image(filename, file):
    t1 = threading.Thread(target=save_image_multithreading, args=(os.path.join(application.config["UPLOAD_FOLDER"], filename), file))
    t1.start()
    t1.join()


def get_ratio(filename, path=application.config['UPLOAD_FOLDER']):
    ratio = 1
    if os.path.exists(path+filename):
        img = Image.open(path+filename)
        ratio = img.size[0] / img.size[1]
    return ratio


def check_user():
    return not password_manager.user_is_authed(current_user.email)


def clear_folder(folder_name, path=application.config['UPLOAD_FOLDER']):
    if os.path.exists(path+folder_name):
        delete_folder(folder_name, path=path)
    os.makedirs(path+folder_name)


def delete_everything_except(folder_name, filenames, path=application.config['UPLOAD_FOLDER']):
    if os.path.exists(path+folder_name):
        for filename in os.listdir(path + folder_name):
            if f"{folder_name}/{filename}" not in filenames and os.path.exists(f"{path}{folder_name}/{filename}"):
                os.remove(f"{path}{folder_name}/{filename}")


def delete_folder(folder_name, path=application.config['UPLOAD_FOLDER']):
    if os.path.exists(path+folder_name):
        for filename in os.listdir(path + folder_name):
            os.remove(f"{path}{folder_name}/{filename}")
        os.rmdir(path+folder_name)


def copy_files(old_folder, new_folder, filenames):
    path, new_filenames = application.config['UPLOAD_FOLDER'], []
    clear_folder(new_folder)
    if os.path.exists(path+old_folder):
        for filename in filenames:
            if filename != "" and os.path.exists(path + filename):
                new_filenames.append(f"{new_folder}/{filename.split('/')[-1]}")
                shutil.copy(f"{path}{old_folder}/{filename.split('/')[-1]}", f"{path}{new_folder}/{filename.split('/')[-1]}")
    return new_filenames


def transport_images(old_folder, new_folder, filenames):
    new_filenames, path = [], application.config['UPLOAD_FOLDER']
    clear_folder(new_folder)
    for filename in filenames:
        if os.path.exists(path+filename):
            os.replace(path+filename, f'{path}{new_folder}/{filename.split("/")[-1]}')
            new_filenames.append(f'{new_folder}/{filename.split("/")[-1]}')
    delete_folder(old_folder)
    return new_filenames


def save_images(cont_name, files, r_img=True, max_image=None, auto_delete=False, logo=False, cont_logo=None, gif=True, icon=False, feedback=False):
    filenames, filenames2, img_list, cont, cont2 = [], [], list(files), containerManager.get_container(cont_name), containerManager.get_container(cont_logo)
    for ind, name in enumerate(files):
        if max_image and len(filenames) >= max_image:
            break
        file = files[name]
        if file.filename != "":
            if file and allowed_file(file.filename, feedback):
                gif_i, mp4 = False, False
                if file.filename.split(".")[-1] == "gif":
                    gif_i = gif
                if file.filename.split(".")[-1] == "mp4":
                    mp4 = True
                if logo and img_list[ind] in ["icon", "iconInput"]:
                    if gif_i:
                        filename = f"{cont_logo}/" + secure_filename(create_new_image_name(gif=gif_i))
                    else:
                        filename = f"{cont_logo}/" + secure_filename(create_new_image_name(logo=True))
                    save_image(filename, file)
                    filenames2.append(filename)
                else:
                    if mp4:
                        file.save(f'{application.config["UPLOAD_FOLDER"]}tmp/gif_{current_user.email}.mp4')
                        for filename in give_me_gif_filenames(f"tmp/gif_{current_user.email}.mp4", cont_name):
                            filenames.append(cont_name+"/"+filename)
                        if os.path.exists(f'{application.config["UPLOAD_FOLDER"]}tmp/gif_{current_user.email}.mp4'):
                            os.remove(f'{application.config["UPLOAD_FOLDER"]}tmp/gif_{current_user.email}.mp4')
                    else:
                        filename = f"{cont_name}/" + secure_filename(create_new_image_name(gif=gif_i))
                        save_image(filename, file)
                        filenames.append(filename)
        else:
            if logo and img_list[ind] in ["icon", "iconInput"] and "image1" in cont2:
                filenames2.append(cont2["image1"])
            elif icon and img_list[ind] in ["icon1", "iconInput1"] and "image1" in cont:
                filenames.append(cont["image1"])
            elif img_list[ind] in cont:
                filenames.append(cont[img_list[ind]])
    if r_img:
        img = Image.open(f"{application.config['UPLOAD_FOLDER']}standard.png")
        if logo and len(filenames2) == 0:
            if not os.path.exists(f"{application.config['UPLOAD_FOLDER']}{cont_logo}"):
                os.makedirs(f"{application.config['UPLOAD_FOLDER']}{cont_logo}")
            img.save(f"{application.config['UPLOAD_FOLDER']}{cont_logo}/standard.png")
            filenames2 = [f"{cont_logo}/standard.png"]
        if len(filenames) == 0:
            if not os.path.exists(f"{application.config['UPLOAD_FOLDER']}{cont_name}"):
                os.makedirs(f"{application.config['UPLOAD_FOLDER']}{cont_name}")
            img.save(f"{application.config['UPLOAD_FOLDER']}{cont_name}/standard.png")
            filenames = [f"{cont_name}/standard.png"]
    if logo:
        containerManager.add_container(cont_logo, filenames2, auto_delete)
    containerManager.add_container(cont_name, filenames, auto_delete)
    if logo:
        return filenames, filenames2
    return filenames


def get_special_params():
    global load_new_footer_params, load_new_params, load_seo_params
    containerManager.clear_container(application.config['UPLOAD_FOLDER'])
    if load_new_footer_params:
        load_new_footer_params = False
        set_footer_params()
    if load_new_params:
        load_new_params = False
        set_other_params()
    if load_seo_params:
        load_seo_params = False
        set_seo_params()
    local_special_params = special_params.copy()
    local_special_params["is_admin"] = not current_user.is_anonymous
    return local_special_params


def delete_img(filename):
    if filename not in ["", "standard.png"] and os.path.exists(f"{application.config['UPLOAD_FOLDER']}{filename}"):
        os.remove(f"{application.config['UPLOAD_FOLDER']}{filename}")


def create_new_image_name(logo=False, gif=False):
    filelist, format = os.listdir(application.config['UPLOAD_FOLDER']), ".gif" if gif else (".png" if logo else ".jpg")
    filename = create_random_name(50) + format
    while filename in filelist:
        filename = create_random_name(50) + format
    return filename


def allowed_file(filename, feedback=False):
    ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4']
    ALLOWED_EXTENSIONS_FEEDBACK = ['pdf', 'png', 'jpg', 'jpeg']
    if feedback:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_FEEDBACK
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def main(port=8000):
    """session = db_session.create_session()
    session.execute("alter table partner add column 'logo' VARCHAR")"""
    application.run(port=port)


def you_dont_have_permission():
    return redirect("/")


def page_not_found():
    return redirect("/")


@application.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_anonymous:
        if password_manager.user_is_authed(current_user.email) is False:
            logout_user()
        else:
            return redirect("/")
    form = AdminForm()
    if request.method == 'POST':
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        session.close()
        if user and user.check_password(form.password.data):
            password_manager.add_user(form.email.data, form.password.data)
            login_user(user, remember=True)
            write_log(f"User login {password_manager.user_is_authed(current_user.email)} {current_user.email}")
            return redirect("/admin")
        return render_template('login.html', message="Неправильный логин или пароль", form=form, special_params=get_special_params())
    return render_template('login.html', title='Авторизация', form=form, special_params=get_special_params())


@application.route("/admin")
@login_required
def admin():
    if check_user():
        return redirect("/login")
    return render_template('admin-panel.html', title='админка', special_params=get_special_params())


@application.route("/admin-footer-settings")
@login_required
def admin_footer_settings():
    set_footer_params()
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = StartForm()
        message, result = "", False
        return render_template('form/admin-form-footer.html', form=form, message=message, result=result,
                               special_params=get_special_params(), title="Настройка подвала")
    return you_dont_have_permission()


@application.route("/admin-seo-settings", methods=['GET', 'POST'])
@login_required
def admin_seo_settings():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = SeoForm()
        seoparams = get(f"{link_website}api/seo/1").json()
        message, result, img_list = "", False, list(request.files)
        if request.method == 'POST':
            if form.set_logo.data:
                for ind, name in enumerate(request.files):
                    file = request.files[name]
                    if file.filename != "" and img_list[ind] in ["icon1", "iconInput1"]:
                        if file and allowed_file(file.filename):
                            save_image("logo.png", file)
                            message, result = "Логотип сайта успешно изменён", True
                        else:
                            message = "Файл неподдерживаемемого формата"
            if form.set_logo_sm.data:
                for ind, name in enumerate(request.files):
                    file = request.files[name]
                    if file.filename != "" and img_list[ind] in ["icon2", "iconInput2"]:
                        if file and allowed_file(file.filename):
                            save_image("logo-sm.png", file)
                            message, result = "Иконка для ссылок успешно изменена", True
                        else:
                            message = "Файл неподдерживаемемого формата"
            if form.set_standard_image.data:
                for ind, name in enumerate(request.files):
                    file = request.files[name]
                    if file.filename != "" and img_list[ind] in ["icon3", "iconInput3"]:
                        if file and allowed_file(file.filename):
                            save_image("standard.png", file)
                            message, result = "Новое изображение по умолчанию сохранено", True
                        else:
                            message = "Файл неподдерживаемемого формата"
            if form.submit.data:
                message = put(f"{link_website}api/seo/1", json={"admin_email": current_user.email, "action": "put",
                                                                "title": form.title.data, "tags": form.tags.data,
                                                                "description": form.description.data,
                                                                "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    result = True
                    set_seo_params()
                message = list(message.values())[0]
        else:
            form.title.data = seoparams["title"]
            form.description.data = seoparams["description"]
            form.tags.data = seoparams["tags"]
        return render_template('form/admin-form-seo.html', form=form, message=message, result=result,
                               special_params=get_special_params(), title="Настройка сайта")
    return you_dont_have_permission()


@application.route("/admin-create-text", methods=['GET', 'POST'])
@login_required
def admin_create_text():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = TextForm()
        message, result = None, False
        if request.method == 'POST':
            if form.submit.data:
                write_log(f"{current_user.email} {password_manager.user_is_authed(current_user.email)} {password_manager.get_password(current_user.email)} {password_manager}")
                message = post(f"{link_website}api/text", json={"heading": form.heading.data, "description": form.description.data,
                                                                "admin_email": current_user.email, "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    result = True
                    set_other_params()
                message = list(message.values())[0]
        return render_template('form/admin-form-text.html', title='Добавление текста', message=message,
                               form=form, result=result, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-edit-text/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_text(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = TextForm()
        message, result = None, False
        text = put(f"{link_website}api/text/{id}", json={"admin_email": current_user.email, "action": "get",
                                                         "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in text:
            if request.method == 'POST':
                if form.submit.data:
                    message = put(f"{link_website}api/text/{id}", json={"heading": form.heading.data, "description": form.description.data,
                                                                        "admin_email": current_user.email, "action": "put",
                                                                        "admin_password": password_manager.get_password(current_user.email)}).json()
                    if "success" in message:
                        result = True
                        set_other_params()
                    message = list(message.values())[0]
            else:
                form.heading.data = text["heading"]
                form.description.data = text["description"]
        else:
            message = "Телефон не найден"
        return render_template('form/admin-form-text.html', title='Редактирование текста', message=message,
                               result=result, form=form, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-delete-text/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_text(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, result, name = None, False, "текст не найден"
        text = put(f"{link_website}api/text/{id}", json={"admin_email": current_user.email, "action": "get",
                                                         "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in text:
            name = "текст " + text["heading"]
            if request.method == 'POST':
                message = put(f"{link_website}api/text/{id}", json={"admin_email": current_user.email, "action": "delete",
                                                                    "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    result = True
                    set_other_params()
                message = list(message.values())[0]
        return render_template('form/admin-form-delete.html', title='Удаление текста', message=message, form=form, name=name,
                               result=result, link_back="/admin-seo-settings", special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-create-phone", methods=['GET', 'POST'])
@login_required
def admin_create_phone():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = PhoneForm()
        message, result = None, False
        if request.method == 'POST':
            if form.submit.data:
                message = post(f"{link_website}api/phone", json={"number": form.number.data, "admin_email": current_user.email,
                                                                 "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    result = True
                    set_footer_params()
                message = list(message.values())[0]
        return render_template('form/admin-form-phone.html', title='Добавление номера телефона', message=message,
                               form=form, result=result, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-edit-phone/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_phone(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = PhoneForm()
        message, result = None, False
        phone = put(f"{link_website}api/phone/{id}", json={"admin_email": current_user.email, "action": "get",
                                                           "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in phone:
            if request.method == 'POST':
                if form.submit.data:
                    message = put(f"{link_website}api/phone/{id}", json={"number": form.number.data, "admin_email": current_user.email, "action": "put",
                                                                         "admin_password": password_manager.get_password(current_user.email)}).json()
                    if "success" in message:
                        result = True
                        set_footer_params()
                    message = list(message.values())[0]
            else:
                form.number.data = phone["number"]
        else:
            message = "Телефон не найден"
        return render_template('form/admin-form-phone.html', title='Редактирование номера телефона', message=message,
                               result=result, form=form, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-delete-phone/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_phone(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, result, name = None, False, "телефон не найден"
        phone = put(f"{link_website}api/phone/{id}", json={"admin_email": current_user.email, "action": "get",
                                                           "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in phone:
            name = "телефон " + phone["number"]
            if request.method == 'POST':
                message = put(f"{link_website}api/phone/{id}", json={"admin_email": current_user.email, "action": "delete",
                                                                     "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    result = True
                    set_footer_params()
                message = list(message.values())[0]
        return render_template('form/admin-form-delete.html', title='Удаление телефона', message=message, form=form, name=name,
                               result=result, link_back="/admin-footer-settings", special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-create-email", methods=['GET', 'POST'])
@login_required
def admin_create_email():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = EmailForm()
        message, result = None, False
        if request.method == 'POST':
            if form.submit.data:
                message = post(f"{link_website}api/email", json={"email_address": form.email.data, "admin_email": current_user.email,
                                                                 "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    result = True
                    set_footer_params()
                message = list(message.values())[0]
        return render_template('form/admin-form-email.html', title='Добавление почтового адреса', message=message,
                               form=form, result=result, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-edit-email/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_email(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = EmailForm()
        message, result = None, False
        email = put(f"{link_website}api/email/{id}", json={"admin_email": current_user.email, "action": "get",
                                                           "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in email:
            if request.method == 'POST':
                if form.submit.data:
                    message = put(f"{link_website}api/email/{id}", json={"email_address": form.email.data, "admin_email": current_user.email, "action": "put",
                                                                         "admin_password": password_manager.get_password(current_user.email)}).json()
                    if "success" in message:
                        result = True
                        set_footer_params()
                    message = list(message.values())[0]
            else:
                form.email.data = email["email_address"]
        else:
            message = "Почтовый адрес не найден"
        return render_template('form/admin-form-email.html', title='Редактирование почтового адреса', message=message,
                               result=result, form=form, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-delete-email/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_email(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, result, name = None, False, "почтовый адрес не найден"
        email = put(f"{link_website}api/email/{id}", json={"admin_email": current_user.email, "action": "get",
                                                           "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in email:
            name = "почтовый адрес " + email["email_address"]
            if request.method == 'POST':
                message = put(f"{link_website}api/email/{id}", json={"admin_email": current_user.email, "action": "delete",
                                                                     "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    result = True
                    set_footer_params()
                message = list(message.values())[0]
        return render_template('form/admin-form-delete.html', title='Удаление почтового адреса', message=message, form=form,
                               name=name, result=result, link_back="/admin-footer-settings", special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-create-socialmedia", methods=['GET', 'POST'])
@login_required
def admin_create_socialmedia():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = SocialmediaForm()
        message, result = None, False
        if request.method == 'POST':
            if form.submit.data:
                message = post(f"{link_website}api/socialmedia", json={"icon_type": get_image_name(form.link.data), "link": form.link.data,
                                                                       "admin_email": current_user.email, "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    result = True
                    set_footer_params()
                message = list(message.values())[0]
        return render_template('form/admin-form-socialmedia.html', title='Добавление ссылки на соцсеть', message=message,
                               form=form, result=result, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-edit-socialmedia/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_socialmedia(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = SocialmediaForm()
        message, result = None, False
        socialmedia = put(f"{link_website}api/socialmedia/{id}", json={"admin_email": current_user.email, "action": "get",
                                                                       "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in socialmedia:
            if request.method == 'POST':
                if form.submit.data:
                    message = put(f"{link_website}api/socialmedia/{id}", json={"admin_email": current_user.email, "action": "put",
                                                                               "icon_type": get_image_name(form.link.data), "link": form.link.data,
                                                                               "admin_password": password_manager.get_password(current_user.email)}).json()
                    if "success" in message:
                        result = True
                        set_footer_params()
                    message = list(message.values())[0]
            else:
                form.link.data = socialmedia["link"]
        else:
            message = "Ссылка на соцсесть не найдена"
        return render_template('form/admin-form-socialmedia.html', title='Редактирование ссылки на соцсеть', message=message,
                               result=result, form=form, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-delete-socialmedia/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_socialmedia(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, result, name = None, False, "ссылка на соцсеть на найдена"
        socialmedia = put(f"{link_website}api/socialmedia/{id}", json={"admin_email": current_user.email, "action": "get",
                                                                       "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in socialmedia:
            name = "почтовый адрес " + socialmedia["link"]
            if request.method == 'POST':
                message = put(f"{link_website}api/socialmedia/{id}", json={"admin_email": current_user.email, "action": "delete",
                                                                           "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    result = True
                    set_footer_params()
                message = list(message.values())[0]
        return render_template('form/admin-form-delete.html', title='Удаление ссылки на соцсеть', message=message, form=form,
                               name=name, result=result, link_back="/admin-footer-settings", special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-edit-address/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_address(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = AddressForm()
        message, result = None, False
        address = put(f"{link_website}api/address/{id}", json={"admin_email": current_user.email, "action": "get",
                                                               "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in address:
            if request.method == 'POST':
                if form.submit.data:
                    res = get_coord(form.address.data)
                    if "success" in res:
                        special_params["our_coord"] = res
                        message = put(f"{link_website}api/address/{id}", json={"coord": res["success"][0], "admin_email": current_user.email,
                                                                               "action": "put", "admin_password": password_manager.get_password(current_user.email),
                                                                               "place": form.address.data}).json()
                        if "success" in message:
                            result = True
                            set_footer_params()
                        message = list(message.values())[0]
                    else:
                        message = list(res.values())[0]
            else:
                form.address.data = address["place"]
        else:
            message = "Адрес не найден"
        return render_template('form/admin-form-address.html', title='Редактирование адреса', message=message,
                               result=result, form=form, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-list-news")
@login_required
def admin_list_news():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        containerManager.delete_container(f"tmp/news/news_{current_user.email}")
        delete_folder(f"tmp/news/news_{current_user.email}")
        newslist = get(f"{link_website}api/newspage").json()
        return render_template('list/admin-list-news.html', title='Новости', newslist=newslist, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-create-news", methods=['GET', 'POST'])
@login_required
def admin_create_news():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        # containerManager.delete_container(f"tmp/news/news_{current_user.email}")
        form = NewspageForm()
        message, result, preview_text = None, False, None
        if request.method == 'POST':
            filenames = save_images(f"tmp/news/news_{current_user.email}", request.files, auto_delete=True, r_img=False)
            text_trans = text_transform(form.text.data, filenames, application.config["UPLOAD_FOLDER"])
            if form.submit.data:
                if text_trans[:5] != "Error":
                    message = post(f"{link_website}api/newspage", json={"heading": form.heading.data, "text": form.text.data, "tags": form.tags.data,
                                   "image": "//".join(filenames), "admin_email": current_user.email, "admin_password": password_manager.get_password(current_user.email)}).json()
                    if "success" in message:
                        filenames = transport_images(f"tmp/news/news_{current_user.email}", f"news/news_{message['id']}", filenames)
                        m = put(f"{link_website}api/newspage/{message['id']}", json={"image": "//".join(filenames),
                                'admin_email': current_user.email, "action": "put", "admin_password": password_manager.get_password(current_user.email)}).json()
                        result = True
                        containerManager.delete_container(f"tmp/news/news_{current_user.email}")
                        set_other_params()
                    message = list(message.values())[-1]
                else:
                    message = text_trans[7:].capitalize()
            elif form.preview.data:
                preview_text = Markup(text_trans)
        else:
            filenames = containerManager.get_container(f"news_{current_user.email}").values()
        return render_template('form/admin-form-news.html', title='Создание новости', message=message, preview_text=preview_text,
                               form=form, result=result, filenames=filenames, image_len=len(filenames) + 1,
                               formatting_text_instruction=formatting_text_instruction, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-edit-news/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_news(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = NewspageForm()
        message, result, filenames, preview_text = None, False, [], None
        news = put(f"{link_website}api/newspage/{id}", json={"admin_email": current_user.email, "action": "get",
                                                             "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in list(news):
            if request.method == 'POST':
                filenames = save_images(f"tmp/news/news_{current_user.email}", request.files, r_img=False)
                text_trans = text_transform(form.text.data, filenames, application.config["UPLOAD_FOLDER"])
                if form.submit.data:
                    if text_trans[:5] != "Error":
                        message = put(f"{link_website}api/newspage/{id}", json={"heading": form.heading.data, "text": form.text.data,
                                      "image": "//".join(filenames), "admin_email": current_user.email, "action": "put", "tags": form.tags.data,
                                      "admin_password": password_manager.get_password(current_user.email)}).json()
                        if "success" in message:
                            result = True
                            filenames = transport_images(f"tmp/news/news_{current_user.email}", f"news/news_{id}", filenames)
                            m = put(f"{link_website}api/newspage/{id}", json={"image": "//".join(filenames),
                                    "action": "put", "admin_email": current_user.email, "admin_password": password_manager.get_password(current_user.email)}).json()
                            containerManager.delete_container(f"tmp/news/news_{current_user.email}")
                            set_other_params()
                        message = list(message.values())[0]
                    else:
                        message = text_trans[7:].capitalize()
                elif form.preview.data:
                    preview_text = Markup(text_transform(form.text.data, filenames, application.config["UPLOAD_FOLDER"]))
            else:
                form.heading.data = news["heading"]
                form.text.data = news["text"]
                form.tags.data = news["tags"]
                if containerManager.get_container(f"tmp/news/news_{current_user.email}") != {}:
                    filenames = containerManager.get_container(f"tmp/news/news_{current_user.email}").values()
                else:
                    filenames = copy_files(f"news/news_{id}", f"tmp/news/news_{current_user.email}", news["image"].split("//"))
                containerManager.add_container(f"tmp/news/news_{current_user.email}", filenames, auto_delete=True)
        else:
            message = news.values()[0]
        return render_template('form/admin-form-news.html', title='Редактирование новости', message=message, result=result,
                               form=form, filenames=filenames, image_len=len(filenames) + 1, preview_text=preview_text,
                               formatting_text_instruction=formatting_text_instruction, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-delete-news/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_news(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, result, name = None, False, "новость не найдена"
        news = put(f"{link_website}api/newspage/{id}", json={"admin_email": current_user.email, "action": "get",
                                                             "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in news:
            name = "новость " + news["heading"]
            if request.method == 'POST':
                message = put(f"{link_website}api/newspage/{id}", json={"admin_email": current_user.email, "action": "delete",
                                                                        "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    result = True
                    delete_folder(f"news/news_{id}")
                    set_other_params()
                message = list(message.values())[0]
                containerManager.delete_container(f"news_{id}")
        return render_template('form/admin-form-delete.html', title='Удаление новости', message=message, form=form,
                               result=result, name=name, link_back="/admin-list-news", special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-list-admin")
@login_required
def admin_list_admin():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        adminlist = put(f"{link_website}api/admin", json={"admin_email": current_user.email, "action": "get_list", "admin_password": password_manager.get_password(current_user.email)}).json()
        return render_template('list/admin-list-admin.html', title='Новости', adminlist=adminlist, status=current_user.status,
                               current_id=current_user.id, flag=(current_user.status > 0), special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-change-password/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_change_password(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 1:
        form = AdminForm()
        if current_user.id == id:
            admin = put(f"{link_website}api/admin", json={"admin_email": current_user.email, "action": "get",
                                                          "admin_password": password_manager.get_password(current_user.email)}).json()
        else:
            admin = put(f"{link_website}api/admin/{id}", json={"admin_email": current_user.email, "action": "get",
                                                               "admin_password": password_manager.get_password(current_user.email)}).json()
        message, result, name = None, False, ""
        if "message" not in admin:
            name = f'{admin["name"]} {admin["surname"]}'
            if request.method == 'POST':
                if form.password.data == form.password_again.data:
                    if id == current_user.id:
                        message = put(f"{link_website}api/admin", json={"admin_email": current_user.email,
                                      "new_admin_password": form.password.data, "action": "put", "change_password": True,
                                      "admin_password": password_manager.get_password(current_user.email),
                                      "check_admin_password": form.password_current.data}).json()
                    else:
                        message = put(f"{link_website}api/admin/{id}", json={"admin_email": current_user.email,
                                      "new_admin_password": form.password.data, "action": "put", "change_password": True,
                                      "admin_password": password_manager.get_password(current_user.email),
                                      "check_admin_password": form.password_current.data}).json()
                    if "success" in message:
                        password_manager.add_user(admin["email"], form.password.data)
                        result = True
                    message = list(message.values())[0]
                else:
                    message = "Новые пароли не совпадают"
        else:
            message = list(admin.values())[0]
        return render_template('admin-change-password.html', title=f'Изменение пароля админу {name}', message=message,
                               form=form, result=result, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-create-admin", methods=['GET', 'POST'])
@login_required
def admin_create_admin():
    if check_user():
        return redirect("/login")
    if current_user.status > 1:
        form = AdminForm()
        message, result = None, False
        if request.method == 'POST':
            if form.password.data == form.password_again.data:
                form.status.data = int(form.status.data)
                message = post(f"{link_website}api/admin/create", json={"name": form.name.data, "surname": form.surname.data,
                               "email": form.email.data, "status": form.status.data, "admin_email": current_user.email,
                               "admin_password": password_manager.get_password(current_user.email), "new_admin_password": form.password.data}).json()
                form.status.data = str(form.status.data)
                if "success" in message:
                    password_manager.add_user(form.email.data, form.password)
                    result = True
                message = list(message.values())[0]
            else:
                message = "Пароли не совпадают"
        return render_template('form/admin-form-admin.html', title='Создание админа', message=message, form=form,
                               result=result, flag=True, special_params=get_special_params(), f=True,
                               roles=["Без прав", "Модератор", "Админ", "Владелец"][:current_user.status])
    return you_dont_have_permission()


@application.route("/admin-edit-admin/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_admin(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 1:
        form = AdminForm()
        if current_user.id == id:
            f = False
            admin = put(f"{link_website}api/admin", json={"admin_email": current_user.email, "action": "get", "admin_password": password_manager.get_password(current_user.email)}).json()
        else:
            f = True
            admin = put(f"{link_website}api/admin/{id}", json={"admin_email": current_user.email, "action": "get", "admin_password": password_manager.get_password(current_user.email)}).json()
        form.stat = current_user.status
        message, result, admin_status = None, False, 0
        if "message" not in admin:
            admin_status = admin["status"]
            if request.method == 'POST':
                if current_user.id == id:
                    message = put(f"{link_website}api/admin", json={"name": form.name.data, "surname": form.surname.data, "email": form.email.data,
                                  "admin_email": current_user.email, "action": "put", "admin_password": password_manager.get_password(current_user.email)}).json()
                else:
                    message = put(f"{link_website}api/admin/{id}", json={"name": form.name.data, "surname": form.surname.data, "email": form.email.data,
                                  "status": int(form.status.data), "admin_email": current_user.email, "action": "put", "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    if f:
                        admin_status = int(form.status.data)
                    if admin["email"] != form.email.data:
                        password_manager.update_email(admin["email"], form.email.data)
                    result = True
                message = list(message.values())[0]
            else:
                admin_status = admin["status"]
                form.name.data = admin["name"]
                form.surname.data = admin["surname"]
                form.email.data = admin["email"]
                form.status.data = str(admin["status"])
        else:
            message = list(admin.values())[0]
        return render_template('form/admin-form-admin.html', title='Редактирование админа', message=message, form=form,
                               result=result, flag=False, admin_status=admin_status, special_params=get_special_params(),
                               roles=["Без прав", "Модератор", "Админ", "Владелец"][:current_user.status], f=f)
    return you_dont_have_permission()


@application.route("/admin-delete-admin/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_admin(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 1:
        form = DeleteForm()
        message, name, result = None, "пользователь не найден", False
        admin = put(f"{link_website}api/admin/{id}", json={"admin_email": current_user.email, "action": "get", "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in admin:
            name = "админа " + f"{admin['name']} {admin['surname']}"
            if admin["status"] < current_user.status:
                if request.method == 'POST':
                    message = put(f"{link_website}api/admin/{id}", json={"admin_email": current_user.email,
                                                                         "action": "delete", "admin_password": password_manager.get_password(current_user.email)}).json()
                    if "success" in message:
                        result = True
                    message = list(message.values())[0]
            else:
                message = "У вас недостаточно прав для этого"
        else:
            name = "пользователь не найден"
        return render_template('form/admin-form-delete.html', title='Удаление админа', message=message, form=form,
                               result=result, name=name, link_back="/admin-list-admin", special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-list-smartpage/<int:page_id>")
@login_required
def admin_list_smartpage(page_id):
    if check_user():
        return redirect("/login")
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
        return render_template('list/admin-list-smartpage.html', title='Страницы', smartpagelist=smartpagelist,
                               contentdict=contentdict, types={"News": "Новости", "Image": "Картинки", "Text": "Текст", "Partner": "Партнёры", "Map": "Карта"},
                               page_id=page_id, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-create-smartpage", methods=['GET', 'POST'])
@login_required
def admin_create_smartpage():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = SmartpageForm()
        containerManager.delete_container(f"tmp/smartpage/smartpage_{current_user.email}")
        message, result, filenames = None, False, []
        if request.method == 'POST':
            filenames = save_images(f"tmp/smartpage/smartpage_{current_user.email}", request.files, auto_delete=True)
            message = post(f"{link_website}api/smartpage", json={"heading": form.heading.data, "image": "//".join(filenames),
                                                                 "admin_email": current_user.email, "admin_password": password_manager.get_password(current_user.email)}).json()
            if "success" in message:
                filenames = transport_images(f"tmp/smartpage/smartpage_{current_user.email}", f"smartpage/smartpage_{message['id']}", filenames)
                m = put(f"{link_website}api/smartpage/{message['id']}", json={"image": "//".join(filenames),
                        "admin_email": current_user.email, "action": "put", "admin_password": password_manager.get_password(current_user.email)}).json()
                result = True
                delete_folder(f"tmp/smartpage/smartpage_{current_user.email}")
                containerManager.delete_container(f"tmp/smartpage/smartpage_{current_user.email}")
                set_other_params()
            message = list(message.values())[-1]
        return render_template('form/admin-form-smartpage.html', title='Создание страницы', message=message, form=form,
                               result=result, filenames=filenames, image_len=len(filenames) + 1, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-edit-smartpage/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_smartpage(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = SmartpageForm()
        smartpage = put(f"{link_website}api/smartpage/{id}", json={"admin_email": current_user.email, "action": "get",
                                                                   "admin_password": password_manager.get_password(current_user.email)}).json()
        message, result, filenames = None, False, []
        if "message" not in smartpage:
            if request.method == 'POST':
                filenames = save_images(f"tmp/smartpage/smartpage_{current_user.email}", request.files, auto_delete=True)
                message = put(f"{link_website}api/smartpage/{id}", json={"heading": form.heading.data, "image": "//".join(filenames),
                              "admin_email": current_user.email, "action": "put", "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    filenames = transport_images(f"tmp/smartpage/smartpage_{current_user.email}", f"smartpage/smartpage_{id}", filenames)
                    m = put(f"{link_website}api/smartpage/{id}", json={"image": "//".join(filenames),
                            "admin_email": current_user.email, "action": "put", "admin_password": password_manager.get_password(current_user.email)}).json()
                    result = True
                    delete_folder(f"tmp/smartpage/smartpage_{current_user.email}")
                    set_other_params()
                message = list(message.values())[0]
            else:
                form.heading.data = smartpage["heading"]
                filenames = copy_files(f"smartpage/smartpage_{id}", f"tmp/smartpage/smartpage_{current_user.email}", smartpage["image"].split("//"))
                containerManager.add_container(f"tmp/smartpage/smartpage_{current_user.email}", filenames, auto_delete=True)
        else:
            message = list(smartpage.values())[-1]
        return render_template('form/admin-form-smartpage.html', title='Редактирование страницы', message=message, form=form,
                               result=result, flag=False, filenames=filenames, image_len=len(filenames) + 1,
                               special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-delete-smartpage/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_smartpage(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result = "", "страница не найдена", False
        smartpage = put(f"{link_website}api/smartpage/{id}", json={"admin_email": current_user.email, "action": "get",
                                                                   "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in smartpage:
            name = "страница " + smartpage['heading']
            if request.method == 'POST':
                content_list = get(f"{link_website}api/content/{smartpage['id']}").json()
                for content in content_list:
                    delete_folder(f"content/content_{content['id']}")
                    containerManager.delete_container(f"content/content_{content['id']}")
                message = put(f"{link_website}api/smartpage/{id}", json={"admin_email": current_user.email, "action": "delete",
                                                                         "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    result = True
                    containerManager.delete_container(f"smartpage/smartpage_{id}")
                    delete_folder(f"smartpage/smartpage_{id}")
                    set_other_params()
                message = list(message.values())[-1]
        return render_template('form/admin-form-delete.html', title='Удаление страницы', message=message, form=form,
                               result=result, name=name, link_back="/admin-list-smartpage/0", special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-create-content/<int:page_id>", methods=['GET', 'POST'])
@login_required
def admin_create_content(page_id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = ContentForm()
        containerManager.delete_container(f"tmp/content/content_{current_user.email}")
        message, result, filenames, filename = None, False, [], None
        if request.method == 'POST':
            filenames = save_images(f"tmp/content/content_{current_user.email}", request.files, auto_delete=True, r_img=False)
            image = "" if len(filenames) == 0 else "//".join(filenames)
            message = post(f"{link_website}api/content", json={"type": form.type.data, "text": form.text.data, "page_id": page_id, "display_type": form.display_type.data,
                           "heading": form.heading.data, "image": image, 'admin_email': current_user.email, "admin_password": password_manager.get_password(current_user.email)}).json()
            if "success" in message:
                filenames = transport_images(f"tmp/content/content_{current_user.email}", f"content/content_{message['id']}", filenames)
                m = put(f"{link_website}api/content/{message['id']}", json={"image": "//".join(filenames), "action": "put",
                                                                            "admin_email": current_user.email, "admin_password": password_manager.get_password(current_user.email)}).json()
                result = True
                containerManager.delete_container(f"tmp/content/content_{current_user.email}")
            message = list(message.values())[-1]
        return render_template('form/admin-form-content.html', title='Создание контента', message=message, form=form,
                               result=result, flag=True, filenames=filenames, image_len=len(filenames) + 1, page_id=page_id,
                               special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-edit-content-move-up/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_content_move_up(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        content, page_id = put(f"{link_website}api/content/{id}", json={"admin_email": current_user.email, "action": "get",
                                                                        "admin_password": password_manager.get_password(current_user.email)}).json(), 0
        if "message" not in content:
            put(f"{link_website}api/content/{id}", json={"position": content["position"] - 1, "action": "put",
                                                         "admin_email": current_user.email, "admin_password": password_manager.get_password(current_user.email)})
            page_id = content['smartpage_id']
        return redirect(f"/admin-list-smartpage/{page_id}")
    return you_dont_have_permission()


@application.route("/admin-edit-content-move-down/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_content_move_down(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        content, page_id = put(f"{link_website}api/content/{id}", json={"admin_email": current_user.email, "action": "get",
                                                                        "admin_password": password_manager.get_password(current_user.email)}).json(), 0
        if "message" not in content:
            put(f"{link_website}api/content/{id}", json={"position": content["position"] + 1, "action": "put",
                                                         "admin_email": current_user.email, "admin_password": password_manager.get_password(current_user.email)})
            page_id = content["smartpage_id"]
        return redirect(f"/admin-list-smartpage/{page_id}")
    return you_dont_have_permission()


@application.route("/admin-edit-content/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_content(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = ContentForm()
        content = put(f"{link_website}api/content/{id}", json={"admin_email": current_user.email, "action": "get",
                                                               "admin_password": password_manager.get_password(current_user.email)}).json()
        message, result, filenames, page_id = None, False, [], 0
        if "message" not in content:
            page_id = content["smartpage_id"]
            if request.method == 'POST':
                filenames = save_images(f"tmp/content/content_{current_user.email}", request.files, auto_delete=True)
                message = put(f"{link_website}api/content/{id}", json={"type": form.type.data, "text": form.text.data,
                              "heading": form.heading.data, "image": '//'.join(filenames), "action": "put", "display_type": form.display_type.data,
                              "admin_email": current_user.email, "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    filenames = transport_images(f"tmp/content/content_{current_user.email}", f"content/content_{id}", filenames)
                    m = put(f"{link_website}api/content/{id}", json={"image": '//'.join(filenames), "action": "put",
                                                                     "admin_email": current_user.email, "admin_password": password_manager.get_password(current_user.email)}).json()
                    result = True
                message = list(message.values())[-1]
            else:
                form.type.data = content["type"]
                form.text.data = content["text"]
                form.heading.data = content["heading"]
                form.display_type.data = content["display_type"]
                page_id = content["smartpage_id"]
                if content["image"]:
                    filenames = content["image"].split("//")
                    filenames = copy_files(f"content/content_{id}", f"tmp/content/content_{current_user.email}", filenames)
                containerManager.add_container(f"tmp/content/content_{current_user.email}", filenames, auto_delete=True)
        else:
            message = list(content.values())[-1]
        return render_template('form/admin-form-content.html', title='Редактирование контента', message=message, form=form,
                               result=result, flag=False, filenames=filenames, image_len=len(filenames) + 1,
                               page_id=page_id, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-delete-content/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_content(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result, page_id = "", "контент не найден", False, 0
        content = put(f"{link_website}api/content/{id}", json={"admin_email": current_user.email, "action": "get",
                                                               "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in content:
            page_id = content["smartpage_id"]
            name = "контент " + content['heading']
            if request.method == 'POST':
                message = put(f"{link_website}api/content/{id}", json={"action": "delete",
                                                                       "admin_email": current_user.email, "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    result = True
                    delete_folder(f"content/content_{id}")
                    containerManager.delete_container(f"content/content_{id}")
                message = list(message.values())[0]
        return render_template('form/admin-form-delete.html', title='Удаление контента', message=message, form=form,
                               result=result, name=name, link_back=f"/admin-list-smartpage/{page_id}", special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-list-worker")
@login_required
def admin_list_worker():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        workerlist = get(f"{link_website}api/worker").json()
        return render_template('list/admin-list-worker.html', title='Сотрудники', workerlist=workerlist,
                               special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-create-worker", methods=['GET', 'POST'])
@login_required
def admin_create_worker():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        containerManager.delete_container(f"tmp/worker/worker_{current_user.email}")
        form = WorkerForm()
        message, result, filenames = None, False, []
        if request.method == 'POST':
            filenames = save_images(f"tmp/worker/worker_{current_user.email}", request.files, auto_delete=True)
            message = post(f"{link_website}api/worker", json={"name": form.name.data, "image": "//".join(filenames), "profession": form.profession.data,
                           "phone": form.phone.data, "email": form.email.data, "admin_email": current_user.email,
                                                              "admin_password": password_manager.get_password(current_user.email)}).json()
            if "success" in message:
                filenames = transport_images(f"tmp/worker/worker_{current_user.email}", f"worker/worker_{message['id']}", filenames)
                m = put(f"{link_website}api/worker/{message['id']}", json={"image": "//".join(filenames), "admin_email": current_user.email, "action": "put",
                                                                           "admin_password": password_manager.get_password(current_user.email)}).json()
                result = True
                delete_folder(f"tmp/worker/worker_{current_user.email}")
                containerManager.delete_container(f"tmp/worker/worker_{current_user.email}")
                set_other_params()
            message = list(message.values())[-1]
        return render_template('form/admin-form-worker.html', title='Добавление сотрудника', message=message, form=form,
                               result=result, filenames=filenames, special_params=get_special_params(), image_len=len(filenames) + 1)
    return you_dont_have_permission()


@application.route("/admin-edit-worker/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_worker(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = WorkerForm()
        worker = put(f"{link_website}api/worker/{id}", json={"admin_email": current_user.email, "action": "get",
                                                             "admin_password": password_manager.get_password(current_user.email)}).json()
        message, result, filenames = None, False, []
        if "message" not in worker:
            if request.method == 'POST':
                filenames = save_images(f"tmp/worker/worker_{current_user.email}", request.files, auto_delete=True)
                message = put(f"{link_website}api/worker/{id}", json={"profession": form.profession.data, "name": form.name.data,
                                                                      "email": form.email.data, "phone": form.phone.data,
                                                                      "image": '//'.join(filenames), "action": "put",
                                                                      "admin_email": current_user.email,
                                                                      "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    filenames = copy_files(f"tmp/worker/worker_{current_user.email}", f"worker/worker_{id}",
                                                 filenames)
                    m = put(f"{link_website}api/worker/{id}", json={"image": '//'.join(filenames), "action": "put",
                                                                    "admin_email": current_user.email,
                                                                    "admin_password": password_manager.get_password(current_user.email)}).json()
                    result = True
                    set_other_params()
                message = list(message.values())[-1]
            else:
                form.profession.data = worker["profession"]
                form.name.data = worker["name"]
                form.email.data = worker["email"]
                form.phone.data = worker["phone"]
                if worker["image"]:
                    filenames = worker["image"].split("//")
                    clear_folder(f"tmp/worker/worker_{current_user.email}")
                    filenames = copy_files(f"worker/worker_{id}", f"tmp/worker/worker_{current_user.email}", filenames)
                containerManager.add_container(f"tmp/worker/worker_{current_user.email}", filenames, auto_delete=True)
        else:
            message = list(worker.values())[-1]
        return render_template('form/admin-form-worker.html', title='Редактирование сотрудника', message=message,
                               form=form, result=result, flag=False, filenames=filenames, image_len=len(filenames) + 1,
                               special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-delete-worker/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_worker(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result = "", "сотрудник не найден", False
        worker = put(f"{link_website}api/worker/{id}", json={"admin_email": current_user.email, "action": "get",
                                                             "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in worker:
            name = "сотрудник " + worker['name']
            if request.method == 'POST':
                message = put(f"{link_website}api/worker/{id}", json={"admin_email": current_user.email, "action": "delete",
                                                                      "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    result = True
                    containerManager.delete_container(f"worker/worker_{id}")
                    delete_folder(f"worker/worker_{id}")
                    set_other_params()
                message = list(message.values())[-1]
        return render_template('form/admin-form-delete.html', title='Удаление сотрудника', message=message, form=form,
                               result=result, name=name, link_back="/admin-list-worker", special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-list-partner")
@login_required
def admin_list_partner():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        partnerlist = get(f"{link_website}api/partner").json()
        return render_template('list/admin-list-partner.html', title='Участники', partnerlist=partnerlist, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-create-partner", methods=['GET', 'POST'])
@login_required
def admin_create_partner():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = PartnerForm()
        cont_name_logo, cont_name_image = f"tmp/partner/partner_{current_user.email}/logo", f"tmp/partner/partner_{current_user.email}/image"
        containerManager.delete_container(cont_name_image)
        containerManager.delete_container(cont_name_logo)
        message, result, filenames1, filenames2 = None, False, [], []
        if request.method == 'POST':
            coord = get_coord(form.address.data)
            filenames2, filenames1 = save_images(cont_name_image, request.files, r_img=True, logo=True, cont_logo=cont_name_logo, auto_delete=True)
            if "success" in coord:
                message = post(f"{link_website}api/partner", json={"name": form.name.data, "logo": "//".join(filenames1),
                               "image": "//".join(filenames2), "text": form.text.data, "link": form.link.data,
                               "coord": coord['success'][0], "occupation": "//".join([oc.strip().capitalize() for oc in form.occupation.data.split(',')]),
                               "address": form.address.data, "province": coord["success"][1], "admin_email": current_user.email,
                                                                   "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    filenames1, filenames2 = transport_images(cont_name_logo, f"partner/partner_{message['id']}/logo", filenames1), \
                                                     transport_images(cont_name_image, f"partner/partner_{message['id']}/image", filenames2)
                    m = put(f"{link_website}api/partner/{message['id']}", json={"image": "//".join(filenames2),
                            'logo': "//".join(filenames1), "admin_email": current_user.email, "action": "put",
                                                                                "admin_password": password_manager.get_password(current_user.email)}).json()
                    containerManager.delete_container(cont_name_image)
                    containerManager.delete_container(cont_name_logo)
                    delete_folder(f"partner/partner_{current_user.email}")
                    # filenames1, filenames2 = [], []
                    result = True
                    set_other_params()
                message = list(message.values())[-1]
            else:
                message = coord["message"]
        return render_template('form/admin-form-partner.html', title='Создание участника', message=message, form=form,
                               result=result, flag=True, filenames1=filenames1, filenames2=filenames2, image_len=len(filenames2) + 1,
                               special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-edit-partner/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_partner(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = PartnerForm()
        cont_name_logo, cont_name_image = f"tmp/partner/partner_{current_user.email}/logo", f"tmp/partner/partner_{current_user.email}/image"
        partner = put(f"{link_website}api/partner/{id}", json={"admin_email": current_user.email, "action": "get",
                                                               "admin_password": password_manager.get_password(current_user.email)}).json()
        message, result, filenames1, filenames2 = None, False, [], []
        if "message" not in partner:
            if request.method == 'POST':
                filenames2, filenames1 = save_images(cont_name_image, request.files, r_img=True, logo=True, cont_logo=cont_name_logo)
                coord = get_coord(form.address.data) if form.address.data != partner["address"] else {"success": [None, None]}
                if "success" in coord:
                    if coord["success"] == [None, None]:
                        coord["success"] = [partner["coord"], partner["province"]]
                    message = put(f"{link_website}api/partner/{id}", json={"name": form.name.data, "image": "//".join(filenames2),
                                  "logo": "//".join(filenames1), "text": form.text.data, "link": form.link.data, "address": form.address.data,
                                  "coord": coord["success"][0], "province": coord["success"][1], "admin_email": current_user.email,
                                  "occupation": '//'.join([oc.strip().capitalize() for oc in form.occupation.data.split(',')]), "action": "put",
                                                                           "admin_password": password_manager.get_password(current_user.email)}).json()
                    if "success" in message:
                        filenames1, filenames2 = transport_images(cont_name_logo, f"partner/partner_{id}/logo", filenames1), \
                                                 transport_images(cont_name_image, f"partner/partner_{id}/image", filenames2)
                        m = put(f"{link_website}api/partner/{id}", json={"image": "//".join(filenames2),
                                'logo': "//".join(filenames1), "admin_email": current_user.email, "action": "put",
                                                                         "admin_password": password_manager.get_password(current_user.email)}).json()
                        result = True
                        set_other_params()
                    message = list(message.values())[0]
                else:
                    message = coord["message"]
            else:
                form.name.data = partner["name"]
                form.text.data = partner["text"]
                form.link.data = partner["link"]
                form.address.data = partner["address"]
                form.occupation.data = ", ".join(partner["occupation"].split("//"))
                filenames1 = copy_files(f"partner/partner_{id}/logo", cont_name_logo, partner["logo"].split("//"))
                filenames2 = copy_files(f"partner/partner_{id}/image", cont_name_image, partner["image"].split("//"))
                containerManager.add_container(cont_name_image, filenames2)
                containerManager.add_container(cont_name_logo, filenames1)
        else:
            message = list(partner.values())[0]
        return render_template('form/admin-form-partner.html', title='Редактирование участника', message=message, form=form,
                               result=result, flag=False, filenames1=filenames1, filenames2=filenames2,
                               image_len=len(filenames2) + 1, special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-delete-partner/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_partner(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result = "", "участник не найден", False
        partner = put(f"{link_website}api/partner/{id}", json={"admin_email": current_user.email, "action": "get",
                                                               "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in partner:
            name = "страница " + partner['name']
            if request.method == 'POST':
                message = put(f"{link_website}api/partner/{id}", json={"admin_email": current_user.email, "action": "delete",
                                                                       "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    result = True
                    delete_folder(f"partner/partner_{id}/image")
                    delete_folder(f"partner/partner_{id}/logo")
                    delete_folder(f"partner/partner_{id}")
                    containerManager.delete_container(f"partner_{id}")
                    set_other_params()
                message = list(message.values())[0]
        else:
            message = list(partner.values())[0]
        return render_template('form/admin-form-delete.html', title='Удаление участника', message=message, form=form,
                               result=result, name=name, link_back="/admin-list-partner", special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-list-member")
@login_required
def admin_list_member():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        memberlist = get(f"{link_website}api/member").json()
        return render_template('list/admin-list-member.html', title='Партнёры', memberlist=memberlist,
                               special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-create-member", methods=['GET', 'POST'])
@login_required
def admin_create_member():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = MemberForm()
        cont_name_logo, cont_name_image = f"tmp/member/member_{current_user.email}/logo", f"tmp/member/member_{current_user.email}/image"
        containerManager.delete_container(cont_name_logo)
        containerManager.delete_container(cont_name_image)
        message, result, filenames2, filenames1 = None, False, [], []
        if request.method == 'POST':
            filenames2, filenames1 = save_images(cont_name_image, request.files, r_img=True, logo=True, cont_logo=cont_name_logo, auto_delete=True)
            message = post(f"{link_website}api/member", json={"name": form.name.data, "image": "//".join(filenames2), "info": form.info.data,
                           "preferences": form.preferences.data, "address": form.address.data, "link": form.link.data, "admin_email": current_user.email,
                           "logo": "//".join(filenames1), "admin_password": password_manager.get_password(current_user.email)}).json()
            if "success" in message:
                filenames1, filenames2 = transport_images(cont_name_logo, f"member/member_{message['id']}/logo", filenames1), \
                                         transport_images(cont_name_image, f"member/member_{message['id']}/image", filenames2)
                m = put(f"{link_website}api/member/{message['id']}", json={"image": "//".join(filenames2), "logo": "//".join(filenames1), "admin_email": current_user.email, "action": "put",
                                                                           "admin_password": password_manager.get_password(current_user.email)}).json()
                containerManager.delete_container(cont_name_image)
                containerManager.delete_container(cont_name_logo)
                result = True
                # filenames1, filenames2 = [], []
                delete_folder(f"member/member_{current_user.email}")
                set_other_params()
            message = list(message.values())[-1]
        return render_template('form/admin-form-member.html', title='Добавление партнёра', message=message, form=form,
                               result=result, filenames1=filenames1, filenames2=filenames2, special_params=get_special_params(), image_len=len(filenames2) + 1)
    return you_dont_have_permission()


@application.route("/admin-edit-member/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_member(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = MemberForm()
        cont_name_logo, cont_name_image = f"tmp/member/member_{current_user.email}/logo", f"tmp/member/member_{current_user.email}/image"
        member = put(f"{link_website}api/member/{id}", json={"admin_email": current_user.email, "action": "get",
                                                             "admin_password": password_manager.get_password(current_user.email)}).json()
        message, result, filenames1, filenames2 = None, False, [], []
        if "message" not in member:
            if request.method == 'POST':
                filenames2, filenames1 = save_images(cont_name_image, request.files, r_img=True, logo=True, cont_logo=cont_name_logo)
                message = put(f"{link_website}api/member/{id}", json={"preferences": form.preferences.data, "name": form.name.data,
                                                                      "address": form.address.data, "link": form.link.data, "info": form.info.data,
                                                                      "image": '//'.join(filenames2), "logo": '//'.join(filenames1), "action": "put",
                                                                      "admin_email": current_user.email,
                                                                      "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    filenames1, filenames2 = transport_images(cont_name_logo, f"member/member_{id}/logo", filenames1), \
                                             transport_images(cont_name_image, f"member/member_{id}/image", filenames2)
                    m = put(f"{link_website}api/member/{id}", json={"image": '//'.join(filenames2), "action": "put",
                                                                    "admin_email": current_user.email, "logo": '//'.join(filenames1),
                                                                    "admin_password": password_manager.get_password(current_user.email)}).json()
                    result = True
                    set_other_params()
                message = list(message.values())[-1]
            else:
                form.preferences.data = member["preferences"]
                form.address.data = member["address"]
                form.name.data = member["name"]
                form.info.data = member["info"]
                form.link.data = member["link"]
                filenames1 = copy_files(f"member/member_{id}/logo", cont_name_logo, member["logo"].split("//"))
                filenames2 = copy_files(f"member/member_{id}/image", cont_name_image, member["image"].split("//"))
                containerManager.add_container(cont_name_image, filenames2)
                containerManager.add_container(cont_name_logo, filenames1)
        else:
            message = list(member.values())[-1]
        return render_template('form/admin-form-member.html', title='Редактирование партнёра', message=message,
                               form=form, result=result, flag=False, filenames1=filenames1, filenames2=filenames2, image_len=len(filenames2) + 1,
                               special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-delete-member/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_member(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result = "", "сотрудник не найден", False
        member = put(f"{link_website}api/member/{id}", json={"admin_email": current_user.email, "action": "get",
                                                             "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in member:
            name = "сотрудник " + member['name']
            if request.method == 'POST':
                message = put(f"{link_website}api/member/{id}", json={"admin_email": current_user.email, "action": "delete",
                                                                      "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    result = True
                    delete_folder(f"member/member_{id}/image")
                    delete_folder(f"member/member_{id}/logo")
                    delete_folder(f"member/member_{id}")
                    containerManager.delete_container(f"member  _{id}")
                    set_other_params()
                message = list(message.values())[-1]
        return render_template('form/admin-form-delete.html', title='Удаление участника', message=message, form=form,
                               result=result, name=name, link_back="/admin-list-member", special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/admin-list-auditlog")
@login_required
def admin_auditlog():
    if check_user():
        return redirect("/login")
    auditlogs = put(f"{link_website}api/auditlog", json={"admin_email": current_user.email, "action": "getlist",
                                                         "admin_password": password_manager.get_password(current_user.email)}).json()
    return render_template('list/admin-list-auditlog.html', title='Журнал аудита', auditlogs=auditlogs, special_params=get_special_params())


@application.route("/admin-list-feedback")
@login_required
def admin_feedback():
    if check_user():
        return redirect("/login")
    feedbacks = put(f"{link_website}api/feedback", json={"admin_email": current_user.email, "action": "getlist",
                                                         "admin_password": password_manager.get_password(current_user.email)}).json()
    return render_template('list/admin-list-feedback.html', title='Отзывы', feedbacks=feedbacks, special_params=get_special_params())


@application.route("/view-feedback/<int:id>", methods=['GET', 'POST'])
@login_required
def view_feedback(id):
    if check_user():
        return redirect("/login")
    feedback = put(f"{link_website}api/feedback", json={"admin_email": current_user.email, "action": "get", "feedback_id": id,
                                                        "admin_password": password_manager.get_password(current_user.email)}).json()
    if "message" in feedback:
        return page_not_found()
    return render_template('feedback.html', title=feedback["heading"], feedback=feedback, special_params=get_special_params())


@application.route("/admin-delete-feedback/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_feedback(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result = "", "отзыв не найден", False
        feedback = put(f"{link_website}api/feedback", json={"admin_email": current_user.email, "action": "get", "feedback_id": id,
                                                            "admin_password": password_manager.get_password(current_user.email)}).json()
        if "message" not in feedback:
            name = "отзыв " + feedback['heading']
            if request.method == 'POST':
                message = put(f"{link_website}api/feedback", json={"feedback_id": id, "admin_email": current_user.email, "action": "delete",
                                                                   "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    delete_folder(f"feedback/feedback_{feedback['id']}")
                    result = True
                message = list(message.values())[0]
                images = feedback["image"]
                for image in images.split("//"):
                    delete_img(image)
        return render_template('form/admin-form-delete.html', title='Удаление отзыва', message=message, form=form,
                               result=result, name=name, link_back="/admin-list-feedback", special_params=get_special_params())
    return you_dont_have_permission()


@application.route("/write-feedback/<string:code>", methods=['GET', 'POST'])
def write_feedback(code):
    form = FeedbackForm()
    message, result, filenames, preview_text = None, False, [], None
    if request.method == 'POST':
        filenames = save_images(f"tmp/feedback/feedback_{code}", request.files, r_img=False, max_image=5, auto_delete=True, gif=False, feedback=True)
        delete_everything_except(f"tmp/feedback/feedback_{code}", filenames)
        text_trans = text_transform(form.text.data, filenames, application.config["UPLOAD_FOLDER"])

        if form.submit.data:
            if text_trans[:5] != "Error":
                message = post(f"{link_website}api/feedback",
                               json={"email": form.email.data, "fullname": form.fullname.data, "heading": form.heading.data,
                                     "image": "//".join(filenames), "text": form.text.data, "code": form.code.data,
                                     "admin_password": password_manager.get_password(current_user.email)}).json()
                if "success" in message:
                    filenames = transport_images(f"tmp/feedback/feedback_{code}", f"feedback/feedback_{message['id']}", filenames)
                    m = put(f"{link_website}api/feedback/{message['id']}/{form.code.data}", json={"image": "//".join(filenames),
                                                                                                  "admin_password": password_manager.get_password(current_user.email)}).json()
                    result = True
                    message = "Спасибо за отзыв"
                    containerManager.delete_container(f"feedback/feedback_{code}")
                else:
                    message = list(message.values())[0]
            else:
                message = text_trans[7:].capitalize()
        elif form.getcode.data:
            code_helper.create_code(form.email.data)
        elif form.preview.data:
            preview_text = Markup(text_trans)
    else:
        filenames = containerManager.get_container(f"feedback_{code}").values()
    page = get(f"{link_website}api/smartpage/6").json()
    content = get(f"{link_website}api/content/{page['id']}").json()
    return render_template('write-feedback.html', title="Отзыв", page=page, content=content,
                           result=result, flag=True, message=message, form=form, preview_text=preview_text,
                           filenames=filenames, image_len=len(filenames) + 1, special_params=get_special_params(),
                           formatting_text_instruction=formatting_text_instruction_usual)


@application.route("/contacts")
def contacts():
    page = get(f"{link_website}api/smartpage/6").json()
    content, flag_map = get(f"{link_website}api/content/{page['id']}").json(), False
    flag_map = any([True if cont['type'] == "Map" else flag_map for cont in content])
    return render_template('contacts.html', title=page["heading"], page=page, content=content, code=create_random_name(15),
                           special_params=get_special_params(), flag_map=flag_map, contacts=True)


@application.route("/agro_and_agro-tourism_sector")
def agro_and_agro_tourism_sector():
    page = get(f"{link_website}api/smartpage/2").json()
    content, flag_map = get(f"{link_website}api/content/{page['id']}").json(), False
    flag_map = any([True if cont['type'] == "Map" else flag_map for cont in content])
    return render_template('agro_and_agro_tourism_sector.html', title=page["heading"], page=page, content=content,
                           special_params=get_special_params(), flag_map=flag_map)


@application.route("/partners")
def partners():
    page = get(f"{link_website}api/smartpage/3").json()
    content, flag_map = get(f"{link_website}api/content/{page['id']}").json(), False
    flag_map = any([True if cont['type'] == "Map" else flag_map for cont in content])
    return render_template('partners.html', title=page["heading"], page=page, content=content, special_params=get_special_params(), flag_map=flag_map)


@application.route("/all_news")
def all_news():
    page = get(f"{link_website}api/smartpage/4").json()
    content, flag_map = get(f"{link_website}api/content/{page['id']}").json(), False
    flag_map = any([True if cont['type'] == "Map" else flag_map for cont in content])
    return render_template('all_news.html', title=page["heading"], page=page, content=content, special_params=get_special_params(), flag_map=flag_map)


@application.route("/team")
def team():
    page = get(f"{link_website}api/smartpage/5").json()
    content, flag_map = get(f"{link_website}api/content/{page['id']}").json(), False
    flag_map = any([True if cont['type'] == "Map" else flag_map for cont in content])
    return render_template('team.html', title=page["heading"], page=page, content=content, special_params=get_special_params(), flag_map=flag_map)


@application.route("/")
def website_main():
    page = get(f"{link_website}api/smartpage/1").json()
    content, flag_map = get(f"{link_website}api/content/{page['id']}").json(), False
    flag_map = any([True if cont['type'] == "Map" else flag_map for cont in content])
    return render_template('main-page.html', len=len(get_special_params()["text"]), title=page["heading"], page=page, content=content, special_params=get_special_params(), flag_map=flag_map)


@application.route("/page/<string:link>")
def page_by_link(link):
    smartpages = get(f"{link_website}api/smartpage").json()
    if link == smartpages[0]["link"]:
        return redirect("/")
    if link == smartpages[1]["link"]:
        return redirect("/agro_and_agro-tourism_sector")
    if link == smartpages[2]["link"]:
        return redirect("/partners")
    if link == smartpages[3]["link"]:
        return redirect("/all_news")
    if link == smartpages[4]["link"]:
        return redirect("/team")
    if link == smartpages[5]["link"]:
        return redirect("/contacts")
    page = get(f"{link_website}api/smartpage/{link}").json()
    if "message" in page:
        return page_not_found()
    content, flag_map = get(f"{link_website}api/content/{page['id']}").json(), False
    flag_map = any([True if cont['type'] == "Map" else flag_map for cont in content])
    return render_template('generated-page.html', title=page["heading"], page=page, content=content,
                           special_params=get_special_params(), flag_map=flag_map)


@application.route("/news-page/<string:link>")
def news_page(link):
    news = get(f"{link_website}api/newspage/{link}").json()
    if "message" in news:
        return page_not_found()
    return render_template('news.html', title=news["heading"], news=news, special_params=get_special_params())


@application.route("/partner-page/<int:id>")
def partner_page(id):
    partner = get(f"{link_website}api/member/{id}").json()
    if "message" in partner:
        return page_not_found()
    return render_template('partner.html', title=partner["name"], partner=partner)


@application.route("/member-page/<int:id>")
def member_page(id):
    member = get(f"{link_website}api/partner/{id}").json()
    if "message" in member:
        return page_not_found()
    return render_template('partner.html', title=member["name"], member=member)


@application.route('/logout')
@login_required
def logout():
    password_manager.delete_user(current_user.email)
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    print("http://127.0.0.1:8000/admin")
    print("http://127.0.0.1:8000/login")
    main()
