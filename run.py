import os
import random
import threading
import moviepy.editor as mp
from markupsafe import Markup
from flask import Flask, render_template, request
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_restful import Api
from werkzeug.utils import redirect
from data import db_session
from data.API.ConfirmationCodeAPI.ConfirmationcodeResource import create_code
from data.API.NewspageAPI.NewspageResource import NewspageListRecourseId, NewspageListRecourseTags

"""from data.API.AdminAPI.AdminResource import CreateAdminResource, AdminResource, UserResourceAdmin
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
from data.API.SeoAPI.SeoResource import SeoGetRecourse, AdminResourceSeo"""

from data.user import User
from main import ManagerContainer, text_transform, get_coord, PasswordManager, write_log
from data.forms import NewspageForm, AdminForm, FeedbackForm, ContentForm, PartnerForm, SmartpageForm, DeleteForm, \
    StartForm, PhoneForm, AddressForm, EmailForm, SocialmediaForm, WorkerForm, SeoForm, TextForm, MemberForm
from werkzeug.utils import secure_filename
from PIL import Image
import config
import shutil
from data.Inner.NewspageInnerAPI import get_newspage_list, get_newspage_link, get_newspage_from_to, edit_newspage, create_newspage
from data.Inner.ContentInnerAPI import edit_content, create_content, get_content_list, get_content_usual
from data.Inner.AddressInnerAPI import get_address_list, edit_address
from data.Inner.SmartpageInnerAPI import edit_smartpage, get_smartpage_list, get_smartpage_usual, get_smartpage_link, create_smartpage
from data.Inner.WorkerInnerAPI import edit_worker, create_worker, get_worker_list
from data.Inner.PartnerInnerAPI import edit_partner, create_partner, get_partner_usual, get_partner_list
from data.Inner.MemberInnerAPI import edit_member, create_member, get_member_usual, get_member_list
from data.Inner.FeedbackInnerAPI import edit_feedback, feedback_edit_image, create_feedback
from data.Inner.EmailInnerAPI import edit_email, create_email, get_email_list
from data.Inner.PhoneInnerAPI import edit_phone, create_phone, get_phone_list
from data.Inner.SocialmediaInnerAPI import edit_socialmedia, create_socialmedia, get_socialmedia_list
from data.Inner.SeoInnerAPI import get_seo_usual, edit_seo
from data.Inner.TextInnerAPI import edit_text, create_text, get_text_list
from data.Inner.AdminInnerAPI import edit_admin, create_admin, edit_admin_admin
from data.Inner.AuditlogInnerAPI import edit_auditlog
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
api.add_resource(NewspageListRecourseId, "/api/newspage/<int:start_id>/<int:end_id>")
api.add_resource(NewspageListRecourseTags, "/api/newspage/<int:start_id>/<int:end_id>/<string:text>")
"""# Подключаем api

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

# SeoApi
api.add_resource(AdminResourceSeo, "/api/seo/<int:seo_id>")
api.add_resource(SeoGetRecourse, "/api/seo/<int:seo_id>")

# TextApi
api.add_resource(TextListRecourse, "/api/text")
api.add_resource(CreateTextResource, "/api/text")
api.add_resource(AdminResourceText, "/api/text/<int:text_id>")"""

db_session.global_init("db/FarmersAssociation.sqlite")
login_manager = LoginManager()
login_manager.init_app(application)
containerManager = ManagerContainer()
formatting_text_instruction = \
    ["<br> новая строка - Указывается в месте переноса на новую строку",
     "<p></p> Текст между тэгов будет курсивным", "<b></b> Текст между тэгов будет жирным",
     "<h></h> Текст между тэгов будет заголовочным и по середине экрана",
     "<a href></a> Текст между тэгов будет подчёркнутым и содержать в себе ссылку, написанную на месте href",
     "<image id> Вставляет на этом месте картинку из поля загрузки картинок (нумерация изображений идёт с 1)"]
formatting_text_instruction_usual = \
    ["<image id> Вставляет на этом месте картинку из поля загрузки картинок (нумерация изображений идёт с 1)"]
admin_images = {}
feedback_images = {}
admin_logos = {}
special_params = {}


def get_render_template(template, **kwargs):
    return render_template(template, special_params=get_special_params(), **kwargs)


def get_path(end=""):
    return f"tmp/{current_user.email}{end}"


def clear_old_files(key, path):
    admin_images[key] = []
    delete_folder(path)


def set_map_params():
    members, provinces, occupations = special_params["member"], [], []
    for member in members:
        if member['province'] not in provinces:
            provinces.append(member['province'])
        for ocup in member['occupation'].split("//"):
            ocup = ocup.strip().capitalize()
            if ocup not in occupations:
                occupations.append(ocup)
    special_params["provinces"] = provinces
    special_params["occupations"] = occupations


def set_footer_params():
    special_params["numbers"] = get_phone_list()
    special_params["socials"] = get_socialmedia_list()
    special_params["emails"] = get_email_list()
    special_params["address"] = get_address_list()
    special_params["link"] = link_website
    special_params['our_coord'] = get_coord(special_params["address"][0]["place"])["success"][0]


def set_seo_params():
    seoparams = get_seo_usual(1)
    special_params["seo"] = {"icon": "logo.png", "link_icon": "logo-sm.png", "title": seoparams['title'],
                             "description": seoparams["description"], "tags": seoparams["tags"].split(", ")}


def set_other_params():
    special_params["news"] = get_newspage_from_to(0, 9)
    members = get_member_list()
    for ind, member in enumerate(members):
        if os.path.exists(application.config["UPLOAD_FOLDER"]+member['logo'].split("//")[0]) and member['logo'].split("//")[0] != "":
            members[ind]["ratio"] = get_ratio(member['logo'].split("//")[0])
        else:
            members[ind]["ratio"] = 1
    special_params['member'] = members
    special_params["smartpages"] = get_smartpage_list() # abc
    special_params["worker"] = get_worker_list()
    special_params["text"] = get_text_list()
    special_params["partner"] = get_partner_list()
    set_map_params()


def crop_center(img):
    img_width, img_height, min_size = img.size[0], img.size[1], min(img.size)
    return img.crop(((img_width - min_size) // 2, (img_height - min_size) // 2,
                     (img_width + min_size) // 2, (img_height + min_size) // 2))


def get_image_name(link, isBlack=False):
    link = link.split("//")
    images = {"vk.com": "vk.png", "t.me": "telegram.png", "instagram.com": "instagram.png",
              "facebook.com": "facebook.png", "twitter.com": "twitter.png", "tiktok.com": "tiktok.png"}
    imagesBLACK = {"vk.com": "vkBLACK.png", "t.me": "telegramBLACK.png", "instagram.com": "instagramBLACK.png",
                   "facebook.com": "facebookBLACK.png", "twitter.com": "twitterBLACK.png", "tiktok.com": "tiktokBLACK.png"}
    if len(link) > 1:
        for key in images.keys():
            if key in link[1]:
                if isBlack:
                    return f"socialmedia/{imagesBLACK[key]}"
                else:
                    return f"socialmedia/{images[key]}"
    return "socialmedia/socialmedia.png"


def get_icons_links(links):
    social = []
    if links:
        for link in links.split():
            social.append({"icon": get_image_name(link, True), "link": link})
    return social


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    a = session.query(User).get(user_id)
    session.close()
    return a


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


def save_image_multithreading(filename, file, feedback=False):
    size = (720, 480) if feedback else (1920, 1080)
    path = "/".join(filename.split("/")[:-1])
    if not os.path.exists(path):
        os.makedirs(path)
    file.save(filename)
    print(filename, "CYKA")
    print(os.path.exists(filename))
    image = Image.open(filename)
    if image.size[0] > size[0] or image.size[1] > size[1]:
        image.thumbnail(size)
    split_name = filename.split('.')
    path, format = '.'.join(split_name[:-1]), split_name[-1]
    if format not in ["png", "gif"]:
        image = image.convert('RGB')
    if format != "gif":
        image.save(filename)


def get_files_from(folder, path=application.config["UPLOAD_FOLDER"]):
    files = []
    if os.path.exists(application.config["UPLOAD_FOLDER"]+folder):
        files = os.listdir(application.config["UPLOAD_FOLDER"]+folder)
    return files


def save_image(filename, file, feedback=False):
    t1 = threading.Thread(target=save_image_multithreading, args=(os.path.join(application.config["UPLOAD_FOLDER"], filename), file, feedback))
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
            if os.path.isdir(f"{path}{folder_name}/{filename}"):
                delete_folder(f"{folder_name}/{filename}")
            else:
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


def transport_images(filenames, new_folder, path=application.config['UPLOAD_FOLDER']):
    new_filenames = []
    clear_folder(new_folder)
    for filename in filenames:
        if os.path.exists(path+filename):
            os.replace(path+filename, f'{path}{new_folder}/{filename.split("/")[-1]}')
            new_filenames.append(f'{new_folder}/{filename.split("/")[-1]}')
    # delete_folder(old_folder)
    return new_filenames


def save_image_test(files, path, email, r_img=False, gif=True, logo=False, feedback=False, max_image=None):  # teleport
    # print(files, list(files), dict(files))
    print(files)
    print(list(files))
    old_files, new_files, img_list, s = [], [], list(files), 0
    dict = feedback_images if feedback else admin_images
    print(dict)
    if email in dict:
        old_files = dict[email]
    print(old_files)
    for index, elem in enumerate(list(files) if max_image and len(files) == max_image else list(files)[:-1]):
        if max_image and index > max_image:
            print("А, ок")
            break
        ind, file = "".join(list(filter(lambda x: x.isdigit(), list(elem)))), files[elem]
        if not ind.isdigit() and not logo:
            continue
        ind = int(ind) - 1 if ind.isdigit() else 0
        print(files[elem], ind, index)
        print(file.filename, "222222222222")
        if files[elem].filename != "" and allowed_file(file.filename, feedback):
            gif_i = True if file.filename.split(".")[-1] == "gif" else False
            mp4 = True if file.filename.split(".")[-1] == "mp4" else False
            png = True if file.filename.split(".")[-1] == "png" else False
            print("add new image", f"gif: {gif_i} mp4: {mp4} png: {png}")
            print(img_list[ind])
            if logo:
                print("Near logo")
                if "icon" in img_list[ind]:
                    print("save logo!!!!")
                    filename = secure_filename(create_new_image_name(logo=png))
                    save_image(f"{path}/" + filename, file)
                    new_files.append(filename)
                    break
            else:
                print("save image (((")
                if mp4:
                    file.save(f'{application.config["UPLOAD_FOLDER"]}tmp/gif_{current_user.email}.mp4')
                    for filename in give_me_gif_filenames(f"tmp/gif_{current_user.email}.mp4", path):
                        new_files.append(path + "/" + filename)
                else:
                    if gif_i:
                        filename = secure_filename(create_new_image_name(gif=gif))
                    else:
                        filename = secure_filename(create_new_image_name())
                    save_image(f"{path}/"+filename, file, feedback)
                    new_files.append(filename)
        elif ind < len(old_files):
            print("add old file:", old_files[ind], ind)
            new_files.append(old_files[ind])
    for file in old_files:
        if file not in new_files:
            print("delete file:", file)
            delete_img(file)
    if len(new_files) == 0 and r_img:
        r_name = f"{create_random_name(50)}.jpg"
        img = Image.open(f"{application.config['UPLOAD_FOLDER']}standard.png")
        if not os.path.exists(f"{application.config['UPLOAD_FOLDER']}{path}"):
            os.makedirs(f"{application.config['UPLOAD_FOLDER']}{path}")
        img.save(f"{application.config['UPLOAD_FOLDER']}{path}/{r_name}")
        new_files.append(r_name)
    dict[email] = new_files
    new_files = [f"{path}/"+_ for _ in new_files]
    delete_everything_except(path, new_files)
    print(new_files, "333333333\n\n\n\n")
    return new_files


def save_images(cont_name, files, r_img=True, max_image=None, auto_delete=False, logo=False, cont_logo=None, gif=True, icon=False, feedback=False):
    filenames, filenames2, img_list, cont, cont2 = [], [], list(files), containerManager.get_container(cont_name), containerManager.get_container(cont_logo)
    for ind, name in enumerate(files):
        if max_image and len(filenames) >= max_image:
            break
        file = files[name]
        if file.filename != "" and allowed_file(file.filename, feedback):
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
        r_name = f"{create_random_name(50)}.png"
        img = Image.open(f"{application.config['UPLOAD_FOLDER']}standard.png")
        if logo and len(filenames2) == 0:
            if not os.path.exists(f"{application.config['UPLOAD_FOLDER']}{cont_logo}"):
                os.makedirs(f"{application.config['UPLOAD_FOLDER']}{cont_logo}")
            img.save(f"{application.config['UPLOAD_FOLDER']}{cont_logo}/{r_name}")
            filenames2 = [f"{cont_logo}/{r_name}"]
        if len(filenames) == 0:
            if not os.path.exists(f"{application.config['UPLOAD_FOLDER']}{cont_name}"):
                os.makedirs(f"{application.config['UPLOAD_FOLDER']}{cont_name}")
            img.save(f"{application.config['UPLOAD_FOLDER']}{cont_name}/{r_name}")
            filenames = [f"{cont_name}/{r_name}"]
    if logo:
        containerManager.add_container(cont_logo, filenames2, auto_delete)
    containerManager.add_container(cont_name, filenames, auto_delete)
    if logo:
        return filenames, filenames2
    return filenames


def get_special_params():
    global load_new_footer_params, load_new_params, load_seo_params
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
    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'mp4']
    ALLOWED_EXTENSIONS_FEEDBACK = ['png', 'jpg', 'jpeg']
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
            # write_log(f"User login {password_manager.user_is_authed(current_user.email)} {current_user.email}")
            return redirect("/admin")
        return get_render_template('login.html', message="Неправильный логин или пароль", form=form)
    return get_render_template('login.html', title='Авторизация', form=form)


@application.route("/admin")
@login_required
def admin():
    if check_user():
        return redirect("/login")
    return get_render_template('admin-panel.html', title='админка')


@application.route("/admin-footer-settings")
@login_required
def admin_footer_settings():
    set_footer_params()
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = StartForm()
        message, result = "", False
        return get_render_template('form/admin-form-footer.html', form=form, message=message, result=result, title="Настройка подвала")
    return you_dont_have_permission()


@application.route("/admin-seo-settings", methods=['GET', 'POST'])
@login_required
def admin_seo_settings():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = SeoForm()
        seoparams = get_seo_usual(1)
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
                message = edit_seo(1, {"admin_email": current_user.email, "action": "put",
                                                                "title": form.title.data, "tags": form.tags.data,
                                                                "description": form.description.data})
                if "success" in message:
                    result = True
                    set_seo_params()
                message = list(message.values())[0]
        else:
            form.title.data = seoparams["title"]
            form.description.data = seoparams["description"]
            form.tags.data = seoparams["tags"]
        return get_render_template('form/admin-form-seo.html', form=form, message=message, result=result, title="Настройка сайта")
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
                message = create_text({"heading": form.heading.data, "description": form.description.data,
                                                                "admin_email": current_user.email})
                if "success" in message:
                    result = True
                    set_other_params()
                message = list(message.values())[0]
        return get_render_template('form/admin-form-text.html', title='Добавление текста', message=message, form=form, result=result)
    return you_dont_have_permission()


@application.route("/admin-edit-text/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_text(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = TextForm()
        message, result = None, False
        text = edit_text(id, {"admin_email": current_user.email, "action": "get"})
        if "message" not in text:
            if request.method == 'POST':
                if form.submit.data:
                    message = edit_text(id, {"heading": form.heading.data, "description": form.description.data,
                                                                        "admin_email": current_user.email, "action": "put"})
                    if "success" in message:
                        result = True
                        set_other_params()
                    message = list(message.values())[0]
            else:
                form.heading.data = text["heading"]
                form.description.data = text["description"]
        else:
            message = "Телефон не найден"
        return get_render_template('form/admin-form-text.html', title='Редактирование текста', message=message, result=result, form=form)
    return you_dont_have_permission()


@application.route("/admin-delete-text/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_text(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, result, name = None, False, "текст не найден"
        text = edit_text(id, {"admin_email": current_user.email, "action": "get"})
        if "message" not in text:
            name = "текст " + text["heading"]
            if request.method == 'POST':
                message = edit_text(id, {"admin_email": current_user.email, "action": "delete"})
                if "success" in message:
                    result = True
                    set_other_params()
                message = list(message.values())[0]
        return get_render_template('form/admin-form-delete.html', title='Удаление текста', message=message, form=form,
                                   name=name, result=result, link_back="/admin-seo-settings")
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
                message = create_phone({"number": form.number.data, "admin_email": current_user.email})
                if "success" in message:
                    result = True
                    set_footer_params()
                message = list(message.values())[0]
        return get_render_template('form/admin-form-phone.html', title='Добавление номера телефона', message=message,
                               form=form, result=result)
    return you_dont_have_permission()


@application.route("/admin-edit-phone/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_phone(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = PhoneForm()
        message, result = None, False
        phone = edit_phone(id, {"admin_email": current_user.email, "action": "get"})
        if "message" not in phone:
            if request.method == 'POST':
                if form.submit.data:
                    message = edit_phone(id, {"number": form.number.data, "admin_email": current_user.email, "action": "put"})
                    if "success" in message:
                        result = True
                        set_footer_params()
                    message = list(message.values())[0]
            else:
                form.number.data = phone["number"]
        else:
            message = "Телефон не найден"
        return get_render_template('form/admin-form-phone.html', title='Редактирование номера телефона', message=message,
                               result=result, form=form)
    return you_dont_have_permission()


@application.route("/admin-delete-phone/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_phone(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, result, name = None, False, "телефон не найден"
        phone = edit_phone(id, {"admin_email": current_user.email, "action": "get"})
        if "message" not in phone:
            name = "телефон " + phone["number"]
            if request.method == 'POST':
                message = edit_phone(id, {"admin_email": current_user.email, "action": "delete"})
                if "success" in message:
                    result = True
                    set_footer_params()
                message = list(message.values())[0]
        return get_render_template('form/admin-form-delete.html', title='Удаление телефона', message=message, form=form, name=name,
                               result=result, link_back="/admin-footer-settings")
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
                message = create_email({"email_address": form.email.data, "admin_email": current_user.email})
                if "success" in message:
                    result = True
                    set_footer_params()
                message = list(message.values())[0]
        return get_render_template('form/admin-form-email.html', title='Добавление почтового адреса', message=message,
                               form=form, result=result)
    return you_dont_have_permission()


@application.route("/admin-edit-email/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_email(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = EmailForm()
        message, result = None, False
        email = edit_email(id, {"admin_email": current_user.email, "action": "get"})
        if "message" not in email:
            if request.method == 'POST':
                if form.submit.data:
                    message = edit_email(id, {"email_address": form.email.data, "admin_email": current_user.email, "action": "put"})
                    if "success" in message:
                        result = True
                        set_footer_params()
                    message = list(message.values())[0]
            else:
                form.email.data = email["email_address"]
        else:
            message = "Почтовый адрес не найден"
        return get_render_template('form/admin-form-email.html', title='Редактирование почтового адреса', message=message,
                               result=result, form=form)
    return you_dont_have_permission()


@application.route("/admin-delete-email/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_email(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, result, name = None, False, "почтовый адрес не найден"
        email = edit_email(id, {"admin_email": current_user.email, "action": "get"})
        if "message" not in email:
            name = "почтовый адрес " + email["email_address"]
            if request.method == 'POST':
                message = edit_email(id, {"admin_email": current_user.email, "action": "delete"})
                if "success" in message:
                    result = True
                    set_footer_params()
                message = list(message.values())[0]
        return get_render_template('form/admin-form-delete.html', title='Удаление почтового адреса', message=message, form=form,
                               name=name, result=result, link_back="/admin-footer-settings")
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
                message = create_socialmedia({"icon_type": get_image_name(form.link.data), "link": form.link.data,
                                                                       "admin_email": current_user.email})
                if "success" in message:
                    result = True
                    set_footer_params()
                message = list(message.values())[0]
        return get_render_template('form/admin-form-socialmedia.html', title='Добавление ссылки на соцсеть', message=message,
                               form=form, result=result)
    return you_dont_have_permission()


@application.route("/admin-edit-socialmedia/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_socialmedia(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = SocialmediaForm()
        message, result = None, False
        socialmedia = edit_socialmedia(id, {"admin_email": current_user.email, "action": "get"})
        if "message" not in socialmedia:
            if request.method == 'POST':
                if form.submit.data:
                    message = edit_socialmedia(id, {"admin_email": current_user.email, "action": "put",
                                                                               "icon_type": get_image_name(form.link.data), "link": form.link.data})
                    if "success" in message:
                        result = True
                        set_footer_params()
                    message = list(message.values())[0]
            else:
                form.link.data = socialmedia["link"]
        else:
            message = "Ссылка на соцсесть не найдена"
        return get_render_template('form/admin-form-socialmedia.html', title='Редактирование ссылки на соцсеть', message=message,
                               result=result, form=form)
    return you_dont_have_permission()


@application.route("/admin-delete-socialmedia/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_socialmedia(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, result, name = None, False, "ссылка на соцсеть на найдена"
        socialmedia = edit_socialmedia(id, {"admin_email": current_user.email, "action": "get"})
        if "message" not in socialmedia:
            name = "почтовый адрес " + socialmedia["link"]
            if request.method == 'POST':
                message = edit_socialmedia(id, {"admin_email": current_user.email, "action": "delete"})
                if "success" in message:
                    result = True
                    set_footer_params()
                message = list(message.values())[0]
        return get_render_template('form/admin-form-delete.html', title='Удаление ссылки на соцсеть', message=message, form=form,
                               name=name, result=result, link_back="/admin-footer-settings")
    return you_dont_have_permission()


@application.route("/admin-edit-address/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_address(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = AddressForm()
        message, result = None, False
        address = edit_address(id, {"admin_email": current_user.email, "action": "get"})
        if "message" not in address:
            if request.method == 'POST':
                if form.submit.data:
                    res = get_coord(form.address.data)
                    if "success" in res:
                        special_params["our_coord"] = res
                        message = edit_address(id, {"coord": res["success"][0], "admin_email": current_user.email,
                                                    "action": "put", "admin_password": password_manager.get_password(current_user.email), "place": form.address.data})
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
        return get_render_template('form/admin-form-address.html', title='Редактирование адреса', message=message,
                               result=result, form=form)
    return you_dont_have_permission()


@application.route("/admin-list-news")
@login_required
def admin_list_news():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        clear_old_files(current_user.email, get_path())
        newslist = get_newspage_list()
        return get_render_template('list/admin-list-news.html', title='Новости', newslist=newslist)
    return you_dont_have_permission()


@application.route("/admin-create-news", methods=['GET', 'POST'])
@login_required
def admin_create_news():  # teleport
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = NewspageForm()
        message, result, preview_text, path = None, False, None, get_path()
        if request.method == 'POST':
            filenames = save_image_test(request.files, path, current_user.email)
            text_trans = text_transform(form.text.data, filenames, application.config["UPLOAD_FOLDER"])
            if form.submit.data:
                if text_trans[:5] != "Error":
                    message = create_newspage({"heading": form.heading.data, "text": form.text.data, "tags": form.tags.data,
                                   "image": "//".join(filenames), "admin_email": current_user.email}) # teleport
                    if "success" in message:
                        filenames = transport_images(filenames, f"news/news_{message['id']}")
                        m = edit_newspage(message['id'], {"image": "//".join(filenames), 'admin_email': current_user.email, "action": "put"}) # teleport
                        result = True
                        set_other_params()
                    message = list(message.values())[-1]
                else:
                    message = text_trans[7:].capitalize()
            elif form.preview.data:
                preview_text = Markup(text_trans)
        else:
            filenames = get_files_from(path)
        return get_render_template('form/admin-form-news.html', title='Создание новости', message=message, preview_text=preview_text,
                               form=form, result=result, filenames=filenames, image_len=len(filenames) + 1,
                               formatting_text_instruction=formatting_text_instruction)
    return you_dont_have_permission()


@application.route("/admin-edit-news/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_news(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = NewspageForm()
        message, result, filenames, preview_text, path = None, False, [], None, get_path()
        news = edit_newspage(id, {"admin_email": current_user.email, "action": "get"}) # teleport
        if "message" not in list(news):
            if request.method == 'POST':
                filenames = save_image_test(request.files, path, current_user.email)
                text_trans = text_transform(form.text.data, filenames, application.config["UPLOAD_FOLDER"])
                if form.submit.data:
                    if text_trans[:5] != "Error":
                        message = edit_newspage(id, {"heading": form.heading.data, "text": form.text.data, "image": "//".join(filenames),
                                                     "admin_email": current_user.email, "action": "put", "tags": form.tags.data}) # teleport
                        if "success" in message:
                            result = True
                            filenames = transport_images(filenames, f"news/news_{id}")
                            m = edit_newspage(id, {"image": "//".join(filenames), 'admin_email': current_user.email, "action": "put"}) # teleport
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
                if get_files_from(path) == []:
                    filenames = copy_files(f"news/news_{id}", path, news["image"].split("//"))
                    admin_images[current_user.email] = [_.split("/")[-1] for _ in filenames]
                else:
                    filenames = get_files_from(path)
        else:
            message = list(news.values())[0]
        return get_render_template('form/admin-form-news.html', title='Редактирование новости', message=message, result=result,
                               form=form, filenames=filenames, image_len=len(filenames) + 1, preview_text=preview_text,
                               formatting_text_instruction=formatting_text_instruction)
    return you_dont_have_permission()


@application.route("/admin-delete-news/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_news(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, result, name = None, False, "новость не найдена"
        news = edit_newspage(id, {"admin_email": current_user.email, "action": "get"})
        if "message" not in news:
            name = "новость " + news["heading"]
            if request.method == 'POST':
                message = edit_newspage(id, {"admin_email": current_user.email, "action": "delete"})
                if "success" in message:
                    result = True
                    delete_folder(f"news/news_{id}")
                    set_other_params()
                message = list(message.values())[0]
        return get_render_template('form/admin-form-delete.html', title='Удаление новости', message=message, form=form,
                               result=result, name=name, link_back="/admin-list-news")
    return you_dont_have_permission()


@application.route("/admin-list-admin")
@login_required
def admin_list_admin():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        adminlist = edit_admin({"admin_email": current_user.email, "action": "get_list", "admin_password": password_manager.get_password(current_user.email)})
        return get_render_template('list/admin-list-admin.html', title='Новости', adminlist=adminlist, status=current_user.status,
                               current_id=current_user.id, flag=(current_user.status > 0))
    return you_dont_have_permission()


@application.route("/admin-change-password/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_change_password(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 1:
        form = AdminForm()
        if current_user.id == id:
            admin = edit_admin({"admin_email": current_user.email, "action": "get"})
        else:
            admin = edit_admin_admin(id, {"admin_email": current_user.email, "action": "get"})
        message, result, name = None, False, ""
        if "message" not in admin:
            name = f'{admin["name"]} {admin["surname"]}'
            if request.method == 'POST':
                if form.password.data == form.password_again.data:
                    if id == current_user.id:
                        message = edit_admin({"admin_email": current_user.email,
                                      "new_admin_password": form.password.data, "action": "put", "change_password": True,
                                      "check_admin_password": form.password_current.data})
                    else:
                        message = edit_admin_admin(id, {"admin_email": current_user.email,
                                      "new_admin_password": form.password.data, "action": "put", "change_password": True,
                                      "check_admin_password": form.password_current.data})
                    if "success" in message:
                        password_manager.add_user(admin["email"], form.password.data)
                        result = True
                    message = list(message.values())[0]
                else:
                    message = "Новые пароли не совпадают"
        else:
            message = list(admin.values())[0]
        return get_render_template('admin-change-password.html', title=f'Изменение пароля админу {name}', message=message,
                               form=form, result=result)
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
                message = create_admin({"name": form.name.data, "surname": form.surname.data,
                               "email": form.email.data, "status": form.status.data, "admin_email": current_user.email,
                               "admin_password": password_manager.get_password(current_user.email), "new_admin_password": form.password.data})
                form.status.data = str(form.status.data)
                if "success" in message:
                    password_manager.add_user(form.email.data, form.password)
                    result = True
                message = list(message.values())[0]
            else:
                message = "Пароли не совпадают"
        return get_render_template('form/admin-form-admin.html', title='Создание админа', message=message, form=form,
                               result=result, flag=True, f=True,
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
            admin = edit_admin({"admin_email": current_user.email, "action": "get", "admin_password": password_manager.get_password(current_user.email)})
        else:
            f = True
            admin = edit_admin_admin(id, {"admin_email": current_user.email, "action": "get", "admin_password": password_manager.get_password(current_user.email)})
        form.stat = current_user.status
        message, result, admin_status = None, False, 0
        if "message" not in admin:
            admin_status = admin["status"]
            if request.method == 'POST':
                if current_user.id == id:
                    message = edit_admin({"name": form.name.data, "surname": form.surname.data, "email": form.email.data,
                                  "admin_email": current_user.email, "action": "put", "admin_password": password_manager.get_password(current_user.email)})
                else:
                    message = edit_admin_admin(id, {"name": form.name.data, "surname": form.surname.data, "email": form.email.data,
                                  "status": int(form.status.data), "admin_email": current_user.email, "action": "put", "admin_password": password_manager.get_password(current_user.email)})
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
        return get_render_template('form/admin-form-admin.html', title='Редактирование админа', message=message, form=form,
                               result=result, flag=False, admin_status=admin_status,
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
        admin = edit_admin_admin(id, {"admin_email": current_user.email, "action": "get", "admin_password": password_manager.get_password(current_user.email)})
        if "message" not in admin:
            name = "админа " + f"{admin['name']} {admin['surname']}"
            if admin["status"] < current_user.status:
                if request.method == 'POST':
                    message = edit_admin_admin(id, {"admin_email": current_user.email,
                                                                         "action": "delete", "admin_password": password_manager.get_password(current_user.email)})
                    if "success" in message:
                        result = True
                    message = list(message.values())[0]
            else:
                message = "У вас недостаточно прав для этого"
        else:
            name = "пользователь не найден"
        return get_render_template('form/admin-form-delete.html', title='Удаление админа', message=message, form=form,
                               result=result, name=name, link_back="/admin-list-admin")
    return you_dont_have_permission()


@application.route("/admin-list-smartpage/<int:page_id>")
@login_required
def admin_list_smartpage(page_id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        clear_old_files(current_user.email, get_path())
        smartpagelist, contentdict = get_smartpage_list(), {}
        contentlist = get_content_list()
        for page in smartpagelist:
            for content in contentlist:
                if page["id"] == content["smartpage_id"]:
                    if page["id"] in contentdict:
                        contentdict[page["id"]].append(content)
                    else:
                        contentdict[page["id"]] = [content]
        return get_render_template('list/admin-list-smartpage.html', title='Страницы', smartpagelist=smartpagelist,
                               contentdict=contentdict, types={"News": "Новости", "Image": "Картинки", "Text": "Текст", "Partner": "Партнёры", "Map": "Карта", "Member": "Участники"},
                               page_id=page_id)
    return you_dont_have_permission()


@application.route("/admin-create-smartpage", methods=['GET', 'POST'])
@login_required
def admin_create_smartpage():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = SmartpageForm()
        message, result, filenames = None, False, []
        if request.method == 'POST':
            path = get_path()
            filenames = save_image_test(request.files, path, current_user.email, r_img=True)
            message = create_smartpage({"heading": form.heading.data, "image": "//".join(filenames),
                                                                 "admin_email": current_user.email})
            if "success" in message:
                filenames = transport_images(filenames, f"smartpage/smartpage_{message['id']}")
                m = edit_smartpage(message['id'], {"image": "//".join(filenames), "admin_email": current_user.email, "action": "put"})
                result = True
                set_other_params()
            message = list(message.values())[-1]
        return get_render_template('form/admin-form-smartpage.html', title='Создание страницы', message=message, form=form,
                               result=result, filenames=filenames, image_len=len(filenames) + 1)
    return you_dont_have_permission()


@application.route("/admin-edit-smartpage/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_smartpage(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = SmartpageForm()
        smartpage = edit_smartpage(id, {"admin_email": current_user.email, "action": "get"})
        message, result, filenames, path = None, False, [], get_path()
        if "message" not in smartpage:
            if request.method == 'POST':
                filenames = save_image_test(request.files, path, current_user.email, r_img=True)
                message = edit_smartpage(id, {"heading": form.heading.data, "image": "//".join(filenames),
                              "admin_email": current_user.email, "action": "put"})
                if "success" in message:
                    filenames = transport_images(filenames, f"smartpage/smartpage_{id}")
                    m = edit_smartpage(id, {"image": "//".join(filenames),
                            "admin_email": current_user.email, "action": "put"})
                    result = True
                    delete_folder(f"tmp/smartpage/smartpage_{current_user.email}")
                    set_other_params()
                message = list(message.values())[0]
            else:
                form.heading.data = smartpage["heading"]
                if get_files_from(path) == []:
                    filenames = copy_files(f"smartpage/smartpage_{id}", path, smartpage["image"].split("//"))
                    admin_images[current_user.email] = [_.split("/")[-1] for _ in filenames]
                else:
                    filenames = get_files_from(path)
        else:
            message = list(smartpage.values())[-1]
        return get_render_template('form/admin-form-smartpage.html', title='Редактирование страницы', message=message, form=form,
                               result=result, flag=False, filenames=filenames, image_len=len(filenames) + 1)
    return you_dont_have_permission()


@application.route("/admin-delete-smartpage/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_smartpage(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result = "", "страница не найдена", False
        smartpage = edit_smartpage(id, {"admin_email": current_user.email, "action": "get"})
        if "message" not in smartpage:
            name = "страница " + smartpage['heading']
            if request.method == 'POST':
                content_list = get_content_usual(id)
                for content in content_list:
                    delete_folder(f"content/content_{content['id']}")
                message = edit_smartpage(id, {"admin_email": current_user.email, "action": "delete"})
                if "success" in message:
                    result = True
                    delete_folder(f"smartpage/smartpage_{id}")
                    set_other_params()
                message = list(message.values())[-1]
        return get_render_template('form/admin-form-delete.html', title='Удаление страницы', message=message, form=form,
                               result=result, name=name, link_back="/admin-list-smartpage/0")
    return you_dont_have_permission()


@application.route("/admin-create-content/<int:page_id>", methods=['GET', 'POST'])
@login_required
def admin_create_content(page_id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = ContentForm()
        path = get_path()
        message, result, filenames, filename = None, False, [], None
        if request.method == 'POST':
            filenames = save_image_test(request.files, path, current_user.email)
            image = "" if len(filenames) == 0 else "//".join(filenames)
            message = create_content({"type": form.type.data, "text": form.text.data, "page_id": page_id, "display_type":
                                      form.display_type.data, "display_type_member": form.display_type_member.data, "heading": form.heading.data,
                                      "image": image, 'admin_email': current_user.email})
            if "success" in message:
                filenames = transport_images(filenames, f"content/content_{message['id']}")
                if filenames != []:
                    m = edit_content(message['id'], {"image": "//".join(filenames), "action": "put", "admin_email": current_user.email})
                clear_old_files(current_user.email, path)
                result = True
            message = list(message.values())[-1]
        return get_render_template('form/admin-form-content.html', title='Создание контента', message=message, form=form,
                               result=result, flag=True, filenames=filenames, image_len=len(filenames) + 1, page_id=page_id)
    return you_dont_have_permission()


@application.route("/admin-edit-content-move-up/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_content_move_up(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        content, page_id = edit_content(id, {"admin_email": current_user.email, "action": "get"}), 0
        if "message" not in content:
            m = edit_content(id, {"position": content["position"] - 1, "action": "put", "admin_email": current_user.email})
            page_id = content['smartpage_id']
        return redirect(f"/admin-list-smartpage/{page_id}")
    return you_dont_have_permission()


@application.route("/admin-edit-content-move-down/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_content_move_down(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        content, page_id = edit_content(id, {"admin_email": current_user.email, "action": "get"}), 0
        if "message" not in content:
            m = edit_content(id, {"position": content["position"] - 1, "action": "put", "admin_email": current_user.email})
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
        content = edit_content(id, {"admin_email": current_user.email, "action": "get"})
        path = get_path()
        message, result, filenames, page_id = None, False, [], 0
        if "message" not in content:
            page_id = content["smartpage_id"]
            if request.method == 'POST':
                filenames = save_image_test(request.files, path, current_user.email)
                message = edit_content(id, {"type": form.type.data, "text": form.text.data, "heading": form.heading.data,
                                            "image": '//'.join(filenames), "action": "put", "display_type": form.display_type.data,
                                            "admin_email": current_user.email, "display_type_member": form.display_type_member.data})
                if "success" in message:
                    filenames = transport_images(filenames, f"content/content_{id}")
                    if filenames != []:
                        m = edit_content(id, {"image": "//".join(filenames), "action": "put", "admin_email": current_user.email})
                    result = True
                message = list(message.values())[-1]
            else:
                form.type.data = content["type"]
                form.text.data = content["text"]
                form.heading.data = content["heading"]
                form.display_type.data = content["display_type"]
                form.display_type_member.data = content["display_type_member"]
                page_id = content["smartpage_id"]
                if get_files_from(path) == []:
                    filenames = copy_files(f"content/content_{id}", path, content["image"].split("//"))
                    admin_images[current_user.email] = [_.split("/")[-1] for _ in filenames]
                else:
                    filenames = get_files_from(path)
        else:
            message = list(content.values())[-1]
        return get_render_template('form/admin-form-content.html', title='Редактирование контента', message=message, form=form,
                               result=result, flag=False, filenames=filenames, image_len=len(filenames) + 1,
                               page_id=page_id)
    return you_dont_have_permission()


@application.route("/admin-delete-content/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_content(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result, page_id = "", "контент не найден", False, 0
        content = edit_content(id, {"admin_email": current_user.email, "action": "get"})
        if "message" not in content:
            page_id = content["smartpage_id"]
            name = "контент " + content['heading']
            if request.method == 'POST':
                message = edit_content(id, {"action": "delete", "admin_email": current_user.email})
                if "success" in message:
                    result = True
                    delete_folder(f"content/content_{id}")
                message = list(message.values())[0]
        return get_render_template('form/admin-form-delete.html', title='Удаление контента', message=message, form=form,
                               result=result, name=name, link_back=f"/admin-list-smartpage/{page_id}")
    return you_dont_have_permission()


@application.route("/admin-list-worker")
@login_required
def admin_list_worker():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        clear_old_files(current_user.email, get_path())
        workerlist = get_worker_list()
        return get_render_template('list/admin-list-worker.html', title='Сотрудники', workerlist=workerlist)
    return you_dont_have_permission()


@application.route("/admin-create-worker", methods=['GET', 'POST'])
@login_required
def admin_create_worker():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form, path = WorkerForm(), get_path()
        message, result, filenames = None, False, []
        if request.method == 'POST':
            filenames = save_image_test(request.files, path, current_user.email, max_image=1)
            message = create_worker({"name": form.name.data, "image": "//".join(filenames), "profession": form.profession.data,
                                     "phone": form.phone.data, "email": form.email.data, "admin_email": current_user.email})
            if "success" in message:
                filenames = transport_images(filenames, f"worker/worker_{message['id']}")
                m = edit_worker(message['id'], {"image": "//".join(filenames), "admin_email": current_user.email, "action": "put"})
                result = True
                clear_old_files(current_user.email, path)
                set_other_params()
            message = list(message.values())[-1]
        return get_render_template('form/admin-form-worker.html', title='Добавление сотрудника', message=message, form=form,
                               result=result, filenames=filenames, image_len=len(filenames) + 1)
    return you_dont_have_permission()


@application.route("/admin-edit-worker/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_worker(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form, path = WorkerForm(), get_path()
        worker = edit_worker(id, {"admin_email": current_user.email, "action": "get"})
        message, result, filenames = None, False, []
        if "message" not in worker:
            if request.method == 'POST':
                filenames = save_image_test(request.files, path, current_user.email, max_image=1)
                message = edit_worker(id, {"profession": form.profession.data, "name": form.name.data,
                                           "email": form.email.data, "phone": form.phone.data,
                                           "image": '//'.join(filenames), "action": "put", "admin_email": current_user.email})
                if "success" in message:
                    filenames = copy_files(path, f"worker/worker_{id}", filenames)
                    m = edit_worker(id, {"image": '//'.join(filenames), "action": "put", "admin_email": current_user.email})
                    result = True
                    set_other_params()
                message = list(message.values())[-1]
            else:
                form.profession.data = worker["profession"]
                form.name.data = worker["name"]
                form.email.data = worker["email"]
                form.phone.data = worker["phone"]
                if get_files_from(path) == []:
                    filenames = copy_files(f"worker/worker_{id}", path, worker["image"].split("//"))
                    admin_images[current_user.email] = [_.split("/")[-1] for _ in filenames]
                else:
                    filenames = get_files_from(path)
                print(filenames)
        else:
            message = list(worker.values())[-1]
        return get_render_template('form/admin-form-worker.html', title='Редактирование сотрудника', message=message,
                               form=form, result=result, flag=False, filenames=filenames, image_len=len(filenames) + 1)
    return you_dont_have_permission()


@application.route("/admin-delete-worker/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_worker(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result, path = "", "сотрудник не найден", False, get_path()
        worker = edit_worker(id, {"admin_email": current_user.email, "action": "get"})
        if "message" not in worker:
            name = "сотрудник " + worker['name']
            if request.method == 'POST':
                message = edit_worker(id, {"admin_email": current_user.email, "action": "delete"})
                if "success" in message:
                    result = True
                    delete_folder(f"worker/worker_{id}")
                    set_other_params()
                message = list(message.values())[-1]
        return get_render_template('form/admin-form-delete.html', title='Удаление сотрудника', message=message, form=form,
                               result=result, name=name, link_back="/admin-list-worker")
    return you_dont_have_permission()


@application.route("/admin-list-member")
@login_required
def admin_list_member():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        clear_old_files(current_user.email, get_path())
        clear_folder(get_path("/logo"))
        clear_folder(get_path("/image"))
        memberlist = get_member_list()
        return get_render_template('list/admin-list-member.html', title='Участники', memberlist=memberlist)
    return you_dont_have_permission()


@application.route("/admin-create-member", methods=['GET', 'POST'])
@login_required
def admin_create_member():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = MemberForm()
        path_image, path_logo = get_path("/image"), get_path("/logo")
        message, result, filenames1, filenames2 = None, False, [], []
        if request.method == 'POST':
            coord = get_coord(form.address.data)
            if "success" in coord:
                filenames2, filenames1 = save_image_test(request.files, path_image, f"{current_user.email}/image"), save_image_test(request.files, path_logo, f"{current_user.email}/logo", logo=True)
                print(filenames1, filenames2)
                message = create_member({"name": form.name.data, "logo": "//".join(filenames1),
                               "image": "//".join(filenames2), "text": form.text.data, "link": form.link.data,
                               "coord": coord['success'][0], "occupation": "//".join([oc.strip().capitalize() for oc in form.occupation.data.split(',')]),
                               "address": form.address.data, "province": coord["success"][1], "admin_email": current_user.email,
                               "socialmedia": form.socialmedia.data})
                if "success" in message:
                    filenames1, filenames2 = transport_images(filenames1, f"member/member_{message['id']}/logo"), transport_images(filenames2, f"member/member_{message['id']}/image")
                    print(filenames1, filenames2)
                    m = edit_member(message['id'], {"image": "//".join(filenames2),
                            'logo': "//".join(filenames1), "admin_email": current_user.email, "action": "put"})
                    result = True
                    set_other_params()
                message = list(message.values())[-1]
            else:
                message = coord["message"]
        return get_render_template('form/admin-form-member.html', title='Создание участника', message=message, form=form,
                               result=result, flag=True, filenames1=filenames1, filenames2=filenames2, image_len=len(filenames2) + 1)
    return you_dont_have_permission()


@application.route("/admin-edit-member/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_member(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = MemberForm()
        path_image, path_logo = get_path("/image"), get_path("/logo")
        member = edit_member(id, {"admin_email": current_user.email, "action": "get"})
        message, result, filenames1, filenames2 = None, False, [], []
        if "message" not in member:
            if request.method == 'POST':
                coord = get_coord(form.address.data) if form.address.data != member["address"] else {"success": [None, None]}
                if "success" in coord:
                    filenames2, filenames1 = save_image_test(request.files, path_image, f"{current_user.email}/image"), save_image_test(request.files, path_logo, f"{current_user.email}/logo", logo=True)
                    if coord["success"] == [None, None]:
                        coord["success"] = [member["coord"], member["province"]]
                    message = edit_member(id, {"name": form.name.data, "image": "//".join(filenames2),
                                  "logo": "//".join(filenames1), "text": form.text.data, "link": form.link.data, "address": form.address.data,
                                  "coord": coord["success"][0], "province": coord["success"][1], "admin_email": current_user.email,
                                  "occupation": '//'.join([oc.strip().capitalize() for oc in form.occupation.data.split(',')]), "action": "put",
                                  "socialmedia": form.socialmedia.data})
                    if "success" in message:
                        filenames1, filenames2 = transport_images(filenames1, f"member/member_{id}/logo"), transport_images(filenames2, f"member/member_{id}/image")

                        m = edit_member(id, {"image": "//".join(filenames2), 'logo': "//".join(filenames1), "admin_email": current_user.email, "action": "put"})
                        result = True
                        set_other_params()
                    message = list(message.values())[0]
                else:
                    message = coord["message"]
            else:
                form.name.data = member["name"]
                form.text.data = member["text"]
                form.link.data = member["link"]
                form.socialmedia.data = member["socialmedia"]
                form.address.data = member["address"]
                form.occupation.data = ", ".join(member["occupation"].split("//"))
                if get_files_from(path_logo) == []:
                    filenames1 = copy_files(f"member/member_{id}/logo", path_logo, member["logo"].split("//"))
                    admin_images[f"{current_user.email}/logo"] = [_.split("/")[-1] for _ in filenames1]
                else:
                    filenames1 = get_files_from(path_logo)
                if get_files_from(path_image) == []:
                    filenames2 = copy_files(f"member/member_{id}/image", path_image, member["image"].split("//"))
                    admin_images[f"{current_user.email}/image"] = [_.split("/")[-1] for _ in filenames2]
                else:
                    filenames2 = get_files_from(path_image)
        else:
            message = list(member.values())[0]
        return get_render_template('form/admin-form-member.html', title='Редактирование участника', message=message, form=form,
                               result=result, flag=False, filenames1=filenames1, filenames2=filenames2,
                               image_len=len(filenames2) + 1)
    return you_dont_have_permission()


@application.route("/admin-delete-member/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_member(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result = "", "участник не найден", False
        member = edit_member(id, {"admin_email": current_user.email, "action": "get"})
        if "message" not in member:
            name = "страница " + member['name']
            if request.method == 'POST':
                message = edit_member(id, {"admin_email": current_user.email, "action": "delete"})
                if "success" in message:
                    result = True
                    delete_folder(f"member/member_{id}")
                    containerManager.delete_container(f"member_{id}")
                    set_other_params()
                message = list(message.values())[0]
        else:
            message = list(member.values())[0]
        return get_render_template('form/admin-form-delete.html', title='Удаление участника', message=message, form=form,
                               result=result, name=name, link_back="/admin-list-member")
    return you_dont_have_permission()


@application.route("/admin-list-partner")
@login_required
def admin_list_partner():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        clear_old_files(current_user.email, get_path())
        partnerlist = get_partner_list()
        return get_render_template('list/admin-list-partner.html', title='Партнёры', partnerlist=partnerlist)
    return you_dont_have_permission()


@application.route("/admin-create-partner", methods=['GET', 'POST'])
@login_required
def admin_create_partner():
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = PartnerForm()
        cont_name_logo, cont_name_image = f"tmp/partner/partner_{current_user.email}/logo", f"tmp/partner/partner_{current_user.email}/image"
        containerManager.delete_container(cont_name_logo)
        containerManager.delete_container(cont_name_image)
        message, result, filenames2, filenames1 = None, False, [], []
        if request.method == 'POST':
            filenames2, filenames1 = save_images(cont_name_image, request.files, r_img=True, logo=True, cont_logo=cont_name_logo, auto_delete=True)
            message = create_partner({"name": form.name.data, "image": "//".join(filenames2), "info": form.info.data,
                           "preferences": form.preferences.data, "address": form.address.data, "link": form.link.data, "admin_email": current_user.email,
                           "logo": "//".join(filenames1), "socialmedia": form.socialmedia.data})
            if "success" in message:
                filenames1, filenames2 = transport_images(cont_name_logo, f"partner/partner_{message['id']}/logo", filenames1), \
                                         transport_images(cont_name_image, f"partner/partner_{message['id']}/image", filenames2)
                m = edit_partner(message['id'], {"image": "//".join(filenames2), "logo": "//".join(filenames1), "admin_email": current_user.email, "action": "put"})
                containerManager.delete_container(cont_name_image)
                containerManager.delete_container(cont_name_logo)
                result = True
                # filenames1, filenames2 = [], []
                delete_folder(f"partner/partner_{current_user.email}")
                set_other_params()
            message = list(message.values())[-1]
        return get_render_template('form/admin-form-partner.html', title='Добавление партнёра', message=message, form=form,
                               result=result, filenames1=filenames1, filenames2=filenames2, image_len=len(filenames2) + 1)
    return you_dont_have_permission()


@application.route("/admin-edit-partner/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_partner(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = PartnerForm()
        cont_name_logo, cont_name_image = f"tmp/partner/partner_{current_user.email}/logo", f"tmp/partner/partner_{current_user.email}/image"
        partner = edit_partner(id, {"admin_email": current_user.email, "action": "get"})
        message, result, filenames1, filenames2 = None, False, [], []
        if "message" not in partner:
            if request.method == 'POST':
                filenames2, filenames1 = save_images(cont_name_image, request.files, r_img=True, logo=True, cont_logo=cont_name_logo)
                message = edit_partner(id, {"preferences": form.preferences.data, "name": form.name.data,
                                                                       "address": form.address.data, "link": form.link.data, "info": form.info.data,
                                                                       "image": '//'.join(filenames2), "logo": '//'.join(filenames1), "action": "put",
                                                                       "admin_email": current_user.email,
                                                                       "socialmedia": form.socialmedia.data})
                if "success" in message:
                    filenames1, filenames2 = transport_images(cont_name_logo, f"partner/partner_{id}/logo", filenames1), \
                                             transport_images(cont_name_image, f"partner/partner_{id}/image", filenames2)
                    m = edit_partner(id, {"image": '//'.join(filenames2), "action": "put",
                                                                    "admin_email": current_user.email, "logo": '//'.join(filenames1)})
                    result = True
                    set_other_params()
                message = list(message.values())[-1]
            else:
                form.preferences.data = partner["preferences"]
                form.address.data = partner["address"]
                form.name.data = partner["name"]
                form.info.data = partner["info"]
                form.link.data = partner["link"]
                form.socialmedia.data = partner["socialmedia"]
                filenames1 = copy_files(f"partner/partner_{id}/logo", cont_name_logo, partner["logo"].split("//"))
                filenames2 = copy_files(f"partner/partner_{id}/image", cont_name_image, partner["image"].split("//"))
                containerManager.add_container(cont_name_image, filenames2)
                containerManager.add_container(cont_name_logo, filenames1)
        else:
            message = list(partner.values())[-1]
        return get_render_template('form/admin-form-partner.html', title='Редактирование партнёра', message=message,
                               form=form, result=result, flag=False, filenames1=filenames1, filenames2=filenames2, image_len=len(filenames2) + 1)
    return you_dont_have_permission()


@application.route("/admin-delete-partner/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_partner(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result = "", "сотрудник не найден", False
        partner = edit_partner(id, {"admin_email": current_user.email, "action": "get"})
        if "message" not in partner:
            name = "сотрудник " + partner['name']
            if request.method == 'POST':
                message = edit_partner(id, {"admin_email": current_user.email, "action": "delete"})
                if "success" in message:
                    result = True
                    delete_folder(f"partner/partner_{id}")
                    containerManager.delete_container(f"partner_{id}")
                    set_other_params()
                message = list(message.values())[-1]
        return get_render_template('form/admin-form-delete.html', title='Удаление участника', message=message, form=form,
                               result=result, name=name, link_back="/admin-list-partner")
    return you_dont_have_permission()


@application.route("/admin-list-auditlog")
@login_required
def admin_auditlog():
    if check_user():
        return redirect("/login")
    auditlogs = edit_auditlog({"admin_email": current_user.email, "action": "getlist"})
    return get_render_template('list/admin-list-auditlog.html', title='Журнал аудита', auditlogs=auditlogs)


@application.route("/admin-list-feedback")
@login_required
def admin_feedback():
    if check_user():
        return redirect("/login")
    feedbacks = edit_feedback({"admin_email": current_user.email, "action": "getlist"})
    return get_render_template('list/admin-list-feedback.html', title='Отзывы', feedbacks=feedbacks)


@application.route("/view-feedback/<int:id>", methods=['GET', 'POST'])
@login_required
def view_feedback(id):
    if check_user():
        return redirect("/login")
    feedback = edit_feedback({"admin_email": current_user.email, "action": "get", "feedback_id": id})
    if "message" in feedback:
        return page_not_found()
    return get_render_template('feedback.html', title=feedback["heading"], feedback=feedback)


@application.route("/admin-delete-feedback/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_feedback(id):
    if check_user():
        return redirect("/login")
    if current_user.status > 0:
        form = DeleteForm()
        message, name, result = "", "отзыв не найден", False
        feedback = edit_feedback({"admin_email": current_user.email, "action": "get", "feedback_id": id})
        if "message" not in feedback:
            name = "отзыв " + feedback['heading']
            if request.method == 'POST':
                message = edit_feedback({"feedback_id": id, "admin_email": current_user.email, "action": "delete"})
                if "success" in message:
                    delete_folder(f"feedback/feedback_{feedback['id']}")
                    result = True
                message = list(message.values())[0]
                images = feedback["image"]
                for image in images.split("//"):
                    delete_img(image)
        return get_render_template('form/admin-form-delete.html', title='Удаление отзыва', message=message, form=form,
                               result=result, name=name, link_back="/admin-list-feedback")
    return you_dont_have_permission()


@application.route("/write-feedback/<string:code>", methods=['GET', 'POST'])
def write_feedback(code):
    form = FeedbackForm()
    message, result, filenames, preview_text, path = None, False, [], None, f"tmp/feedback/feedback_{code}"
    if request.method == 'POST':
        filenames = save_image_test(request.files, path, code, r_img=False, max_image=5, gif=False, feedback=True)
        text_trans = text_transform(form.text.data, filenames, application.config["UPLOAD_FOLDER"])
        if form.submit.data:
            if text_trans[:5] != "Error":
                message = create_feedback({"email": form.email.data, "fullname": form.fullname.data, "heading": form.heading.data,
                                     "image": "//".join(filenames), "text": form.text.data, "code": form.code.data})
                if "success" in message:
                    filenames = transport_images(filenames, f"feedback/feedback_{message['id']}")
                    m = feedback_edit_image(message['id'], form.code.data, {"image": "//".join(filenames)})
                    result = True
                    message = "Спасибо за отзыв"
                    delete_folder(path)
                else:
                    message = list(message.values())[0]
            else:
                message = text_trans[7:].capitalize()
        elif form.getcode.data:
            create_code(form.email.data)
        elif form.preview.data:
            preview_text = Markup(text_trans)
    else:
        filenames = get_files_from(path)
    page = get_smartpage_usual(6)
    content = get_content_usual(page['id'])
    return get_render_template('write-feedback.html', title="Отзыв", page=page, content=content,
                           result=result, flag=True, message=message, form=form, preview_text=preview_text,
                           filenames=filenames, image_len=len(filenames) + 1,
                           formatting_text_instruction=formatting_text_instruction_usual)


@application.route("/contacts")
def contacts():
    page = get_smartpage_usual(6)
    content, flag_map = get_content_usual(page['id']), False
    flag_map = any([True if cont['type'] == "Map" else flag_map for cont in content])
    return get_render_template('contacts.html', title=page["heading"], page=page, content=content, code=create_random_name(15),
                               flag_map=flag_map, contacts=True)


@application.route("/agro_and_agro-tourism_sector")
def agro_and_agro_tourism_sector():
    page = get_smartpage_usual(2)
    content, flag_map = get_content_usual(page['id']), False
    flag_map = any([True if cont['type'] == "Map" else flag_map for cont in content])
    return get_render_template('agro_and_agro_tourism_sector.html', title=page["heading"], page=page, content=content,
                               flag_map=flag_map)


@application.route("/partners")
def partners():
    page = get_smartpage_usual(3)
    content, flag_map = get_content_usual(page['id']), False
    flag_map = any([True if cont['type'] == "Map" else flag_map for cont in content])
    return get_render_template('partners.html', title=page["heading"], page=page, content=content, flag_map=flag_map)


@application.route("/all_news")
def all_news():
    page = get_smartpage_usual(4)
    content, flag_map = get_content_usual(page['id']), False
    flag_map = any([True if cont['type'] == "Map" else flag_map for cont in content])
    return get_render_template('all_news.html', title=page["heading"], page=page, content=content,
                               flag_map=flag_map)


@application.route("/team")
def team():
    page = get_smartpage_usual(5)
    content, flag_map = get_content_usual(page['id']), False
    flag_map = any([True if cont['type'] == "Map" else flag_map for cont in content])
    return get_render_template('team.html', title=page["heading"], page=page, content=content,
                               flag_map=flag_map)


@application.route("/")
def website_main():
    page = get_smartpage_usual(1)
    content, flag_map = get_content_usual(page['id']), False
    flag_map = any([True if cont['type'] == "Map" else flag_map for cont in content])
    return get_render_template('main-page.html', len=len(get_special_params()["text"]), title=page["heading"], page=page,
                           content=content, flag_map=flag_map)


@application.route("/page/<string:link>")
def page_by_link(link):
    smartpages = get_smartpage_list()
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
    page = get_smartpage_link(link)
    if "message" in page:
        return page_not_found()
    content, flag_map = get_content_usual(page['id']), False
    flag_map = any([True if cont['type'] == "Map" else flag_map for cont in content])
    return get_render_template('generated-page.html', title=page["heading"], page=page, content=content,
                               flag_map=flag_map)


@application.route("/news-page/<string:link>")
def news_page(link):
    news = get_newspage_link(link)
    if "message" in news:
        return page_not_found()
    return get_render_template('news.html', title=news["heading"], news=news)


@application.route("/partner-page/<int:id>")
def partner_page(id):
    partner = get_partner_usual(id)
    if "message" in partner:
        return page_not_found()
    return get_render_template('partner.html', title=partner["name"], partner=partner,
                           social=get_icons_links(partner['socialmedia']))


@application.route("/member-page/<int:id>")
def member_page(id):
    member = get_member_usual(id)
    if "message" in member:
        return page_not_found()
    return get_render_template('member.html', title=member["name"], member=member, social=get_icons_links(member['socialmedia']))


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
