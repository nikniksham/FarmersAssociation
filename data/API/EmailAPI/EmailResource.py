import datetime
from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.user import User
from data.API.EmailAPI.parser_email import parser_email
from data.email import Email


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
    email = session.query(Email).get(id)
    if not email:
        raise_error(f"Электронная почта не найдена")
    return email, session


class EmailListRecourse(Resource):
    def get(self):
        session = db_session.create_session()
        emails = session.query(Email).all()
        return jsonify([item.to_dict(only=('id', 'email_address')) for item in emails])


class AdminResourceEmail(Resource):
    def get(self, email, password, email_id):
        admin, session = check_admin_status(email, password)
        email, session = find_by_id(email_id, session)
        return jsonify(email.to_dict(only=('id', 'email_address')))

    def delete(self, email, password, email_id):
        admin, session = check_admin_status(email, password, 2)
        email, session = find_by_id(email_id, session)
        email_address = email.email_address
        session.delete(email)
        session.commit()
        add_auditlog("Удаление", f"Админ {admin.name} {admin.surname} удаляет электронную почту {email_address}", admin,
                     datetime.datetime.now())
        return jsonify({"success": f"Электроная почта {email_address} успешно удалена"})

    def put(self, email, password, email_id):
        admin, session = check_admin_status(email, password, 2)
        email, session = find_by_id(email_id, session)
        args, count = parser_email.parse_args(), 0
        email_dict = email.to_dict(only=('id', 'email_address'))
        keys = list(filter(lambda key: args[key] is not None and key in email_dict and args[key] != email_dict[key], args.keys()))
        for key in args.keys():
            if args[key] is not None and args[key] != email_dict[key]:
                count += 1
                if key == 'email_address':
                    email.email_address = args["email_address"]
        if count == 0:
            return raise_error("Пустой запрос")
        email_dict_2 = email.to_dict(only=('id', 'email_address'))
        list_chang = [f'изменяет {key} с {email_dict[key]} на {email_dict_2[key]}' for key in keys]
        session.commit()
        add_auditlog("Изменение", f"Админ {admin.name} {admin.surname} изменяет электронную почту {email.email_address}:"
                                  f" {', '.join(list_chang)}", admin, datetime.datetime.now())
        return jsonify({"success": f"Электронная почта {email.email_address} успешно изменена"})


class CreateEmailResource(Resource):
    def post(self, email, password):
        admin, session = check_admin_status(email, password)
        args = parser_email.parse_args()
        if not all(args[key] is not None for key in ['email_address']):
            raise_error('Пропущены некоторые аргументы, необходимые для создания нового адреса электронной почты')
        if session.query(Email).filter(Email.email_address == args['email_address']).first():
            raise_error("Этот адрес электронной почты уже существует")
        new_email = Email()
        new_email.email_address = args["email_address"]
        session.add(new_email)
        session.commit()
        add_auditlog("Создание", f"Админ {admin.name} {admin.surname} добавляет почтовый адрес {new_email.email_address}: {new_email.to_dict(only=('id', 'email_address'))}",
                     admin, datetime.datetime.now())
        return jsonify({'success': f'Почтовый адрес {new_email.email_address} создан'})
