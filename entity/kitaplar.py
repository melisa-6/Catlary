class Kitaplar:
    def __init__(self, isim, yazar, kategori, sayfa_sayisi, stok, yayinevi, raf_no, baski_yili, id=None):
        self.id = id  # veritabanı AUTO_INCREMENT ile atanacak
        self.isim = isim
        self.yazar = yazar
        self.kategori = kategori
        self.sayfa_sayisi = sayfa_sayisi
        self.stok = stok
        self.yayinevi = yayinevi
        self.raf_no = raf_no
        self.baski_yili = baski_yili

    def __repr__(self):
        return f"<Kitap {self.isim} by {self.yazar}>"
