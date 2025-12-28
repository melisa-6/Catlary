from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, g

# dependencies dosyasından gerekli fonksiyonları ve sınıfları çekiyoruz
from depencies import (
    kullanici_islemleri,
    kitap_islemleri,
    odunc_controller_instance,
    make_json_compatible
)
from send_mail import send_pending_mails
from services.mailServices import mailService
# decorators dosyasından yetki kontrollerini çekiyoruz
from decorators import admin_or_personel_required, login_required

# Blueprint oluşturuluyor
odunc_bp = Blueprint('odunc', __name__)

@odunc_bp.route("/kitapoduncver", methods=["GET", "POST"])
@admin_or_personel_required
def kitap_odunc_ver():

    kullanicilar = kullanici_islemleri.tum_kullanicilari_getir()
    kitaplar = kitap_islemleri.tum_kitaplari_getir()
    print(kitaplar)

    if request.method == "POST":
        data = request.get_json(silent=True) or request.form

        kullanici_mail = data.get("kullanici_mail")
        kitap_id = data.get("kitap_id")

        # Controller artık tarihlerle kendisi ilgileniyor
        sonuc = odunc_controller_instance.odunc_ver_controller({
            "kullanici_mail": kullanici_mail,
            "kitap_id": kitap_id
        })

        # JSON veya HTML cevabı
        if request.accept_mimetypes.best == "application/json":
            return jsonify(sonuc), (200 if sonuc.get("success") else 400)

        flash(sonuc.get("message"), "success" if sonuc.get("success") else "error")
        return redirect(url_for("odunc.kitap_odunc_ver"))

    # GET isteği için sayfa render
    role = getattr(g, "role", None)
    if role == "admin":
        geri_donus_url = url_for("admin.admin_anasayfa")
        geri_donus_text = "← Admin Paneline Dön"
    else:
        geri_donus_url = url_for("personel.personel_sayfasi")
        geri_donus_text = "← Personel Paneline Dön"

    return render_template(
        "oduncver.html",
        kullanicilar=kullanicilar,
        kitaplar=kitaplar,
        geri_donus_url=geri_donus_url,
        geri_donus_text=geri_donus_text
    )

@odunc_bp.route('/kitapiadeal', methods=['POST'])
@admin_or_personel_required        #yalnızca admin ve personelin bu route’a erişmesine izin verir
def kitap_iade_al():
    username = g.username          #  Sistemde oturum açmış kullanıcı adını alır 
    role = g.role                  # Kullanıcının rolünü alır
    form_data = request.form       # Formdan gelen POST verilerini alır
    
    #Controller katmanına form datasını göndererek iade işlemini başlatır
    mesaj = odunc_controller_instance.odunc_iade_controller(form_data)
    

    # Controller'dan gelen mesaj içeriğinde "başarıyla" kelimesi geçiyorsa işlem başarılı kabul edilir
    basarili_mi = "başarıyla" in mesaj.lower()

    kategori = "success" if basarili_mi else "danger"
    flash(mesaj, kategori)

    # Eğer istek JSON formatında geldiyse JSON olarak cevap dönülür
    if request.accept_mimetypes.best == "application/json":
        return jsonify({"mesaj": mesaj, "success": basarili_mi}), 200 if basarili_mi else 400

    # İşlemden sonra kullanıcının rolüne göre yönlendirileceği sayfa
    if role == "admin":
        return redirect(url_for('admin.admin_anasayfa')) 
    elif role == "personel":
        return redirect(url_for('personel.personel_sayfasi'))
    else:
        return redirect(url_for('kullanici.kullanici_sayfasi'))


@odunc_bp.route('/oduncalmagecmisim/<username>')
@login_required
def oduncalmagecmisim(username):

    #    session içindeki giriş yapan kullanıcı adını kullanıyoruz
    #    Böylece başka kullanıcıların geçmişini URL ile görüntülemek engellemiş oluruz
    username = g.username
    
    # Controller çağrılır ve kullanıcının ödünç alma geçmişi veritabanından getirilir
    gecmis = odunc_controller_instance.kullanici_odunc_gecmisi_controller(username)

    # JSON dönebilmesi için liste/dict/json olmayan veri tipleri dönüştürülür.
    gecmis_json = make_json_compatible(gecmis)

    # Eğer istek JSON tipinde ise sayfa render edilmez, JSON döndürülür.
    if request.accept_mimetypes.best == "application/json":
        return jsonify({
            "username": username,
            "odunc_gecmisi": gecmis_json
        }), 200

    # HTML isteklerde template render edilir ve verilere aktarılır.
    return render_template(
        "odunc_gecmisim.html",
        username=username, 
        odunc_gecmisi=gecmis
    )


@odunc_bp.route('/tumkullanicioduncalmagecmisigoster', methods=['GET'])
@admin_or_personel_required 
def tum_odunc_gecmisi():
    # Giriş yapan kullanıcının rolünü alır (admin / personel)
    role = g.role
    
    # Giriş yapan kullanıcının adını alır
    username = g.username
    
    # Controller katmanına gidip Tüm kullanıcıların ödünç geçmişini çeker
    tum_gecmis = odunc_controller_instance.tum_kullanicilarin_odunc_gecmisi_controller(
        role, 
        username
    )
    print(tum_gecmis)
    is_api_request = request.accept_mimetypes.best == "application/json"
    
    if is_api_request:
        gecmis_json = make_json_compatible(tum_gecmis)
        
        return jsonify({
            "success": True,
            "role": role,
            "username": username,
            "tum_odunc_gecmisi": gecmis_json
        }), 200

    return render_template(
        "tum_odunc_gecmisi.html",        # → Gösterilecek HTML dosyası
        tum_odunc_gecmisi=tum_gecmis,    # → Template’e veri gönderme
        role=g.role,                     # → Template’te rol bilgisi kullanılır
        username=g.username              # → Template’te username göstermek için
    )