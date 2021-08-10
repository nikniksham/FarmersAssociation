import datetime
from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.user import User
from data.API.PhoneAPI.parser_phone import parser_phone
from data.phone import Phone


def raise_error(error):
    abort(400, message=error)


def check_admin_status(phone, password, need_status=1):
    admin, session = check_admin(phone, password)
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
    phone = session.query(Phone).get(id)
    if not phone:
        raise_error(f"Номер телефона не найден")
    return phone, session


class PhoneListRecourse(Resource):
    def get(self):
        session = db_session.create_session()
        phones = session.query(Phone).all()
        return jsonify([item.to_dict(only=('id', 'number')) for item in phones])


class AdminResourcePhone(Resource):
    def get(self, email, password, phone_id):
        admin, session = check_admin_status(email, password)
        phone, session = find_by_id(phone_id, session)
        return jsonify(phone.to_dict(only=('id', 'number')))

    def delete(self, email, password, phone_id):
        admin, session = check_admin_status(email, password, 2)
        phone, session = find_by_id(phone_id, session)
        number = phone.number
        session.delete(phone)
        session.commit()
        add_auditlog("Удаление", f"Админ {admin.name} {admin.surname} удаляет номер телефона {number}", admin,
                     datetime.datetime.now())
        return jsonify({"success": f"Номер телефона {number} успешно удалён"})

    def put(self, email, password, phone_id):
        admin, session = check_admin_status(email, password, 2)
        phone, session = find_by_id(phone_id, session)
        args, count = parser_phone.parse_args(), 0
        phone_dict = phone.to_dict(only=('id', 'number'))
        keys = list(filter(lambda key: args[key] is not None and key in phone_dict and args[key] != phone_dict[key], args.keys()))
        for key in args.keys():
            if args[key] is not None and args[key] != phone_dict[key]:
                count += 1
                if key == 'number':
                    phone.number = args["number"]
        if count == 0:
            return raise_error("Пустой запрос")
        phone_dict_2 = phone.to_dict(only=('id', 'number'))
        list_chang = [f'изменяет {key} с {phone_dict[key]} на {phone_dict_2[key]}' for key in keys]
        session.commit()
        add_auditlog("Изменение", f"Админ {admin.name} {admin.surname} изменяет номер телефона {phone.number}:"
                                  f" {', '.join(list_chang)}", admin, datetime.datetime.now())
        return jsonify({"success": f"Номер телефона {phone.number} успешно изменён"})


class CreatePhoneResource(Resource):
    def post(self, email, password):
        admin, session = check_admin_status(email, password)
        args = parser_phone.parse_args()
        if not all(args[key] is not None for key in ['number']):
            raise_error('Пропущены некоторые аргументы, необходимые для добавления нового номера телефона')
        if session.query(Phone).filter(Phone.number == args['number']).first():
            raise_error("Этот номер телефона уже существует")
        new_phone = Phone()
        new_phone.number = args["number"]
        session.add(new_phone)
        session.commit()
        add_auditlog("Создание", f"Админ {admin.name} {admin.surname} добавляет номер телефона {new_phone.number}: {new_phone.to_dict(only=('id', 'number'))}",
                     admin, datetime.datetime.now())
        return jsonify({'success': f'Номер телефона {new_phone.number} создан'})
