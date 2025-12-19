from flask import Blueprint, render_template, request, jsonify, flash, g

# depencies dosyasından gerekli kontrolcüleri ve decoratorları çekiyoruz
from depencies import (
    adminkontroller, 
    yazarlar_controller, 
    kategoriler_controller, 
    kitap_islemleri, 
    make_json_compatible,
)

from decorators import (admin_required, 
    admin_or_personel_required)
# Blueprint Tanımlaması: Adı 'admin'
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin_anasayfasi')
@admin_required
# Sadece admin rolundeki kullanıcıların erişmesini saglar
def admin_anasayfa():
    # Kullanici giris yaptıgında olusan sessiondan gelen bilgilerden ismi alır
    username = g.username 
    
    # Admin panelinde kullanılacak verileri veritabanından çeker
    yazarlar = yazarlar_controller.tum_yazarlari_getir_controller()
    kategoriler = kategoriler_controller.tum_kategorileri_getir_controller()
    kitaplar = kitap_islemleri.tum_kitaplari_getir()
    
    # Eğer kullanıcı API üzerinden JSON formatında istiyorsa
    if request.accept_mimetypes.best == "application/json":
        return jsonify({"username": username, "message": "Admin sayfası erişimi başarılı"}), 200
    
    # Eger json formatında istek gelmediyse html arayuzu doner
    return render_template("admin.html", kitaplar=kitaplar, username=username, yazarlar=yazarlar, kategoriler=kategoriler)


@admin_bp.route('/adminekle', methods=['POST'])
@admin_required   # Sadece admin giriş yapmış kullanıcılar erişebilir
def admin_ekle_route():
    current_admin_username = g.username   # Şu anda giriş yapmış adminin kullanıcı adı
    
    # İstek türü JSON ise JSON'dan oku, form ise formdan okur
    data = request.get_json(silent=True) or request.form
    
    # Kullanıcıdan gelen admin bilgileri
    username = data.get("yeni_admin_adi")
    email = data.get("yeni_admin_email")
    sifre = data.get("yeni_admin_sifre")
    sifre_tekrar = data.get("yeni_admin_sifre_tekrar")

    try:
        # Admin ekleme işlemi controller katmanına iletir
        sonuc = adminkontroller.admin_ekle_controller(username, email, sifre, sifre_tekrar)

        # İşlem başarılı mı kontrol et
        basarili_mi = sonuc.get("success", False)

        # Başarı durumuna göre mesaj göster
        flash(
            sonuc.get("message", "İşlem tamamlandı."), 
            "success" if basarili_mi else "danger"
        )

        # Eğer istek JSON formatında gelmişse cevap JSON olarak döndürülür
        if request.accept_mimetypes.best == "application/json" or request.is_json:
            status_code = 201 if basarili_mi else 400  # Başarılı → 201, başarısız → 400
            return jsonify(sonuc), status_code

        # Normal form isteği ise admin paneline geri dön
        return render_template("admin.html", username=current_admin_username)

    except Exception as e:
        # Backend tarafında herhangi bir hata olursa buraya düşer
        mesaj = f"Hata oluştu: {str(e)}"
        print(f"HATA /adminekle: {e}") 

        flash(mesaj, "danger")

        # JSON isteği ise JSON hata mesajı dön
        if request.accept_mimetypes.best == "application/json" or request.is_json:
            return jsonify({"success": False, "message": mesaj}), 500

        # Değilse admin paneline hata mesajıyla dön
        return render_template("admin.html", username=current_admin_username)


@admin_bp.route('/adminsil', methods=['POST'])
@admin_required   # Sadece admin kullanıcılar erişebilir
def admin_sil_route():
    current_admin_username = g.username  # Şu anda giriş yapan adminin kullanıcı adı

    try:
        # Formdan gelen veri alınır
        data = request.form
        
        # Silinecek admin bilgileri formdan çekilir
        username = data.get("silinecek_admin_adi")
        username_tekrar = data.get("silinecek_admin_adi_tekrar")

        # Kullanıcı adı ve doğrulama alanı boşsa hata döndürür
        if not all([username, username_tekrar]):
            mesaj = "Silinecek admin kullanıcı adı ve tekrarı gereklidir."
            flash(mesaj, "danger")

            # Admin listesiyle admin sayfasına geri dön
            return render_template(
                "admin.html",
                username=current_admin_username,
                adminler=adminkontroller.tum_adminleri_getir()
            )

        # Controller üzerinden admin silme işlemi çağırılır
        sonuc = adminkontroller.admin_sil_controller(username, username_tekrar)

        # İşlem başarılı mı kontrol edilir
        basarili_mi = sonuc.get("success", False)

        # Sonuca göre kullanıcıya mesaj gösterilir
        flash(
            sonuc.get("message", "İşlem tamamlandı."),
            "success" if basarili_mi else "danger"
        )

        # Admin sayfasına güncel admin listesiyle dönülür
        return render_template(
            "admin.html",
            username=current_admin_username,
            adminler=adminkontroller.tum_adminleri_getir()
        )

    except Exception as e:
        # Backend tarafında beklenmeyen bir hata olursa buraya düşer
        mesaj = f"Hata oluştu: {str(e)}"
        flash(mesaj, "danger")

        # Admin listesiyle admin sayfasına dön
        return render_template(
            "admin.html",
            username=current_admin_username,
            adminler=adminkontroller.tum_adminleri_getir()
        )

@admin_bp.route('/adminler') 
@admin_or_personel_required   # Hem admin hem personel erişebilir
def adminler_goster():
    username = g.username   # Şu anda sisteme giriş yapan kullanıcının adı alınır
    
    # Tüm adminler controller katmanından çekilir
    adminler = adminkontroller.tum_adminleri_getir()  
    
    print(f"DEBUG: Adminler listesi çekildi: {adminler}")  # Terminal çıktısı
    
    # İstek JSON formatında talep edildiyse JSON döndürülür
    if request.accept_mimetypes.best == "application/json":
        # JSON yapısına dönüştürülür
        adminler_json = make_json_compatible(adminler)

        # JSON cevap döndürülür
        return jsonify({
            "username": username, 
            "adminler": adminler_json 
        }), 200 
    
    # JSON değil, normal bir web sayfası isteği geldiyse HTML şablon döndürülür
    return render_template(
        "adminler.html", 
        adminler=adminler, 
        username=username 
    )

@admin_bp.route('/admin_sifre_degistir', methods=['POST'])
@admin_required
def admin_sifre_degistir():
    # Giriş yapan adminin kullanıcı adını session içindeki g'den alıyoruz
    username = g.username

    # Hem JSON hem de HTML form POST isteği için veri alma işlemi
    data = request.get_json(silent=True) or request.form

    # Controller üzerinden şifre değiştirme işlemi yapılır
    sonuc = adminkontroller.admin_sifre_degistir_controller(data)

    # İşlem başarılı mı kontrol ediliyor
    basarili_mi = sonuc.get('success', False)

    # Geri dönecek mesaj belirleniyor
    mesaj = sonuc.get('message', "İşlem tamamlandı.")

    status_code = 200 if basarili_mi else 400

    # Ekranda kullanıcıya mesaj göstermek için flash kullanılıyor
    flash(mesaj, "success" if basarili_mi else "danger")

    # Eğer istek JSON bekliyorsa JSON formatında cevap döndür
    if request.accept_mimetypes.best == "application/json":
        return jsonify(sonuc), status_code

    # HTML sayfasına dönüyoruz
    return render_template("admin.html", username=username)