from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, g, session
import random
import base64
import hmac
import hashlib

# dependencies dosyasından gerekli nesneleri çekiyoruz
from depencies import (
    kullanicikontroller,
    ceza_controller_instance,
    kullanici_islemleri,
    make_json_compatible,
    kullanici_controller_instance
)
from decorators import (admin_required,login_required,
    admin_or_personel_required)
# Blueprint oluşturuluyor
kullanici_bp = Blueprint('kullanici', __name__)

# --- PAYTR TEST AYARLARI ---
PAYTR_MERCHANT_ID = "111111"
PAYTR_MERCHANT_KEY = "11111111111111111111111111111111"
PAYTR_MERCHANT_SALT = "11111111111111111111111111111111"


@kullanici_bp.route('/kullanici_sayfasi')
@login_required
#bu sayfaya sadece giris yapan kulanıcıların girebilecegini belirtir
def kullanici_sayfasi():
    username = g.username 
    #kullanici logini sirasinda kaydedilen bilgilerden ismini alır
    #eger gelen istek apı gibi json istiyorsa
    if request.accept_mimetypes.best == "application/json":
        return jsonify({"username": username, "message": "Kullanıcı sayfası erişimi başarılı"}), 200
        #html istegi ise
    return render_template("kullanici.html", username=username)


@kullanici_bp.route("/kullaniciekle", methods=["POST"])
@admin_or_personel_required
#sadece admin veya personel rolundeki kullanicilarin girisini saglar
def kullanici_ekle_route():
    #JSON olarak gelmisse json formdan gelmissse formdan bilgileri aliı
    data = request.get_json(silent=True) or request.form

    # ilgili Controlleri cagirir
    sonuc = kullanicikontroller.kullanici_ekle_controller(data)
    #gelen sonuc degiskeninden basari durumunu alir
    basarili_mi = sonuc.get("basarili", False)
    mesaj = sonuc.get("mesaj", "İşlem tamamlandı.")
#flash  mesaji ile basarili ise succes deilse danger gosterilir
    flash(mesaj, "success" if basarili_mi else "danger")
    # JSON isteği gelmişse JSON döndurur
    if request.is_json or request.accept_mimetypes.best == "application/json":
        return jsonify({"success": basarili_mi, "message": mesaj}), 201 if basarili_mi else 400
    #  Rol bazlı HTML yönlendirme
    rol = getattr(g, "role", None)  
    if rol == "admin":
        return redirect(url_for("admin.admin_anasayfa"))
    elif rol == "personel":
        # Personel blueprint'i ve route ismine göre düzenlendi
        return redirect(url_for("personel.personel_sayfasi"))

    return render_template("admin.html", username=getattr(g, "username", ""))
@kullanici_bp.route('/kendiborc_ode/<username>', methods=['GET', 'POST'])
@login_required
def kendiborc_ode(username):
    # API kontrolü
    is_api_request = request.is_json or request.headers.get('Accept') == 'application/json'

    if username != g.username:
        return redirect(url_for('genel.anasayfa'))

    # Elinde iade edilmemiş kitap olsa bile SADECE bilgi için tutuyoruz
    iade_edilmemis_var = ceza_controller_instance.iade_edilmemis_kitap_var_mi_controller(username)

    # ÖNEMLİ: Bu fonksiyon sadece iade edilenlerin borcunu (2.00 TL) getiriyor
    toplam_borc = ceza_controller_instance.borc_getir_controller(username)
    
    mesaj = None
    odeme_basarili = False

    if request.method == "POST":
        data = request.json if request.is_json else request.form
        
        # --- DÜZELTME: ARTIK BURADA 'iade_edilmemis_var' KONTROLÜYLE ENGELLEME YAPMIYORUZ ---
        try:
            kart_sahibi = data.get("kart_sahibi")
            kart_numarasi = data.get("kart_numarasi")
            
            if not kart_sahibi or not kart_numarasi:
                mesaj = "Eksik kart bilgisi!"
            elif toplam_borc <= 0:
                mesaj = "Ödenecek (iade edilmiş kitap) borcunuz bulunmamaktadır."
            else:
                # Ödeme başarılı kabul ediliyor
                gelen_cevap = ceza_controller_instance.ceza_odendi_yap(
                    kullanici_id=g.user_id,
                    odeme_yapilsin_mi=True
                )
                
                if isinstance(gelen_cevap, dict) and gelen_cevap.get('success'):
                    mesaj = "İade ettiğiniz kitapların borcu başarıyla ödendi!"
                    odeme_basarili = True
                    toplam_borc = 0 
                else:
                    mesaj = "Ödeme yapılamadı."
        except Exception as e:
            mesaj = "Sunucu hatası oluştu."

    # HTML'e iade_edilmemis_var bilgisini hala gönderiyoruz ama HTML'de bunu ENGEL olarak kullanmayacağız
    return render_template("borcode.html", 
                           toplam_borc=toplam_borc, 
                           mesaj=mesaj, 
                           odeme_basarili=odeme_basarili,
                           iade_edilmemis_var=iade_edilmemis_var)
@kullanici_bp.route('/kullanici_durum_degistir', methods=['POST'])
@admin_or_personel_required
#personel veya admin bu route a erisebilir sadece
def kullanici_durum_degistir():
    print("TEST")

    # JSON geldiyse JSON'u, yoksa FORM verisini al
    data = request.get_json(silent=True) or request.form

    # Gönderilen kullanıcı adını al
    kullanici_adi = data.get('kullanici_adi')
    
    # Kullanıcı adı yoksa hata dön
    if not kullanici_adi:
        mesaj = "Eksik veri: 'kullanici_adi' gereklidir."
        #JSON verisi isteniyosa veya APIistegi ise
        if request.accept_mimetypes.best == "application/json" or request.is_json:
            return jsonify({"success": False, "message": mesaj}), 400
        return redirect(url_for('kullanici.kullanicilar'))

    try:
        # Kullanıcı adından kullanıcı bilgilerini al
        user_data = kullanici_islemleri.get_by_username(kullanici_adi) 
        
        # Kullanıcı bulunamazsa hata dön
        if not user_data:
            mesaj = f"Kullanıcı '{kullanici_adi}' bulunamadı."
            if request.accept_mimetypes.best == "application/json":
                return jsonify({"success": False, "message": mesaj}), 404
            return redirect(url_for('kullanici.kullanicilar'))
        
        # Kullanıcı ID'sini çek
        user_id = user_data['id']

        # Kullanıcının aktiflik durumunu tersine çevir
        sonuc = kullanici_islemleri.kullanici_aktiflik_durumu_degistir(user_id) 
        
        # Veri işlem sonucu
        basarili_mi = sonuc.get('success')
        status_code = 200 if basarili_mi else 400
        
        # Eğer API isteğiyse JSON döndür
        if request.accept_mimetypes.best == "application/json" or request.is_json:
            return jsonify(sonuc), status_code
        
        # Değilse kullanıcı listesine yönlendir
        # 'kullanicilar_goster' yerine blueprint altındaki 'kullanicilar' fonksiyonuna yönlendirildi
        return redirect(url_for('kullanici.kullanicilar'))
            
    except Exception as e:
        # Beklenmeyen hata yakalanır
        mesaj = f"İşlem Başarısız: Sunucu tarafında beklenmedik bir hata oluştu: {e}"
        print(f"HATA /kullanici_durum_degistir: {e}") 
        
        # API ise JSON dön
        if request.accept_mimetypes.best == "application/json":
            return jsonify({"success": False, "message": mesaj}), 500
        
        # değilse yönlendir
        return redirect(url_for('kullanici.kullanicilar'))


@kullanici_bp.route('/kullanicilar', methods=['GET'])
@admin_or_personel_required  # Bu route'a sadece admin ve personel girebilir
def kullanicilar():
    # Oturumu açık kullanıcının bilgilerini al
    username = g.username
    role = g.role 

    try:
        # Veritabanından tüm kullanıcıları çek
        kullanicilar_listesi = kullanici_islemleri.tum_kullanicilari_getir()
    except Exception as e:
        # Veritabanı hatası olursa liste boş dön
        print(f"HATA: Kullanıcı listesi alınamadı: {e}")
        kullanicilar_listesi = []

    # İstek JSON formatında ise HTML yerine JSON cevap gönder
    if request.accept_mimetypes.best == "application/json":
        return jsonify({
            "username": username,  # oturumu açık kullanıcı adı
            "role": role,          # kullanıcının rolü
            "kullanicilar": make_json_compatible(kullanicilar_listesi)  # liste JSON'a uygun hale getirildi
        }), 200

    # HTML sayfası döndürür
    return render_template(
        "kullanicilar.html",
        kullanicilar=kullanicilar_listesi,   
        # geri dönüş butonu admin ise admin anasayfasına, personel ise personel sayfasına yönlendirir
        geri_url=url_for("admin.admin_anasayfa") if role=="admin" else url_for("personel.personel_sayfasi")
    )


@kullanici_bp.route('/kullanici_sifre_degistir', methods=['POST'])
@login_required   # Kullanıcının giriş yapmış olması şart
def kullanici_sifre_degistir():

    user_id = g.get("user_id")       # Session / g üzerinden kullanıcı ID alınır
    username = g.get("username")     # Kullanıcı adı alınır

    # Hem JSON hem HTML form gönderimlerini desteklemesi için
    data = request.get_json(silent=True) or request.form

    # Eğer kullanıcı bilgisi yoksa güvenlik gereği işlem iptal edilir
    if not user_id:
        mesaj = "Kimlik doğrulanamadı. Lütfen tekrar giriş yapın."
        
        # JSON istek gelmişse JSON dön
        if request.accept_mimetypes.best == "application/json":
            return jsonify({
                "success": False, 
                "message": mesaj
            }), 401
        
        # HTML istek gelmişse flash mesaj bas ve yönlendir
        flash(mesaj, "danger")
        return redirect(url_for("genel.anasayfa"))

    try:
        # Controller katmanına şifre değiştirme talebi gönderilir
        sonuc = kullanici_controller_instance.kullanici_sifre_degistir_controller(
            user_id, 
            data
        )

    except Exception as e:
        # Sunucu hatası durumunda API kullanıcıları için JSON hata cevabı
        if request.accept_mimetypes.best == "application/json":
            return jsonify({
                "success": False,
                "message": "Bir hata oluştu. Sistem yöneticisine bildiriniz.",
                "detail": str(e)
            }), 500
        
        # HTML kullanıcıları için flash mesaj ve yönlendirme
        flash("Bir hata oluştu. Lütfen tekrar deneyin.", "danger")
        return redirect(url_for("kullanici.kullanici_sayfasi"))

    # Controller'dan gelen sonucu çözümle
    basarili_mi = sonuc.get("success", False)
    mesaj = sonuc.get("message", "")

    # Eğer JSON talebi geldiyse JSON döndür
    if request.accept_mimetypes.best == "application/json":
        status = 200 if basarili_mi else 400
        return jsonify(sonuc), status

    # HTML kullanıcıları için mesaj durumuna göre flash bas
    if basarili_mi:
        flash("Şifreniz başarıyla değiştirildi.", "success")
    else:
        flash(mesaj or "Şifre değiştirilemedi.", "danger")

    # Kullanıcı sayfasına yönlendir
    return redirect(url_for("kullanici.kullanici_sayfasi"))

@kullanici_bp.route('/kullanici_sifre_sifirla', methods=['POST'])
@admin_or_personel_required   # Sadece admin veya personel erişebilir
def admin_kullanici_sifre_sifirla_route():
    # Eğer JSON gönderilmişse veya istemci JSON response bekliyorsa True olur
    is_api_request = request.is_json or request.accept_mimetypes.best == "application/json"
    form_data = request.get_json(silent=True) if is_api_request else request.form
    
    # Form boşsa hata ver
    if not form_data:
        mesaj = "Form verisi eksik."
        
        # API kullanıcısına JSON döndür
        if is_api_request:
            return jsonify({"success": False, "message": mesaj}), 400
        
        # HTML kullanıcılarına flash mesaj göster ve yönlendir
        flash(mesaj, "danger")
        return redirect(url_for('admin.admin_anasayfa'))
        
    #  Controller katmanına şifre sıfırlama talebi gönderilir
    sonuc = kullanici_controller_instance.admin_kullanici_sifre_sifirla_controller(form_data)
    
    # Controller'dan gelen sonuç çözülür
    basarili_mi = sonuc.get("success", False)
    mesaj = sonuc.get("message", "İşlem tamamlandı.")

    #    API cevabı türü
    if is_api_request:
        
        # Başarılıysa JSON dön
        if basarili_mi:
            return jsonify({
                "success": True,
                "message": mesaj,
                "username": sonuc.get("username")
            }), 200
        
        # Başarısızsa JSON hata dön
        else:
            return jsonify({"success": False, "message": mesaj}), 400

    #   HTML tabanlı kullanıcı   
    flash(mesaj, "success" if basarili_mi else "danger")

    # Personel ise  personel sayfasına
    # Admin ise admin anasayfasına
    return redirect(
        url_for('personel.personel_sayfasi') if g.role=="personel" else url_for('admin.admin_anasayfa')
    )