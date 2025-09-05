from flask_login import UserMixin

class UserObject(UserMixin):
    def __init__(self, user_id, first_name, last_name, email, role="customer"):
        self.id = user_id
        self.fname = first_name
        self.lname = last_name
        self.email = email
        self.role = role

    def get_id(self):
        return str(self.id)

    def is_admin(self):
        return self.role.lower() == "admin"
