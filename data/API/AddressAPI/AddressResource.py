import datetime
from flask import jsonify
from flask_restful import Resource
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.API.AddressAPI.parser_address import parser_address
from data.address import Address
from data.API.main_file import raise_error, check_admin_status


def find_by_id(id, session):
    address = session.query(Address).get(id)
    if not address:
        raise_error(f"Адрес не найден", session)
    return address, session


class AddressListRecourse(Resource):
    def get(self):
        session = db_session.create_session()
        addresss = session.query(Address).all()
        session.close()
        return jsonify([item.to_dict(only=('id', 'name', 'place')) for item in addresss])


class AdminResourceAddress(Resource):
    def put(self, address_id):
        args, count = parser_address.parse_args(), 0
        if not all(args[key] is not None for key in ['admin_email', 'action', 'admin_password']):
            raise_error('Пропущены некоторые важные аргументы')
        admin, session = check_admin_status(args["admin_email"], args["admin_password"])
        address, session = find_by_id(address_id, session)
        if args['action'] == "get":
            session.close()
            return jsonify(address.to_dict(only=('id', 'name', 'place')))
        elif args['action'] == 'put':
            address_dict = address.to_dict(only=('place',))
            keys = list(filter(lambda key: args[key] is not None and key in address_dict and args[key] != address_dict[key], args.keys()))
            for key in keys:
                count += 1
                if key == 'place':
                    address.place = args["place"]
                if key == 'coord':
                    address.coord = args["coord"]
            if count == 0:
                return raise_error("Пустой запрос", session)
            address_dict_2 = address.to_dict(only=('place',))
            list_chang = [f'изменяет {key} с {address_dict[key]} на {address_dict_2[key]}' for key in keys]
            session.commit()
            add_auditlog("Изменение",
                         f"Админ {admin.name} {admin.surname} изменяет {address.name} адрес: {', '.join(list_chang)}",
                         admin, datetime.datetime.now())
            session.close()
            return jsonify({"success": f"Адрес {address.name} успешно изменён"})
