from services import cezaService
from services.cezaService import cezaService
from services.kullaniciService import kullaniciService

class cezaController:
    def __init__(self, db_config):
        self.ceza_service = cezaService(db_config)
        self.kullanici_service = kullaniciService(db_config)
    def odeme_yap_controller(self, kullanici_id):
        try:
            return self.ceza_service.ceza_odendi_yap(kullanici_id, odeme_yapilsin_mi=True)
        except Exception as e:
            print(f"Controller hatası - ödeme yap: {e}")
            return {"toplam_tutar": 0, "success": False, "message": "Ödeme işlemi başarısız."}
    # Tüm cezaları getir (admin)
    def tum_cezalari_getir(self):
        try:
            return self.ceza_service.tum_cezalari_getir()
        except Exception as e:
            print(f"Controller hatası - tüm cezalar: {e}")
            return []
    def ceza_odendi_yap(self, kullanici_id, odeme_yapilsin_mi, kart_numarasi=None, admin=False):
        return self.ceza_service.ceza_odendi_yap(kullanici_id, odeme_yapilsin_mi, admin=admin)
    def ceza_ode(self, ceza_id):
        success, message = self.ceza_service.ceza_ode(ceza_id)
        return success, message

    def kullanici_cezalarini_goster(self, username):
        kullanici = self.kullanici_service.get_by_username(username)
        if not kullanici:
            return []
        return self.ceza_service.kullanici_cezalari_getir(kullanici['id'])

    def borc_getir_controller(self, username):
        
        kullanici = self.kullanici_service.get_by_username(username)
        if not kullanici:
            print(f"Kullanıcı bulunamadı: {username}")
            return 0  # Borç yok

        user_id = kullanici['id']
        print(f"DEBUG: user_id: {user_id}")
        toplam_borc = self.ceza_service.kullanici_borc_getir_by_id(user_id)
        print(f"DEBUG: {username} ödenmemiş toplam borç: {toplam_borc}")

        return toplam_borc

    def borc_getir_by_id(self, kullanici_id):
       
        try:
            return self.ceza_service.kullanici_borc_getir_by_id(kullanici_id)
        except Exception as e:
            print(f"Controller hatası - borç getirme: {e}")
            return 0

    def iade_edilmemis_kitap_var_mi_controller(self, username):
        kullanici = self.kullanici_service.get_by_username(username)
        if not kullanici:
            return True
        return self.ceza_service.iade_edilmemis_kitap_var_mi(kullanici['id'])
    def ceza_bilgilerini_getir(self, ceza_id):
        try:
            return self.ceza_service.ceza_bilgilerini_getir(ceza_id)
        except Exception as e:
            print("Controller hata - ceza sorgula:", e)
            return None
