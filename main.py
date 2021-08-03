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
