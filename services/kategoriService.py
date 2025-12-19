from repository.kategoriRepository import KategoriRepository


class KategoriService:
    def __init__(self):
        self.repo = KategoriRepository()

    def tum_kategoriler(self):
        #ilgili  repoya yonlendirir
        return self.repo.tum_kategoriler()
    
    #ilgili  repoya yonlendirir
    def kategori_ekle(self, kategori_adi):
        return self.repo.kategori_ekle(kategori_adi)
   
   #ilgili  repoya yonlendirir
    def kategori_bul(self, kategori_adi):
        return self.repo.kategori_bul(kategori_adi)

#ilgili  repoya yonlendirir
    def kategori_sil(self, id):
        return self.repo.kategori_sil(id)
    
    #ilgili  repoya yonlendirir
    def kitap_var_mi(self, id):
        return self.repo.kitap_var_mi(id)