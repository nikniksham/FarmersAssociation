import datetime
from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.user import User
from data.smartpage import Smartpage
from data.content import Content
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
    def get(self, email, password, smartpage_id):
        admin, session = check_admin_status(email, password)
        smartpage, session = find_by_id(smartpage_id, session)
        return jsonify(smartpage.to_dict(only=('id', 'heading', 'image', 'created_date', 'author_id')))

    def delete(self, email, password, smartpage_id):
        admin, session = check_admin_status(email, password)
        smartpage, session = find_by_id(smartpage_id, session)
        heading = smartpage.heading
        session.delete(smartpage)
        session.commit()
        add_auditlog("Удаление", f"{admin.name} {admin.surname} удаляет страницу: {heading}", admin,
                     datetime.datetime.now())
        return jsonify({"success": f"Страница {heading} успешно удалена"})

    def put(self, email, password, smartpage_id):
        admin, session = check_admin_status(email, password)
        smartpage, session = find_by_id(smartpage_id, session)
        args, count = parser_smartpage.parse_args(), 0
        keys = list(filter(lambda key: args[key] is not None, list(args.keys())))
        page_dict = smartpage.to_dict(only=('id', 'heading', 'image', 'created_date', 'author_id'))
        for key in list(args.keys()):
            if args[key] is not None:
                count += 1
                if key == 'id':
                    if session.query(Smartpage).filter(Smartpage.id == args["id"]).first():
                        raise_error("Этот id уже занят")
                    smartpage.id = args['id']
                if key == 'image':
                    smartpage.image = args['image']
                if key == 'heading':
                    smartpage.heading = args["heading"]
        if count == 0:
            return raise_error("Пустой запрос")
        page_dict_2 = smartpage.to_dict(only=('id', 'heading', 'image', 'created_date', 'author_id'))
        list_chang = [f'изменяет {key} с {page_dict[key]} на {page_dict_2[key]}' for key in keys]
        session.commit()
        add_auditlog("Изменение", f"{admin.name} {admin.surname} изменяет страницу {smartpage.heading}: {', '.join(list_chang)}", admin,
                     datetime.datetime.now())
        return jsonify({"success": f"Страница {smartpage.heading} успешно изменена"})


class SmartpageListRecourse(Resource):
    def get(self):
        session = db_session.create_session()
        smartpages = session.query(Smartpage).all()
        return jsonify([item.to_dict(only=('id', 'heading', 'image', 'created_date', 'author_id')) for item in smartpages])


class CreateSmartpageResource(Resource):
    def post(self, email, password):
        admin, session = check_admin_status(email, password)
        args = parser_smartpage.parse_args()
        if not all(args[key] is not None for key in ['heading']):
            raise_error('Пропущены некоторые аргументы, необходимые для создания страницы')
        new_smartpage = Smartpage()
        new_smartpage.heading = args["heading"]
        new_smartpage.image = args['image'] if args['image'] is not None else "standard.png"
        new_smartpage.created_date = datetime.datetime.now()
        if args["id"] is not None:
            if session.query(Smartpage).get(args["id"]) is not None:
                raise_error("Этот id уже занят")
            new_smartpage.id = args["id"]
        admin.smartpage.append(new_smartpage)
        session.merge(admin)
        session.commit()
        add_auditlog("Создание",
                     f"{admin.name} {admin.surname} создаёт страницу {new_smartpage.heading}: {new_smartpage.to_dict(only=('id', 'heading', 'image', 'created_date', 'author_id'))}",
                     admin, datetime.datetime.now())
        return jsonify({'success': f'Страница {new_smartpage.heading} создана'})
