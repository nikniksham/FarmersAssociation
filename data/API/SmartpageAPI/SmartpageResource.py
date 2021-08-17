import datetime
from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.user import User
from data.smartpage import Smartpage
from data.content import Content
from data.API.NewspageAPI.NewspageResource import trans_link
from data.API.SmartpageAPI.parser_smartpage import parser_smartpage


def raise_error(error):
    abort(400, message=error)


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
    smartpage = session.query(Smartpage).get(id)
    if not smartpage:
        raise_error(f"Страница не найдена")
    return smartpage, session


class SmartpageResource(Resource):
    def put(self, smartpage_id):
        args, count = parser_smartpage.parse_args(), 0
        if not all(args[key] is not None for key in ['admin_email', 'action', 'admin_password']):
            raise_error('Пропущены некоторые важные аргументы')
        admin, session = check_admin_status(args['admin_email'], args["admin_password"])
        smartpage, session = find_by_id(smartpage_id, session)
        if args['action'] == "get":
            return jsonify(smartpage.to_dict(only=('id', 'link', 'heading', 'image', 'created_date', 'author_id')))
        elif args['action'] == 'delete':
            if smartpage.id < 7:
                raise_error("У вас недостаточно прав для этого")
            contentlist = session.query(Content).filter(Content.smartpage_id == smartpage.id).all()
            for content in contentlist:
                add_auditlog("Удаление", f"{admin.name} {admin.surname} удаляет блок контента на позиции: {content.position}, с типом данных: {content.type}",
                             admin, datetime.datetime.now())
                session.delete(content)
            heading = smartpage.heading
            session.delete(smartpage)
            session.commit()
            add_auditlog("Удаление", f"{admin.name} {admin.surname} удаляет страницу: {heading}", admin, datetime.datetime.now())
            return jsonify({"success": f"Страница {heading} успешно удалена"})
        elif args['action'] == 'put':
            page_dict = smartpage.to_dict(only=('heading', 'image', 'created_date'))
            keys = list(filter(lambda key: args[key] is not None and key in page_dict.keys() and args[key] != page_dict[key], list(args.keys())))
            for key in keys:
                count += 1
                if key == 'image':
                    smartpage.image = args['image']
                if key == 'heading':
                    if session.query(Smartpage).filter(Smartpage.heading == args["heading"]).first() is not None:
                        raise_error("Этот заголовок уже занят")
                    smartpage.heading = args["heading"]
                    link, count = trans_link(args["heading"]), 0
                    while session.query(Smartpage).filter(Smartpage.link == link).first() is not None:
                        if link[-len(str(count)):] == str(count):
                            link = link[:-len(str(count))] + str(count + 1)
                            count += 1
                        else:
                            link += str(count)
                    smartpage.link = link
            if count == 0:
                return raise_error("Пустой запрос")
            page_dict_2 = smartpage.to_dict(only=('heading', 'image', 'created_date', 'author_id'))
            list_chang = [f'изменяет {key} с {page_dict[key]} на {page_dict_2[key]}' if key != "image" else "изменяет изображения" for key in keys]
            session.commit()
            add_auditlog("Изменение", f"{admin.name} {admin.surname} изменяет страницу {smartpage.heading}: {', '.join(list_chang)}",
                         admin, datetime.datetime.now())
            return jsonify({"success": f"Страница {smartpage.heading} успешно изменена"})
        raise_error("Неизвестный метод")


class SmartpageRecourseUsual(Resource):
    def get(self, smartpage_id):
        session = db_session.create_session()
        smartpage, session = find_by_id(smartpage_id, session)
        return jsonify(smartpage.to_dict(only=('id', 'link', 'heading', 'image', 'created_date', 'author_id')))


class SmartpageRecourseLink(Resource):
    def get(self, link):
        session = db_session.create_session()
        smartpage = session.query(Smartpage).filter(Smartpage.link == link).first()
        if smartpage:
            return jsonify(smartpage.to_dict(only=('id', 'link', 'heading', 'image', 'created_date', 'author_id')))
        raise_error("Страница не найдена")


class SmartpageListRecourse(Resource):
    def get(self):
        session = db_session.create_session()
        smartpages = session.query(Smartpage).all()
        return jsonify(
            [item.to_dict(only=('id', 'link', 'heading', 'image', 'created_date', 'author_id')) for item in smartpages])


class CreateSmartpageResource(Resource):
    def post(self):
        args = parser_smartpage.parse_args()
        if not all(args[key] is not None for key in ['heading', 'admin_email', 'admin_password']):
            raise_error('Пропущены некоторые аргументы, необходимые для создания страницы')
        admin, session = check_admin_status(args['admin_email'], args["admin_password"])
        if session.query(Smartpage).filter(Smartpage.heading == args["heading"]).first() is not None:
            raise_error("Этот заголовок уже занят")
        new_smartpage = Smartpage()
        new_smartpage.heading = args["heading"]
        link, count = trans_link(args["heading"]), 0
        while session.query(Smartpage).filter(Smartpage.link == link).first() is not None:
            if link[-len(str(count)):] == str(count):
                link = link[:-len(str(count))] + str(count + 1)
                count += 1
            else:
                link += str(count)
        new_smartpage.link = link
        new_smartpage.image = args['image'] if args['image'] is not None else "standard.png"
        new_smartpage.created_date = datetime.datetime.now()
        if args["id"] is not None:
            if session.query(Smartpage).get(args["id"]) is not None:
                raise_error("Этот id уже занят")
            new_smartpage.id = args["id"]
        admin.smartpage.append(new_smartpage)
        session.merge(admin)
        session.commit()
        params_dict = new_smartpage.to_dict(only=('id', 'link', 'heading', 'image', 'created_date', 'author_id'))
        params_dict["image"] = f'кол-во изображений: {len(args["image"].split("//"))}'
        add_auditlog("Создание",
                     f"{admin.name} {admin.surname} создаёт страницу {new_smartpage.heading}: {params_dict}",
                     admin, datetime.datetime.now())
        return jsonify({'success': f'Страница {new_smartpage.heading} создана', "id": new_smartpage.id})
