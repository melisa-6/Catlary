from repository.yazarRepository import YazarRepository

class YazarService:
    def __init__(self):
        self.repo = YazarRepository()

    def tum_yazarlar(self):
        return self.repo.tum_yazarlar()

    def yazar_ekle(self, ad):
        return self.repo.yazar_ekle(ad)

    def yazar_sil(self, id):
        return self.repo.yazar_sil(id)

    def kitap_var_mi(self, id):
        return self.repo.kitap_var_mi(id)

    def yazar_bul(self, ad):
        return self.repo.yazar_bul(ad)
