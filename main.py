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
        self.containers = {}

    def add_container(self, name, filenames):
        self.containers[name] = ImageContainer(filenames)

    def delete_container(self, name):
        if name in self.containers:
            new_container = {}
            for container in self.containers.keys():
                if name != container:
                    new_container[container] = self.containers[container]
            self.containers = new_container

    def get_container(self, name):
        if name in self.containers:
            return self.containers[name].get_dict()
        return None
