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
        kullanici_adi = form_data.get("verilcek_kullanici_adi")
        kitap_adi = form_data.get("verilcek_kitap_adi")
        odunc_tarihi = form_data.get("verildigi_tarih")
        
        result = self.service.odunc_ver(kullanici_adi, kitap_adi, odunc_tarihi)
        
        if not isinstance(result, dict):
            return {"success": False, "message": str(result), "odunc_id": None}

        return result
    
    def ceza_ode(odunc_id):
        try:
            sonuc = cezaService.ceza_ode_by_odunc_id(odunc_id)

            basarili_mi = sonuc.get("success", False)
            mesaj = sonuc.get("message", "İşlem tamamlandı.")

            # JSON isteği gelmişse
            if hasattr(sonuc, 'get') and request.accept_mimetypes.best == "application/json":
                return jsonify(sonuc), 200 if basarili_mi else 400

            flash(mesaj, "success" if basarili_mi else "danger")

            return render_template("admin.html")
        except Exception as e:
            mesaj = f"Beklenmedik hata: {str(e)}"
            flash(mesaj, "danger")
            return render_template("admin.html")
    
    def odunc_iade_controller(self, form_data):
        odunc_id_raw = form_data.get("odunc_id")
        
        if not odunc_id_raw:
            return "Hata: İade edilecek ödünç ID'si (odunc_id) bulunamadı."
        
        try:
            odunc_id = int(odunc_id_raw.strip()) 
        except ValueError:
            return "Hata: Ödünç ID geçerli bir sayı formatında değil."
            
        return self.service.odunc_iade(odunc_id)
    # [OduncController.py]

    # [OduncController.py dosyası]

    def odeme_tamamla_controller(self, username, borc_miktari):
        
        try:
            # Service'ten (success, message) ikilisi döner.
            success, message = self.service.odeme_tamamla_service(username, borc_miktari) 
            
            # Rota'ya {'success': False, 'message': 'HATA: Kitap iade edilmeden ceza ödenemez.'} sözlüğünü gönderir.
            return {"success": success, "message": message} 
            
        except Exception as e:
            print(f"Controller'da hata: Ödeme Tamamlama başarısız oldu. Hata: {e}")
            return {"success": False, "message": "Ödeme işlemi sırasında beklenmeyen bir hata oluştu."}
    def iade_edilmemis_gecikmis_kayitlari_getir_controller(self, username):
       
        return self.service.iade_edilmemis_gecikmis_kayitlari_getir_service(username)

    
    def kullanici_toplam_borc_miktari_getir_controller(self, username):
        
        return self.service.kullanici_toplam_borc_miktari_getir_service(username)
odunc_controller_instance = odunccontroller()