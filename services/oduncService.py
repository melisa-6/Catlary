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

    # Tüm kullanıcıların ödünç gecmisini dondurmesi icin repoya yonlendirir
    # Tüm kullanıcıların ödünç geçmişi (admin ve personel için)
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

    def odunc_ver(self, kullanici_adi, kitap_adi, verildigi_tarih_str=None):
        # odunc verildigi tarih bossa o gunu alir
        if verildigi_tarih_str is None:
            verildigi_tarih_str = datetime.now().strftime("%Y-%m-%d")

        # Kullanıcı ve kitap bilgisini uygun serviceden uygun fonksiyon ile alir
        kullanici = self.kullanici_service.get_by_username(kullanici_adi)
        if not kullanici:
            return {"success": False, "message": f"Kullanıcı bulunamadı: {kullanici_adi}"}
       #kullanici veya kitabi bulunamadiysa uygun hatayi verir
        kitap = self.kitap_service.get_by_name(kitap_adi)
        if not kitap:
            return {"success": False, "message": f"Kitap bulunamadı: {kitap_adi}"}

        # kullanicinin cezasi varsa buna uygun hata verir
        if self.ceza_service.odeme_durumu_var_mi(kullanici["id"]):
            print("DEBUG: odeme_durumu_var_mi:", self.ceza_service.odeme_durumu_var_mi(kullanici["id"]))
            return {"success": False, "message": "Kullanıcının ödenmemiş cezası var!"}

        # Gerekli iade tarihini uygun sekilde hesaplar
        verildigi_tarih = datetime.strptime(verildigi_tarih_str, "%Y-%m-%d")
        gerekli_iade_tarihi = (verildigi_tarih + timedelta(days=15)).strftime("%Y-%m-%d")

        #bilgiler ile repodaki uygun fonksiyonu cagirir
        sonuc = self.repo.odunc_ver(kullanici["id"], kitap["id"], verildigi_tarih_str, gerekli_iade_tarihi)
        return sonuc
  
    def _get_kullanici_id(self,username):
        kullanici_id = self.repo.get_kullanici_id_by_username_repo(username)
        
        if kullanici_id is None:
            # ID bulunamazsa veya hata olursa uygun bir uyarı verilebilir.
            print(f"HATA: '{username}' adında kullanıcı ID'si bulunamadı.") 
            
        return kullanici_id
    def odunc_iade(self, odunc_id):
        #su ani iade_tarihi yapar ve parametre olarak repoya gonderir
        iade_tarihi = datetime.now().strftime("%Y-%m-%d")
        odunc = self.repo.odunc_iade(odunc_id, iade_tarihi)

        if isinstance(odunc, str):
            return odunc
        #ilgili service in ilgili fonksiyonlari ile kullanici ve kitap bilgileri alinir
        kullanici = self.kullanici_service.get_kullanici_by_id(odunc['kullanici_id'])
        kitap = self.kitap_service.get_by_id(odunc['kitap_id'])
        #stok guncelleme kısmı trigger ile yapılıyor!

        return f"{kitap['isim']} kitabı iade alındı. Kullanıcı: {kullanici['username']}"
    
    def iade_edilmemis_gecikmis_kayitlari_getir_service(self, username):
        kullanici_id = self._get_kullanici_id(username)
        
        if kullanici_id is None:
             return [] # Kullanıcı bulunamazsa boş liste dön

        # Repo'yu doğru örnek (self.repo) üzerinden ve ID ile çağırıyoruz.
        aktif_oduncler = self.repo.kullanici_aktif_odunc_detaylari_getir_repo(kullanici_id)
        
        gecikmis_kayitlar = []
        bugunun_tarihi = datetime.now().date()
        
        for odunc in aktif_oduncler:
            # Not: 'beklenen_iade_tarihi' formatının datetime.date objesi olduğundan emin olun.
            if odunc['beklenen_iade_tarihi'] < bugunun_tarihi:
                gecikmis_kayitlar.append(odunc)
                
        return gecikmis_kayitlar

 
    def odeme_tamamla_service(self, username, borc_miktari):
        # Kullanılan hata sınıfını import ettiğinizden emin olun (Örn: mysql.connector.Error)
        # from mysql.connector import Error as MySQLError 
        # veya sadece 'Exception' bırakıp log çıktısına güvenin.

        kullanici_id = self._get_kullanici_id(username)
        
        if kullanici_id is None:
            return False, f"HATA: '{username}' adında kullanıcı bulunamadı."
        
        odenmemis_cezalar = self.repo.kullanici_odenecek_cezalarini_getir_repo(kullanici_id)
        
        if not odenmemis_cezalar:
            return True, "Ödenecek aktif borç bulunmamaktadır."
            
        # 1. PYTHON IÇINDEKI IADE KONTROLÜ
        for ceza in odenmemis_cezalar:
            ceza_id = ceza['ceza_id'] 
            kitap_iade_edildi_mi = self.repo.cezanin_iade_edilmis_olup_olmadigini_kontrol_et(ceza_id)
            
            if not kitap_iade_edildi_mi:
                # 🔥 Eğer buraya düşerse, net hata mesajı döner ve alttaki try bloğu çalışmaz.
                mesaj = f"HATA: Ödeme yapabilmeniz için {ceza_id} ID'li cezaya konu olan kitabı önce iade etmelisiniz."
                return False, mesaj 
                
        # 3. Ödeme İşlemi
        try:
            sonuc = self.repo.cezalar_odendi_yap_repo(kullanici_id)
            
            if sonuc:
                return True, f"{str(borc_miktari)} TL tutarındaki borç başarıyla ödendi."
            else:
                # Bu, ödenecek ceza bulunmadığında veya güncelleme başarısız olduğunda tetiklenir.
                return False, "HATA: Veritabanı güncellemesi sırasında bir sorun oluştu."
                
        except DBError as e: # DBError yerine kullandığınız spesifik MySQL hata sınıfını yazın!
            
            # MySQL/Constraint/Trigger 1644 hatasını yakala
            if getattr(e, 'errno', None) == 1644:
                # Service'in kendi kontrolü başarısız olsa bile, MySQL'in net mesajını kullanıcıya ver.
                return False, f"HATA: Kitap iade edilmeden ceza ödenemez. Lütfen önce iade yapınız." 
            else:
                print(f"Bilinmeyen MySQL Hatası: {e}")
                return False, "HATA: Veritabanında beklenmeyen bir sorun oluştu."
                
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