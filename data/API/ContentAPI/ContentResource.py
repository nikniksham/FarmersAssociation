import datetime
from flask import jsonify
from flask_restful import Resource
from data import db_session
from data.content import Content
from data.API.ContentAPI.parser_content import parser_content
from data.smartpage import Smartpage
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.API.main_file import raise_error, check_admin_status


def find_by_id(id, session):
    content = session.query(Content).get(id)
    if not content:
        raise_error(f"Блок контента не найден", session)
    return content, session


class ContentResource(Resource):
    def put(self, content_id):
        args, count = parser_content.parse_args(), 0
        if not all(args[key] is not None for key in ['admin_email', 'action', 'admin_password']):
            raise_error('Пропущены некоторые важные аргументы')
        admin, session = check_admin_status(args['admin_email'], args["admin_password"])
        content, session = find_by_id(content_id, session)
        if args['action'] == "get":
            session.close()
            return jsonify(content.to_dict(only=('id', 'position', 'heading', 'type', 'image', 'animation_type', 'text', 'tags', 'author_id', 'smartpage_id', "display_type", "display_type_member")))
        elif args["action"] == "delete":
            c_pos = 1
            session.delete(content)
            blocks = session.query(Content).filter(Content.smartpage_id == content.smartpage_id).order_by(
                Content.position).all()
            for block in blocks:
                block.position, c_pos = c_pos, c_pos + 1
            session.commit()
            add_auditlog("Удаление", f"{admin.name} {admin.surname} удаляет блок контента {content.heading}, "
                                     f"с типом данных: {content.type}", admin, datetime.datetime.now())
            session.close()
            return jsonify({"success": f"Блок контента {content.heading} успешно удален"})
        elif args["action"] == "put":
            cont_dict = content.to_dict(only=('position', 'heading', 'type', 'image', 'animation_type', 'text', 'tags', "display_type", "display_type_member"))
            keys = list(filter(lambda key: args[key] is not None and key in list(cont_dict.keys()) and args[key] != cont_dict[key], list(args.keys())))
            for key in keys:
                count += 1
                if key == "position":
                    if args["position"] < 1:
                        args["position"] = 1
                    max_pos = session.query(Content).filter(Content.smartpage_id == content.smartpage_id).order_by(Content.position).all()[-1].position
                    if args["position"] > max_pos:
                        pos = 1
                        content.position = max_pos + 1
                        blocks = session.query(Content).filter(Content.smartpage_id == content.smartpage_id).order_by(
                            Content.position).all()
                        for block in blocks:
                            block.position, pos = pos, pos + 1
                    else:
                        elem = session.query(Content).filter(Content.smartpage_id == content.smartpage_id).filter(
                            Content.position == args["position"]).first()
                        if elem:
                            elem.position = content.position
                        content.position = args["position"]
                if key == 'type':
                    content.type = args["type"]
                if key == 'image':
                    content.image = args['image']
                if key == 'animation_type':
                    content.animation_type = args["animation_type"]
                if key == "text":
                    content.text = args["text"]
                if key == "tags":
                    content.tags = args["tags"]
                if key == "heading":
                    content.heading = args["heading"]
                if key == "display_type":
                    content.display_type = args["display_type"]
                if key == "display_type_member":
                    content.display_type_member = args["display_type_member"]
            if count == 0:
                raise_error("Пустой запрос", session)
            cont_dict_2 = content.to_dict(only=('position', 'heading', 'type', 'image', 'animation_type', 'text', 'tags', "display_type", "display_type_member"))
            list_chang = [
                f'изменяет {key} с {cont_dict[key]} на {cont_dict_2[key]}' if key != "image" else "изменяет изображения" for
                key in keys]
            session.commit()
            add_auditlog("Изменение", f"{admin.name} {admin.surname} изменяет блок контента: {', '.join(list_chang)}",
                         admin, datetime.datetime.now())
            position = content.position
            session.close()
            return jsonify({"success": f"Блок контента на позиции {position} успешно изменен"})
        raise_error("Неизвестный метод", session)


class ContentListRecourse(Resource):
    def get(self):
        session = db_session.create_session()
        contents = session.query(Content).order_by(Content.position).all()
        session.close()
        return jsonify([item.to_dict(
            only=('id', 'position', 'heading', 'type', 'image', 'animation_type', 'text', 'tags', 'author_id', 'smartpage_id', "display_type", "display_type_member"))
            for item in contents])


class ContentListRecourseId(Resource):
    def get(self, smartpage_id):
        session = db_session.create_session()
        contents = session.query(Content).filter(Content.smartpage_id == smartpage_id).order_by(Content.position).all()
        session.close()
        return jsonify([item.to_dict(
            only=('id', 'position', 'heading', 'type', 'image', 'animation_type', 'text', 'tags', 'author_id', 'smartpage_id', "display_type", "display_type_member"))
            for item in contents])


class CreateContentResource(Resource):
    def post(self):
        args = parser_content.parse_args()
        if not all(args[key] is not None for key in ['type', 'page_id', 'heading', 'admin_email', 'admin_password']):
            raise_error('Пропущены некоторые аргументы, необходимые для создания страницы')
        admin, session = check_admin_status(args['admin_email'], args["admin_password"])
        page = session.query(Smartpage).get(args["page_id"])
        if page is None:
            raise_error(f"Страница с id {args['page_id']} не найдена", session)
        new_content = Content()
        elem = session.query(Content).filter(Content.smartpage_id == args['page_id']).filter(
            Content.position == args["position"]).first()
        if elem is not None:
            blocks = session.query(Content).filter(Content.smartpage_id == args['page_id']).order_by(
                Content.position).all()
            pos = args["position"] if args["position"] else blocks[-1]["position"] + 1
            new_content.position = pos
            for block in blocks:
                if block.position == pos:
                    pos += 1
                    block.position = pos
        else:
            i = session.query(Content).filter(Content.smartpage_id == args['page_id']).order_by(Content.position).all()
            i = i[-1].position + 1 if i else 1
            new_content.position = i

        new_content.heading = args['heading']
        new_content.type = args["type"]
        new_content.image = args['image']
        new_content.animation_type = args["animation_type"]
        new_content.text = args["text"]
        new_content.tags = args["tags"]
        new_content.display_type = args["display_type"]
        new_content.display_type_member = args["display_type_member"]
        new_content.created_date = datetime.datetime.now()
        new_content.smartpage = page
        if args["id"] is not None:
            if session.query(Content).get(args["id"]) is not None:
                raise_error("Этот id уже занят", session)
            new_content.id = args["id"]
        admin.content.append(new_content)
        session.merge(admin)
        session.commit()
        params_dict = new_content.to_dict(
            only=('id', 'position', 'type', 'animation_type', 'text', 'tags', 'author_id', 'smartpage_id', 'heading', "display_type", "display_type_member"))
        params_dict["image"] = f'кол-во изображений: {len(args["image"].split("//")) if args["image"] else 0}'
        add_auditlog("Создание", f"{admin.name} {admin.surname} создаёт блок контента с параметрами: {params_dict}",
                     admin, datetime.datetime.now())
        session.close()
        return jsonify({'success': f'Блок контента на позиции {new_content.position} создан', 'id': new_content.id})
