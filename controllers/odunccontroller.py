from flask import flash, jsonify, render_template, request

from services import cezaService
from services.oduncService import oduncService 

db_config = {
    "host": "localhost",
    "user": "melisa",
    "password": "Mtz0504*",
    "database": "kutuphane_db"
}

class odunccontroller:
    def __init__(self):
        self.service = oduncService(db_config)
    
  
    def tum_kullanicilarin_odunc_gecmisi_controller(self, role, username):
        # Sadece admin ve personel görebilir
        if role in ["admin", "personel"]:
            return self.service.tum_kullanicilarin_odunc_gecmisi()
        return []

    def kullanici_odunc_gecmisi_controller(self, username):
        return self.service.kullanici_odunc_gecmisi(username)
    def odunc_ver_controller(self, form_data):
        # 🔧 DOĞRU KEYLER
        kullanici_mail = form_data.get("kullanici_mail")
        kitap_id = form_data.get("kitap_id")
        odunc_tarihi = form_data.get("verildigi_tarih")

        # 🔍 Güvenlik kontrolü
        if not kullanici_mail or not kitap_id or not odunc_tarihi:
            return {
                "success": False,
                "message": "Eksik bilgi gönderildi.",
                "odunc_id": None
            }

        # Service katmanına doğru parametreleri gönder
        result = self.service.odunc_ver(
            kullanici_mail,
            kitap_id,
            odunc_tarihi
        )

        if not isinstance(result, dict):
            return {
                "success": False,
                "message": str(result),
                "odunc_id": None
            }

        return result

    
    def odunc_iade_controller(self, form_data):
        odunc_id_raw = form_data.get("odunc_id")
        
        if not odunc_id_raw:
            return "Hata: İade edilecek ödünç ID'si (odunc_id) bulunamadı."
        
        try:
            odunc_id = int(odunc_id_raw.strip()) 
        except ValueError:
            return "Hata: Ödünç ID geçerli bir sayı formatında değil."
            
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
odunc_controller_instance = odunccontroller()