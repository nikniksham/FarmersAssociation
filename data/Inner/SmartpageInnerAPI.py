import datetime
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.smartpage import Smartpage
from data.content import Content
from data.API.NewspageAPI.NewspageResource import trans_link
from data.Inner.main_file import raise_error, check_admin_status


def find_by_id(id, session):
    smartpage = session.query(Smartpage).get(id)
    if not smartpage:
        return raise_error(f"Страница не найдена", session), 1
    return smartpage, session


def edit_smartpage(smartpage_id, args):
    count = 0
    if not all(args[key] is not None for key in ['admin_email', 'action']):
        return raise_error('Пропущены некоторые важные аргументы')
    admin, session = check_admin_status(args['admin_email'])
    smartpage, session = find_by_id(smartpage_id, session)
    if type(smartpage) == dict:
        session.close()
        return smartpage
    if args['action'] == "get":
        session.close()
        return smartpage.to_dict(only=('id', 'link', 'heading', 'image', 'created_date', 'author_id'))
    elif args['action'] == 'delete':
        if smartpage.id < 7:
            return raise_error("У вас недостаточно прав для этого", session)
        contentlist = session.query(Content).filter(Content.smartpage_id == smartpage.id).all()
        for content in contentlist:
            add_auditlog("Удаление", f"{admin.name} {admin.surname} удаляет блок контента на позиции: {content.position}, с типом данных: {content.type}",
                         admin, datetime.datetime.now())
            session.delete(content)
        heading = smartpage.heading
        session.delete(smartpage)
        session.commit()
        add_auditlog("Удаление", f"{admin.name} {admin.surname} удаляет страницу: {heading}", admin, datetime.datetime.now())
        session.close()
        return {"success": f"Страница {heading} успешно удалена"}
    elif args['action'] == 'put':
        page_dict = smartpage.to_dict(only=('heading', 'image', 'created_date'))
        keys = list(filter(lambda key: args[key] is not None and key in page_dict.keys() and args[key] != page_dict[key], list(args.keys())))
        for key in keys:
            count += 1
            if key == 'image':
                smartpage.image = args['image']
            if key == 'heading':
                if session.query(Smartpage).filter(Smartpage.heading == args["heading"]).first() is not None:
                    return raise_error("Этот заголовок уже занят")
                smartpage.heading = args["heading"]
                link, count = trans_link(args["heading"]), 0
                while session.query(Smartpage).filter(Smartpage.link == link).first() is not None:
                    if link[-len(str(count)):] == str(count):
                        link = link[:-len(str(count))] + str(count + 1)
                        count += 1
                    else:
                        link += str(count)
                smartpage.link = link
        if count == 0:
            return raise_error("Пустой запрос", session)
        page_dict_2 = smartpage.to_dict(only=('heading', 'image', 'created_date', 'author_id'))
        list_chang = [f'изменяет {key} с {page_dict[key]} на {page_dict_2[key]}' if key != "image" else "изменяет изображения" for key in keys]
        session.commit()
        add_auditlog("Изменение", f"{admin.name} {admin.surname} изменяет страницу {smartpage.heading}: {', '.join(list_chang)}",
                     admin, datetime.datetime.now())
        session.close()
        return {"success": f"Страница {smartpage.heading} успешно изменена"}
    return raise_error("Неизвестный метод", session)


def get_smartpage_usual(smartpage_id):
    session = db_session.create_session()
    smartpage, session = find_by_id(smartpage_id, session)
    if type(smartpage) == dict:
        session.close()
        return smartpage
    session.close()
    return smartpage.to_dict(only=('id', 'link', 'heading', 'image', 'created_date', 'author_id'))


def get_smartpage_link(link):
    session = db_session.create_session()
    smartpage = session.query(Smartpage).filter(Smartpage.link == link).first()
    session.close()
    if smartpage:
        return smartpage.to_dict(only=('id', 'link', 'heading', 'image', 'created_date', 'author_id'))
    return raise_error("Страница не найдена")


def get_smartpage_list():
    session = db_session.create_session()
    smartpages = session.query(Smartpage).all()
    session.close()
    return [item.to_dict(only=('id', 'link', 'heading', 'image', 'created_date', 'author_id')) for item in smartpages]


def create_smartpage(args):
    if not all(args[key] is not None for key in ['heading', 'admin_email']):
        return raise_error('Пропущены некоторые аргументы, необходимые для создания страницы')
    admin, session = check_admin_status(args['admin_email'])
    if session.query(Smartpage).filter(Smartpage.heading == args["heading"]).first() is not None:
        return raise_error("Этот заголовок уже занят", session)
    new_smartpage = Smartpage()
    new_smartpage.heading = args["heading"]
    link, count = trans_link(args["heading"]), 0
    while session.query(Smartpage).filter(Smartpage.link == link).first() is not None:
        if link[-len(str(count)):] == str(count):
            link = link[:-len(str(count))] + str(count + 1)
            count += 1
        else:
            link += str(count)
    new_smartpage.link = link
    new_smartpage.image = args['image'] if args['image'] is not None else "standard.png"
    new_smartpage.created_date = datetime.datetime.now()
    admin.smartpage.append(new_smartpage)
    session.merge(admin)
    session.commit()
    params_dict = new_smartpage.to_dict(only=('id', 'link', 'heading', 'image', 'created_date', 'author_id'))
    params_dict["image"] = f'кол-во изображений: {len(args["image"].split("//"))}'
    add_auditlog("Создание",
                 f"{admin.name} {admin.surname} создаёт страницу {new_smartpage.heading}: {params_dict}",
                 admin, datetime.datetime.now())
    session.close()
    return {"id": new_smartpage.id, 'success': f'Страница {new_smartpage.heading} создана'}
