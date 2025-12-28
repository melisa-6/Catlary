from repository.yayinevleriRepository import YayinevleriRepository

class YayineviService:
    def __init__(self, db_config):
        
        self.repo = YayinevleriRepository(db_config)   
          
    def tum_yayinevleri(self):
        return self.repo.tum_yayinevleri()
    
    def yayinevi_ekle(self, ad):
        try:
            if not ad or ad.strip() == "":
                return False, "Yayınevi adı boş olamaz!"

            mevcut_yayinevi = self.repo.isme_gore_getir(ad)
            
            if mevcut_yayinevi:
                return False, f"'{ad}' isminde bir yayınevi zaten sistemde kayıtlı!"

            self.repo.yayinevi_ekle(ad)
            return True, "Yayınevi başarıyla eklendi."
            
        except Exception as e:
            return False, f"Ekleme işlemi sırasında hata: {str(e)}"

    def yayinevi_sil(self, id):
        try:
            print(f"--- SİLME İŞLEMİ BAŞLADI (ID: {id}) ---") 
            
            kitap_sayisi = self.repo.yayinevine_ait_kitap_sayisi(id)
            print(f"--- BULUNAN KİTAP SAYISI: {kitap_sayisi} ---") 
            
            if kitap_sayisi > 0:
                print("--- SİLME İPTAL EDİLDİ (KİTAP VAR) ---") 
                return False, f"Bu yayınevine bağlı {kitap_sayisi} kitap var! Silemezsiniz."

            print("--- KİTAP YOK, SİLİNİYOR... ---") 
            self.repo.yayinevi_sil(id)
            return True, "Yayınevi başarıyla silindi."
            
        except Exception as e:
            hata_mesaji = str(e)
            if "1451" in hata_mesaji:
                return False, "Bu yayınevine kayıtlı kitaplar olduğu için SİLEMEZSİNİZ! Önce kitapları silin veya düzenleyin."
            
            return False, f"Bir hata oluştu: {hata_mesaji}"