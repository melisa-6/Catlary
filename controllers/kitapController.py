from services.oduncService import oduncService
from services.kitapService import kitapService

class kitapController:
    def __init__(self, db_config):
        self.kitap_service = kitapService(db_config)
        self.odunc_service = oduncService(db_config)

    def kitap_getir(self,kitap_id):
        return self.kitap_service.get_by_id(kitap_id)
    def kitap_guncelle(
        self, kitap_id, kitap_adi, yazar_id, kategori_id,
        sayfa_sayisi, stok_miktari, raf_no, baski_yili, yayinevi_id, resim
    ):
        # Kitap ID'nin geçerli bir sayı olup olmadığını kontrol et
        try:
            kitap_id = int(kitap_id)
        except (ValueError, TypeError):
            return "Hata: Kitap ID geçerli değil.", "Kitap Güncelleme Hatası", False

        try:
            # Servis katmanına güncelleme işlemini gönder
            sonuc = self.kitap_service.kitap_guncelle(
                kitap_id=kitap_id,
                isim=kitap_adi,
                sayfa_sayisi=sayfa_sayisi,
                stok=stok_miktari,
                raf_no=raf_no,
                baski_yili=baski_yili,
                yazar_id=yazar_id,
                kategori_id=kategori_id,
                yayinevi_id=yayinevi_id,
                resim=resim
            )

            # Servisten dönen sonucu kontrol et
            if sonuc.get('success'):
                return sonuc.get('message', "Kitap başarıyla güncellendi."), "Kitap Güncelleme", True
            else:
                return sonuc.get('message', "Kitap güncellenemedi."), "Kitap Güncelleme Hatası", False

        except Exception as e:
            print(f"Kitap Güncelleme Hatası: {e}")
            return f"Beklenmedik hata: {str(e)}", "Kitap Güncelleme Hatası", False
    
    def kitaplari_goruntule_controller(self, username, role, aranan_kitap=""):
        # Kullanıcı kitap aradı mı kontrol et
        # Eğer aranan_kitap parametresi boş değilse sadece filtrelenmiş sonuçlar getir
        if aranan_kitap:
         kitaplar = self.kitap_service.kitap_ara(aranan_kitap)
        else:
            # Hiç arama yapılmadıysa tüm kitapları getirir
            kitaplar = self.kitap_service.tum_kitaplari_getir()

        # Kullanıcının rolüne göre admin yetkisi var mı kontrol eder
        # Eğer rol 'admin' ise admin_mi True olacak, değilse False
        admin_mi = role == 'admin'
        
        # Kitap listesini ve admin bilgisiyle birlikte geri döndür
        return kitaplar, admin_mi

        
    def kitap_ekle_controller(self, kitap_adi, yazar_id, kategori_id, sayfa_sayisi, stok_miktari, raf_no, baski_yili, yayinevi,resim):
        try:
            # Gelen verileri servise iletiyoruz
            return self.kitap_service.kitap_ekle(
                kitap_adi, yazar_id, kategori_id, sayfa_sayisi, 
                stok_miktari, raf_no, baski_yili, yayinevi,resim
            )
        except Exception as e:
            print(f"Controller HATA: Kitap eklenemedi: {e}")
            return False

    def kitap_sil_controller(self, kitap_id):
    
    # Kitap ID sayıya çevrilebilir mi kontrol eder
        try:
            kitap_id = int(kitap_id)
        except (ValueError, TypeError):
            return "Hata: Kitap ID geçerli değil.", "Kitap Silme Hatası", False

        try:
            # Servis katmanında kitap silme fonksiyonu çağırır
            sonuc = self.kitap_service.kitap_sil_by_id(kitap_id)

            # Servisten gelen 'success' bilgisine göre sonuç oluştur
            if sonuc.get('success'):
                # Silme başarılı ise
                return sonuc.get('message', "Kitap başarıyla silindi."), "Kitap Silme", True
            else:
                # Silme başarısız ise
                return sonuc.get('message', "Kitap silinemedi."), "Kitap Silme Hatası", False

        # Beklenmeyen bir hata oluşursa
        except Exception as e:
            print(f"Kitap Silme Hatası: {e}")
            return f"Beklenmedik hata: {str(e)}", "Kitap Silme Hatası", False
