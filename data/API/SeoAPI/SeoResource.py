import datetime
from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.user import User
from data.API.SeoAPI.parser_seo import parser_seo
from data.seo import Seo
from main import password_manager


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
    seo = session.query(Seo).get(id)
    if not seo:
        raise_error(f"Seo настройка не найдена")
    return seo, session


class SeoGetRecourse(Resource):
    def get(self, seo_id):
        session = db_session.create_session()
        seo, session = find_by_id(seo_id, session)
        return jsonify(seo.to_dict(only=('id', 'title', 'description', 'tags')))


class AdminResourceSeo(Resource):
    def put(self, seo_id):
        args, count = parser_seo.parse_args(), 0
        if not all(args[key] is not None for key in ['admin_email', 'action']):
            raise_error('Пропущены некоторые важные аргументы')
        admin, session = check_admin_status(args["admin_email"], password_manager.get_password(args["admin_email"]))
        seo, session = find_by_id(seo_id, session)
        if args['action'] == "get":
            return jsonify(seo.to_dict(only=('id', 'title', 'description', 'tags')))
        elif args['action'] == 'put':
            seo_dict = seo.to_dict(only=('id', 'title', 'description', 'tags'))
            keys = list(filter(lambda key: args[key] is not None and key in seo_dict and args[key] != seo_dict[key], args.keys()))
            for key in keys:
                count += 1
                if key == 'title':
                    seo.title = args["title"]
                if key == 'description':
                    seo.description = args["description"]
                if key == 'tags':
                    seo.tags = args["tags"]
            if count == 0:
                return raise_error("Пустой запрос")
            seo_dict_2 = seo.to_dict(only=('id', 'title', 'description', 'tags'))
            list_chang = [f'изменяет {key} с {seo_dict[key]} на {seo_dict_2[key]}' for key in keys]
            session.commit()
            add_auditlog("Изменение",
                         f"Админ {admin.name} {admin.surname} изменяет настройку seo: {', '.join(list_chang)}",
                         admin, datetime.datetime.now())
            return jsonify({"success": f"Seo настройка успешно изменена"})
