from services.oduncService import oduncService
from services.kitapService import kitapService

class kitapController:
    def __init__(self, db_config):
        self.kitap_service = kitapService(db_config)
        self.odunc_service = oduncService(db_config)

    
    def kitaplari_goruntule_controller(self, username, role, aranan_kitap=""):
        if aranan_kitap:
           kitaplar = self.kitap_service.kitap_ara(aranan_kitap)
        else:
            kitaplar = self.kitap_service.tum_kitaplari_getir()

        admin_mi = role == 'admin'
        
        return kitaplar, admin_mi
        
    def kitap_ekle_controller(self, kitap_adi, yazar_id, kategori_id, sayfa_sayisi, stok_miktari, raf_no, baski_yili, yayinevi):
        try:
            # Gelen verileri servise iletiyoruz
            return self.kitap_service.kitap_ekle(
                kitap_adi, yazar_id, kategori_id, sayfa_sayisi, 
                stok_miktari, raf_no, baski_yili, yayinevi
            )
        except Exception as e:
            print(f"Controller HATA: Kitap eklenemedi: {e}")
            return False

    def kitap_sil_controller(self, kitap_id):
        try:
            kitap_id = int(kitap_id)
        except (ValueError, TypeError):
            return "Hata: Kitap ID geçerli değil.", "Kitap Silme Hatası", False

        try:
            sonuc = self.kitap_service.kitap_sil_by_id(kitap_id)

            if sonuc.get('success'):
                return sonuc.get('message', "Kitap başarıyla silindi."), "Kitap Silme", True
            else:
                return sonuc.get('message', "Kitap silinemedi."), "Kitap Silme Hatası", False

        except Exception as e:
            print(f"Kitap Silme Hatası: {e}")
            return f"Beklenmedik hata: {str(e)}", "Kitap Silme Hatası", False