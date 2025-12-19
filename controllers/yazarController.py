from services.yazarService import YazarService

class YazarController:
    def __init__(self):
        self.service = YazarService()

    def tum_yazarlari_getir_controller(self):
        #uygun service e yonlendirir
        try:
            return self.service.tum_yazarlar()
        except Exception as e:
            print(f"Controller HATA: Yazarlar çekilemedi: {e}")
            return []

    def yazarekle_controller(self, ad):
        mevcut = self.service.yazar_bul(ad)
#yazar mevcutsa hata verir
        if mevcut:
            return False, "Bu yazar zaten kayıtlı!"
#mevcut deilse eklemek icin ilgili service yonlendirir
        self.service.yazar_ekle(ad)
        return True, "Yazar başarıyla eklendi."

    def yazar_sil_controller(self, id):
        if self.service.kitap_var_mi(id):
            #yazara ait kitap varsa silinemez hatası
            return False, "Bu yazara ait kitaplar var! Önce o kitapları silin."

        basarili = self.service.yazar_sil(id)
        #kitabı yoksa service e yonlendir
        if basarili:
            return True, "Yazar başarıyla silindi."
        
        return False, "Silme sırasında hata oluştu."
