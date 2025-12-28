from flask import flash, jsonify, render_template, request

from services import cezaService
from services.oduncService import oduncService 
from db_config import db_config

class odunccontroller:
    def __init__(self,db_config):
        self.db_config=db_config
        self.service = oduncService(db_config)
    
  
    def tum_kullanicilarin_odunc_gecmisi_controller(self, role, username):
        # Sadece admin ve personel görebilir
        if role in ["admin", "personel"]:
            return self.service.tum_kullanicilarin_odunc_gecmisi()
        return []

    def kullanici_odunc_gecmisi_controller(self, username):
        #gelen parametre ile ilgili service fonksiyonuna yonlendrilir
        return self.service.kullanici_odunc_gecmisi(username)
    
    def odunc_ver_controller(self, form_data):

        # Formdan gelen verileri alıyoruz
        kullanici_mail = form_data.get("kullanici_mail")
        kitap_id = form_data.get("kitap_id")

        # Gelen verilerden herhangi biri eksikse işlem durdurulur
        if not kullanici_mail or not kitap_id:
            return {
                "success": False,
                "message": "Eksik bilgi gönderildi.",
                "odunc_id": None
            }

        # Otomatik tarihleri oluştur
        from datetime import datetime, timedelta
        odunc_tarihi = datetime.now()
        iade_tarihi = odunc_tarihi + timedelta(minutes=1)

        # Controller sadece yönlendiriyor
        result = self.service.odunc_ver(
            kullanici_mail,
            kitap_id,
            odunc_tarihi,
            iade_tarihi
        )

        if not isinstance(result, dict):
            return {
                "success": False,
                "message": str(result),
                "odunc_id": None
            }

        return result
    
    def odunc_iade_controller(self, form_data):
        # HTML formundan gelen verilerden ödünç ID bilgisi alınır
        odunc_id_raw = form_data.get("odunc_id")
        
        # Eğer formda "odunc_id" alanı yoksa işlem gerçekleşemez
        if not odunc_id_raw:
            return "Hata: İade edilecek ödünç ID'si (odunc_id) bulunamadı."
        
        try:
            # ID string gelmesi ihtimali olduğu için önce boşluklar temizlenip
            # Ardından integer'a çevririr ve geçerli bir sayı olup olmadığı kontrol edilir
            odunc_id = int(odunc_id_raw.strip()) 
        except ValueError:
            # Eğer integer dönüşümü başarısız olursa format hatası döner
            return "Hata: Ödünç ID geçerli bir sayı formatında değil."
        
        #  Buraya kadar geldiysek ID geçerli olur ve service katmanına yönlendirilir
        return self.service.odunc_iade(odunc_id)

  

    def odeme_tamamla_controller(self, username, borc_miktari):
        
        try:
            success, message = self.service.odeme_tamamla_service(username, borc_miktari) 
            return {"success": success, "message": message} 
            
        except Exception as e:
            print(f"Controller'da hata: Ödeme Tamamlama başarısız oldu. Hata: {e}")
            return {"success": False, "message": "Ödeme işlemi sırasında beklenmeyen bir hata oluştu."}
    def iade_edilmemis_gecikmis_kayitlari_getir_controller(self, username):
       
        return self.service.iade_edilmemis_gecikmis_kayitlari_getir_service(username)

    
    def kullanici_toplam_borc_miktari_getir_controller(self, username):
        
        return self.service.kullanici_toplam_borc_miktari_getir_service(username)