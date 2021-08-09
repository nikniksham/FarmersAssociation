import datetime
import os


class User:
    def __init__(self, email, password, status):
        self.email = email
        self.password = password
        self.status = status


class PasswordManager:
    def __init__(self):
        self.data = {}

    def add_user(self, email, password, status):
        self.data[email] = User(email, password, status)
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

    def get_password(self, email, status):
        if email in list(self.data.keys()):
            if self.data[email].status <= status:
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
    commands = ['br>', 'p>', 'b>', 'h>', 'image ', 'a ', '/p>', '/b>', '/h>', '/a>']
    text = text.split('<')
    start_p = False
    tegs = []
    res = ""
    for elem in text:
        if any([elem.lower().startswith(com) for com in commands]):
            if elem.lower().startswith('br>'):
                res += "<br>"
            elif elem.lower().startswith('p>'):
                tegs.append('p')
                if not start_p:
                    res += "<p>"
                    start_p = True
                res += "<i>"
                res += elem[2:]
            elif elem.lower().startswith('/p>'):
                if tegs[-1] == 'p':
                    tegs.pop(-1)
                else:
                    return f'Error: тэг <{tegs[-1]}> не был закрыт тэгом </{tegs[-1]}>'
                res += "<i>"
                res += elem[3:]
            elif elem.lower().startswith('b>'):
                if not start_p:
                    res += "<p>"
                    start_p = True
                tegs.append('b')
                res += "<b>"
                res += elem[2:]
            elif elem.lower().startswith('/b>'):
                if tegs[-1] == 'b':
                    tegs.pop(-1)
                else:
                    return f'Error: тэг <{tegs[-1]}> не был закрыт тэгом </{tegs[-1]}>'
                res += "</b>"
                res += elem[3:]
            elif elem.lower().startswith('h>'):
                if start_p:
                    res += "</p>"
                tegs.append('h')
                res += "<p class='title'>"
                res += elem[2:]
            elif elem.lower().startswith('/h>'):
                if tegs[-1] == 'h':
                    tegs.pop(-1)
                else:
                    return f'Error: тэг <{tegs[-1]}> не был закрыт тэгом </{tegs[-1]}>'
                res += "</p>"
                start_p = False
                res += elem[3:]
            elif elem.lower().startswith('image') and elem.lower().split()[1].split('>')[0].isdigit():
                if start_p:
                    res += "</p>"
                    start_p = False
                if len(filenames) <= int(elem.lower().split()[1].split('>')[0]) - 1 or int(elem.lower().split()[1].split('>')[0]) - 1 < 0:
                    return f'Error: нет такой картинки {elem.lower().split()[1].split(">")[0]}'
                res += f"<div><img src='/{path}{filenames[int(elem.lower().split()[1].split('>')[0])-1]}'></div>"
            elif elem.lower().startswith('a') and elem.find('>') > -1:
                if not start_p:
                    res += "<p>"
                    start_p = True
                tegs.append('a')
                res += f"<a href='{elem.split()[1].split('>')[0]}'>"
                res += elem.split('>')[1]
            elif elem.lower().startswith('/a>'):
                if tegs[-1] == 'a':
                    tegs.pop(-1)
                else:
                    return f'Error: тэг <{tegs[-1]}> не был закрыт тэгом </{tegs[-1]}> 1'
                res += "</a>"
                res += elem[3:]
        else:
            if not start_p:
                res += "<p>"
                start_p = True
            res += elem
    return res
