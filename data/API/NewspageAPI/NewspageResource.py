import datetime
from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.user import User
from data.newspage import Newspage
from data.API.NewspageAPI.parser_newspage import parser_newspage
from main import mini_text, text_transform

path = ""


def set_path(new_path):
    global path
    path = new_path


def raise_error(error):
    abort(400, message=error)


def trans_link(text):
    trans = {"а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo", "ж": "zh", "з": "z", "и": "i",
             "й": "j", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
             "у": "u", "ф": "f", "х": "x", "ц": "cz", "ч": "ch", "ш": "sh", "щ": "sch", "ы": "y", "э": "e", "ю": "yu",
             "я": "ya", " ": "_"}
    link, keys, isup = "", list(trans.keys()), False
    for letter in text:
        isup = letter.isupper()
        if letter.isdigit():
            link += letter
        elif letter.lower() in keys:
            link += trans[letter.lower()].upper() if isup else trans[letter]
        elif letter.lower() in trans:
            link += letter
    return link


def check_admin_status(email, password, need_status=1):
    admin, session = check_admin(email, password)
    if admin.status < need_status:
        raise_error("У вас недостаточно прав для этого")
    return admin, session


def check_admin(email, password):
    session = db_session.create_session()
    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise_error(f"Админ {email} не найден")
    if not user.check_password(password):
        raise_error("Неправильный пароль")
    return user, session


def find_by_id(id, session):
    newspage = session.query(Newspage).get(id)
    if not newspage:
        raise_error(f"Страница не найдена")
    return newspage, session


class NewspageResource(Resource):
    def get(self, email, password, newspage_id):
        admin, session = check_admin_status(email, password)
        newspage, session = find_by_id(newspage_id, session)
        news_dict = newspage.to_dict(only=('id', 'heading', 'text', 'link', 'image', 'tags', 'created_date', 'author_id'))
        news_dict["mini_text"] = mini_text(newspage.text)
        news_dict["text_render"] = text_transform(newspage.text, newspage.image.split("//"), path)
        return jsonify(news_dict)

    def delete(self, email, password, newspage_id):
        admin, session = check_admin_status(email, password)
        newspage, session = find_by_id(newspage_id, session)
        heading = newspage.heading
        session.delete(newspage)
        session.commit()
        add_auditlog("Удаление", f"{admin.name} {admin.surname} удаляет новостную страницу: {heading}", admin,
                     datetime.datetime.now())
        return jsonify({"success": f"Новостная страница {heading} успешно удалена"})

    def put(self, email, password, newspage_id):
        admin, session = check_admin_status(email, password)
        newspage, session = find_by_id(newspage_id, session)
        args, count = parser_newspage.parse_args(), 0
        page_dict = newspage.to_dict(only=('heading', 'text', 'image', 'tags'))
        keys = list(filter(lambda key: args[key] is not None and args[key] != page_dict[key] and key in list(page_dict.keys()), list(args.keys())))
        for key in list(args.keys()):
            if args[key] is not None and args[key] != page_dict[key]:
                count += 1
                if key == 'image':
                    newspage.image = args['image']
                if key == 'heading':
                    newspage.heading = args["heading"]
                    link, count = trans_link(args["heading"]), 0
                    while session.query(Newspage).filter(Newspage.link == link).first() is not None:
                        if link[-len(str(count)):] == str(count):
                            link = link[:-len(str(count))] + str(count + 1)
                            count += 1
                        else:
                            link += str(count)
                    newspage.link = link
                if key == "text":
                    newspage.text = args["text"]
                if key == "tags":
                    newspage.tags = args["tags"]
        if count == 0:
            return raise_error("Пустой запрос")
        page_dict_2 = newspage.to_dict(only=('heading', 'text', 'image', 'tags'))
        list_chang = [f'изменяет {key} с {page_dict[key]} на {page_dict_2[key]}' if key != "image" else "изменяет изображения" for key in keys]
        session.commit()
        add_auditlog("Изменение",
                     f"{admin.name} {admin.surname} изменяет новостную страницу {newspage.heading}: {', '.join(list_chang)}",
                     admin, datetime.datetime.now())
        return jsonify({"success": f"Новостная страница {newspage.heading} успешно изменена"})


class NewspageResourceUsual(Resource):
    def get(self, newspage_id):
        session = db_session.create_session()
        newspage, session = find_by_id(newspage_id, session)
        news_dict = newspage.to_dict(only=('id', 'heading', 'text', 'link', 'image', 'tags', 'created_date'))
        news_dict["mini_text"] = mini_text(newspage.text)
        news_dict["text_render"] = text_transform(newspage.text, newspage.image.split("//"), path)
        return jsonify(news_dict)


class NewspageResourceLink(Resource):
    def get(self, link):
        session = db_session.create_session()
        newspage = session.query(Newspage).filter(Newspage.link == link).first()
        if newspage:
            news_dict = newspage.to_dict(only=('id', 'heading', 'text', 'link', 'image', 'tags', 'created_date'))
            news_dict["mini_text"] = mini_text(newspage.text)
            news_dict["text_render"] = text_transform(newspage.text, newspage.image.split("//"), path)
            return jsonify(news_dict)
        raise_error("Новость не найдена")


class NewspageListRecourseId(Resource):
    def get(self, start_id, end_id):
        session = db_session.create_session()
        newspages = session.query(Newspage).order_by(Newspage.created_date)[::-1]
        if start_id > len(newspages):
            return jsonify([])
        if end_id > len(newspages):
            end_id = len(newspages)
        newspages, news_list = newspages[start_id:end_id], []
        for item in newspages:
            news_dict = item.to_dict(only=('id', 'heading', 'text', 'link', 'image', 'tags', 'created_date'))
            news_dict["mini_text"] = mini_text(item.text)
            news_dict["text_render"] = text_transform(item.text, item.image.split("//"), path)
            news_list.append(news_dict)
        return jsonify(news_list)


class NewspageListRecourse(Resource):
    def get(self):
        session = db_session.create_session()
        newspages, news_list = session.query(Newspage).order_by(Newspage.created_date)[::-1], []
        for item in newspages:
            news_dict = item.to_dict(only=('id', 'heading', 'text', 'link', 'image', 'tags', 'created_date'))
            news_dict["mini_text"] = mini_text(item.text)
            news_dict["text_render"] = text_transform(item.text, item.image.split("//"), path)
            news_list.append(news_dict)
        return jsonify(news_list)


class CreateNewspageResource(Resource):
    def post(self, email, password):
        admin, session = check_admin_status(email, password)
        args = parser_newspage.parse_args()
        if not all(args[key] is not None for key in ['heading', 'text', 'tags']):
            raise_error('Пропущены некоторые аргументы, необходимые для создания новостной страницы')
        new_newspage = Newspage()
        new_newspage.heading = args["heading"]
        new_newspage.text = args["text"]
        link, count = args["link"] if args["link"] is not None else trans_link(args["heading"]), 0
        while session.query(Newspage).filter(Newspage.link == link).first() is not None:
            if link[-len(str(count)):] == str(count):
                link = link[:-len(str(count))] + str(count + 1)
                count += 1
            else:
                link += str(count)
        new_newspage.link = link
        new_newspage.image = args['image']
        new_newspage.tags = args['tags']
        new_newspage.created_date = datetime.datetime.now()
        if args["id"] is not None:
            if session.query(Newspage).get(args["id"]) is not None:
                raise_error("Этот id уже занят")
            new_newspage.id = args["id"]
        admin.newspage.append(new_newspage)
        session.merge(admin)
        session.commit()
        params_dict = new_newspage.to_dict(only=('id', 'heading', 'text', 'link', 'tags', 'created_date', 'author_id'))
        params_dict["image"] = f'кол-во изображений: {len(args["image"].split("//"))}'
        add_auditlog("Создание",
                     f"{admin.name} {admin.surname} создаёт новостную страницу {new_newspage.heading}: {params_dict}",
                     admin, datetime.datetime.now())
        return jsonify({'success': f'Новостная страница {new_newspage.heading} создана'})
