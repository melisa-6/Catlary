class Oduncler:
    def __init__(self, kullanici_id, kitap_id, odunc_tarihi, gerekli_iade_tarihi, gercek_iade_tarihi=None, id=None):
        self.id = id  # veritabanı AUTO_INCREMENT ile atanacak
        self.kullanici_id = kullanici_id
        self.kitap_id = kitap_id
        self.odunc_tarihi = odunc_tarihi
        self.gerekli_iade_tarihi = gerekli_iade_tarihi
        self.gercek_iade_tarihi = gercek_iade_tarihi

    def __repr__(self):
        return f"<Odunc Kullanici:{self.kullanici_id} Kitap:{self.kitap_id}>"
