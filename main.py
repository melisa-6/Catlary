# ------------------- FLASK VE TEMEL KÜTÜPHANELER -------------------
from flask import Flask, flash, request, session, render_template, redirect, url_for, jsonify
from functools import wraps
import secrets, string
from werkzeug.security import generate_password_hash, check_password_hash

# ------------------- CONTROLLERLAR -------------------
from controllers import (
    adminkontroller,
    odunccontroller,
    cezaController,
    kullanicikontroller,
    kitapController
)
from controllers.cezaController import CezaController

# ------------------- SERVİSLER -------------------
from services.adminService import AdminService
from services.kullaniciService import KullaniciService
from services.kitapService import KitapService
from services.cezaService import CezaService
from services.oduncService import OduncService
from send_mail import send_pending_mails


# ------------------- VERİTABANI -------------------
from database import baglanti_olustur

# ------------------- REPO -------------------
from repository.veriRepository import VeriService

# ------------------- DECORATORS -------------------
from decorators import admin_required, login_required

# ------------------- DB CONFIG -------------------
db_config = {
    "host": "127.0.0.1",
    "user": "melisa",
    "password": "",
    "database": "kutuphane_db",
    "port": 3306
}

# ------------------- OBJELER -------------------
ceza_islemleri = CezaService(db_config)
kitap_islemleri = KitapService()
kullanici_islemleri = KullaniciService(db_config)
odunc_islemleri = OduncService(db_config)
admin_service = AdminService(db_config)
ceza_controller=CezaController(db_config)

# db sifirlamak ve varsayilan admin eklemek icin
#if __name__ == "__main__":
#    conn = baglanti_olustur(db_config)
#    service = VeriService(conn)
#    service.veri_sifirla_delete()
#    from repository.varsayilanekleme import setup_database
#    setup_database()
# ------------------- FLASK APP -------------------
app = Flask(__name__)
app.secret_key = "GizliAnahtar"



#sayfa ilk acildiginda karsimiza anasayfa.html in gelmesi icin
@app.route('/')
def anasayfa():
    return render_template("anasayfa.html")

#anasayfada kayit ol butonuna tiklayinca bu route a yonlendirilir
@app.route('/kayitol', methods=['POST'])
def kayit_ol():
    form = request.form
    #controller kismina uygun parametreler ile yonlendirilir
    return kullanicikontroller.kayit_ol_controller(form, kullanici_islemleri)

@app.route('/girisyap', methods=['POST'])
def giris_yap():
    form = request.form
    #anasayfa da admin veya kullanici olarak giris yapmak istedigimizde bu route a yonlendirilirz
    return kullanicikontroller.giris_yap_controller(form, session, kullanici_islemleri)

# Admin sayfası
@app.route('/admin/<username>')
@admin_required
def admin_anasayfa(username):
    return render_template("admin.html", username=username)

# Kullanıcı sayfası
@app.route('/kullanici/<username>')
@login_required
def kullanici_sayfasi(username):
    return render_template("kullanici.html", username=username)

#admin anasayfasindan veya kullanici anasayfasindan basariyla cikmak icin   
@app.route('/cikis')
def cikis_yap():
    session.clear()
    flash("Başarıyla çıkış yaptınız.", "success")
    return redirect(url_for('anasayfa'))
    

@app.route('/kullanicilar/<username>')
def kullanicilar_goster(username):
    kullanicilar = kullanicikontroller.tum_kullanicilari_getir()
    return render_template("kullanicilar.html", kullanicilar=kullanicilar)
 #admin anasayfasinda bulunan kullanicilari goster butonuna tıklayinca bu route a yonlendirir
 #kullanicilar degiskenini controllerdaki ilgili fonksiyona esitler ve uygun kullanicilar.html e yonlendirir    
    
    
@app.route("/kullaniciekle/<username>", methods=["POST"])
@admin_required
def kullanici_ekle_route(username):
    form = request.form
    sonuc = kullanicikontroller.kullanici_ekle_controller(form)
#admin anasayfasinda bulunan kullanici ekle butonuna tiklayınca bu route a yonlendirir
#sonuc degiskenine controllerdaki ilgili fonksiyona yonlendirerek uygun mesaji verir ve admin anasayfasina yonlenirir
    if sonuc.get("basarili"):
        flash(sonuc["mesaj"], "success")
    else:
        flash(sonuc["mesaj"], "error")

    return redirect(url_for("admin_anasayfa", username=username))

@app.route('/kullanici_durum_degistir', methods=['POST'])
@admin_required 
def kullanici_durum_degistir():
#kullanicilar.html de pasiflestir veya aktiflestir butonuna bastigimizda bu route a yonlendirir

    try:
        # JSON verisini alir
        data = request.get_json()
        
        #eksik veya geçersiz veri kontrolu yapar
        if not data or 'kullanici_adi' not in data:
            return jsonify({"success": False, "message": "Eksik veri: 'kullanici_adi' gereklidir."}), 400
            
        kullanici_adi = data.get('kullanici_adi')
        
        # Kullanıcıyı kullanıcı adına göre bulur ve uygun service fonksiyonu ile ID'sini alir
        user_data = kullanici_islemleri.get_by_username(kullanici_adi) 
        
        if not user_data:
            return jsonify({"success": False, "message": f"Kullanıcı '{kullanici_adi}' bulunamadı."}), 404
        
        user_id = user_data['id']
        
        #sonuc degiskenine uygun service fonksiyonu gelen id parametre verilerek atanir 
        sonuc = kullanici_islemleri.kullanici_aktiflik_durumu_degistir(user_id) 
        
        #Sonuca göre JSON yanıtı döndür
        if sonuc.get('success'):
            return jsonify(sonuc), 200
        else:
            # İşlem başarısız olduysa hata mesajını ve 400 durum kodunu döndür
            return jsonify(sonuc), 400
            
    except Exception as e:
        # Sunucu tarafında beklenmedik hata yakalamak için
        print(f"HATA /kullanici_durum_degistir: {e}") 
        return jsonify({
            "success": False, 
            "message": "İşlem Başarısız: Sunucu tarafında beklenmedik bir hata oluştu."
        }), 500


@app.route('/kitaplari_goruntule/<username>', methods=['GET'])
@login_required
def kitaplari_goruntule(username):
    #kullanici veya admin kendi anasayfalarinda bulunan kitaplari goruntule butonuna tiklayinca bu route a yonlendirilir
    if session.get('username') != username and session.get('role') != 'admin':
        return "Bu sayfaya erişim izniniz yok.", 403
#admin veya kullanici degilse uygun uyariyi verir
    aranan_kitap = request.args.get('aranacak_kitap', '')
    #kitap arama alanindan gelen verii alir
#aranan kitabi controllerda uygun fonksiyonla goruntulemek icin yonlendirir
    kitaplar, admin_mi = kitapController.kitaplari_goruntule_controller(
        username, session.get('role'), aranan_kitap
    )
    
#controllerdan gelen kitaplar aranan kitap username admin mi ile kitaplar.html gosterilir
    return render_template(
        "kitaplar.html",
        kitaplar=kitaplar,
        username=username,
        aranan_kitap=aranan_kitap,
        admin_mi=admin_mi
    )
    
@app.route('/kitapekle/<username>', methods=['POST'])
@admin_required
def kitap_ekle(username):
    #admin kitap eklemek istediginde bu route a yonlendirilir 
    form_data = request.form
    
    mesaj, kitap_id, kitap_bilgileri = kitapController.kitap_ekle_controller(form_data)
  #uygun kontrollera yonlendirilir
    # gelen bilgiler ile kitap_islem.html gosterilir
    return render_template(
        "kitap_islem.html",
        islem_turu="Kitap Ekleme",
        mesaj=mesaj,
        kitap_id=kitap_id,
        username=username,
        **kitap_bilgileri
    )
    
@app.route('/kitapsil/<username>', methods=['POST'])
@admin_required
def kitap_sil(username):
    #admin kitap silmek istediginde bu route a yonlendirilir 
    #formdan gelen silinecek kitap id si ile uygun controller fonksiyonuna yonlendirir
    kitap_id = request.form.get('kitap_id')
    mesaj, islem_turu = kitapController.kitap_sil_controller(kitap_id)
    #gelen degiskenlerle kitap_islem.html e yonlendirir
    return render_template(
        "kitap_islem.html",
        islem_turu=islem_turu,
        mesaj=mesaj,
        username=username
    ) 
    
@app.route("/kitapoduncver/<username>", methods=["POST"])
@admin_required
def kitap_odunc_ver(username):
    #admin kullaniciya kitap odunc vermeye calistiginda bu route a yonlendirir
    mesaj_dict = odunccontroller.odunc_ver_controller(request.form)
    send_pending_mails()

 #Formdan gelen veriler odunc_ver_controller fonksiyonuna iletilir
# Kullanıcıya ödünç verme işleminin sonucunu gösteren sayfaya yonlendirir
    return render_template(
        "odunc.html",
        mesaj=mesaj_dict.get("message"),
        kullanici_adi=request.form.get("verilcek_kullanici_adi"),
        kitap_adi=request.form.get("verilcek_kitap_adi"),
        odunc_id=mesaj_dict.get("odunc_id"),
        username=username
    )

@app.route('/kitapiadeal/<username>', methods=['POST'])
@admin_required
def kitap_iade_al(username):
    #admin kullanicidan kitap iade aldigind bu route a yonlendirilir
    #formdaki bilgiler ile ilgili controllerin ilgili fonksiyonuna yonlendirilir ve gelen degiskenlerle oduncçhtml e yonlendirilir
    mesaj = odunccontroller.odunc_iade_controller(request.form)
    send_pending_mails()

    return render_template("odunc.html", username=username, mesaj=mesaj)


@app.route('/oduncalmagecmisim/<username>')
@login_required
def oduncalmagecmisim(username):
    #kullanici odunc alma gecmisini gormek istediginde bu route calisir
    return odunccontroller.kullanici_odunc_gecmisi_controller(username)

@app.route('/tumkullanicioduncalmagecmisigoster/<username>')
@admin_required
def tumkullanicioduncalmagecmisigoster(username):
    #admin tum kullanicilarin odunc alma gecmisini gormek istediginde u route calisir
    return odunccontroller.tumkullanici_odunc_gecmisi_controller(username)


@app.route('/adminekle/<username>', methods=['POST'])
@admin_required
def admin_ekle_route(username):
    #admin yeni bir admin eklemek istediginde bu route calısır
    return adminkontroller.admin_ekle_controller(username)

@app.route('/adminsil/<username>', methods=['POST'])
@admin_required
def admin_sil_route(username):
    #admin bir admin silmek istediginde bu route a yonlendirir
    return adminkontroller.admin_sil_controller(username)

from flask import render_template, request, jsonify
@app.route('/cezatablosunugoster/<username>')
@admin_required
def ceza_tablosunu_goster(username):
    #admin kullanici tablosunu gormek isitediginde bu route a calısır
    try:
        #controllera yonlendirir
        cezalar = ceza_controller.tum_cezalari_getir()
        return render_template('tum_cezalar.html', 
                               username=username, 
                               cezalar=cezalar)
    except Exception as e:
        return f"Hata oluştu: {str(e)}", 500

@app.route('/cezalarimigoster/<username>')
@login_required
def cezalarimigoster(username):
    #kullanici spesifik olarak kendi cezalarını gomrmek istediginde bu route calisir
    try:
        cezalar = ceza_controller.kullanici_cezalarini_goster(username) 
        return render_template('cezalarim.html', username=username, cezalar=cezalar)
    except Exception as e:
        return f"Hata oluştu: {str(e)}", 500
    
@app.route('/cezaode', methods=['POST'])
@admin_required
def ceza_ode():
    #admin kullanicinin cezasini odemek istediginde bu route calisir
    try:
        data = request.get_json()
        kullanici_id = data.get("kullanici_id")
        odeme_yapilsin_mi = data.get("odeme_yapilsin_mi", False)
        if kullanici_id is None:
            return jsonify({"error": "Kullanici ID gerekli"}), 400
#her sey onaylanırsa ceza odendi yapmak icin controllera yonlnediri
        response = ceza_controller.ceza_odendi_yap(kullanici_id, odeme_yapilsin_mi)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/kullanici_sifre_degistir', methods=['POST'])
@login_required
def kullanici_sifre_degistir():
    user_id = session.get('user_id')
    #kullanicinin id sini sessionda alir 
    #bulunamadıysa hata verir
    if not user_id:
        flash("Oturum bulunamadı.", "error")
        return redirect(url_for('kullanici_sayfasi', username=session['username']))

    sonuc = kullanicikontroller.sifre_degistir_controller(user_id, request.form)
#kullaniccinin sifresini degistirmesi icin controllerda uyugun fonksiyona yonlendirr
    if sonuc['success']:
        flash(sonuc['message'], "success")
    else:
        flash(sonuc['message'], "error")

    return redirect(url_for('kullanici_sayfasi', username=session['username']))

@app.route('/admin_sifre_degistir', methods=['POST'])
@admin_required
def admin_sifre_degistir():
    #adminin sifresini degistirmesiicin bu route kullanilir
    #ilgili controllere yonlendirerek returnlar
    return adminkontroller.admin_sifre_degistir_controller()
    

@app.route('/kullanici_sifre_sifirla', methods=['POST'])
@admin_required
def admin_kullanici_sifre_sifirla_route():
    #admin tarafinda kullanicinin sifresini sifirlamak icin bu route kullanilir
    send_pending_mails()

    return kullanicikontroller.admin_kullanici_sifre_sifirla_controller()
    

if __name__ == "__main__":
    app.run(debug=True)
