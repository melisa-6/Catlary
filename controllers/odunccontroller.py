# controllers/oduncController.py
from flask import flash, render_template
from services.oduncService import OduncService

db_config = {
    "host": "localhost",
    "user": "melisa",
    "password": "Mtz0504*",
    "database": "kutuphane_db"
}

oduncService = OduncService(db_config)

def odunc_ver_controller(form_data):
#formdan gelen verileri alir
    kullanici_adi = form_data.get("verilcek_kullanici_adi")
    kitap_adi = form_data.get("verilcek_kitap_adi")
    odunc_tarihi = form_data.get("verildigi_tarih")
# Alınan veriler uygun servicedeki uygun  fonksiyona gönderilir
    result = oduncService.odunc_ver(kullanici_adi, kitap_adi, odunc_tarihi)
  # Servis düzgün bir dict dönmezse hata durumunu belirten bir dict döndürür.
    if not isinstance(result, dict):
        return {"success": False, "message": str(result), "odunc_id": None}

    return result

def tumkullanici_odunc_gecmisi_controller(username):
    #tum kullanicilari gostermek icin service katmaniina yonlendirir
    odunc_gecmisi = oduncService.tum_kullanicilarin_odunc_gecmisi()
    #route kısmına gerekli seyleri returnlar 
    return render_template("tum_odunc_gecmisi.html", odunc_gecmisi=odunc_gecmisi, username=username)


def kullanici_odunc_gecmisi_controller(username):
   #service ile kullanicinin odunc gecmisi dondurulur
    odunc_gecmisi = oduncService.kullanici_odunc_gecmisi(username)
    return render_template("odunc_gecmisim.html", odunc_gecmisi=odunc_gecmisi, username=username)


def odunc_iade_controller(form_data):
    # Form verilerinden odunc_id'yi alinir
    odunc_id = form_data.get("odunc_id")
 
    if not odunc_id:
        return "Hata: İade edilecek ödünç ID'si (odunc_id) bulunamadı."
        #serviceden uygun fonksiyona degiskeni atayarak islemi yaptirir ve bunu route kısmına gonderir
    result_message = oduncService.odunc_iade(odunc_id)

    return result_message