# ------------------- FLASK VE TEMEL KÜTÜPHANELER -------------------

from mysql.connector.errors import DatabaseError, ProgrammingError, IntegrityError
from ssl import SSLError
from flask import Flask, abort, flash, request, session, render_template, redirect, url_for, jsonify,g
from functools import wraps
import secrets, string
import os
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import sys
# ------------------- CONTROLLERLAR -------------------
from controllers.personelController import personelController
from controllers.adminkontroller import adminkontroller 
from controllers.kitapController import kitapController
from controllers.kullanicikontroller import  kullanicikontroller
from controllers.odunccontroller import odunccontroller
from controllers.cezaController import cezaController
from controllers.odunccontroller import odunc_controller_instance
# ------------------- SERVİSLER -------------------
from repository.varsayilanekleme import setup_database
from services.adminService import adminService
from services.kullaniciService import kullaniciService
from services.kitapService import kitapService
from services.cezaService import cezaService
from services.oduncService import oduncService
# ------------------- OBJELER -------------------
from services.personelService import personelService

# ------------------- MAIL -------------------
from send_mail import send_pending_mails
# ------------------- VERİTABANI -------------------
from database import baglanti_olustur, tablolar_olustur

# ------------------- REPO -------------------
from repository.veriRepository import VeriService

# ------------------- DECORATORS -------------------
from decorators import admin_required, login_required,admin_or_personel_required

# ------------------- DB CONFIG -------------------
db_config = {
    "host": "127.0.0.1",
    "user": "melisa",
    "password": "Mtz0504*",
    "database": "kutuphane_db",
    "port": 3306
#mysql e baglanmak iicn gerekli bilgiler
}
cezaService = cezaService(db_config)
kitap_islemleri = kitapService(db_config)
odunc_islemleri = oduncService(db_config)
kullanici_islemleri = kullaniciService(db_config)
admin_service = adminService(db_config)
personel_service = personelService(db_config)
ceza_controller_instance = cezaController(db_config)
kullanici_controller_instance = kullanicikontroller()
personel_service = personelService(db_config)
personel_controller_instance=personelController(db_config)
# db sifirlamak ve varsayilan admin eklemek icin
#if __name__ == "__main__":
#    conn = baglanti_olustur() 
 #   service = VeriService(conn)
 #   service.veri_sifirla_delete() 
#    tablolar_olustur() 
#    setup_database()
# ------------------- FLASK APP -------------------
app = Flask(__name__)
SECRET = "56925541090436581"
app.secret_key = "super_secret_12345_melisa"  

def make_json_compatible(obj):
#donebilecek her veri tipini json formatına uyarlamak için
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, dict):
        return {k: make_json_compatible(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        if hasattr(obj, "_fields"):  
            return {k: make_json_compatible(v) for k, v in obj._asdict().items()}
        else:
            return [make_json_compatible(i) for i in obj]
    else:
        return obj

@app.route('/')
def anasayfa():
    #jdon istegi gelirse
    if request.accept_mimetypes.best == "application/json":
        return jsonify({
            "success": True, 
            "message": "Catlary Yönetim Sistemine hoşgeldiniz! "
        }), 200
        #json istegi gelmezse direkt anasayfa.html e yonlendirir
    return render_template("anasayfa.html")

@app.route('/kayitol', methods=['POST'])
def kayit_ol():
    # JSON isteği kontrolü
    is_api_request = request.accept_mimetypes.best == "application/json" or request.is_json
    
    if is_api_request and request.is_json:
    
        data = request.get_json(silent=True) or {}
    else:
        # Standart HTML Formundan veri alir
        data = request.form
    
    controller_sonuc = kullanicikontroller.kayit_ol_controller(data, kullanici_islemleri)

    if isinstance(controller_sonuc, tuple) or hasattr(controller_sonuc, 'get_data'):
      return controller_sonuc 

    sonuc = controller_sonuc 
    basarili_mi = sonuc.get("basarili", False) 

    
    #  JSON yanıtı
    if is_api_request:
        status_code = 201 if basarili_mi else 400
        return jsonify(sonuc), status_code
    
    if basarili_mi:
        flash(sonuc.get("mesaj", "Kayıt başarılı."), "success")
    else:
        flash(sonuc.get("mesaj", "Kayıt başarısız."), "error")
        
    return redirect(url_for('anasayfa'))

@app.route("/girisyap", methods=["POST"])
def girisyap():
    SECRET2 = SECRET 
    if request.is_json:
        form = request.get_json()
        form['is_web'] = False
    else:
        form = request.form.to_dict()
        form['is_web'] = True
    
    controller_sonuc = kullanicikontroller.giris_yap_controller(form, SECRET2)
    
    # json kontrolu
    if isinstance(controller_sonuc, tuple) or hasattr(controller_sonuc, 'get_data'):
        return controller_sonuc
    
    # WEB Kontrolü
    if isinstance(controller_sonuc, dict):
        # Başarısız ise
        if controller_sonuc.get("basarili") is False:
            mesaj = controller_sonuc.get("mesaj", "Giriş başarısız.")
            flash(mesaj, "error") 
            return redirect(url_for('anasayfa'))
        
        # Başarılı ise
        if controller_sonuc.get("redirect_url"):
            flash(controller_sonuc.get("mesaj", "Giriş başarılı."), "success")
            return redirect(controller_sonuc['redirect_url'])
        
        return redirect(url_for('anasayfa'))
    
    return "Beklenmeyen sunucu yanıtı.", 500

@app.route('/admin_anasayfasi')
@admin_required
def admin_anasayfa():
    username = g.username 
    
    if request.accept_mimetypes.best == "application/json":
        return jsonify({"username": username, "message": "Admin sayfası erişimi başarılı"}), 200
        
    return render_template("admin.html", username=username)

@app.route('/kullanici_sayfasi')
@login_required
def kullanici_sayfasi():
    username = g.username 
    
    if request.accept_mimetypes.best == "application/json":
        return jsonify({"username": username, "message": "Kullanıcı sayfası erişimi başarılı"}), 200
        
    return render_template("kullanici.html", username=username)

@app.route('/personel_sayfasi') 
@admin_or_personel_required 
def personel_sayfasi(): 
   
    user_id = g.user_id 
    username = g.username
    role = g.role

    is_api_request = request.accept_mimetypes.best == "application/json"
    
    if is_api_request:
        return jsonify({
            "success": True,
            "message": "Personel/Admin sayfası erişimi başarılı.",
            "kullanici_adi": username,
            "kullanici_rolu": role,
            "user_id": user_id
        }), 200
        
    return render_template('personel.html', 
                            kullanici_adi=username,
                            kullanici_rolu=role,
                            user_id=user_id)
    
@app.route('/cikis', methods=['GET'])
def cikis_yap():
    response =(redirect(url_for('anasayfa')))
    
    response.set_cookie(
        'jwt_token', 
        '', 
        expires=0,
        httponly=True,
        secure=True, 
        samesite='Lax' 
    )
    
    if request.accept_mimetypes.best == "application/json":
        return jsonify({"success": True, "message": "Başarıyla çıkış yaptınız. JWT silindi."}), 200
    return response


@app.route("/kullaniciekle", methods=["POST"])
@admin_or_personel_required
def kullanici_ekle_route():
    # kullanıcı verilerini alir
    data = request.get_json(silent=True) or request.form

    # ilgili Controlleri cagirir
    sonuc = kullanicikontroller.kullanici_ekle_controller(data)
    basarili_mi = sonuc.get("basarili", False)
    mesaj = sonuc.get("mesaj", "İşlem tamamlandı.")

    flash(mesaj, "success" if basarili_mi else "danger")
    # JSON isteği gelmişse JSON döndurur
    if request.is_json or request.accept_mimetypes.best == "application/json":
        return jsonify({"success": basarili_mi, "message": mesaj}), 201 if basarili_mi else 400
    #  Rol bazlı HTML yönlendirme
    rol = getattr(g, "role", None)  
    if rol == "admin":
        return redirect(url_for("admin_anasayfa"))
    elif rol == "personel":
        return redirect(url_for("personel_sayfasi"))

    return render_template("admin.html", username=getattr(g, "username", ""))

@app.route('/kendiborc_ode/<username>', methods=['GET', 'POST'])
@login_required
def kendiborc_ode(username):

    is_api_request = request.accept_mimetypes.best == "application/json"

    if username != g.username:
        mesaj = "Bu işlem için yetkiniz yok."
        if is_api_request:
            return jsonify({"success": False, "message": mesaj}), 403
        flash(mesaj, "danger")
        return redirect(url_for("kullanici_sayfasi", username=g.username))

    toplam_borc = ceza_controller_instance.borc_getir_controller(username)

    if toplam_borc is None:
        mesaj = "Borç bilgisi alınamadı."
        if is_api_request:
            return jsonify({"success": False, "message": mesaj}), 500
        flash(mesaj, "danger")
        return redirect(url_for("kullanici_sayfasi", username=username))

    if request.method == "POST":
        if toplam_borc <= 0:
            mesaj = "Ödenecek aktif borcunuz bulunmamaktadır."
            if is_api_request:
                return jsonify({"success": False, "message": mesaj}), 400
            flash(mesaj, "info")
            return redirect(url_for("kullanici_sayfasi", username=username))

        sonuc = ceza_controller_instance.ceza_odendi_yap(
            kullanici_id=g.user_id,
            odeme_yapilsin_mi=True,
            admin=False
        )

        if not sonuc.get("success"):
            mesaj = sonuc.get("message", "Ödeme gerçekleştirilemedi.")
            if is_api_request:
                return jsonify({"success": False, "message": mesaj}), 400
            flash(mesaj, "danger")
            return redirect(url_for("kendiborc_ode", username=username))

        if is_api_request:
            return jsonify({"success": True, "message": "Ödeme başarıyla tamamlandı."}), 200

        flash("Borç ödeme işlemi başarıyla tamamlandı.", "success")
        return redirect(url_for("kullanici_sayfasi", username=username))

    if is_api_request:
        return jsonify({
            "success": True,
            "toplam_borc": toplam_borc,
            "message": "Borç bilgisi getirildi"
        }), 200

    return render_template("borcode.html", toplam_borc=toplam_borc, username=username)

@app.route('/kullanici_durum_degistir', methods=['POST'])
@admin_or_personel_required
def kullanici_durum_degistir():
    print("TEST")
    data = request.get_json(silent=True) or request.form
    kullanici_adi = data.get('kullanici_adi')
    
    if not kullanici_adi:
        mesaj = "Eksik veri: 'kullanici_adi' gereklidir."
        if request.accept_mimetypes.best == "application/json" or request.is_json:
            return jsonify({"success": False, "message": mesaj}), 400
        return redirect(url_for('kullanicilar'))

    try:
        user_data = kullanici_islemleri.get_by_username(kullanici_adi) 
        
        if not user_data:
            mesaj = f"Kullanıcı '{kullanici_adi}' bulunamadı."
            if request.accept_mimetypes.best == "application/json":
                return jsonify({"success": False, "message": mesaj}), 404
            return redirect(url_for('kullanicilar'))
        
        user_id = user_data['id']
        sonuc = kullanici_islemleri.kullanici_aktiflik_durumu_degistir(user_id) 
        
        basarili_mi = sonuc.get('success')
        status_code = 200 if basarili_mi else 400
        
        if request.accept_mimetypes.best == "application/json" or request.is_json:
            return jsonify(sonuc), status_code
        
        return redirect(url_for('kullanicilar_goster'))
            
    except Exception as e:
        mesaj = f"İşlem Başarısız: Sunucu tarafında beklenmedik bir hata oluştu: {e}"
        print(f"HATA /kullanici_durum_degistir: {e}") 
        
        if request.accept_mimetypes.best == "application/json":
            return jsonify({"success": False, "message": mesaj}), 500
        return redirect(url_for('kullanicilar_goster'))
        

@app.route('/kitaplari_goruntule', methods=['GET'])
@login_required
def kitaplari_goruntule():
    username = g.username
    role = g.role 
    aranan_kitap = request.args.get('aranacak_kitap', '')
    kitaplar, admin_mi = kitapController.kitaplari_goruntule_controller(
        username, role, aranan_kitap
    )

    if role in ["admin", "personel"]:
        admin_mi = True
    else:
        admin_mi = False

    if request.accept_mimetypes.best == "application/json":
        return jsonify({
            "kitaplar": make_json_compatible(kitaplar),
            "username": username,
            "aranan_kitap": aranan_kitap,
            "admin_mi": admin_mi
        }), 200

    return render_template(
    "kitaplar.html",
    kitaplar=kitaplar,
    username=username,
    aranan_kitap=aranan_kitap,
    admin_mi=admin_mi,
    role=role
)

@app.route('/kullanicilar', methods=['GET'])
@admin_or_personel_required 
def kullanicilar():
    username = g.username
    role = g.role 
    try:
        kullanicilar_listesi = kullanici_islemleri.tum_kullanicilari_getir()
    except Exception as e:
        print(f"HATA: Kullanıcı listesi alınamadı: {e}")
        kullanicilar_listesi = []

    # JSON isteği gelirse
    if request.accept_mimetypes.best == "application/json":
        return jsonify({
            "username": username,
            "role": role,
            "kullanicilar": make_json_compatible(kullanicilar_listesi)
        }), 200
    return render_template(
        "kullanicilar.html",
        kullanicilar=kullanicilar_listesi,
        geri_url=url_for("admin_anasayfa") if role=="admin" else url_for("personel_sayfasi")
    )

@app.route('/kitapsil', methods=['POST']) 
@admin_or_personel_required
def kitap_sil():
    username = g.username
    # JSON isteği kontrolü ve Veri Alma
    is_api_request = request.is_json or request.accept_mimetypes.best == "application/json"
    if is_api_request:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form
    kitap_id = data.get('kitap_id')
    # Eksik Veri Kontrolü
    if not kitap_id:
        mesaj = "Hata: Silinecek kitap ID'si sağlanmadı."
        basarili_mi = False
        
        # Eğer  veri eksikse, 400 Bad Request döner
        if is_api_request:
             return jsonify({"success": False, "mesaj": mesaj}), 400
    else:
        mesaj, _, basarili_mi = kitapController.kitap_sil_controller(kitap_id)
        
    # JSON Yanıtı
    if is_api_request:
        # Başarılı ise 200 OK, değilse 400 Bad Request
        status_code = 200 if basarili_mi else 400
        return jsonify({"success": basarili_mi, "mesaj": mesaj}), status_code

    flash(mesaj, "success" if basarili_mi else "danger")
    return redirect(request.referrer or url_for('kitaplari_goruntule'))

@app.route('/kitapekle', methods=['POST']) 
@admin_or_personel_required
def kitap_ekle():
    username = g.username
    form_data = request.form
    try:
        mesaj, kitap_id, kitap_bilgileri, basarili_mi = kitapController.kitap_ekle_controller(form_data)
    except ValueError as e:
        print(f"HATA /kitapekle: Controller'dan yanlış sayıda değer geldi: {e}")
        mesaj = "Sunucu Hatası: Kitap ekleme kontrolcüsü eksik/fazla değer döndürdü."
        kitap_id = None
        kitap_bilgileri = {}
        basarili_mi = False

    status_code = 201 if basarili_mi else 400

    # JSON için
    if request.accept_mimetypes.best == "application/json":
        response_data = {
            "islem_turu": "Kitap Ekleme",
            "mesaj": mesaj,
            "success": basarili_mi,
            "kitap_id": kitap_id,
            "username": username,
            **kitap_bilgileri
        }
        return jsonify(response_data), status_code

    # FLASH MESAJ
    if basarili_mi:
        flash(mesaj, "success")
    else:
        flash(mesaj, "error")

    return redirect(request.referrer or url_for('kitaplari_goruntule'))


@app.route("/kitapoduncver", methods=["POST"])
@admin_or_personel_required
def kitap_odunc_ver():
    username = g.username
    data = request.get_json(silent=True) or request.form

    mesaj_dict = odunc_controller_instance.odunc_ver_controller(data)
    send_pending_mails()

    basarili_mi = mesaj_dict.get("success", False)

    # Kullanıcı JSON istiyorsa
    if request.accept_mimetypes.best == "application/json":
        status_code = 200 if basarili_mi else 400
        return jsonify(mesaj_dict), status_code

    if basarili_mi:
        flash(mesaj_dict.get("message", "Ödünç verme işlemi başarılı!"), "success")
    else:
        flash(mesaj_dict.get("message", "Ödünç verme işlemi başarısız!"), "error")

    return redirect(request.referrer or url_for("admin_anasayfa"))


@app.route('/kitapiadeal', methods=['POST'])
@admin_or_personel_required
def kitap_iade_al():
    username = g.username
    role = g.role
    form_data = request.form
    
    mesaj = odunc_controller_instance.odunc_iade_controller(form_data)
    send_pending_mails()

    basarili_mi = "başarıyla" in mesaj.lower()

    kategori = "success" if basarili_mi else "danger"
    flash(mesaj, kategori)

    # JSON İSTEĞİ GELDİYSE 
    if request.accept_mimetypes.best == "application/json":
        return jsonify({"mesaj": mesaj, "success": basarili_mi}), 200 if basarili_mi else 400

    if role == "admin":
        return redirect(url_for('admin_anasayfa')) 
    elif role == "personel":
        return redirect(url_for('personel_sayfasi'))
    else:
        # Normal kullanıcılar için iade rotası normalde buraya düşmez ama güvenlik amaçlı
        return redirect(url_for('kullanici_sayfasi'))

@app.route('/oduncalmagecmisim/<username>')
@login_required
def oduncalmagecmisim(username):
    username = g.username
    
    gecmis = odunc_controller_instance.kullanici_odunc_gecmisi_controller(username)
    gecmis_json = make_json_compatible(gecmis)

    if request.accept_mimetypes.best == "application/json":
        return jsonify({
            "username": username,
            "odunc_gecmisi": gecmis_json
        }), 200

    return render_template(
        "odunc_gecmisim.html",
        username=username, 
        odunc_gecmisi=gecmis
    )

@app.route('/tumkullanicioduncalmagecmisigoster', methods=['GET'])
@admin_or_personel_required 
def tum_odunc_gecmisi():
    role = g.role
    username = g.username
    
    tum_gecmis = odunc_controller_instance.tum_kullanicilarin_odunc_gecmisi_controller(role, username)
    
    # JSON İsteği 
    is_api_request = request.accept_mimetypes.best == "application/json"
    
    if is_api_request:
        gecmis_json = make_json_compatible(tum_gecmis)
        
        return jsonify({
            "success": True,
            "role": role,
            "username": username,
            "tum_odunc_gecmisi": gecmis_json
        }), 200

    # HTML Render
    return render_template(
        "tum_odunc_gecmisi.html",
        tum_odunc_gecmisi=tum_gecmis,
        role=g.role,
        username=g.username
    )
    
@app.route('/adminekle', methods=['POST'])
@admin_required
def admin_ekle_route():
    current_admin_username = g.username
    data = request.get_json(silent=True) or request.form
    
    username = data.get("yeni_admin_adi")
    email = data.get("yeni_admin_email")
    sifre = data.get("yeni_admin_sifre")
    sifre_tekrar = data.get("yeni_admin_sifre_tekrar")

    try:
        sonuc = adminkontroller.admin_ekle_controller(username, email, sifre, sifre_tekrar)
        basarili_mi = sonuc.get("success", False)

        flash(sonuc.get("message", "İşlem tamamlandı."), "success" if basarili_mi else "danger")

        # JSON isteği gelirse JSON dön
        if request.accept_mimetypes.best == "application/json" or request.is_json:
            status_code = 201 if basarili_mi else 400
            return jsonify(sonuc), status_code

        # Ekrana mesaj göstermek için template render
        return render_template("admin.html", username=current_admin_username)

    except Exception as e:
        mesaj = f"Hata oluştu: {str(e)}"
        print(f"HATA /adminekle: {e}") 

        flash(mesaj, "danger")
        if request.accept_mimetypes.best == "application/json" or request.is_json:
            return jsonify({"success": False, "message": mesaj}), 500
        return render_template("admin.html", username=current_admin_username)

@app.route('/adminsil', methods=['POST'])
@admin_required
def admin_sil_route():
    current_admin_username = g.username
    
    try:
        data = request.get_json(silent=True) or request.form
        username = data.get("silinecek_admin_adi")
        username_tekrar = data.get("silinecek_admin_adi_tekrar")

        if not all([username, username_tekrar]):
            mesaj = "Silinecek admin kullanıcı adı ve tekrarı gereklidir."
            flash(mesaj, "danger")
            if request.accept_mimetypes.best == "application/json" or request.is_json:
                return jsonify({"success": False, "message": mesaj}), 400
            return render_template("admin.html", username=current_admin_username)

        sonuc = adminkontroller.admin_sil_controller(username, username_tekrar)
        basarili_mi = sonuc.get("success", False)

        flash(sonuc.get("message", "İşlem tamamlandı."), "success" if basarili_mi else "danger")

        if request.accept_mimetypes.best == "application/json" or request.is_json:
            status_code = 200 if basarili_mi else 400
            return jsonify(sonuc), status_code

        return render_template("admin.html", username=current_admin_username)

    except Exception as e:
        mesaj = f"Hata oluştu: {str(e)}"
        print(f"HATA /adminsil: {e}") 
        flash(mesaj, "danger")

        if request.accept_mimetypes.best == "application/json" or request.is_json:
            return jsonify({"success": False, "message": mesaj}), 500

        return render_template("admin.html", username=current_admin_username)


@app.route('/adminler') 
@admin_or_personel_required
def adminler_goster():
    username = g.username 
    
    adminler = adminkontroller.tum_adminleri_getir() 
    
    print(f"DEBUG: Adminler listesi çekildi: {adminler}")
    
    # JSON isteği için
    if request.accept_mimetypes.best == "application/json":
        adminler_json = make_json_compatible(adminler)
        return jsonify({"username": username, "adminler": adminler_json}), 200
    
    # HTML Render
    return render_template("adminler.html", adminler=adminler, username=username)

@app.route('/cezatablosunugoster')
@admin_or_personel_required
def ceza_tablosunu_goster():
    username = g.username
    cezalar = [] 
    try:
        print("CEZALAR VERİSİ:", cezalar) 
        print("TİPİ:", type(cezalar))
        
        cezalar_json = make_json_compatible(cezalar)
        cezalar = ceza_controller_instance.tum_cezalari_getir()
        cezalar_json = make_json_compatible(cezalar)

        if request.accept_mimetypes.best == "application/json":
            return jsonify({"username": username, "cezalar": cezalar_json}), 200

        # Başarılı olduğunda çalışır
        return render_template('tum_cezalar.html', username=username, role=g.role, cezalar=cezalar)

    except Exception as e:
        mesaj = f"İşlem Başarısız: Sunucu tarafında beklenmedik bir hata oluştu: {str(e)}"
        print(f"HATA /cezatablosunugoster: {e}")
        
        if request.accept_mimetypes.best == "application/json":
            return jsonify({"success": False, "message": mesaj}), 500
        return render_template('tum_cezalar.html', username=username, role=g.role, cezalar=cezalar)

@app.route('/cezalarimigoster/<username>')
@login_required
def cezalarimigoster(username):
    username = g.username
    
    try:
        cezalar = ceza_controller_instance.kullanici_cezalarini_goster(username)
        cezalar_json = make_json_compatible(cezalar)

        if request.accept_mimetypes.best == "application/json":
            return jsonify({"username": username, "cezalar": cezalar_json}), 200
        
        return render_template('cezalarim.html', username=username, cezalar=cezalar)

    except Exception as e:
        mesaj = f"İşlem Başarısız: Sunucu tarafında beklenmedik bir hata oluştu: {str(e)}"
        print(f"HATA /cezalarimigoster: {e}")
        
        if request.accept_mimetypes.best == "application/json":
            return jsonify({"success": False, "message": mesaj}), 500
        return redirect(url_for('kullanici_sayfasi'))

@app.route('/kullanici_sifre_degistir', methods=['POST'])
@login_required
def kullanici_sifre_degistir():
    user_id = g.get("user_id")
    username = g.get("username")
    # Hem JSON hem HTML form için veri alir
    data = request.get_json(silent=True) or request.form

    if not user_id:
        mesaj = "Kimlik doğrulanamadı. Lütfen tekrar giriş yapın."
        if request.accept_mimetypes.best == "application/json":
            return jsonify({"success": False, "message": mesaj}), 401
        
        flash(mesaj, "danger")
        return redirect(url_for("anasayfa"))
    try:
        sonuc = kullanici_controller_instance.kullanici_sifre_degistir_controller(user_id, data)
    except Exception as e:
        if request.accept_mimetypes.best == "application/json":
            return jsonify({
                "success": False, 
                "message": "Bir hata oluştu. Sistem yöneticisine bildiriniz.",
                "detail": str(e)
            }), 500
        
        flash("Bir hata oluştu. Lütfen tekrar deneyin.", "danger")
        return redirect(url_for("kullanici_sayfasi"))
    basarili_mi = sonuc.get("success", False)
    mesaj = sonuc.get("message", "")

    if request.accept_mimetypes.best == "application/json":
        status = 200 if basarili_mi else 400
        return jsonify(sonuc), status

    if basarili_mi:
        flash("Şifreniz başarıyla değiştirildi.", "success")
    else:
        flash(mesaj or "Şifre değiştirilemedi.", "danger")

    return redirect(url_for("kullanici_sayfasi"))
@app.route('/kullanici_sifre_sifirla', methods=['POST'])
@admin_or_personel_required
def admin_kullanici_sifre_sifirla_route():
    
    is_api_request = request.is_json or request.accept_mimetypes.best == "application/json"
    
    form_data = request.get_json(silent=True) if is_api_request else request.form
    
    if not form_data:
        mesaj = "Form verisi eksik."
        if is_api_request:
            return jsonify({"success": False, "message": mesaj}), 400
        flash(mesaj, "danger")
        return redirect(url_for('admin_anasayfa'))
        
    sonuc = kullanici_controller_instance.admin_kullanici_sifre_sifirla_controller(form_data)
    basarili_mi = sonuc.get("success", False)
    mesaj = sonuc.get("message", "İşlem tamamlandı.")

    if is_api_request:
        if basarili_mi:
            return jsonify({
                "success": True,
                "message": mesaj,
                "username": sonuc.get("username")
            }), 200
        else:
            return jsonify({"success": False, "message": mesaj}), 400

    flash(mesaj, "success" if basarili_mi else "danger")
    return redirect(url_for('personel_sayfasi') if g.role=="personel" else url_for('admin_anasayfa'))

@app.route('/admin_sifre_degistir', methods=['POST'])
@admin_required
def admin_sifre_degistir():
    username = g.username
    data = request.get_json(silent=True) or request.form
    sonuc = adminkontroller.admin_sifre_degistir_controller(data)
    basarili_mi = sonuc.get('success', False)
    mesaj = sonuc.get('message', "İşlem tamamlandı.")
    status_code = 200 if basarili_mi else 400
    flash(mesaj, "success" if basarili_mi else "danger")

    # JSON istek gelirse
    if request.accept_mimetypes.best == "application/json":
        return jsonify(sonuc), status_code
    return render_template("admin.html", username=username)

@app.route('/ceza_sorgula', methods=['POST'])
@admin_or_personel_required
def ceza_sorgula_api_route():
    data = request.get_json(silent=True) or {}
    ceza_id = data.get("ceza_id")

    if not ceza_id:
        return jsonify({"success": False, "message": "Ceza ID belirtilmedi."}), 400

    try:
        ceza_id = int(ceza_id)
    except ValueError:
        return jsonify({"success": False, "message": "Geçersiz Ceza ID."}), 400

    sorgu_sonucu = ceza_controller_instance.ceza_bilgilerini_getir(ceza_id)

    if not sorgu_sonucu:
        return jsonify({"success": False, "message": "Belirtilen ID'ye ait ceza bulunamadı."}), 404

    if sorgu_sonucu.get('odendi_mi') == 1:
        return jsonify({"success": False, "message": "Bu ceza zaten ödenmiş."}), 400

    return jsonify({
        "success": True,
        "borc_miktari": sorgu_sonucu['miktar'],
        "username": sorgu_sonucu['username']
    }), 200

@app.route('/cezaode', methods=['POST'])
@admin_or_personel_required
def ceza_ode():
    data = request.get_json(silent=True) or {}
    ceza_id = data.get("ceza_id")

    if not ceza_id:
        return jsonify({"success": False, "message": "Ceza ID belirtilmedi."}), 400

    try:
        ceza_id = int(ceza_id)
    except ValueError:
        return jsonify({"success": False, "message": "Geçersiz Ceza ID."}), 400

    try:
        success, message = ceza_controller_instance.ceza_ode(ceza_id)

    except (DatabaseError, IntegrityError, ProgrammingError) as e:
        if "1644" in str(e) or "45000" in str(e):
            return jsonify({"success": False, "message": "Kitap iade edilmeden ceza ödenemez."}), 400
        
        return jsonify({"success": False, "message": "Veritabanı hatası oluştu."}), 500

    except Exception as e:
        print("CEZA ÖDEME HATA:", e)
        return jsonify({"success": False, "message": "Beklenmeyen bir sunucu hatası oluştu."}), 500

    return jsonify({"success": success, "message": message}), 200 if success else 400

@app.route("/personel_ekle", methods=["POST"])
@admin_required
def personel_ekle():
    is_api_request = request.is_json or request.accept_mimetypes.best == "application/json"
    
    if is_api_request:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form
        
    ad_soyad = data.get("ad_soyad")
    email = data.get("email")
    sifre = data.get("sifre")
    sifre_tekrar = data.get("sifre_tekrar")

    if not all([ad_soyad, email, sifre, sifre_tekrar]):
        mesaj = "Tüm alanları doldurmalısın!"
        
        if is_api_request:
            return jsonify({"success": False, "message": mesaj}), 400
            
        flash(mesaj, "error")
        return redirect(url_for("admin_anasayfa"))

    try:
        sonuc = personel_controller_instance.personel_ekle(
             ad_soyad, email, sifre, sifre_tekrar
        )
        
        basarili_mi = sonuc.get("success", False)
        mesaj = sonuc.get("message", "İşlem tamamlandı.")

        if is_api_request:
            status_code = 201 if basarili_mi else 400
            return jsonify(sonuc), status_code
    
        if basarili_mi:
            flash(mesaj, "success")
        else:
            flash(mesaj, "error")

        return redirect(url_for("admin_anasayfa"))

    except Exception as e:
        import traceback
        mesaj = f"Beklenmeyen bir sistem hatası oluştu: {e}"
        print("PERSONEL EKLE HATA:", e)
        traceback.print_exc() 
        
        if is_api_request:
            return jsonify({"success": False, "message": mesaj}), 500
            
        flash(mesaj, "error")
        return redirect(url_for("admin_anasayfa"))
    
@app.route("/personel_sifre_sifirla", methods=["POST"])
@admin_required
def admin_personel_sifre_sifirla_route():
    is_api_request = request.is_json or request.accept_mimetypes.best == "application/json"
    
    # Gelen isteğin JSON mu yoksa standart form verisi mi olduğunu kontrol eder
    form_data = request.get_json(silent=True) if is_api_request else request.form
    
    if not form_data:
        mesaj = "Form verisi eksik."
        if is_api_request:
            return jsonify({"success": False, "message": mesaj}), 400
        flash(mesaj, "danger")
        return redirect(url_for('admin_anasayfa'))

    sonuc = personel_controller_instance.admin_personel_sifre_sifirla_controller(form_data)

    basarili_mi = sonuc.get("success", False)
    mesaj = sonuc.get("message", "İşlem tamamlandı.")

    if is_api_request:
        if basarili_mi:
           
            return jsonify({
                "success": True,
                "message": mesaj,
                "personel_id": sonuc.get("personel_id") 
            }), 200
        else:
            return jsonify({"success": False, "message": mesaj}), 400

    flash(mesaj, "success" if basarili_mi else "danger")
    return redirect(url_for('admin_anasayfa'))

@app.route("/personel_liste", methods=["GET"])
@admin_required 
def personel_listesi_goster():
    is_api_request = request.accept_mimetypes.best == "application/json"
    
    try:
        personel_listesi = personel_controller_instance.tum_personelleri_getir()
        
        if is_api_request:
            personel_json = make_json_compatible(personel_listesi)
            return jsonify({
                "success": True,
                "personeller": personel_json
            }), 200
        
        return render_template("personel_listesi.html", personeller=personel_listesi)
        
    except Exception as e:
        import traceback
        hata_mesaji = "Personel listesi yüklenirken beklenmeyen bir hata oluştu."
        print(f"Personel Listesi Getirme Hatası: {e}")
        traceback.print_exc()
        
        if is_api_request:
            return jsonify({
                "success": False, 
                "message": hata_mesaji
            }), 500
            
        flash(hata_mesaji, "error")
        return redirect(url_for('admin_anasayfa'))
    
@app.route("/personel/aktiflik_degistir", methods=["POST"])
@admin_required
def personel_aktiflik_degistir_route():
    is_api_request = request.is_json or request.accept_mimetypes.best == "application/json"
    
    # JSON veya Form verisini al
    if is_api_request:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form

    try:
        personel_id_str = data.get("personel_id")
        yeni_durum_str = data.get("yeni_durum")
        
        if not personel_id_str or yeni_durum_str is None:
            mesaj = "Personel ID veya yeni durum bilgisi eksik."
            status_code = 400
            
            if is_api_request:
                return jsonify({"success": False, "message": mesaj}), status_code
            
            flash(mesaj, "error")
            return redirect(url_for('personel_listesi_goster'))

        personel_id = int(personel_id_str)
        yeni_durum = yeni_durum_str in ['1', 1, 'true', True] 
        
        sonuc = personel_controller_instance.personel_aktiflik_degistir(personel_id, yeni_durum)

        basarili_mi = sonuc.get("success", False)
        mesaj = sonuc.get("message", "İşlem tamamlandı.")
        
        if is_api_request:
            status_code = 200 if basarili_mi else 400
            return jsonify({
                "success": basarili_mi, 
                "message": mesaj,
                "personel_id": personel_id
            }), status_code
        flash(mesaj, "success" if basarili_mi else "error")
    except ValueError:
        mesaj = "Geçersiz personel ID formatı."
        if is_api_request:
            return jsonify({"success": False, "message": mesaj}), 400
        flash(mesaj, "error")
    except Exception as e:
        mesaj = "Aktiflik değiştirme işlemi sırasında beklenmeyen bir hata oluştu."
        print(f"Aktiflik Değiştirme Hatası: {e}")
        
        if is_api_request:
            return jsonify({"success": False, "message": mesaj}), 500
        flash(mesaj, "error")

    return redirect(url_for('personel_listesi_goster'))

@app.route("/personel_sifre_degistir", methods=["POST"])
@admin_or_personel_required 
def personel_sifre_degistir_route():
    personel_id = g.user_id
    data = request.get_json(silent=True) or request.form
    try:
        if not personel_id:
            flash("Yetkiniz yok. Lütfen tekrar giriş yapın.", "danger")
            return redirect(url_for("anasayfa"))
        sonuc = personel_controller_instance.personel_sifre_degistir_controller(personel_id, data)
        basarili_mi = sonuc.get("success", False)
        mesaj = sonuc.get("message", "İşlem tamamlandı.")
        
        # JSON yanıtı 
        if request.is_json:
            return jsonify(sonuc), 200 if basarili_mi else 400

        flash(mesaj, "success" if basarili_mi else "danger")
        return redirect(url_for("personel_sayfasi"))

    except Exception as e:
        print(f"PERSONEL ŞİFRE DEĞİŞTİR HATA: {e}")
        if request.is_json:
            return jsonify({"success": False, "message": "Beklenmeyen sunucu hatası."}), 500
        flash("Beklenmeyen bir hata oluştu.", "danger")
        return redirect(url_for("personel_sayfasi"))
    
if __name__ == "__main__":
    app.run(debug=True)