from datetime import datetime, timedelta
from ssl import SSLError
from repository.odunclerRepository import odunclerRepository
from services.cezaService import cezaService
from services.kullaniciService import kullaniciService
from services.kitapService import kitapService
from decimal import Decimal
from datetime import datetime, timedelta
class oduncService:
    def __init__(self, db_config):
        self.repo = odunclerRepository(db_config)
        self.ceza_service = cezaService(db_config)
        self.kullanici_service = kullaniciService(db_config)
        self.kitap_service = kitapService(db_config)
        
#reponun ilgili fonksiyonuna yönlendirir
    def tum_kullanicilarin_odunc_gecmisi(self):
      return self.repo.tum_kullanici_odunc_gecmisi_getir()


    def kullanici_odunc_gecmisi(self, username):        
        #Verilen kullanıcının ödünç geçmişini döndürür
        kullanici = self.kullanici_service.get_by_username(username)
        if not kullanici:
            return f"Kullanıcı bulunamadı: {username}"
        return self.repo.kullanici_odunc_gecmisi_getir(kullanici['id'])

    # Kitap ödünçte mi kontrol eder
    def kitap_oduncte_mi(self, kitap_id: int) -> bool:
        return self.repo.kitap_oduncte_mi(kitap_id)

    def odunc_ver(self, kullanici_mail, kitap_id, verildigi_tarih_str,gerekli_iade_tarihi):

        #  Kullanıcı tarih girmemişse otomatik olarak bugünün tarihini alir
        if not verildigi_tarih_str:
            verildigi_tarih_str = datetime.now().strftime("%Y-%m-%d")

        #  Kullanıcıyı e-posta ile veritabanından bulur
        kullanici = self.kullanici_service.get_kullanici_by_email(kullanici_mail)
        if not kullanici:
            return {
                "success": False,
                "message": f"Kullanıcı bulunamadı: {kullanici_mail}"
            }

        # Seçilen kitap ID'sine göre kitap bilgisi alır
        kitap = self.kitap_service.get_by_id(kitap_id)
        if not kitap:
            return {
                "success": False,
                "message": f"Kitap bulunamadı (ID): {kitap_id}"
            }

        # Kullanıcının üzerinde ödenmemiş ceza var mı kontrol edilir
        if self.ceza_service.odeme_durumu_var_mi(kullanici["id"]):
            return {
                "success": False,
                "message": "Kullanıcının ödenmemiş cezası var!"
            }
        # Repo katmanı çağrılır
        sonuc = self.repo.odunc_ver(
            kullanici["id"],       # kullanıcı ID
            kitap["id"],           # kitap ID
            verildigi_tarih_str,   # ödünç verilen tarih
            gerekli_iade_tarihi    # otomatik hesaplanan iade tarihi
        )

        # Repo'dan dönen sonuç aynen servisten geri döndürülür
        return sonuc

    def _get_kullanici_id(self,username):
        kullanici_id = self.repo.get_kullanici_id_by_username_repo(username)
        
        if kullanici_id is None:
            # ID bulunamazsa veya hata olursa uygun bir uyarı verilebilir.
            print(f"HATA: '{username}' adında kullanıcı ID'si bulunamadı.") 
            
        return kullanici_id
    
    def odunc_iade(self, odunc_id):

        # Şu anki tarihi iade tarihi olarak alıyoruz 
        iade_tarihi = datetime.now()

        # Repo katmanına iade işlemini yaptırıyoruz
        odunc = self.repo.odunc_iade(odunc_id, iade_tarihi)

        #  Repo bir hata mesajı string dönerse direkt kullanıcıya iletilir
        if isinstance(odunc, str):
            return odunc

        # Service katmanı ile kullanıcı bilgisi çekilir
        #    odunc sözlüğünden kullanıcı ID alınır → veritabanından kullanıcı bulunur
        kullanici = self.kullanici_service.get_kullanici_by_id(odunc['kullanici_id'])

        #    odunc sözlüğünden kitap ID alınır ve veritabanından kitap bulunur
        kitap = self.kitap_service.get_by_id(odunc['kitap_id'])

        #Stok güncelleme işlemi veritabanında TRIGGER ile otomatik yapılıyor

        # Başarılı mesaj dönülür
        return f"{kitap['isim']} kitabı iade alındı. Kullanıcı: {kullanici['username']}"

    
    def iade_edilmemis_gecikmis_kayitlari_getir_service(self, username):
        kullanici_id = self._get_kullanici_id(username)
        
        if kullanici_id is None:
             return [] 
        aktif_oduncler = self.repo.kullanici_aktif_odunc_detaylari_getir_repo(kullanici_id)
        
        gecikmis_kayitlar = []
        bugunun_tarihi = datetime.now().date()
        
        for odunc in aktif_oduncler:
            if odunc['beklenen_iade_tarihi'] < bugunun_tarihi:
                gecikmis_kayitlar.append(odunc)
                
        return gecikmis_kayitlar

 
    def odeme_tamamla_service(self, username, borc_miktari):
        kullanici_id = self._get_kullanici_id(username)
        
        if kullanici_id is None:
            return False, f"HATA: '{username}' adında kullanıcı bulunamadı."
        
        odenmemis_cezalar = self.repo.kullanici_odenecek_cezalarini_getir_repo(kullanici_id)
        
        if not odenmemis_cezalar:
            return True, "Ödenecek aktif borç bulunmamaktadır."
            
        for ceza in odenmemis_cezalar:
            ceza_id = ceza['ceza_id'] 
            kitap_iade_edildi_mi = self.repo.cezanin_iade_edilmis_olup_olmadigini_kontrol_et(ceza_id)
            
            if not kitap_iade_edildi_mi:
                mesaj = f"HATA: Ödeme yapabilmeniz için {ceza_id} ID'li cezaya konu olan kitabı önce iade etmelisiniz."
                return False, mesaj 
                
        try:
            sonuc = self.repo.cezalar_odendi_yap_repo(kullanici_id)
            
            if sonuc:
                return True, f"{str(borc_miktari)} TL tutarındaki borç başarıyla ödendi."
            else:
                return False, "HATA: Veritabanı güncellemesi sırasında bir sorun oluştu."
                
        except Exception as e:
            print(f"Genel Python Hatası: {e}")
            return False, "HATA: İşlem sırasında beklenmeyen bir teknik sorun oluştu."
    def kullanici_toplam_borc_miktari_getir_service(self, username):
      
        kullanici_id = self._get_kullanici_id(username)
        
        if kullanici_id is None:
            return 0.0 
        toplam_borc=Decimal('0.0')
       
        odenecek_cezalar = self.repo.kullanici_odenecek_cezalarini_getir_repo(kullanici_id)
        
        for ceza in odenecek_cezalar:
            toplam_borc += ceza['ceza_miktari']
        
        return toplam_borc