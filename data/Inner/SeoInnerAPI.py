import datetime
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.seo import Seo
from data.Inner.main_file import raise_error, check_admin_status


def find_by_id(id, session):
    seo = session.query(Seo).get(id)
    if not seo:
        raise_error(f"Seo настройка не найдена", session)
    return seo, session


def get_seo_usual(seo_id):
    session = db_session.create_session()
    seo, session = find_by_id(seo_id, session)
    session.close()
    return seo.to_dict(only=('id', 'title', 'description', 'tags'))


def edit_seo(seo_id, args):
    count = 0
    if not all(args[key] is not None for key in ['admin_email', 'action']):
        raise_error('Пропущены некоторые важные аргументы')
    admin, session = check_admin_status(args['admin_email'])
    seo, session = find_by_id(seo_id, session)
    if args['action'] == "get":
        session.close()
        return seo.to_dict(only=('id', 'title', 'description', 'tags'))
    elif args['action'] == 'put':
        seo_dict = seo.to_dict(only=('id', 'title', 'description', 'tags'))
        keys = list(filter(lambda key: args[key] is not None and key in seo_dict and args[key] != seo_dict[key], args.keys()))
        for key in keys:
            count += 1
            if key == 'title':
                seo.title = args["title"]
            if key == 'description':
                seo.description = args["description"]
            if key == 'tags':
                seo.tags = args["tags"]
        if count == 0:
            return raise_error("Пустой запрос", session.close())
        seo_dict_2 = seo.to_dict(only=('id', 'title', 'description', 'tags'))
        list_chang = [f'изменяет {key} с {seo_dict[key]} на {seo_dict_2[key]}' for key in keys]
        session.commit()
        add_auditlog("Изменение",
                     f"Админ {admin.name} {admin.surname} изменяет настройку seo: {', '.join(list_chang)}",
                     admin, datetime.datetime.now())
        session.close()
        return {"success": f"Seo настройка успешно изменена"}
