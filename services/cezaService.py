from repository.cezalarRepository import cezalarRepository
from repository.odunclerRepository import odunclerRepository

class cezaService:
  
    def __init__(self, db_config):
        self.repo = cezalarRepository(db_config)
        self.odunc_repo = odunclerRepository(db_config) 
        self.repo = cezalarRepository(db_config)

    def odeme_durumu_var_mi(self, kullanici_id):
        return self.repo.odeme_durumu_var_mi(kullanici_id)
  
    def ceza_bilgilerini_getir(self, ceza_id):
        """Ceza miktarı, kullanıcı adı ve ödeme durumunu getirir."""
        
    
        detaylar = self.repo.ceza_detaylari_getir(ceza_id)

        if not detaylar:
            return None
            
        return {
            "odendi_mi": detaylar.get('odeme_durumu', 0),
            "miktar": float(detaylar.get('miktar', 0)), # Miktarı float yapalım
            "username": detaylar.get('username')
        }
    def ceza_ode(self, ceza_id):
        ceza = self.repo.ceza_durumu_getir(ceza_id)
        if not ceza:
            return False, "Ceza bulunamadı."

        if ceza['odeme_durumu']:
            return False, "Ceza zaten ödenmiş."

        if not ceza['iade_tarihi']:
            return False, "Kitap iade edilmemiş, ödeme yapılamaz."

        ok = self.repo.ceza_ode(ceza_id)
        if ok:
            return True, "Ceza başarıyla ödendi."
        else:
            return False, "Ödeme sırasında hata oluştu."

    def tum_cezalari_getir(self):
        return self.repo.tum_cezalari_getir()

    def kullanici_cezalari_getir(self, kullanici_id):
        return self.repo.kullanici_cezalari_getir(kullanici_id)

    def iade_edilmemis_kitap_var_mi(self, kullanici_id):
        return self.repo.iade_edilmemis_kitap_var_mi(kullanici_id)

    def borc_getir(self, username):
        user_id = self.repo.kullanici_id_getir(username) 
        if not user_id:
            return 0
        return self.repo.toplam_borc_getir(user_id)
    
    def kullanici_borc_getir_by_id(self, kullanici_id):
        return self.repo.toplam_borc_getir(kullanici_id)

    def ceza_odendi_yap(self, kullanici_id, odeme_yapilsin_mi=False, admin=False):
        if self.iade_edilmemis_kitap_var_mi(kullanici_id):
            return {"toplam_tutar": 0, "success": False, "message": "Kitap iade edilmeden ceza ödenemez!"}

        toplam_tutar, success = self.repo.ceza_odendi_yap(kullanici_id, odeme_yapilsin_mi)

        if not success:
            return {"toplam_tutar": 0, "success": False, "message": toplam_tutar}  

        return {
            "toplam_tutar": toplam_tutar,
            "success": True,
            "message": "Ödeme tamamlandı."  
        }


