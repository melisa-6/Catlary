
# entity/yazar.py
class Yazarlar:
    def __init__(self, id=None, isim=None, dogum_tarihi=None, email=None):
        self.id = id
        self.isim = isim
        self.dogum_tarihi = dogum_tarihi  # opsiyonel tarih bilgisi
        self.email = email

    def __repr__(self):
        return f"<Yazar {self.isim} (ID: {self.id})>"