from flask import flash, render_template, redirect, request, session, url_for, jsonify
from services.adminService import AdminService
from services.kullaniciService import KullaniciService
from werkzeug.security import generate_password_hash # Şifre hashleme için eklendi

db_config = {
    "host": "localhost",
    "user": "melisa",
    "password": "",
    "database": "kutuphane_db"
}

kullaniciService = KullaniciService(db_config) 
admin_service=AdminService(db_config)


def kayit_ol_controller(form, kullanici_service: KullaniciService):
#ilgili route un yonlendirmesi ile formdan gelen bilgileri alir 
    username = form.get('username')
    email = form.get('email')
    sifre = form.get('yeni_sifre') 
    sifre_tekrar = form.get('yeni_sifre_tekrar') 

    # tum alanlarin dolulugunu kontrol eder
    if not all([username, email, sifre, sifre_tekrar]):
        flash("Tüm alanlar boş bırakılamaz.", "error")
        return redirect(url_for('anasayfa'))
        
    #girilen sifrelerin eslesip eslesmedigini kontrol eder
    if sifre != sifre_tekrar:
        flash("Şifreler eşleşmiyor!", "error")
        return redirect(url_for('anasayfa'))
        
    #sonuc degiskeni ile ilgili service fonksiyonuna yonlendiriyoruz
    sonuc = kullanici_service.kayit_ol(username, email, sifre, sifre_tekrar)

    # İşlem sonucuna göre kullanıcıya uygun mesajı flash ile gösterir
    flash(
        sonuc['message'],  # Service'den dönen mesaj
        "success" if sonuc.get('success') else "error"
    )
    return redirect(url_for('anasayfa'))
    # Kullanıcıyı ana sayfaya yönlendir
    
    

def giris_yap_controller(form, user_session: session, kullanici_service: KullaniciService):
  #ilgili route dan gelen formu ve formdaki verileri alir 
    email = form.get('email')
    sifre = form.get('password') 
    islem = form.get('islem')  
    #alanlarin dolulugunu kontrol eder duruma gore  uyarı verir ve ve ana sayfaya yönlendirir
    if not all([email, sifre, islem]):
        flash("Lütfen tüm giriş alanlarını doldurun.", "error")
        return redirect(url_for('anasayfa'))
    user_data = None
    #formdan aldigi islem degerine gore uygun service e yonlendirir 
    # formdan alinan email parametre yapilarak uygun service fonksiyonuna gonderilerek emailden sifre alinir
  
    try:
        if islem == 'admin':
            user_data = admin_service.get_admin_by_email(email)
        else:
            user_data = kullanici_service.get_kullanici_by_email(email)
     # Service/Repository bağlantısında hata oluşursa ekrana hata mesajı yaz ve uyarı ver
    except Exception as e:
        print(f"Giriş sırasında Repository/Service hatası: {e}") 
        flash("Veritabanı bağlantısında bir sorun oluştu.", "error")
        return redirect(url_for('anasayfa'))

# veritabanından gelen kullanıcı bilgileri ile formdan girilen şifre eslesmez ise 
# kullanıcıya uygun mesaji gösterir ve anasayfaya yonlendirir
    if not kullanici_service.sifre_dogrula(user_data, sifre):
        flash("Email veya şifre hatalı.", "error")
        return redirect(url_for('anasayfa'))
    
#giris yapmaya calisan kullanicinin rolu kullanici degilse yani adminse veya aktif degilse uygun hatayı verir
    if islem != 'admin' and not user_data.get('aktiflik', 1):
        flash("Hesabınız askıya alınmıştır.", "error")
        return redirect(url_for('anasayfa'))

    #giris basarili ise session u buna uygun doldurur
    user_session['logged_in'] = True 
    user_session['user_id'] = user_data['id']
    user_session['username'] = user_data['username']
    user_session['role'] = islem 
    
    #eger formdan gelen veri admin ise uygun bilgilendirmeyi yapar ve 
    if islem == 'admin':
        flash("Admin olarak giriş başarılı!", "success")
        return redirect(url_for('admin_anasayfa', username=user_data['username']))
    else:
        flash("Giriş başarılı!", "success")
        return redirect(url_for('kullanici_sayfasi', username=user_data['username']))
    

    
def tum_kullanicilari_getir():
   #ilgili service fonksiyonuna yonlendirir
    return kullaniciService.tum_kullanicilari_getir()

def kullanici_ekle_controller(form):
   #formdan gelen bilgileri alir 
    username = form.get('username') or form.get('yeni_kullanici_adi')
    email = form.get('email') or form.get('yeni_kullanici_email')
    sifre = form.get('yeni_sifre') or form.get('yeni_kullanici_sifre')
    sifre_tekrar = form.get('yeni_sifre_tekrar') or form.get('yeni_kullanici_sifre_tekrar')
##alanlarin doluluk kontrolunu yapar
    if not username or not email or not sifre or not sifre_tekrar:
        return {"basarili": False, "mesaj": "Tüm alanlar gerekli!"}
#yeni sifre ile eski sifrenin eslesmesi kontrolunu yapar
    if sifre != sifre_tekrar:
        return {"basarili": False, "mesaj": "Şifreler eşleşmiyor!"}

    #sifreyi hashleyerek service e yonlendirir
    hashed_password = generate_password_hash(sifre)
    
    eklendi_mi = kullaniciService.kullanici_ekle(username, email, hashed_password)


    if eklendi_mi:
    
        return {"basarili": True, "mesaj": f"Kullanıcı '{username}' başarıyla eklendi."}
    else:
    
        return {"basarili": False, "mesaj": "Kullanıcı adı veya e-posta zaten kullanımda veya veritabanı hatası oluştu."}
    
    #kullanici adi ile kullaniciyi getirmek icin service e yonlendirir
def get_by_username(username):
    return kullaniciService.get_by_username(username)


def sifre_degistir_controller(user_id, form_data):
    #eski sifre ve yeni sifreyi formdan alarak service e yonlendirir 
    eski_sifre = form_data.get('eski_sifre')
    yeni_sifre = form_data.get('yeni_sifre')
    yeni_sifre_tekrar = form_data.get('yeni_sifre_tekrar')
    return kullaniciService.sifre_degistir(user_id, eski_sifre, yeni_sifre, yeni_sifre_tekrar)

def admin_kullanici_sifre_sifirla_controller():
    try:
        #formdan gelen kullanici id i alir ve int e donusturur
        kullanici_id = int(request.form.get('kullanici_id'))
    except (TypeError, ValueError):
        flash("Geçersiz kullanıcı ID.", "error")
        # Admin anasayfasına yönlendir, session kontrolü yapıldığı varsayılır
        return redirect(url_for('admin_anasayfa', username=session.get('username')))

#id den kullaniciyi bulur
    user = kullaniciService.get_kullanici_by_id(kullanici_id)
    if not user:
        flash("Kullanıcı bulunamadı!", "error")
        return redirect(url_for('admin_anasayfa', username=session.get('username')))
#sifre sifirla service ine yonlendirir
    sonuc = kullaniciService.sifre_sifirla_by_user(user)

    if sonuc.get("success"):
        flash(sonuc["message"], "success")
    else:
        flash(sonuc["message"], "error")

    return redirect(url_for('admin_anasayfa', username=session.get('username')))



def kullanici_durum_degistir_controller():
  
    if request.method != 'POST':
        return jsonify({"success": False, "message": "Geçersiz istek metodu."}), 405
    
    # JSON verisini alir
    data = request.get_json()
    

    if not data or 'kullanici_adi' not in data:
        return jsonify({"success": False, "message": "Eksik veri: 'kullanici_adi' gereklidir."}), 400
        
    kullanici_adi = data.get('kullanici_adi')
    
    # kullanıcıyı kullanıcı adına göre bul ve ID'sini alir
    user_data = kullaniciService.get_by_username(kullanici_adi) 
    
    if not user_data:
        # Eğer Kullanıcı bulunamazsa 404 döndür
        return jsonify({"success": False, "message": "Kullanıcı bulunamadı!"}), 404

    user_id = user_data['id']
    
    # Service'i çağırarak durumu değiştirme işlemini yap
    sonuc = kullaniciService.kullanici_aktiflik_durumu_degistir(user_id) 

    #  JSON yanıtı döndür
    if sonuc['success']:
        return jsonify(sonuc), 200
    else:
        # Service'ten dönen hatayı döndür
        return jsonify(sonuc), 400
