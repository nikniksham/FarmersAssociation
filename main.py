import datetime
import os


class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password


class PasswordManager:
    def __init__(self):
        self.data = {}

    def add_user(self, email, password):
        self.data[email] = User(email, password)
        return "Пользователь успешно добавлен"

    def delete_user(self, email):
        if email in list(self.data.keys()):
            new_data = {}
            for key in list(self.data.keys()):
                if key != email:
                    new_data[key] = self.data[key]
            self.data = new_data
            return "Пользователь успешно удалён"
        return "Пользователь уже удалён"

    def get_password(self, email):
        if email in list(self.data.keys()):
            return self.data[email].password
        return False


class ImageContainer:
    def __init__(self, filenames):
        self.image_container = {}
        for imageIndex, filename in enumerate(filenames, start=1):
            self.image_container[f"image{imageIndex}"] = filename

    def get_dict(self):
        return self.image_container


class ManagerContainer:
    def __init__(self):
        self.delete_superfluous_image = DeleteSuperfluousImage()
        self.containers = {}

    def add_container(self, name, filenames, auto_delete=False):
        self.containers[name] = ImageContainer(filenames)
        if auto_delete:
            self.delete_superfluous_image.create_container(name, filenames)

    def delete_container(self, name):
        if name in self.containers:
            self.delete_superfluous_image.delete_container(name)
            new_container = {}
            for container in self.containers.keys():
                if name != container:
                    new_container[container] = self.containers[container]
            self.containers = new_container

    def get_container(self, name):
        if name in self.containers:
            return self.containers[name].get_dict()
        return {}

    def clear_container(self, folder):
        self.delete_superfluous_image.clear_container(folder)


class DeleteSuperfluousImage:
    def __init__(self):
        self.container = {}

    def create_container(self, name, filenames):
        self.container[name] = [filenames, datetime.datetime.now()]

    def delete_container(self, name):
        if name in self.container:
            new_container = {}
            for container in self.container.keys():
                if name != container:
                    new_container[container] = self.container[container]
            self.container = new_container

    def clear_container(self, folder):
        for images, created_date in self.container.values():
            if (datetime.datetime.now() - created_date).total_seconds() > 1800:
                for image in images:
                    if image not in ["", "standard.png"] and os.path.exists(f"{folder}{image}"):
                        os.remove(f"{folder}{image}")


def text_transform(text, filenames, path):  # Я не знаю, как это работает, это писал безумный человек
    # крейзи здесь
    text = "".join(text.split("\r"))
    commands = ['br>', 'p>', 'b>', 'h>', 'image ', 'a ', '/p>', '/b>', '/h>', '/a>', "a>", "image>", '\n']
    text = text.split('<')
    start_p = False
    tegs = []
    res = ""
    for data in text:
        for i, elem in enumerate(data.split("\n")):
            if i != 0:
                elem = "br>" + elem
            # elem = "<br>".join(elem.split("\n"))
            if any([elem.lower().startswith(com) for com in commands]):
                if elem.lower().find('\n') > -1:
                    elem.lower().find('\n')
                    elem = "<br>".join(elem.split("\n"))
                    continue
                if elem.lower().startswith('br>'):
                    res += "<br>" + elem[3:]
                elif elem.lower().startswith('p>'):
                    tegs.append('p')
                    if not start_p:
                        res += "<p>"
                        start_p = True
                    res += "<i>"
                    res += elem[2:]
                elif elem.lower().startswith('/p>'):
                    if len(tegs) == 0:
                        return "Error: тэг p не был открыт"
                    elif tegs[-1] == 'p':
                        tegs.pop(-1)
                    else:
                        return f'Error: тэг {tegs[-1]} не был закрыт'
                    res += "</i>"
                    res += elem[3:]
                elif elem.lower().startswith('b>'):
                    if not start_p:
                        res += "<p>"
                        start_p = True
                    tegs.append('b')
                    res += "<b>"
                    res += elem[2:]
                elif elem.lower().startswith('/b>'):
                    if len(tegs) == 0:
                        return "Error: тэг b не был открыт"
                    elif tegs[-1] == 'b':
                        tegs.pop(-1)
                    else:
                        return f'Error: тэг {tegs[-1]} не был закрыт'
                    res += "</b>"
                    res += elem[3:]
                elif elem.lower().startswith('h>'):
                    if start_p:
                        res += "</p>"
                    tegs.append('h')
                    res += "<p class='title'>"
                    res += elem[2:]
                elif elem.lower().startswith('/h>'):
                    if len(tegs) == 0:
                        return "Error: тэг h не был открыт"
                    elif tegs[-1] == 'h':
                        tegs.pop(-1)
                    else:
                        return f'Error: тэг {tegs[-1]} не был закрыт'
                    res += "</p>"
                    start_p = False
                    res += elem[3:]
                elif elem.lower().startswith('image>'):
                    return "Error: нет картинки в теге image"
                elif elem.lower().startswith('image') and (elem.lower().split()[1].split('>')[0].isdigit() or elem.lower().split()[1].split('>')[0][0] == "-" and elem.lower().split()[1].split('>')[0][1:].isdigit()):
                    if start_p:
                        res += "</p>"
                        start_p = False
                    if len(filenames) <= int(elem.lower().split()[1].split('>')[0]) - 1 or int(elem.lower().split()[1].split('>')[0]) - 1 < 0:
                        return f'Error: нет такой картинки {elem.lower().split()[1].split(">")[0]}'
                    res += f"<div><img src='/{path}{filenames[int(elem.lower().split()[1].split('>')[0])-1]}'></div>"
                elif elem.lower().startswith('a>'):
                    return "Error: нет ссылки в теге a"
                elif elem.lower().startswith('a') and elem.find('>') > -1:
                    if not start_p:
                        res += "<p>"
                        start_p = True
                    tegs.append('a')
                    res += f"<a href='{elem.split()[1].split('>')[0]}'>"
                    res += elem.split('>')[1]
                elif elem.lower().startswith('/a>'):
                    if len(tegs) == 0:
                        return "Error: тэг a не был открыт"
                    elif tegs[-1] == 'a':
                        tegs.pop(-1)
                    else:
                        return f'Error: тэг {tegs[-1]} не был закрыт'
                    res += "</a>"
                    res += elem[3:]
            else:
                if not start_p:
                    res += "<p>"
                    start_p = True
                if ">" in elem:
                    return "Error: нет тега " + elem.split(">")[0]
                if elem in text[1:]:
                    res += "<" + elem
                else:
                    res += elem
    if tegs != []:
        return f"Error: тег {tegs[-1]} не был закрыт"
    if start_p:
        res += "</p>"
    return res


def mini_text(text):  # Я не знаю, как это работает, это умный писал человек
    # умный здесь
    res = ""
    for elem in text.split("<"):
        if ">" in elem:
            res += " " + elem[elem.find(">")+1:].strip()
        else:
            res += " " + elem.strip()
    tmp = ""
    for word in res.split():
        if len(word) > 20:
            word = word[:17] + "..."
        if len((tmp + " " + word).strip()) > 200:
            break
        tmp += " " + word
    return tmp.strip()


if __name__ == '__main__':
    print('test for mini text')
    print(mini_text("teeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeext"))
    print(mini_text("<a />teext</a>"))
    print(mini_text("<p>teext</p>"))
    print(mini_text("<b>teext</b>"))
    print(mini_text("<b>teext</b><br><p>teext</p><br><yes>"))
    print(mini_text("<yes>"))
    print(mini_text("<b>Мы почти сделали сайт, нам осталось совсем чуть чуть!</b><br>Много текста.<p>И немного курсивом</p>, а <p><b>еще немного жирным курсивом</b></p>!<h>А теперь картинка застолья!</h><image 1><p>Вот и новости конец</p><a />а теперь на главную</a><a /all-news>или на все новости!</a>"))
    print('test news')
    print(text_transform("<p>",[""],"") == "Error: тег p не был закрыт")
    print(text_transform("<a https://rostec.ru/ Ссылка на ростех</a>", ["", ""], "") == "Error: тэг a не был открыт")
    print(text_transform("a\na", ["", ""], "") == "<p>a<br>a</p>")
    print(text_transform("<a></a>", ["", ""], "") == "Error: нет ссылки в теге a")
    print(text_transform("<image>", ["", ""], "") == "Error: нет картинки в теге image")
    print(text_transform("<afafa>", ["", ""], "") == "Error: нет тега afafa")
    print(text_transform("<gei>", ["", ""], "") == "Error: нет тега gei")
    print(text_transform("<image -2141>", ["", ""], "") == "Error: нет такой картинки -2141")
    print(text_transform("<p>a\na", ["", ""], "") == "Error: тег p не был закрыт")
    print(text_transform("Урааа, у нас теперь можно писать новости<br><br><p>Текст курсивом</p><h>Какой-то заголовок</h><image 1><image 2><a https://rostec.ru/%3E Ссылка на ростех</a>", ["", ""], "") == "Error: тэг a не был открыт")
    print(text_transform("this is statya about statyu about statyu about statyu about statyu about statyu kotoraya o statye kotoraya statye I talk about this <a />statya</a><image 1><h>this is imgage fom sobranie</h>", [""], "") == "<p>this is statya about statyu about statyu about statyu about statyu about statyu kotoraya o statye kotoraya statye I talk about this <a href='/'>statya</a></p><div><img src='/'></div><p class='title'>this is imgage fom sobranie</p>")
    print(text_transform("<p><b>iii</b></p><b>bbb</b>", ["", ""], "") == "<p><i><b>iii</b></i><b>bbb</b></p>")
    print(text_transform("<image 1>", ["gei.png"], "foolder/") == "<p></p><div><img src='/foolder/gei.png'></div>")
    print(text_transform("Красивый текст\r\n<b>Толстый</b>\r\n<p>Курсивный</p>\r\n<a 127.0.0.1:8000/>Ссылка на сайт</a>\r\n<image 1>\r\n<h>Заголовок</h>", ["gei.png"], "foolder/"))