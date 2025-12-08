from repository.kitaplarRepository import kitaplarRepository

class kitapService:
    def __init__(self, db_config=None, odunc_service=None):

        self.repo = kitaplarRepository(db_config)  
        self.odunc_service = odunc_service  

    # Tüm kitapları getirir
    def tum_kitaplari_getir(self):
        return self.repo.tum_kitaplari_getir()

        
    def kitap_ekle(self, isim, yazar, kategori, yayinevi, sayfa_sayisi, stok, raf_no, baski_yili):
        try:
      #gelen sayisal degerleri int e cevirir ve bosluklari siler 
            sayfa_sayisi = int(str(sayfa_sayisi).strip())
            stok = int(str(stok).strip())
            raf_no = int(str(raf_no).strip())
            baski_yili = int(str(baski_yili).strip())
        except ValueError:
            return "Hata: Sayısal alanlarda geçersiz değer var", None
#uygun repoya yonlendirir
        return self.repo.kitap_ekle(isim, yazar, kategori, yayinevi, sayfa_sayisi, stok, raf_no, baski_yili)

    def kitap_sil_by_id(self, kitap_id):
        if not kitap_id:
            return {"success": False, "message": "Lütfen bir kitap seçin!"}

        try:
            mesaj, silinen_kitap = self.repo.kitap_sil_db_islemi(kitap_id)
            if silinen_kitap:
                return {"success": True, "message": mesaj}
            else:
                return {"success": False, "message": mesaj}
        except Exception as e:
            return {"success": False, "message": f"Servis Katmanı Hatası: {str(e)}"}

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
