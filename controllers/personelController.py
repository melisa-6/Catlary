# controllers/personelcontroller.py

from services.personelService import personelService


class personelController:
   
    def __init__(self, db_config):
        self.service = personelService(db_config)
        #gelen parametreler ile ilgili service katmaına yonlendirilir 
    def personel_ekle(self, ad_soyad, email, sifre, sifre_tekrar):
        try:
            return self.service.personel_ekle(ad_soyad, email, sifre, sifre_tekrar)
        except Exception as e:
            print("Controller PERSONEL EKLE HATA:", e)
            return {"success": False, "message": "Beklenmeyen bir hata oluştu!"}

#tum personelleri gostermek icin ilgili service katmanına gonderir
    def tum_personelleri_getir(self):
        try:
            return self.service.tum_personelleri_getir()
        except Exception as e:
            print("Controller PERSONEL LİSTE HATA:", e)
            return []
#gelen bilgiler ile ilgili service katmanına yonlendirir
    def personel_aktiflik_degistir(self, personel_id, yeni_durum):
        try:
            sonuc_bool = self.service.personel_aktiflik_degistir(personel_id, yeni_durum)
            if sonuc_bool:
                yeni_durum_str = "Aktif" if yeni_durum else "Pasif"
                mesaj = f"Personel (ID: {personel_id}) durumu başarıyla {yeni_durum_str} olarak güncellendi."
                return {"success": True, "message": mesaj}
            else:
                mesaj = f"Hata: Personel (ID: {personel_id}) bulunamadı veya durum güncellenemedi."
                return {"success": False, "message": mesaj}
                
        except Exception as e:
            print("Controller AKTİFLİK DEĞİŞTİR HATA:", e)
            return {"success": False, "message": f"Sistem hatası: {e}"}

    def admin_personel_sifre_sifirla_controller(self, form_data):
        try:
            personel_email = form_data.get("personel_email")
            
            # Email'in boş olup olmadığını kontrol eder
            if not personel_email:
                return {"success": False, "message": "E-posta adresi boş olamaz."}
            
        except Exception: 
           
            return {"success": False, "message": "Form verisi işlenirken hata oluştu."}
#ilgili service e yonlendirir
        sonuc = self.service.sifre_sifirla_by_email(personel_email)
        
        if sonuc["success"]:
            return {
                "success": True,
                "message": sonuc["message"],
                "personel_id": sonuc["personel_id"],    
                "username": sonuc["username"],          
                "yeni_sifre": sonuc["yeni_sifre"]       
            }
        else:
            return {"success": False, "message": sonuc["message"]}
        #gelen parametreler ile ilgili service e yonlendiri
    def personel_sifre_degistir_controller(self, personel_id, data):
        try:
            return self.service.personel_sifre_degistir(personel_id, data)
        except Exception as e:
            print(f"Controller KENDİ ŞİFRE DEĞİŞTİR HATA: {e}")
            return {"success": False, "message": "Şifre değiştirme sırasında beklenmeyen hata."}
        