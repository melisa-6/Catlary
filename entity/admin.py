# entity/admin.py
class Adminler:
    def __init__(self, id=None, username=None, email=None, password=None):
        # id = None olarak bırakıyoruz, veritabanı eklediğinde otomatik artacak
        self.id = id
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return f"<Admin {self.username} (ID: {self.id})>"
