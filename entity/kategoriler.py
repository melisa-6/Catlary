# entity/kategori.py
class Kategoriler:
    def __init__(self, id=None, isim=None, aciklama=None):
        self.id = id
        self.isim = isim
        self.aciklama = aciklama

    def __repr__(self):
        return f"<Kategori {self.isim} (ID: {self.id})>"