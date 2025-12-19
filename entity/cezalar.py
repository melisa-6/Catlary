class Cezalar:
    def __init__(self,id, kullanici_id, kitap_id, ceza_miktari, odunc_tarihi, iade_tarihi, odeme_durumu,ilk_gecikme_mail_tarihi,son_gecikme_mail_tarihi ):
        self.id = id  # veritabanında AUTO_INCREMENT ile atanacak
        self.kullanici_id = kullanici_id
        self.kitap_id = kitap_id
        self.ceza_miktari = ceza_miktari
        self.odunc_tarihi = odunc_tarihi
        self.iade_tarihi = iade_tarihi
        self.odeme_durumu = bool(odeme_durumu)
        self.ilk_gecikme_mail_tarihi=ilk_gecikme_mail_tarihi
        self.son_gecikme_mail_tarihi=son_gecikme_mail_tarihi        
        

    def __repr__(self):
        return f"<Ceza Kullanici:{self.kullanici_id} Kitap:{self.kitap_id} Ceza:{self.ceza_miktari} Durum:{self.odeme_durumu}>"
