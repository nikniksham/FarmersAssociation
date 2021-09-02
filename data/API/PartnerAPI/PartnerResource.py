import datetime
from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.user import User
from data.partner import Partner
from data.API.PartnerAPI.parser_partner import parser_partner


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
    partner = session.query(Partner).get(id)
    if not partner:
        raise_error(f"Партнёр не найден")
    return partner, session


class PartnerResource(Resource):
    def put(self, partner_id):
        args, count = parser_partner.parse_args(), 0
        if not all(args[key] is not None for key in ['admin_email', 'action', 'admin_password']):
            raise_error('Пропущены некоторые важные аргументы')
        admin, session = check_admin_status(args['admin_email'], args["admin_password"])
        partner, session = find_by_id(partner_id, session)
        if args['action'] == "get":
            return jsonify(partner.to_dict(only=('id', 'logo', 'image', 'name', 'info', 'preferences', 'address', 'link', "socialmedia")))
        elif args['action'] == 'delete':
            session.delete(partner)
            session.commit()
            add_auditlog("Удаление", f"{admin.name} {admin.surname} удаляет партнёра: {partner.name}", admin, datetime.datetime.now())
            return jsonify({"success": f"Партнёр {partner.name} успешно удален"})
        elif args['action'] == 'put':
            part_dict = partner.to_dict(only=('image', 'logo', 'name', 'info', 'preferences', 'address', 'link'))
            keys = list(filter(lambda key: args[key] is not None and key in part_dict.keys() and args[key] != part_dict[key], list(args.keys())))
            name = partner.name
            for key in keys:
                count += 1
                if key == "name":
                    partner.name = args["name"]
                if key == "info":
                    partner.info = args["info"]
                if key == 'image':
                    print("WHWFAPOASNOPASMFM,ASASC", args["image"])
                    partner.image = args['image']
                if key == "preferences":
                    partner.preferences = args["preferences"]
                if key == "link":
                    partner.link = args["link"]
                if key == "socialmedia":
                    partner.socialmedia = args["socialmedia"]
                if key == "address":
                    partner.address = args["address"]
                if key == 'logo':
                    partner.logo = args['logo']
            if count == 0:
                return raise_error("Пустой запрос")
            part_dict_2 = partner.to_dict(only=('image', 'logo', 'name', 'info', 'preferences', 'address', 'link', "socialmedia"))
            list_chang = [f'изменяет {key} с {part_dict[key]} на {part_dict_2[key]}' if key not in ["image", "logo"] else "изменяет изображения/аватарку" for key in keys]
            session.commit()
            add_auditlog("Изменение", f"{admin.name} {admin.surname} изменяет партнёра {name}: {', '.join(list_chang)}",
                         admin, datetime.datetime.now())
            return jsonify({"success": f"Партнёр {name} успешно изменен"})
        raise_error("Неизвестный метод")


class PartnerResourceUsual(Resource):
    def get(self, partner_id):
        session = db_session.create_session()
        partner, session = find_by_id(partner_id, session)
        return jsonify(partner.to_dict(only=('id', 'logo', 'image', 'name', 'info', 'preferences', 'address', 'link', "socialmedia")))


class PartnerListRecourse(Resource):
    def get(self):
        session = db_session.create_session()
        partners = session.query(Partner).all()
        return jsonify([item.to_dict(only=('id', 'logo', 'image', 'name', 'info', 'preferences', 'address', 'link', "socialmedia")) for item in partners])


class CreatePartnerResource(Resource):
    def post(self):
        args = parser_partner.parse_args()
        if not all(args[key] is not None for key in ['image', 'logo', 'name', 'info', 'preferences', 'address', 'link', "socialmedia", 'admin_email', 'admin_password']):
            raise_error('Пропущены некоторые аргументы, необходимые для создания партнёра')
        admin, session = check_admin_status(args['admin_email'], args["admin_password"])
        new_partner = Partner()
        new_partner.name = args["name"]
        new_partner.image = args["image"]
        new_partner.preferences = args["preferences"]
        new_partner.link = args["link"]
        new_partner.address = args["address"]
        new_partner.info = args["info"]
        new_partner.logo = args['logo']
        new_partner.socialmedia = args["socialmedia"]
        session.add(new_partner)
        session.commit()
        params_dict = new_partner.to_dict(only=('id', 'logo', 'image', 'name', 'info', 'preferences', 'address', 'link', "socialmedia"))
        params_dict["image"] = f'кол-во изображений: {len(args["image"].split("//"))}'
        add_auditlog("Создание",
                     f"{admin.name} {admin.surname} создаёт партнёра {new_partner.name}: {params_dict}",
                     admin, datetime.datetime.now())
        return jsonify({'success': f'Партнёр {new_partner.name} создан', 'id': new_partner.id})
