from requests import get, post, put, delete

link_website = 'http://127.0.0.1:8000/'
test_admin = {"email": "admin@gmail.com", "password": "adminsk1"}
test_admin_without_status = {"email": "admin2@gmail.com", "password": "adminsk1"}
test_user = {"email": "admin3@gmail.com", "password": "adminsk1"}

test_get = True
test_post = True
test_put = True
test_delete = True

test_admin_api = True

if test_admin_api:
    if test_post:
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
