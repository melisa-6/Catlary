# entity/kategori.py
class Kategoriler:
    def __init__(self, id=None, kategori_adi=None):
        self.id = id
        self.kategori_adi = kategori_adi
        
    def __repr__(self):
        return f"<Kategori {self.kategori_adi} (ID: {self.id})>"