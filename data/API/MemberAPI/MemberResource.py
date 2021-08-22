import datetime
from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.user import User
from data.member import Member
from data.API.MemberAPI.parser_member import parser_member


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
    member = session.query(Member).get(id)
    if not member:
        raise_error(f"Партнёр не найден")
    return member, session


class MemberResource(Resource):
    def put(self, member_id):
        args, count = parser_member.parse_args(), 0
        if not all(args[key] is not None for key in ['admin_email', 'action', 'admin_password']):
            raise_error('Пропущены некоторые важные аргументы')
        admin, session = check_admin_status(args['admin_email'], args["admin_password"])
        member, session = find_by_id(member_id, session)
        if args['action'] == "get":
            return jsonify(member.to_dict(only=('id', 'image', 'name', 'info', 'preferences', 'address', 'link')))
        elif args['action'] == 'delete':
            session.delete(member)
            session.commit()
            add_auditlog("Удаление", f"{admin.name} {admin.surname} удаляет партнёра: {member.name}", admin, datetime.datetime.now())
            return jsonify({"success": f"Партнёр {member.name} успешно удален"})
        elif args['action'] == 'put':
            part_dict = member.to_dict(only=('image', 'name', 'info', 'preferences', 'address', 'link'))
            keys = list(filter(lambda key: args[key] is not None and key in part_dict.keys() and args[key] != part_dict[key], list(args.keys())))
            name = member.name
            for key in keys:
                count += 1
                if key == "name":
                    member.name = args["name"]
                if key == "info":
                    member.info = args["info"]
                if key == 'image':
                    member.image = args['image']
                if key == "preferences":
                    member.preferences = args["preferences"]
                if key == "link":
                    member.link = args["link"]
                if key == "address":
                    member.address = args["address"]
            if count == 0:
                return raise_error("Пустой запрос")
            part_dict_2 = member.to_dict(only=('image', 'name', 'info', 'preferences', 'address', 'link'))
            list_chang = [f'изменяет {key} с {part_dict[key]} на {part_dict_2[key]}' if key not in ["image", "logo"] else "изменяет изображения/аватарку" for key in keys]
            session.commit()
            add_auditlog("Изменение", f"{admin.name} {admin.surname} изменяет партнёра {name}: {', '.join(list_chang)}",
                         admin, datetime.datetime.now())
            return jsonify({"success": f"Партнёр {name} успешно изменен"})
        raise_error("Неизвестный метод")


class MemberResourceUsual(Resource):
    def get(self, member_id):
        session = db_session.create_session()
        member, session = find_by_id(member_id, session)
        return jsonify(member.to_dict(only=('id', 'image', 'name', 'info', 'preferences', 'address', 'link')))


class MemberListRecourse(Resource):
    def get(self):
        session = db_session.create_session()
        members = session.query(Member).all()
        return jsonify([item.to_dict(only=('id', 'image', 'name', 'info', 'preferences', 'address', 'link')) for item in members])


class CreateMemberResource(Resource):
    def post(self):
        args = parser_member.parse_args()
        if not all(args[key] is not None for key in ['image', 'name', 'info', 'preferences', 'address', 'link', 'admin_email', 'admin_password']):
            raise_error('Пропущены некоторые аргументы, необходимые для создания партнёра')
        admin, session = check_admin_status(args['admin_email'], args["admin_password"])
        new_member = Member()
        new_member.name = args["name"]
        new_member.image = args["image"]
        new_member.preferences = args["preferences"]
        new_member.link = args["link"]
        new_member.address = args["address"]
        new_member.info = args["info"]
        session.add(new_member)
        session.commit()
        params_dict = new_member.to_dict(only=('id', 'image', 'name', 'info', 'preferences', 'address', 'link'))
        params_dict["image"] = f'кол-во изображений: {len(args["image"].split("//"))}'
        add_auditlog("Создание",
                     f"{admin.name} {admin.surname} создаёт партнёра {new_member.name}: {params_dict}",
                     admin, datetime.datetime.now())
        return jsonify({'success': f'Партнёр {new_member.name} создан', 'id': new_member.id})
