from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app

# dependencies dosyasından gerekli nesneleri çekiyoruz
from depencies import (
    kullanicikontroller, 
    kullanici_islemleri, 
    personel_service
)

# Blueprint oluşturuluyor
genel_bp = Blueprint('genel', __name__)

@genel_bp.route('/')
def anasayfa():
    #istemcinin en cok istedigi json ise API gibi davranır ve html vb dondurmeden direkt Json formatında birseyler dondurur
    if request.accept_mimetypes.best == "application/json":
        return jsonify({
            "success": True, 
            "message": "Catlary Yönetim Sistemine hoşgeldiniz! "
        }), 200
        #json istegi gelmezse direkt anasayfa.html e yonlendirir
    return render_template("anasayfa.html")

@genel_bp.route('/kayitol', methods=['POST'])
def kayit_ol():
    #istemci cevabı json istiyorsa veya gonderilen veri json ise 
    is_api_request = request.accept_mimetypes.best == "application/json" or request.is_json
    #API istegi ise ve gelen veri json ise formdan degil gelen json un bodysinden okur
    if is_api_request and request.is_json:
    #eger gelen json bozuksa veya hatalı ise silent sayesinde patlamaz bos dict dondurur
        data = request.get_json(silent=True) or {}
    else:
        # API istegi degilse HTML Formundan veri alir
        data = request.form
    #gerekli parametreler ile ilgili kontrollere a yonlendirilir
    controller_sonuc = kullanicikontroller.kayit_ol_controller(data, kullanici_islemleri)
#gelen cevap tuple sa veya get data ozelligini iceriosa yani flask mesaji ise direkt bunu dondur
    if isinstance(controller_sonuc, tuple) or hasattr(controller_sonuc, 'get_data'):
      return controller_sonuc 
#degilse sonuc degiiskeninden basarili kisimi varsa orayi al yoksa basarisiz kabul et
    sonuc = controller_sonuc 
    basarili_mi = sonuc.get("basarili", False) 

    
    #  eger API istegi ise JSON yanıtı
    if is_api_request:
        status_code = 201 if basarili_mi else 400
        return jsonify(sonuc), status_code
    
    if basarili_mi:
        flash(sonuc.get("mesaj", "Kayıt başarılı."), "success")
    else:
        flash(sonuc.get("mesaj", "Kayıt başarısız."), "error")
        
    return redirect(url_for('genel.anasayfa'))

@genel_bp.route("/girisyap", methods=["POST"])
def girisyap():
    #sifre dogrulama ve token olusturmak icin seccret key
    SECRET2 = current_app.secret_key 
     # Eğer API üzerinden JSON formatında veri gelmişse
    if request.is_json:
        form = request.get_json()
        form['is_web'] = False
        # Eğer web formundan normal POST isteği gelmişse
    else:
        form = request.form.to_dict()
        form['is_web'] = True
    #giris kontrolu yapmak icin controllera iletir
    controller_sonuc = kullanicikontroller.giris_yap_controller(form, SECRET2)
    
    #controllerden donen sonuc tuplesa veya get_data iceriyorsa return eder
    if isinstance(controller_sonuc, tuple) or hasattr(controller_sonuc, 'get_data'):
        return controller_sonuc
    
    # WEB istegi ise
    if isinstance(controller_sonuc, dict):
        # Başarısız ise
        if controller_sonuc.get("basarili") is False:
            mesaj = controller_sonuc.get("mesaj", "Giriş başarısız.")
            flash(mesaj, "error") 
            return redirect(url_for('genel.anasayfa'))
        
        # Başarılı ise
        if controller_sonuc.get("redirect_url"):
            flash(controller_sonuc.get("mesaj", "Giriş başarılı."), "success")
            return redirect(controller_sonuc['redirect_url'])
        #giris basarili ise ve yonlendirme adresi varsa oraya yonlendiri
        return redirect(url_for('genel.anasayfa'))
    
    return "Beklenmeyen sunucu yanıtı.", 500

@genel_bp.route('/cikis', methods=['GET'])
def cikis_yap():
    #kullaniciyı anasayfaya yonlendircek response nesnesini hazirlar
    response =(redirect(url_for('genel.anasayfa')))
    #cikis yapan kullanıcının jwt cerezini silmek icin
    response.set_cookie(
        'jwt_token', #silincek cookie adi
        '',  #cookie degerini bos yapar
        expires=0,#suresini sifirlar
        httponly=True,#js ile erisilemesin
        secure=True, #https olmadan calismasin
        samesite='Lax' 
    )
    #eger json formatında cevap bekleniosa 
    if request.accept_mimetypes.best == "application/json":
        return jsonify({"success": True, "message": "Başarıyla çıkış yaptınız. JWT silindi."}), 200
#html istegi ise
    return response

@genel_bp.route('/sifremi_unuttum', methods=['POST'])
def sifremi_unuttum_route():
    # Kullanıcıdan gelen form verilerini email ve rol alıyoruz
    email = request.form.get('email')
    rol = request.form.get('rol')

    # Email veya rol yoksa işlem iptal edilir
    if not email or not rol:
        flash("Lütfen email ve hesap türünü seçiniz.", "error")
        return redirect(url_for('genel.anasayfa'))

    # İşlem varsayılan olarak başarısız kabul edilir
    sonuc = {"success": False, "message": "İşlem başarısız."}
    try:
        # Şifre sıfırlama talebi personel içinse
        if rol == 'personel':
            # Personel servisi zaten email’e göre şifre sıfırlar
            sonuc = personel_service.sifre_sifirla_by_email(email)

        # Şifre sıfırlama talebi normal kullanıcı içinse
        elif rol == 'kullanici':
            # İlk olarak email’e göre user çekilir
            user = kullanici_islemleri.get_kullanici_by_email(email)
            if user:
                # Ardından şifresi sıfırlanır
                sonuc = kullanici_islemleri.sifre_sifirla_by_user(user)
            else:
                # Kullanıcı bulunamazsa hata döner
                sonuc = {"success": False, "message": "Bu e-posta ile kayıtlı kullanıcı bulunamadı."}
        
        # Rol hatalı seçilmişse işlem reddedilir
        else:
            flash("Geçersiz rol seçimi.", "error")
            return redirect(url_for('genel.anasayfa'))

    # Beklenmeyen bir hata oluşursa yakalanır
    except Exception as e:
        print(f"HATA: {e}")
        sonuc = {"success": False, "message": "Sunucu tarafında bir hata oluştu."}

    # İşlem başarılıysa kullanıcıya olumlu mesaj gösterilir
    if sonuc.get("success"):
        flash(sonuc.get("message"), "success")
    else:
        # Hata varsa kırmızı uyarı gösterilir
        flash(sonuc.get("message"), "error")

    # İşlem tamamlanınca anasayfaya yönlendirilir
    return redirect(url_for('genel.anasayfa'))