from repository.cezalarRepository import CezaRepository

class CezaService:
    def __init__(self, db_config):
        self.repo = CezaRepository(db_config)
    
     #kullanicinin odeme durumunun olup olmadıgını kontrol etmesi icin repository e yonlendirir
    def odeme_durumu_var_mi(self, kullanici_id):
        return self.repo.odeme_durumu_var_mi(kullanici_id)
  
     #ceza eklemek icin repository e yonlendirir
    def ceza_ekle(self, kullanici_id, miktar, aciklama):
        return self.repo.ceza_ekle(kullanici_id, miktar, aciklama)
  
     #ceza silmek icin repository e yonlendirir
    def ceza_sil(self, ceza_id):
        return self.repo.ceza_sil(ceza_id)
    
     #kullanicinin ceza getirmek icin repository e yonlendirir
    def kullanici_cezalari_getir(self, kullanici_id):
        return self.repo.kullanici_cezalari_getir(kullanici_id)

      #cezalarin hepsini getirmek  icin repository e yonlendirir
    def tum_cezalari_getir(self):
        return self.repo.tum_cezalari_getir()
     
     #ceza odendi yapmak icin repository e yonlendirir    
    def ceza_odendi_yap(self, kullanici_id, odeme_yapilsin_mi=False):
        return self.repo.ceza_odendi_yap(kullanici_id, odeme_yapilsin_mi)











