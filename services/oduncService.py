# services/oduncService.py
from datetime import datetime, timedelta
from repository.odunclerRepository import OduncRepository
from services.cezaService import CezaService
from services.kullaniciService import KullaniciService
from services.kitapService import KitapService

class OduncService:
    def __init__(self, db_config):
        self.repo = OduncRepository(db_config)
        self.ceza_service = CezaService(db_config)
        self.kullanici_service = KullaniciService(db_config)
        self.kitap_service = KitapService(db_config)

    # Tüm kullanıcıların ödünç gecmisini dondurmesi icin repoya yonlendirir
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
            return {"success": False, "message": "Kullanıcının ödenmemiş cezası var!"}

        # Gerekli iade tarihini uygun sekilde hesaplar
        verildigi_tarih = datetime.strptime(verildigi_tarih_str, "%Y-%m-%d")
        gerekli_iade_tarihi = (verildigi_tarih + timedelta(days=15)).strftime("%Y-%m-%d")

        #bilgiler ile repodaki uygun fonksiyonu cagirir
        sonuc = self.repo.odunc_ver(kullanici["id"], kitap["id"], verildigi_tarih_str, gerekli_iade_tarihi)
        return sonuc
  
  
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
