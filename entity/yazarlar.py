
# entity/yazar.py
class Yazarlar:
    def __init__(self, id=None, isim=None):
        self.id = id
        self.isim = isim
      

    def __repr__(self):
        return f"<Yazar {self.isim} (ID: {self.id})>"