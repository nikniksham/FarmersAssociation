from requests import get, post, put, delete

link_website = 'http://127.0.0.1:8000/'
test_admin = {"email": "admin@gmail.com", "password": "adminsk1"}
test_admin_without_status = {"email": "admin2@gmail.com", "password": "adminsk1"}
test_user = {"email": "admin3@gmail.com", "password": "adminsk1"}
page_id = 50

test_get = True
test_post = True
test_put = True
test_delete = True

test_admin_api = True
test_smartpage_api = True
test_content = True
test_newspage = True
test_partner = True
test_feedback = True
test_auditlog = True

# x17dfWqpc94
# farmersassociationmoscowregion
# pbkdf2:sha256:150000$ienbNff2$f899740f7999e24b06b519d5305cf8f2e34643033b6e3086fff3e0c8e39d795b
if test_admin_api:
    if test_post:
        print(post(f"{link_website}api/admin/{test_admin['email']}/{test_admin['password']}",
                   json={"name": 'Василий', "email": test_user["email"], "password": test_user["password"]}).json())
        print(post(f"{link_website}api/admin/{test_admin['email']}/{test_admin['password']}",
                   json={"name": 'Василий', "surname": "Петров", "email": test_user["email"],
                         "password": test_user["password"]}).json())
        print(post(
            f"{link_website}api/admin/{test_admin_without_status['email']}/{test_admin_without_status['password']}",
            json={"name": 'Василий', "Петров": "Админович", "email": test_user["email"],
                  "password": test_user["password"]}).json())
    post(f"{link_website}api/admin/{test_admin['email']}/{test_admin['password']}",
         json={"name": 'Василий', "Петров": "Админович", "email": test_user["email"],
               "password": test_user["password"]}).json()
    new_admin_id = get(f"{link_website}api/admin/{test_user['email']}/{test_user['password']}").json()["admin"]["id"]

    if test_put:
        print("Админ изменил сам себя", put(f"{link_website}api/admin/{test_user['email']}/{test_user['password']}",
                                            json={"name": "Всё хорошо 1"}).json())
        print("Админ не может менять сам себя по id, если его статус меньше 1",
              put(f"{link_website}api/admin/{test_user['email']}/{test_user['password']}/{new_admin_id}",
                  json={"name": "Ошибочка 1"}).json())
        print("Админ был изменён другим админом",
              put(f"{link_website}api/admin/{test_admin['email']}/{test_admin['password']}/{new_admin_id}",
                  json={"name": "Всё хорошо 2"}).json())
        print("Админ не был изменён админом с более низким статусом", put(
            f"{link_website}api/admin/{test_admin_without_status['email']}/{test_admin_without_status['password']}/{new_admin_id}",
            json={"name": "Ошибочка 2"}).json())

    if test_get:
        print("получает сам себя", get(f"{link_website}api/admin/{test_user['email']}/{test_user['password']}").json())
        print("не может получить сам себя по id, если его статус ниже 1",
              get(f"{link_website}api/admin/{test_user['email']}/{test_user['password']}/{new_admin_id}").json())
        print("другой админ получает по id",
              get(f"{link_website}api/admin/{test_admin['email']}/{test_admin['password']}/{new_admin_id}").json())
        print("другой админ c более низким статусом не получает по id", get(
            f"{link_website}api/admin/{test_admin_without_status['email']}/{test_admin_without_status['password']}/{new_admin_id}").json())
        print("не может получить список админов, если статус ниже 1",
              get(
                  f"{link_website}api/admin/list/{test_admin_without_status['email']}/{test_admin_without_status['password']}").json())
        print("Админ получает список админов",
              get(f"{link_website}api/admin/list/{test_admin['email']}/{test_admin['password']}").json())

    if test_delete:
        print("удаляет сам себя",
              delete(f"{link_website}api/admin/{test_user['email']}/{test_user['password']}").json())
        post(f"{link_website}api/admin/{test_admin['email']}/{test_admin['password']}",
             json={"name": 'Василий', "surname": "Петров", "email": test_user["email"],
                   "password": test_user["password"], "status": 0}).json()
        print("не может удалить сам себя по id, если статус ниже 1",
              delete(f"{link_website}api/admin/{test_user['email']}/{test_user['password']}/{new_admin_id}").json())
        post(f"{link_website}api/admin/{test_admin['email']}/{test_admin['password']}",
             json={"name": 'Василий', "surname": "Петров", "email": test_user["email"],
                   "password": test_user["password"], "status": 0}).json()
        print("другой админ удаляет по id",
              delete(f"{link_website}api/admin/{test_admin['email']}/{test_admin['password']}/{new_admin_id}").json())
        post(f"{link_website}api/admin/{test_admin['email']}/{test_admin['password']}",
             json={"name": 'Василий', "surname": "Петров", "email": test_user["email"],
                   "password": test_user["password"], "status": 0}).json()
        print("другой админ c более низким статусом не может удалить по id", delete(
            f"{link_website}api/admin/{test_admin_without_status['email']}/{test_admin_without_status['password']}/{new_admin_id}").json())

if test_smartpage_api:
    if test_post:
        print("Админ, с нулевым стасусом не может создать страницу", post(
            f"{link_website}api/smartpage/{test_admin_without_status['email']}/{test_admin_without_status['password']}",
            json={"heading": "Главная страница", "id": page_id}).json())
        print("Пропущен важный аргумент для создания", post(
            f"{link_website}api/smartpage/{test_admin['email']}/{test_admin['password']}",
            json={"id": page_id}).json())
        print("Админ создаёт страницу, всё хорошо", post(
            f"{link_website}api/smartpage/{test_admin['email']}/{test_admin['password']}",
            json={"heading": "Главная страница", "id": page_id}).json())

    post(f"{link_website}api/smartpage/{test_admin['email']}/{test_admin['password']}",
         json={"heading": "Главная страница", "id": page_id})
    if test_get:
        print("Админ со статусом ниже 1 не может получить страницу по id",
              get(
                  f"{link_website}api/smartpage/{test_admin_without_status['email']}/{test_admin_without_status['password']}/{page_id}").json())
        print("Админ получает страницу по id",
              get(f"{link_website}api/smartpage/{test_admin['email']}/{test_admin['password']}/{page_id}").json())
        print("Любой пользователь может получить список страниц", get(f"{link_website}api/smartpage").json())
    if test_put:
        print("Админ со статусом, ниже 1 не может менять", put(
            f"{link_website}api/smartpage/{test_admin_without_status['email']}/{test_admin_without_status['password']}/{page_id}",
            json={"heading": "Главная страница со стразами"}).json())
        print("Админ может изменить страницу", put(
            f"{link_website}api/smartpage/{test_admin['email']}/{test_admin['password']}/{page_id}",
            json={"heading": "Главная страница со стразами"}).json())
    if test_delete:
        print("Админ со статусом доступа ниже 1 не может удалить страницу", delete(
            f"{link_website}api/smartpage/{test_admin_without_status['email']}/{test_admin_without_status['password']}/{page_id}").json())
        post(f"{link_website}api/smartpage/{test_admin['email']}/{test_admin['password']}",
             json={"heading": "Главная страница", "id": page_id})
        print("Админ может удалить страницу", delete(
            f"{link_website}api/smartpage/{test_admin['email']}/{test_admin['password']}/{page_id}").json())

if test_content:
    if test_get:
        print(get(
            f"{link_website}api/content/{test_admin_without_status['email']}/{test_admin_without_status['password']}/10").json())
        print(get(f"{link_website}api/content/{test_admin['email']}/{test_admin['password']}/10").json())

    # По защищённости всё тоже самое, что и раньше, по функциональности всё работает отлично
    print(post(f"{link_website}api/content/{test_admin['email']}/{test_admin['password']}",
               json={"type": "image", "position": -13, "page_id": 1, "id": 20}).json())
    print(get(f"{link_website}api/content/{test_admin['email']}/{test_admin['password']}/20").json())
    print(put(f"{link_website}api/content/{test_admin['email']}/{test_admin['password']}/20",
              json={"position": -685}).json())
    print(delete(f"{link_website}api/content/{test_admin['email']}/{test_admin['password']}/20").json())

params = {"heading": "Первая новость на сайте", "text": "Теперь на сайте можно создавать новости, вот это круто!",
          "tags": "технологии", "id": page_id}
if test_newspage:
    if test_post:
        print("Админ, с нулевым стасусом не может создать страницу", post(
            f"{link_website}api/newspage/{test_admin_without_status['email']}/{test_admin_without_status['password']}",
            json=params).json())
        print("Пропущен важный аргумент для создания", post(
            f"{link_website}api/newspage/{test_admin['email']}/{test_admin['password']}",
            json={"heading": "some head"}).json())
        print("Админ создаёт страницу, всё хорошо", post(
            f"{link_website}api/newspage/{test_admin['email']}/{test_admin['password']}", json=params).json())

    post(f"{link_website}api/newspage/{test_admin['email']}/{test_admin['password']}", json=params)
    if test_get:
        print("Админ со статусом ниже 1 не может получить страницу по id",
              get(
                  f"{link_website}api/newspage/{test_admin_without_status['email']}/{test_admin_without_status['password']}/{page_id}").json())
        print("Простой человек может получить страницу па id", get(f"{link_website}api/newspage/{page_id}").json())
        print("Админ получает страницу по id",
              get(f"{link_website}api/newspage/{test_admin['email']}/{test_admin['password']}/{page_id}").json())
        print("Любой пользователь может получить список страниц", get(f"{link_website}api/newspage").json())
    if test_put:
        print("Админ со статусом, ниже 1 не может менять", put(
            f"{link_website}api/newspage/{test_admin_without_status['email']}/{test_admin_without_status['password']}/{page_id}",
            json={"heading": "Может быть и не самая первая новость"}).json())
        print("Админ может изменить страницу", put(
            f"{link_website}api/newspage/{test_admin['email']}/{test_admin['password']}/{page_id}",
            json={"heading": "Может быть и не самая первая новость"}).json())
    if test_delete:
        print("Админ со статусом доступа ниже 1 не может удалить страницу", delete(
            f"{link_website}api/newspage/{test_admin_without_status['email']}/{test_admin_without_status['password']}/{page_id}").json())
        post(f"{link_website}api/newspage/{test_admin['email']}/{test_admin['password']}",
             json=params)
        print("Админ может удалить страницу", delete(
            f"{link_website}api/newspage/{test_admin['email']}/{test_admin['password']}/{page_id}").json())

params = {"name": "Гугл", "image": "standard.png", "text": "Да да, наш партнёр гугл!", "link": "google.com",
          "id": page_id}
if test_partner:
    if test_post:
        print("Админ, с нулевым стасусом не может создать партнёра", post(
            f"{link_website}api/partner/{test_admin_without_status['email']}/{test_admin_without_status['password']}",
            json=params).json())
        print("Пропущен важный аргумент для создания", post(
            f"{link_website}api/partner/{test_admin['email']}/{test_admin['password']}",
            json={"name": "some name"}).json())
        print("Админ создаёт партёра, всё хорошо", post(
            f"{link_website}api/partner/{test_admin['email']}/{test_admin['password']}", json=params).json())

    post(f"{link_website}api/partner/{test_admin['email']}/{test_admin['password']}", json=params)
    if test_get:
        print("Админ со статусом ниже 1 не может получить партнёра по id",
              get(
                  f"{link_website}api/partner/{test_admin_without_status['email']}/{test_admin_without_status['password']}/{page_id}").json())
        print("Простой человек может получить партнёра па id", get(f"{link_website}api/partner/{page_id}").json())
        print("Админ получает партнёра по id",
              get(f"{link_website}api/partner/{test_admin['email']}/{test_admin['password']}/{page_id}").json())
        print("Любой пользователь может получить список партнёров", get(f"{link_website}api/partner").json())
    if test_put:
        print("Админ со статусом, ниже 1 не может менять", put(
            f"{link_website}api/partner/{test_admin_without_status['email']}/{test_admin_without_status['password']}/{page_id}",
            json={"name": "Яндекс"}).json())
        print("Админ может изменить партнёра", put(
            f"{link_website}api/partner/{test_admin['email']}/{test_admin['password']}/{page_id}",
            json={"name": "Яндекс"}).json())
    if test_delete:
        print("Админ со статусом доступа ниже 1 не может удалить партнёра", delete(
            f"{link_website}api/partner/{test_admin_without_status['email']}/{test_admin_without_status['password']}/{page_id}").json())
        post(f"{link_website}api/partner/{test_admin['email']}/{test_admin['password']}", json=params)
        print("Админ может удалить партнёра", delete(
            f"{link_website}api/partner/{test_admin['email']}/{test_admin['password']}/{page_id}").json())

if test_feedback:
    print(post(f"{link_website}api/feedback/WMN1E6",
               json={"email": "admin@gmail.com", "fullname": "Шамков Николай Николаевич",
                     "heading": "Какой-то заголовок", "image": "standard.png",
                     "text": "Мне нравиться ваш сайт!"}).json())

if test_auditlog:
    print(get(f"{link_website}api/auditlog/{test_admin['email']}/{test_admin['password']}/1").json())
    for log in get(f"{link_website}api/auditlog/{test_admin['email']}/{test_admin['password']}").json()["Записи"]:
        print(log)
