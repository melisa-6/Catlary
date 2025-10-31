from repository.kitaplarRepository import KitaplarRepository

class KitapService:
    def __init__(self, db_config=None, odunc_service=None):

        self.repo = KitaplarRepository(db_config)  
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
            return "Lütfen bir kitap seçin!", None

        mesaj, silinen_kitap = self.repo.kitap_sil_by_id(kitap_id)
        return mesaj, silinen_kitap

    #repoya yonlendirir
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
