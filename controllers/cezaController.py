from services.cezaService import CezaService
from services.kullaniciService import KullaniciService

db_config = {
    "host": "localhost",
    "user": "melisa",
    "password": "Mtz0504*",
    "database": "kutuphane_db"
}

class CezaController:
    def __init__(self, db_config):
        self.ceza_service = CezaService(db_config)
        self.kullanici_service = KullaniciService(db_config)

    def tum_cezalari_getir(self):
        try:
            #tum cezalari getirmesi icin service e yonlendirir
            cezalar = self.ceza_service.tum_cezalari_getir()
            return cezalar
        except Exception as e:
            print(f"Controller hatası - tüm cezalar: {e}")
            return []

    def kullanici_cezalarini_goster(self, username):
        #kullaniciyi bulmak icin serviceden uygun fonksiyon username ile gonderilir
     kullanici = self.kullanici_service.get_by_username(username)
     if not kullanici:
         #kullanici bulunamadiysa hata verir
        print(f"Kullanıcı bulunamadı: {username}")
        return []  
    #kullanici id si ile kullanicinin cezalari getirmek icin uygun kontrollere gonderilir
     cezalar = self.ceza_service.kullanici_cezalari_getir(kullanici['id'])
     return cezalar


    def ceza_odendi_yap(self, kullanici_id, odeme_yapilsin_mi=False):
        try:
            #kullaniic id int e donusturulut 
            kullanici_id = int(kullanici_id)
            
            # Service toplam tutarı hesaplar ve ödeme yaparsa güncellemek icin service e yonlendirir
            toplam_tutar = self.ceza_service.ceza_odendi_yap(kullanici_id, odeme_yapilsin_mi)
            
            success = odeme_yapilsin_mi and toplam_tutar > 0
            message = "Ödeme tamamlandı" if success else f"Toplam tutar: {toplam_tutar} TL"
            
            return {"toplam_tutar": toplam_tutar, "success": success, "message": message}

        except ValueError:
            return {"toplam_tutar": 0, "success": False, "message": "Geçersiz Kullanıcı ID"}
        except Exception as e:
            return {"toplam_tutar": 0, "success": False, "message": f"Hata: {str(e)}"}