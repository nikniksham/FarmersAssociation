import datetime
from flask import jsonify
from flask_restful import Resource
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.user import User
from data.member import Member
from data.API.MemberAPI.parser_member import parser_member
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
    member = session.query(Member).get(id)
    if not member:
        raise_error(f"Участник не найден", session)
    return member, session


class MemberResource(Resource):
    def put(self, member_id):
        args, count = parser_member.parse_args(), 0
        if not all(args[key] is not None for key in ['admin_email', 'action', 'admin_password']):
            raise_error('Пропущены некоторые важные аргументы')
        admin, session = check_admin_status(args['admin_email'], args["admin_password"])
        member, session = find_by_id(member_id, session)
        if args['action'] == "get":
            session.close()
            return jsonify(member.to_dict(only=('id', 'name', 'logo', 'image', 'text', 'address', 'coord', 'province', 'occupation', 'link', "socialmedia", 'created_date', 'author_id')))
        elif args['action'] == 'delete':
            session.delete(member)
            session.commit()
            add_auditlog("Удаление", f"{admin.name} {admin.surname} удаляет участника: {member.name}", admin, datetime.datetime.now())
            session.close()
            return jsonify({"success": f"Участник {member.name} успешно удален"})
        elif args['action'] == 'put':
            part_dict = member.to_dict(only=('name', 'logo', 'image', 'text', 'address', 'coord', 'province', 'occupation', 'link', "socialmedia"))
            keys = list(filter(lambda key: args[key] is not None and key in part_dict.keys() and args[key] != part_dict[key], list(args.keys())))
            name = member.name
            for key in keys:
                count += 1
                if key == "name":
                    member.name = args["name"]
                if key == "logo":
                    member.logo = args["logo"]
                if key == 'image':
                    member.image = args['image']
                if key == "text":
                    member.text = args["text"]
                if key == "link":
                    member.link = args["link"]
                if key == "socialmedia":
                    member.socialmedia = args["socialmedia"]
                if key == "occupation":
                    member.occupation = args["occupation"]
                if key == "address":
                    member.address = args["address"]
                if key == "coord":
                    member.coord = args["coord"]
                if key == "province":
                    member.province = args["province"]
            if count == 0:
                return raise_error("Пустой запрос", session)
            part_dict_2 = member.to_dict(only=('name', 'logo', 'image', 'text', 'address', 'coord', 'province', 'occupation', 'link', "socialmedia"))
            list_chang = [f'изменяет {key} с {part_dict[key]} на {part_dict_2[key]}' if key not in ["image", "logo"] else "изменяет изображения/аватарку" for key in keys]
            session.commit()
            add_auditlog("Изменение", f"{admin.name} {admin.surname} изменяет участника {name}: {', '.join(list_chang)}",
                         admin, datetime.datetime.now())
            session.close()
            return jsonify({"success": f"Участник {name} успешно изменен"})
        raise_error("Неизвестный метод", session)


class MemberResourceUsual(Resource):
    def get(self, member_id):
        session = db_session.create_session()
        member, session = find_by_id(member_id, session)
        session.close()
        return jsonify(member.to_dict(only=('id', 'name', 'logo', 'image', 'text', 'address', 'coord', 'province', 'occupation', 'link', "socialmedia")))


class MemberListRecourse(Resource):
    def get(self):
        session = db_session.create_session()
        members = session.query(Member).all()
        session.close()
        return jsonify([item.to_dict(only=('id', 'name', 'logo', 'image', 'text', 'address', 'coord', 'province', 'occupation', 'link', "socialmedia")) for item in members])


class CreateMemberResource(Resource):
    def post(self):
        args = parser_member.parse_args()
        if not all(args[key] is not None for key in ['name', 'logo', 'image', 'text', 'address', 'coord', 'province', 'occupation', 'link', "socialmedia", 'admin_email', 'admin_password']):
            raise_error('Пропущены некоторые аргументы, необходимые для создания участника')
        admin, session = check_admin_status(args['admin_email'], args["admin_password"])
        new_member = Member()
        new_member.name = args["name"]
        new_member.logo = args["logo"]
        new_member.image = args["image"]
        new_member.text = args["text"]
        new_member.link = args["link"]
        new_member.address = args["address"]
        new_member.coord = args["coord"]
        new_member.province = args['province']
        new_member.occupation = args["occupation"]
        new_member.created_date = datetime.datetime.now()
        if args["id"] is not None:
            if session.query(Member).get(args["id"]) is not None:
                raise_error("Этот id уже занят", session)
            new_member.id = args["id"]
        admin.member.append(new_member)
        session.merge(admin)
        session.commit()
        params_dict = new_member.to_dict(only=('id', 'name', 'image', 'text', 'link', "socialmedia", 'address', 'coord', 'province', 'occupation', 'created_date', 'author_id'))
        params_dict["image"] = f'кол-во изображений: {len(args["image"].split("//"))}'
        add_auditlog("Создание",
                     f"{admin.name} {admin.surname} создаёт участника {new_member.name}: {params_dict}",
                     admin, datetime.datetime.now())
        session.close()
        return jsonify({'success': f'Участник {new_member.name} создан', 'id': new_member.id})
