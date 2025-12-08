from services.oduncService import oduncService
from services.kitapService import kitapService

db_config = {
    "host": "localhost",
    "user": "melisa",
    "password": "Mtz0504*",
    "database": "kutuphane_db"
}

kitapService = kitapService(db_config)            
oduncService = oduncService(db_config)  

class kitapController:
    def kitaplari_goruntule_controller(username, role, aranan_kitap=""):
        #Kullanıcının ya da adminin kitapları görüntülemesini saglar
        #Arama kelimesi verilmişse filtreleme yapar yoksa tüm kitapları döndürür
        if aranan_kitap:
            # Arama kelimesi varsa service de uygun fonksiyon ile filtreler
            kitaplar = kitapService.kitap_ara(aranan_kitap)
        else:
            # Yoksa tüm kitapları getirir
            kitaplar = kitapService.tum_kitaplari_getir()

        # Kullanıcı admin mi kontrol eder buna gore anasayfalarina geri dondurur
        admin_mi = role == 'admin'
        # Route'a döndür
        return kitaplar, admin_mi
    
    def kitap_ekle_controller(form_data):
        # parametrelerden verileri al
        isim = form_data.get('kitap_adi')
        yazar = form_data.get('kitap_yazari')
        yayinevi = form_data.get('kitap_yayini')
        tur_list = form_data.getlist('kitap_turu')
        sayfa_sayisi = form_data.get('kitap_sayfa_sayisi')
        stok = form_data.get('stok_miktari')
        raf_no = form_data.get('raf_no')
        baski_yili = form_data.get('baski_yili')

        # Service'e yönlendirir ve ekleme işlemini yapar
        mesaj, kitap_id = kitapService.kitap_ekle(
            isim, yazar, ','.join(tur_list), yayinevi,
            sayfa_sayisi, stok, raf_no, baski_yili
        )

        # Route'a göndermek için kitap bilgilerini dict olarak hazırlar
        kitap_bilgileri = {
            "isim": isim,
            "yazar": yazar,
            "kategori": ', '.join(tur_list),
            "sayfa_sayisi": sayfa_sayisi,
            "stok": stok,
            "raf_no": raf_no,
            "baski_yili": baski_yili
        }

        basarili_mi = True if kitap_id else False

        return mesaj, kitap_id, kitap_bilgileri, basarili_mi

    def kitap_sil_controller(kitap_id):
        try:
            kitap_id = int(kitap_id)
        except (ValueError, TypeError):
            return "Hata: Kitap ID geçerli değil.", "Kitap Silme Hatası", False

        try:
            sonuc = kitapService.kitap_sil_by_id(kitap_id)

            if sonuc.get('success'):
                return sonuc.get('message', "Kitap başarıyla silindi."), "Kitap Silme", True
            else:
                return sonuc.get('message', "Kitap silinemedi."), "Kitap Silme Hatası", False

        except Exception as e:
            print(f"Kitap Silme Hatası: {e}")
            return f"Beklenmedik hata: {str(e)}", "Kitap Silme Hatası", False
