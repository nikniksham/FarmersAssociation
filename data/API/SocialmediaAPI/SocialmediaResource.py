import datetime
from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.user import User
from data.API.SocialmediaAPI.parser_socialmedia import parser_socialmedia
from data.socialmedia import Socialmedia


def raise_error(error):
    abort(400, message=error)


def check_admin_status(socialmedia, password, need_status=1):
    admin, session = check_admin(socialmedia, password)
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
    socialmedia = session.query(Socialmedia).get(id)
    if not socialmedia:
        raise_error(f"Ссылка на соцсеть не найдена")
    return socialmedia, session


class SocialmediaListRecourse(Resource):
    def get(self):
        session = db_session.create_session()
        socialmedias = session.query(Socialmedia).order_by(Socialmedia.icon_type).all()
        return jsonify([item.to_dict(only=('id', 'icon_type', 'link')) for item in socialmedias])


class AdminResourceSocialmedia(Resource):
    def put(self, socialmedia_id):
        args, count = parser_socialmedia.parse_args(), 0
        if not all(args[key] is not None for key in ['admin_email', 'action', 'admin_password']):
            raise_error('Пропущены некоторые важные аргументы')
        admin, session = check_admin_status(args['admin_email'], args["admin_password"])
        socialmedia, session = find_by_id(socialmedia_id, session)
        if args['action'] == "get":
            return jsonify(socialmedia.to_dict(only=('id', 'icon_type', 'link')))
        elif args['action'] == 'delete':
            session.delete(socialmedia)
            session.commit()
            add_auditlog("Удаление", f"Админ {admin.name} {admin.surname} удаляет ссылку на соцсеть {socialmedia.link}",
                         admin, datetime.datetime.now())
            return jsonify({"success": f"Ссылка на соцсеть {socialmedia.link} успешно удалена"})
        elif args['action'] == 'put':
            args, count = parser_socialmedia.parse_args(), 0
            socialmedia_dict = socialmedia.to_dict(only=('icon_type', 'link'))
            keys = list(filter(lambda key: args[key] is not None and key in socialmedia_dict and args[key] != socialmedia_dict[key], args.keys()))
            for key in keys:
                count += 1
                if key == 'icon_type':
                    socialmedia.icon_type = args["icon_type"]
                if key == 'link':
                    if session.query(Socialmedia).filter(Socialmedia.link == args['link']).first():
                        raise_error("Эта ссылка уже существует")
                    socialmedia.link = args["link"]
            if count == 0:
                return raise_error("Пустой запрос")
            socialmedia_dict_2 = socialmedia.to_dict(only=('icon_type', "link"))
            list_chang = [f'изменяет {key} с {socialmedia_dict[key]} на {socialmedia_dict_2[key]}' for key in keys]
            session.commit()
            add_auditlog("Изменение", f"Админ {admin.name} {admin.surname} изменяет ссылку на соцсеть {socialmedia.link}:"
                                      f" {', '.join(list_chang)}", admin, datetime.datetime.now())
            return jsonify({"success": f"Ссылка на соцсеть {socialmedia.link} успешно изменена"})
        raise_error("Неизвестный метод")


class CreateSocialmediaResource(Resource):
    def post(self):
        args = parser_socialmedia.parse_args()
        if not all(args[key] is not None for key in ['icon_type', "link", "admin_email", 'admin_password']):
            raise_error('Пропущены некоторые аргументы, необходимые для добавления новой ссылки на соцсеть')
        admin, session = check_admin_status(args['admin_email'], args["admin_password"])
        if session.query(Socialmedia).filter(Socialmedia.link == args['link']).first():
            raise_error("Эта ссылка уже существует")
        new_socialmedia = Socialmedia()
        new_socialmedia.icon_type = args["icon_type"]
        new_socialmedia.link = args["link"]
        session.add(new_socialmedia)
        session.commit()
        add_auditlog("Создание", f"Админ {admin.name} {admin.surname} добавляет ссылку на соцсеть {new_socialmedia.link}: "
                                 f"{new_socialmedia.to_dict(only=('id', 'icon_type', 'link'))}", admin, datetime.datetime.now())
        return jsonify({'success': f'Ссылка на соцсеть {new_socialmedia.link} создана'})
