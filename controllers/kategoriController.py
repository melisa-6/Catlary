from services.kategoriService import KategoriService

class KategoriController:
    def __init__(self, db_config): 
       self.service = KategoriService()  
    def tum_kategorileri_getir_controller(self):
        try:
             return self.service.tum_kategoriler()
        except Exception as e:
            print(f"Controller HATA: Kategoriler çekilemedi: {e}")
            return []

    def kategoriekle_controller(self, kategori_adi):
        # Aynı kategori var mı kontrolü
        mevcut = self.service.kategori_bul(kategori_adi)

        if mevcut:
            return False, "Bu kategori zaten mevcut!"

        # Ekleme işlemi
        self.service.kategori_ekle(kategori_adi)
        return True, "Kategori başarıyla eklendi."

    def kategori_sil_controller(self, id):
        if self.service.kitap_var_mi(id):
            return False, "HATA: Bu kategoride kayıtlı kitaplar var! Önce o kitapları silmelisiniz."

        # Kitap yoksa silme işlemini yap
        basarili = self.service.kategori_sil(id)
        if basarili:
            return True, "Kategori başarıyla silindi."
        return False, "Silme işlemi sırasında hata oluştu."