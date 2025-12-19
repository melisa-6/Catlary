from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, g, session

# dependencies dosyasından gerekli controllerları ve yardımcı fonksiyonları çekiyoruz
from depencies import (
    kitap_controller, 
    yazarlar_controller, 
    kategoriler_controller, 
    make_json_compatible
)


from decorators import (admin_required,login_required,
    admin_or_personel_required)
# Blueprint oluşturuluyor
kitap_bp = Blueprint('kitap', __name__)

@kitap_bp.route('/kitapsil', methods=['POST']) 
@admin_or_personel_required  # Bu route'a sadece admin ve personel erişebilmesini saglar
def kitap_sil():
    # Oturumdaki kullanıcı adını alır
    username = g.username
    
    # API isteği mi veya JSON gönderiyor mu kontrolü
    is_api_request = request.is_json or request.accept_mimetypes.best == "application/json"
    
    # JSON geldiyse JSON'dan alır, gelmediyse formdan alır
    if is_api_request:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form
        
    # Silinecek kitap ID'sini alır
    kitap_id = data.get('kitap_id')
    
    # Eksik Veri Kontrolü
    if not kitap_id:
        mesaj = "Hata: Silinecek kitap ID'si sağlanmadı."
        basarili_mi = False
        
        # Eksik veri varsa ve bu bir API isteğiyse JSON hata döner
        if is_api_request:
             return jsonify({"success": False, "mesaj": mesaj}), 400
    else:
        # Controller üzerinden kitap silme işlemi yapılır
        mesaj, _, basarili_mi = kitap_controller.kitap_sil_controller(kitap_id)
        
    # JSON İstek Karşılığı
    if is_api_request:
        # Silme başarılı olduysa 200, başarısızsa 400 döner
        status_code = 200 if basarili_mi else 400
        return jsonify({"success": basarili_mi, "mesaj": mesaj}), status_code
    # HTML İstek Karşılığı
    flash(mesaj, "success" if basarili_mi else "danger")
    
    # Sayfayı gönderilen yere geri yönlendirir, yoksa kitap listelemeye dön
    # Blueprint içinde olduğumuz için 'kitap.kitaplari_goruntule' kullanıyoruz
    return redirect(request.referrer or url_for('kitap.kitaplari_goruntule'))


@kitap_bp.route("/kitapekle", methods=["GET", "POST"])
def kitap_ekle_route():

    # Eğer sayfaya POST isteği geliyorsa — yani kitap ekleme işlemi yapılacaksa
    if request.method == "POST":
        try:
            # API tarafında JSON ile veri gelmişse bu blok çalışır
            if request.is_json:
                data = request.get_json()
                kitap_adi = data.get("kitap_adi")
                yazar_id = data.get("yazar_id")
                kategori_id = data.get("kategori_id")
                sayfa_sayisi = data.get("kitap_sayfa_sayisi")
                stok_miktari = data.get("stok_miktari")
                raf_no = data.get("raf_no")
                baski_yili = data.get("baski_yili")
                yayinevi = data.get("kitap_yayini")

            # Formdan gelen HTML istekleri buradan okunur
            else:
                kitap_adi = request.form.get("kitap_adi")
                yazar_id = request.form.get("yazar_id")
                kategori_id = request.form.get("kategori_id")
                sayfa_sayisi = request.form.get("kitap_sayfa_sayisi")
                stok_miktari = request.form.get("stok_miktari")
                raf_no = request.form.get("raf_no")
                baski_yili = request.form.get("baski_yili")
                yayinevi = request.form.get("kitap_yayini")

            # Controller katmanına aktarır
            kitap_controller.kitap_ekle_controller(
                kitap_adi, yazar_id, kategori_id, sayfa_sayisi,
                stok_miktari, raf_no, baski_yili, yayinevi
            )

            # Eğer istek JSON ise API'ye özel başarı mesajı dön
            if request.is_json:
                return jsonify({"success": True, "message": "Kitap başarıyla eklendi!"}), 201
            
            # HTML ise kullanıcıya bildirim göster
            else:
                flash("Kitap başarıyla eklendi!", "success")

                # Kullanıcı rolünü session’dan al
                rol = session.get('role') 

                # Eğer kullanıcı personelse personel anasayfaya yönlendir
                if rol == 'personel':
                    # NOT: Personel blueprinti oluşturulunca 'personel.anasayfa' olarak güncellenmeli
                    # Şimdilik varsayılan isimlendirmeyi kullanıyorum.
                    return redirect(url_for('personel.personel_anasayfa_route')) 
                
                # Değilse admin sayfasına yönlendir
                else:
                    return redirect(url_for('admin.admin_anasayfa'))

        # Hata meydana gelirse
        except Exception as e:
            # API isteği ise:
            if request.is_json:
                return jsonify({"success": False, "message": str(e)}), 400
            
            # HTML isteği ise:
            else:
                flash(f"Hata: {str(e)}", "danger")
                return redirect(url_for("kitap.kitap_ekle_route"))

    # GET isteği ise formu göstermek için yazar ve kategori bilgilerini al
    yazarlar = yazarlar_controller.tum_yazarlari_getir_controller()
    kategoriler = kategoriler_controller.tum_kategorileri_getir_controller()

    # Eğer API JSON talebi varsa — veri olarak liste döndür
    if request.is_json or request.args.get('type') == 'json':
        return jsonify({
            "yazarlar": yazarlar,
            "kategoriler": kategoriler
        })

    # Kullanıcı rolünü ve adını sessiondan al
    rol = session.get('role')
    kullanici_adi = session.get('username') 

    # Eğer personel ise personel şablonunu döndürür
    if rol == 'personel':
        return render_template("personel.html", yazarlar=yazarlar, kategoriler=kategoriler, kullanici_adi=kullanici_adi)

    # Değilse admin sayfasını döndürür
    else:
        return render_template("admin.html", yazarlar=yazarlar, kategoriler=kategoriler, username=kullanici_adi)
 
 
@kitap_bp.route('/kitaplari_goruntule', methods=['GET'])
@login_required
def kitaplari_goruntule():
    # Oturum açmış kullanıcının adını al
    username = g.username

    # Kullanıcı rolünü al
    role = g.role 

    # URL üzerinden kitap arama parametresini al 
    aranan_kitap = request.args.get('aranacak_kitap', '')

    # Kitapları getir + admin/personel bilgisi controllerdan döner
    kitaplar, admin_mi = kitap_controller.kitaplari_goruntule_controller(
        username, role, aranan_kitap
    )

    # Eğer kullanıcı admin veya personelse admin yetkisi aç
    if role in ["admin", "personel"]:
        admin_mi = True
    else:
        admin_mi = False

    # Eğer istek JSON ise JSON formatında cevap ver
    if request.accept_mimetypes.best == "application/json":
        return jsonify({
            "kitaplar": make_json_compatible(kitaplar),  # JSON uyumlu hale getirir
            "username": username,                       # kullanıcı adı gönderir
            "aranan_kitap": aranan_kitap,               # kullanıcı ne aradı gösterir
            "admin_mi": admin_mi                        # admin mi personel mi
        }), 200

    # HTML istemi ise template döndürr ve uygun htlm sayfasına yonlendirir
    return render_template(
        "kitaplar.html",
        kitaplar=kitaplar,
        username=username,
        aranan_kitap=aranan_kitap,
        admin_mi=admin_mi,
        role=role
    )