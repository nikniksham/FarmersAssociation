import datetime
from flask import jsonify
from flask_restful import Resource
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.API.PhoneAPI.parser_phone import parser_phone
from data.phone import Phone
from data.API.main_file import raise_error, check_admin_status


def find_by_id(id, session):
    phone = session.query(Phone).get(id)
    if not phone:
        raise_error(f"Номер телефона не найден", session)
    return phone, session


class PhoneListRecourse(Resource):
    def get(self):
        session = db_session.create_session()
        phones = session.query(Phone).all()
        session.close()
        return jsonify([item.to_dict(only=('id', 'number')) for item in phones])


class AdminResourcePhone(Resource):
    def put(self, phone_id):
        args, count = parser_phone.parse_args(), 0
        if not all(args[key] is not None for key in ['admin_email', 'action', 'admin_password']):
            raise_error('Пропущены некоторые важные аргументы')
        admin, session = check_admin_status(args['admin_email'], args["admin_password"])
        phone, session = find_by_id(phone_id, session)
        if args['action'] == "get":
            session.close()
            return jsonify(phone.to_dict(only=('id', 'number')))
        elif args['action'] == 'delete':
            session.delete(phone)
            session.commit()
            add_auditlog("Удаление", f"Админ {admin.name} {admin.surname} удаляет номер телефона {phone.number}", admin,
                         datetime.datetime.now())
            session.close()
            return jsonify({"success": f"Номер телефона {phone.number} успешно удалён"})
        elif args['action'] == 'put':
            args, count = parser_phone.parse_args(), 0
            phone_dict = phone.to_dict(only=('number',))
            keys = list(filter(lambda key: args[key] is not None and key in phone_dict and args[key] != phone_dict[key], args.keys()))
            for key in keys:
                count += 1
                if key == 'number':
                    if session.query(Phone).filter(Phone.number == args['number']).first():
                        raise_error("Этот номер телефона уже существует", session)
                    phone.number = args["number"]
            if count == 0:
                return raise_error("Пустой запрос", session)
            phone_dict_2 = phone.to_dict(only=('number',))
            list_chang = [f'изменяет {key} с {phone_dict[key]} на {phone_dict_2[key]}' for key in keys]
            session.commit()
            add_auditlog("Изменение", f"Админ {admin.name} {admin.surname} изменяет номер телефона {phone.number}:"
                                      f" {', '.join(list_chang)}", admin, datetime.datetime.now())
            session.close()
            return jsonify({"success": f"Номер телефона {phone.number} успешно изменён"})
        raise_error("Неизвестный метод", session)


class CreatePhoneResource(Resource):
    def post(self):
        args = parser_phone.parse_args()
        if not all(args[key] is not None for key in ['number', 'admin_email', 'admin_password']):
            raise_error('Пропущены некоторые аргументы, необходимые для добавления нового номера телефона')
        admin, session = check_admin_status(args['admin_email'], args["admin_password"])
        print(admin)
        if session.query(Phone).filter(Phone.number == args['number']).first():
            raise_error("Этот номер телефона уже существует", session)
        new_phone = Phone()
        new_phone.number = args["number"]
        session.add(new_phone)
        session.commit()
        print(admin)
        add_auditlog("Создание", f"Админ {admin.name} {admin.surname} добавляет номер телефона {new_phone.number}: {new_phone.to_dict(only=('id', 'number'))}",
                     admin, datetime.datetime.now())
        session.close()
        return jsonify({'success': f'Номер телефона {new_phone.number} создан'})
