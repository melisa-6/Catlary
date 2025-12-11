from repository.kategoriRepository import KategoriRepository


class KategoriService:
    def __init__(self):
        self.repo = KategoriRepository()

    def tum_kategoriler(self):
        return self.repo.tum_kategoriler()
    def kategori_ekle(self, kategori_adi):
        return self.repo.kategori_ekle(kategori_adi)
   
    def kategori_bul(self, kategori_adi):
        return self.repo.kategori_bul(kategori_adi)

    def kategori_sil(self, id):
        return self.repo.kategori_sil(id)
    
    def kitap_var_mi(self, id):
        return self.repo.kitap_var_mi(id)