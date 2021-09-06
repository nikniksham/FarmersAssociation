import datetime
from data import db_session
from data.API.AuditlogAPI.AuditlogResource import add_auditlog
from data.newspage import Newspage
from main import mini_text, text_transform
from config import UPLOAD_FOLDER as path
from data.Inner.main_file import raise_error, check_admin_status


def trans_link(text):
    trans = {"а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo", "ж": "zh", "з": "z", "и": "i",
             "й": "j", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
             "у": "u", "ф": "f", "х": "x", "ц": "cz", "ч": "ch", "ш": "sh", "щ": "sch", "ы": "y", "э": "e", "ю": "yu",
             "я": "ya", " ": "_"}
    eng_letter = "qwertyuiopasdfghjklzxcvbnm"
    link, keys, isup = "", list(trans.keys()), False
    for letter in text:
        isup = letter.isupper()
        if letter.isdigit():
            link += letter
        elif letter.lower() in keys:
            link += trans[letter.lower()].upper() if isup else trans[letter]
        elif letter.lower() in eng_letter:
            link += letter
    return link


def find_by_id(id, session):
    newspage = session.query(Newspage).get(id)
    if not newspage:
        raise_error(f"Страница не найдена", session)
    return newspage, session


def edit_newspage(newspage_id, args):
    if not all(args[key] is not None for key in ['admin_email', 'action']):
        raise_error('Пропущены некоторые важные аргументы')
    admin, session = check_admin_status(args['admin_email'])
    newspage, session = find_by_id(newspage_id, session)
    if args["action"] == "get":
        news_dict = newspage.to_dict(only=('id', 'heading', 'text', 'link', 'image', 'tags', 'created_date', 'author_id'))
        news_dict["mini_text"] = mini_text(newspage.text)
        news_dict["text_render"] = text_transform(newspage.text, newspage.image.split("//"), path)
        session.close()
        return news_dict
    elif args["action"] == "delete":
        session.delete(newspage)
        session.commit()
        add_auditlog("Удаление", f"{admin.name} {admin.surname} удаляет новостную страницу: {newspage.heading}", admin,
                     datetime.datetime.now())
        session.close()
        return {"success": f"Новостная страница {newspage.heading} успешно удалена"}
    elif args["action"] == "put":
        count_params = 0
        page_dict = newspage.to_dict(only=('heading', 'text', 'image', 'tags'))
        keys = list(filter(lambda key: args[key] is not None and key in page_dict and args[key] != page_dict[key], list(args.keys())))
        for key in keys:
            count_params += 1
            if key == 'image':
                print(args['image'])
                newspage.image = args['image']
            if key == 'heading':
                newspage.heading = args["heading"]
                link, count = trans_link(args["heading"]), 0
                while session.query(Newspage).filter(Newspage.link == link).first() is not None:
                    if link[-len(str(count)):] == str(count):
                        link = link[:-len(str(count))] + str(count + 1)
                        count += 1
                    else:
                        link += str(count)
                newspage.link = link
            if key == "text":
                newspage.text = args["text"]
            if key == "tags":
                newspage.tags = args["tags"]
        if count_params == 0:
            return raise_error("Пустой запрос", session)
        page_dict_2 = newspage.to_dict(only=('heading', 'text', 'image', 'tags'))
        list_chang = [f'изменяет {key} с {page_dict[key]} на {page_dict_2[key]}' if key != "image" else "изменяет изображения" for key in keys]
        session.commit()
        add_auditlog("Изменение",
                     f"{admin.name} {admin.surname} изменяет новостную страницу {newspage.heading}: {', '.join(list_chang)}",
                     admin, datetime.datetime.now())
        session.close()
        return {"success": f"Новостная страница {newspage.heading} успешно изменена"}
    raise_error("Неизвестный метод", session)


def get_newspage_ususal(newspage_id):
    session = db_session.create_session()
    newspage, session = find_by_id(newspage_id, session)
    session.close()
    news_dict = newspage.to_dict(only=('id', 'heading', 'text', 'link', 'image', 'tags', 'created_date'))
    news_dict["mini_text"] = mini_text(newspage.text)
    news_dict["text_render"] = text_transform(newspage.text, newspage.image.split("//"), path)
    return news_dict


def get_newspage_link(link):
    session = db_session.create_session()
    newspage = session.query(Newspage).filter(Newspage.link == link).first()
    session.close()
    if newspage:
        news_dict = newspage.to_dict(only=('id', 'heading', 'text', 'link', 'image', 'tags', 'created_date'))
        news_dict["mini_text"] = mini_text(newspage.text)
        news_dict["text_render"] = text_transform(newspage.text, newspage.image.split("//"), path)
        return news_dict
    raise_error("Новость не найдена")


def get_newspage_from_to(start_id, end_id):
    session = db_session.create_session()
    newspages = session.query(Newspage).order_by(Newspage.created_date)[::-1]
    session.close()
    if start_id > len(newspages):
        return []
    if end_id > len(newspages):
        end_id = len(newspages)
    newspages, news_list = newspages[start_id:end_id], []
    for item in newspages:
        news_dict = item.to_dict(only=('id', 'heading', 'text', 'link', 'image', 'tags', 'created_date'))
        news_dict["mini_text"] = mini_text(item.text)
        news_dict["text_render"] = text_transform(item.text, item.image.split("//"), path)
        news_list.append(news_dict)
    return news_list


def get_newspage_find(start_id, end_id, text):
    session = db_session.create_session()
    pages, newspages = session.query(Newspage).order_by(Newspage.created_date)[::-1], []
    session.close()
    if text is None:
        text = ""
    find_text = text.replace("<", "").replace(">", "").replace("/", "").lower().rstrip()
    for news in pages:
        tags = news.tags.lower() if news.tags else ""
        text = news.text.lower() if news.text else ""
        heading = news.heading.lower() if news.heading else ""
        if find_text in tags or find_text in text or find_text in heading:
            newspages.append(news)
    if start_id > len(newspages):
        return []
    if end_id > len(newspages):
        end_id = len(newspages)
    newspages, news_list = newspages[start_id:end_id], []
    for item in newspages:
        news_dict = item.to_dict(only=('id', 'heading', 'text', 'link', 'image', 'tags', 'created_date'))
        news_dict["mini_text"] = mini_text(item.text)
        news_dict["text_render"] = text_transform(item.text, item.image.split("//"), path)
        news_list.append(news_dict)
    return news_list


def get_newspage_list():
    session = db_session.create_session()
    newspages, news_list = session.query(Newspage).order_by(Newspage.created_date)[::-1], []
    for item in newspages:
        news_dict = item.to_dict(only=('id', 'heading', 'text', 'link', 'image', 'tags', 'created_date'))
        news_dict["mini_text"] = mini_text(item.text)
        news_dict["text_render"] = text_transform(item.text, item.image.split("//"), path)
        news_list.append(news_dict)
    session.close()
    return news_list


def create_newspage(args):
    if not all(args[key] is not None for key in ['heading', 'text', 'tags', 'admin_email']):
        raise_error('Пропущены некоторые аргументы, необходимые для создания новостной страницы')
    admin, session = check_admin_status(args['admin_email'])
    new_newspage = Newspage()
    new_newspage.heading = args["heading"]
    new_newspage.text = args["text"]
    link, count = trans_link(args["heading"]), 0
    while session.query(Newspage).filter(Newspage.link == link).first() is not None:
        if link[-len(str(count)):] == str(count):
            link = link[:-len(str(count))] + str(count + 1)
            count += 1
        else:
            link += str(count)
    new_newspage.link = link
    new_newspage.image = args['image']
    new_newspage.tags = args['tags']
    new_newspage.created_date = datetime.datetime.now()
    admin.newspage.append(new_newspage)
    session.merge(admin)
    session.commit()
    params_dict = new_newspage.to_dict(only=('id', 'heading', 'text', 'link', 'tags', 'created_date', 'author_id'))
    params_dict["image"] = f'кол-во изображений: {len(args["image"].split("//"))}'
    add_auditlog("Создание",
                 f"{admin.name} {admin.surname} создаёт новостную страницу {new_newspage.heading}: {params_dict}",
                 admin, datetime.datetime.now())
    session.close()
    return {'id': new_newspage.id, 'success': f'Новостная страница {new_newspage.heading} создана'}
