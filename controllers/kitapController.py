from services import oduncService
from services.kitapService import KitapService

db_config = {
    "host": "localhost",
    "user": "melisa",
    "password": "",
    "database": "kutuphane_db"
}

kitapService = KitapService(db_config)            
oduncService = oduncService.OduncService(db_config)  


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
    
    #parametre gonderilen Formdan verileri alir
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

    return mesaj, kitap_id, kitap_bilgileri


def kitap_sil_controller(kitap_id):
#gelen kitap id si ile kitap silmek icin uygun service a yonlendirir
    if not kitap_id:
        # Kitap ID yoksa hata dondurur
        return "Lütfen bir kitap seçin!", "Kitap Silme Hatası"

    # oduncte mi kontrol eder
    if oduncService.kitap_oduncte_mi(kitap_id):
        return "Bu kitap şu anda ödünçte olduğu için silinemez!", "Kitap Silme Hatası"

    # ID ile silme işlemini service üzerinden yapmak icin ygun service fonksiyonuna yonlendirir
    mesaj, silinen_kitap = kitapService.kitap_sil_by_id(kitap_id)

    # İşlem türünü belirler
    islem_turu = "Kitap Silme" if silinen_kitap else "Kitap Silme Hatası"

    return mesaj, islem_turu
