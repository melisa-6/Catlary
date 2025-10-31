class Kullanicilar:
    def __init__(self, username, aktiflik=True, email=None, password=None, id=None):
        self.id = id  # veritabanı AUTO_INCREMENT ile atanacak
        self.username = username
        self.aktiflik = aktiflik
        self.email = email
        self.password = password

    def __repr__(self):
        return f"<Kullanici {self.username}>"
