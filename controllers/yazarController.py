from services.yazarService import YazarService

class YazarController:
    def __init__(self):
        self.service = YazarService()

    def tum_yazarlari_getir_controller(self):
        try:
            return self.service.tum_yazarlar()
        except Exception as e:
            print(f"Controller HATA: Yazarlar çekilemedi: {e}")
            return []

    def yazarekle_controller(self, ad):
        mevcut = self.service.yazar_bul(ad)

        if mevcut:
            return False, "Bu yazar zaten kayıtlı!"

        self.service.yazar_ekle(ad)
        return True, "Yazar başarıyla eklendi."

    def yazar_sil_controller(self, id):
        if self.service.kitap_var_mi(id):
            return False, "Bu yazara ait kitaplar var! Önce o kitapları silin."

        basarili = self.service.yazar_sil(id)
        if basarili:
            return True, "Yazar başarıyla silindi."
        
        return False, "Silme sırasında hata oluştu."
