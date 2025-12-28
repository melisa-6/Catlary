from repository.cezalarRepository import cezalarRepository
from repository.odunclerRepository import odunclerRepository

class cezaService:
  
    def __init__(self, db_config):
        self.repo = cezalarRepository(db_config)
        self.odunc_repo = odunclerRepository(db_config) 
        self.repo = cezalarRepository(db_config)
    
    def ceza_odendi_yap(self, kullanici_id, odeme_yapilsin_mi=False, admin=False):
        
        toplam_tutar, success = self.repo.ceza_odendi_yap(kullanici_id, odeme_yapilsin_mi)

        if not success:
            return {"toplam_tutar": 0, "success": False, "message": "Ödenecek borç bulunamadı veya bir hata oluştu."}  

        return {
            "toplam_tutar": toplam_tutar,
            "success": True,
            "message": "Ödeme başarıyla tamamlandı."  
        }
    def odeme_durumu_var_mi(self, kullanici_id):
        return self.repo.odeme_durumu_var_mi(kullanici_id)

    def ceza_bilgilerini_getir(self, ceza_id):
        detaylar = self.repo.ceza_detaylari_getir(ceza_id)
        if not detaylar:
            return None
            
        return {
            "odendi_mi": detaylar.get('odeme_durumu', 0),
            "miktar": float(detaylar.get('miktar', 0)), 
            "username": detaylar.get('username'),
            "gercek_iade": detaylar.get('gercek_iade_tarihi') 
        }
        
    def ceza_ode(self, ceza_id):
        # nce cezanın ve kitabın iade durumunu çeker
        durum = self.repo.ceza_ve_iade_durumu_getir(ceza_id)
        
        if not durum:
            return False, "Ceza kaydı bulunamadı."

        if durum['gercek_iade_tarihi'] is None:
            return False, "Bu kitap henüz iade edilmemiş! Kitap iade edilmeden ceza kesilemez ve ödenemez."

        # Zaten ödenmiş mi kontrolü
        if durum['odeme_durumu'] == 1:
            return False, "Bu ceza zaten ödenmiş."

        #  Her şey tamamsa ödemeyi yapar
        ok = self.repo.ceza_ode(ceza_id)
        if ok:
            return True, "Ceza başarıyla tahsil edildi."
        else:
            return False, "Veritabanı güncelleme hatası."

    def tum_cezalari_getir(self):
           #ilgili repoya  yonlendirir
        return self.repo.tum_cezalari_getir()

 #ilgili repoya  yonlendirir
    def kullanici_cezalari_getir(self, kullanici_id):
        return self.repo.kullanici_cezalari_getir(kullanici_id)
    
#kitabın iade edilip edilmedigini kontrol eder
    def iade_edilmemis_kitap_var_mi(self, kullanici_id):
        return self.repo.cezanin_iade_edilmis_olup_olmadigini_kontrol_et(kullanici_id)

    def borc_getir(self, username):
        user_id = self.repo.kullanici_id_getir(username) 
        if not user_id:
            return 0
        return self.repo.toplam_borc_getir(user_id)
    
    def kullanici_borc_getir_by_id(self, kullanici_id):
        return self.repo.toplam_borc_getir(kullanici_id)

#


