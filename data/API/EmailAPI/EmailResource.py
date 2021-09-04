import datetime
from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.user import User
from data.API.EmailAPI.parser_email import parser_email
from data.email import Email
from data.API.main_file import raise_error, check_admin_status


def check_admin(email, password):
    session = db_session.create_session()
    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise_error(f"Админ {email} не найден", session)
    if not user.check_password(password):
        raise_error("Неправильный пароль", session)
    return user, session


def find_by_id(id, session):
    email = session.query(Email).get(id)
    if not email:
        raise_error(f"Электронная почта не найдена", session)
    return email, session


class EmailListRecourse(Resource):
    def get(self):
        session = db_session.create_session()
        emails = session.query(Email).all()
        session.close()
        return jsonify([item.to_dict(only=('id', 'email_address')) for item in emails])


class AdminResourceEmail(Resource):
    def put(self, email_id):
        args, count = parser_email.parse_args(), 0
        if not all(args[key] is not None for key in ['admin_email', 'action', 'admin_password']):
            raise_error('Пропущены некоторые важные аргументы')
        admin, session = check_admin_status(args['admin_email'], args["admin_password"])
        email, session = find_by_id(email_id, session)
        if args['action'] == "get":
            session.close()
            return jsonify(email.to_dict(only=('id', 'email_address')))
        elif args['action'] == 'delete':
            session.delete(email)
            session.commit()
            session.close()
            add_auditlog("Удаление", f"Админ {admin.name} {admin.surname} удаляет электронную почту {email.email_address}",
                         admin, datetime.datetime.now())
            return jsonify({"success": f"Электроная почта {email.email_address} успешно удалена"})
        elif args['action'] == 'put':
            email, session = find_by_id(email_id, session)
            email_dict = email.to_dict(only=('email_address',))
            keys = list(filter(lambda key: args[key] is not None and key in email_dict and args[key] != email_dict[key], args.keys()))
            for key in keys:
                count += 1
                if key == 'email_address':
                    if session.query(Email).filter(Email.email_address == args['email_address']).first():
                        raise_error("Этот адрес электронной почты уже существует", session)
                    email.email_address = args["email_address"]
            if count == 0:
                return raise_error("Пустой запрос")
            email_dict_2 = email.to_dict(only=('email_address',))
            list_chang = [f'изменяет {key} с {email_dict[key]} на {email_dict_2[key]}' for key in keys]
            session.commit()
            session.close()
            add_auditlog("Изменение", f"Админ {admin.name} {admin.surname} изменяет электронную почту {email.email_address}:"
                                      f" {', '.join(list_chang)}", admin, datetime.datetime.now())
            return jsonify({"success": f"Электронная почта {email.email_address} успешно изменена"})
        raise_error("Неизвестный метод", session)


class CreateEmailResource(Resource):
    def post(self):
        args = parser_email.parse_args()
        if not all(args[key] is not None for key in ['email_address', 'admin_email', 'admin_password']):
            raise_error('Пропущены некоторые аргументы, необходимые для создания нового адреса электронной почты')
        admin, session = check_admin_status(args['admin_email'], args["admin_password"])
        if session.query(Email).filter(Email.email_address == args['email_address']).first():
            raise_error("Этот адрес электронной почты уже существует", session)
        new_email = Email()
        new_email.email_address = args["email_address"]
        session.add(new_email)
        session.commit()
        session.close()
        add_auditlog("Создание", f"Админ {admin.name} {admin.surname} добавляет почтовый адрес {new_email.email_address}: {new_email.to_dict(only=('id', 'email_address'))}",
                     admin, datetime.datetime.now())
        return jsonify({'success': f'Почтовый адрес {new_email.email_address} создан'})
