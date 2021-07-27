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

test_admin_api = False
test_smartpage_api = False
test_content = False
test_auditlog = False

if test_admin_api:
    if test_post:
        print(post(f"{link_website}api/admin/{test_admin['email']}/{test_admin['password']}",
                   json={"name": 'Админ', "email": test_user["email"], "password": test_user["password"]}).json())
        print(post(f"{link_website}api/admin/{test_admin['email']}/{test_admin['password']}",
                   json={"name": 'Админ', "surname": "Админович", "email": test_user["email"],
                         "password": test_user["password"]}).json())
        print(post(
            f"{link_website}api/admin/{test_admin_without_status['email']}/{test_admin_without_status['password']}",
            json={"name": 'Админ', "surname": "Админович", "email": test_user["email"],
                  "password": test_user["password"]}).json())
    post(f"{link_website}api/admin/{test_admin['email']}/{test_admin['password']}",
         json={"name": 'Админ', "surname": "Админович", "email": test_user["email"],
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
             json={"name": 'Админ', "surname": "Админович", "email": test_user["email"],
                   "password": test_user["password"], "status": 0}).json()
        print("не может удалить сам себя по id, если статус ниже 1",
              delete(f"{link_website}api/admin/{test_user['email']}/{test_user['password']}/{new_admin_id}").json())
        post(f"{link_website}api/admin/{test_admin['email']}/{test_admin['password']}",
             json={"name": 'Админ', "surname": "Админович", "email": test_user["email"],
                   "password": test_user["password"], "status": 0}).json()
        print("другой админ удаляет по id",
              delete(f"{link_website}api/admin/{test_admin['email']}/{test_admin['password']}/{new_admin_id}").json())
        post(f"{link_website}api/admin/{test_admin['email']}/{test_admin['password']}",
             json={"name": 'Админ', "surname": "Админович", "email": test_user["email"],
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
               json={"type": "image", "position": -13, "page_id": 2, "id": 20}).json())
    print(get(f"{link_website}api/content/{test_admin['email']}/{test_admin['password']}/20").json())
    print(put(f"{link_website}api/content/{test_admin['email']}/{test_admin['password']}/20",
              json={"position": -685}).json())
    print(delete(f"{link_website}api/content/{test_admin['email']}/{test_admin['password']}/20").json())

if test_auditlog:
    print(get(f"{link_website}api/auditlog/{test_admin['email']}/{test_admin['password']}/1").json())
    for log in get(f"{link_website}api/auditlog/{test_admin['email']}/{test_admin['password']}").json()["Запись"]:
        print(log)
