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
    def get(self, email, password, partner_id):
        admin, session = check_admin_status(email, password)
        partner, session = find_by_id(partner_id, session)
        return jsonify(partner.to_dict(only=('id', 'name', 'image', 'text', 'link', 'created_date', 'author_id')))

    def delete(self, email, password, partner_id):
        admin, session = check_admin_status(email, password)
        partner, session = find_by_id(partner_id, session)
        name = partner.name
        session.delete(partner)
        session.commit()
        add_auditlog("Удаление", f"{admin.name} {admin.surname} удаляет партнёра: {name}", admin, datetime.datetime.now())
        return jsonify({"success": f"Партнёр {name} успешно удален"})

    def put(self, email, password, partner_id):
        admin, session = check_admin_status(email, password)
        partner, session = find_by_id(partner_id, session)
        args, count = parser_partner.parse_args(), 0
        keys = list(filter(lambda key: args[key] is not None, list(args.keys())))
        page_dict = partner.to_dict(only=('id', 'name', 'image', 'text', 'link'))
        name = partner.name
        for key in list(args.keys()):
            if args[key] is not None:
                count += 1
                if key == 'id':
                    if session.query(Partner).filter(Partner.id == args["id"]).first():
                        raise_error("Этот id уже занят")
                    partner.id = args['id']
                if key == "name":
                    partner.name = args["name"]
                if key == 'image':
                    partner.image = args['image']
                if key == "text":
                    partner.text = args["text"]
                if key == "link":
                    partner.tags = args["link"]
        if count == 0:
            return raise_error("Пустой запрос")
        page_dict_2 = partner.to_dict(only=('id', 'name', 'image', 'text', 'link'))
        list_chang = [f'изменяет {key} с {page_dict[key]} на {page_dict_2[key]}' for key in keys]
        session.commit()
        add_auditlog("Изменение",
                     f"{admin.name} {admin.surname} изменяет партнёра {name}: {', '.join(list_chang)}", admin,
                     datetime.datetime.now())
        return jsonify({"success": f"Партнёр {name} успешно изменен"})


class PartnerResourceUsual(Resource):
    def get(self, partner_id):
        session = db_session.create_session()
        partner, session = find_by_id(partner_id, session)
        return jsonify(partner.to_dict(only=('id', 'name', 'image', 'text', 'link')))


class PartnerListRecourse(Resource):
    def get(self):
        session = db_session.create_session()
        partners = session.query(Partner).all()
        return jsonify([item.to_dict(only=('id', 'name', 'image', 'text', 'link')) for item in partners])


class CreatePartnerResource(Resource):
    def post(self, email, password):
        admin, session = check_admin_status(email, password)
        args = parser_partner.parse_args()
        if not all(args[key] is not None for key in ['name', 'image', 'text', 'link']):
            raise_error('Пропущены некоторые аргументы, необходимые для создания партнёра')
        new_partner = Partner()
        new_partner.name = args["name"]
        new_partner.image = args["image"]
        new_partner.text = args["text"]
        new_partner.link = args["link"]
        new_partner.created_date = datetime.datetime.now()
        if args["id"] is not None:
            if session.query(Partner).get(args["id"]) is not None:
                raise_error("Этот id уже занят")
            new_partner.id = args["id"]
        admin.partner.append(new_partner)
        session.merge(admin)
        session.commit()
        add_auditlog("Создание",
                     f"{admin.name} {admin.surname} создаёт партнёра {new_partner.name}: {new_partner.to_dict(only=('id', 'name', 'image', 'text', 'link', 'created_date', 'author_id'))}",
                     admin, datetime.datetime.now())
        return jsonify({'success': f'Партнёр {new_partner.name} создан'})
