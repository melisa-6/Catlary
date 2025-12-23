from services.yayineviService import YayineviService

class YayineviController:
    def __init__(self, db_config):
        self.service = YayineviService(db_config)
        
    def yayinevleri_getir_controller(self):
        try:
             return self.service.tum_yayinevleri()
        except Exception as e:
            print(f"Controller HATA: Yayınevleri çekilemedi: {e}") 
            return []

    def yayinevi_ekle(self, ad):
        try:
            return self.service.yayinevi_ekle(ad) 
        except Exception as e:
            print(f"Controller HATA: Yayınevi eklenemedi: {e}")
            return False, f"Ekleme işleminde hata: {str(e)}"

    def yayinevi_sil(self, id):
        try:
            if not id:
                return False, "Geçersiz ID."
            return self.service.yayinevi_sil(id)
        except Exception as e:
            print(f"Controller HATA: Yayınevi silinemedi: {e}")
            return False, f"Silme işleminde hata: {str(e)}"