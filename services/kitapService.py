from repository.kitaplarRepository import kitaplarRepository

class kitapService:
    def __init__(self, db_config=None, odunc_service=None):

        self.repo = kitaplarRepository(db_config)  
        self.odunc_service = odunc_service  

    # Tüm kitapları getirmesi icin ilgili repoya yonlendirir
    def tum_kitaplari_getir(self):
        return self.repo.tum_kitaplari_getir()
    def kitap_guncelle(self, kitap_id, isim, 
                        sayfa_sayisi, stok, raf_no, baski_yili,yazar_id, kategori_id, yayinevi_id, resim=None):
        try:
            success = self.repo.kitap_guncelle(
                kitap_id, isim,
                sayfa_sayisi, stok, raf_no, baski_yili,  yazar_id, kategori_id,yayinevi_id, resim
            )
            if success:
                return {"success": True, "message": "Kitap başarıyla güncellendi."}
            else:
                return {"success": False, "message": "Kitap bulunamadı veya değişiklik yapılmadı."}
        except Exception as e:
            print(f"Service Hata: {e}")
            return {"success": False, "message": f"Beklenmeyen hata: {str(e)}"}
        
    #repositorydeki ilgili fonksiyona iletiyoruz
    def kitap_ekle(self, isim, yazar_id, kategori_list, yayinevi,
               sayfa_sayisi, stok, raf_no, baski_yili,resim):

        return self.repo.kitap_ekle(
            isim, yazar_id, kategori_list, yayinevi,
            sayfa_sayisi, stok, raf_no, baski_yili,resim
        )


    def kitap_sil_by_id(self, kitap_id):
        if not kitap_id:
            # ID yoksa uyarı döndürür
            return {"success": False, "message": "Lütfen bir kitap seçin!"}

        try:
            # Repo katmanına iletilir 
            mesaj, silinen_kitap = self.repo.kitap_sil_db_islemi(kitap_id)

            # Eğer kitap gerçekten silindiyse True döndür
            if silinen_kitap:
                return {"success": True, "message": mesaj}
            else:
                return {"success": False, "message": mesaj}

        except Exception as e:
            # DB işlemi hata verirse servis mesaj üretir
            return {"success": False, "message": f"Servis Katmanı Hatası: {str(e)}"}


#ilgili repoya yonlendirir
    def kitap_ara(self, aranan):
        return self.repo.kitap_ara(aranan)

    # gelen id ile uygun repoya yonlendirir
    def get_by_id(self, kitap_id):
        return self.repo.get_by_id(kitap_id)

    
    # gelen isme gore repoya yonlendirir
    def get_by_name(self, isim):
        # girdiyi temizleyeerek repoya yonlendirir
        temiz_isim = isim.strip()
      
        return self.repo.get_by_name(temiz_isim)
