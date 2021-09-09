import datetime
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.member import Member
from data.Inner.main_file import raise_error, check_admin_status


def find_by_id(id, session):
    member = session.query(Member).get(id)
    if not member:
        return raise_error(f"Участник не найден", session), 1
    return member, session


def edit_member(member_id, args):
    count = 0
    if not all(args[key] is not None for key in ['admin_email', 'action']):
        return raise_error('Пропущены некоторые важные аргументы')
    admin, session = check_admin_status(args['admin_email'])
    member, session = find_by_id(member_id, session)
    if type(member) == dict:
        return member
    if args['action'] == "get":
        session.close()
        return member.to_dict(only=('id', 'name', 'logo', 'image', 'text', 'address', 'coord', 'province', 'occupation', 'link', "socialmedia", 'created_date', 'author_id'))
    elif args['action'] == 'delete':
        session.delete(member)
        session.commit()
        add_auditlog("Удаление", f"{admin.name} {admin.surname} удаляет участника: {member.name}", admin, datetime.datetime.now())
        session.close()
        return {"success": f"Участник {member.name} успешно удален"}
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
        return {"success": f"Участник {name} успешно изменен"}
    return raise_error("Неизвестный метод", session)


def get_member_usual(member_id):
    session = db_session.create_session()
    member, session = find_by_id(member_id, session)
    if type(member) == dict:
        return member
    session.close()
    return member.to_dict(only=('id', 'name', 'logo', 'image', 'text', 'address', 'coord', 'province', 'occupation', 'link', "socialmedia"))


def get_member_list():
    session = db_session.create_session()
    members = session.query(Member).all()
    session.close()
    return [item.to_dict(only=('id', 'name', 'logo', 'image', 'text', 'address', 'coord', 'province', 'occupation', 'link', "socialmedia")) for item in members]


def create_member(args):
    if not all(args[key] is not None for key in ['name', 'logo', 'image', 'text', 'address', 'coord', 'province', 'occupation', 'link', "socialmedia", 'admin_email']):
        return raise_error('Пропущены некоторые аргументы, необходимые для создания участника')
    admin, session = check_admin_status(args['admin_email'])
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
    new_member.socialmedia = args["socialmedia"]
    new_member.created_date = datetime.datetime.now()
    admin.member.append(new_member)
    session.merge(admin)
    session.commit()
    params_dict = new_member.to_dict(only=('id', 'name', 'image', 'text', 'link', "socialmedia", 'address', 'coord', 'province', 'occupation', 'created_date', 'author_id'))
    params_dict["image"] = f'кол-во изображений: {len(args["image"].split("//"))}'
    add_auditlog("Создание",
                 f"{admin.name} {admin.surname} создаёт участника {new_member.name}: {params_dict}",
                 admin, datetime.datetime.now())
    session.close()
    return {'id': new_member.id, 'success': f'Участник {new_member.name} создан'}
