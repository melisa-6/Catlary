from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, g
import traceback

# dependencies dosyasından gerekli nesneleri çekiyoruz
from depencies import (
    kategoriler_controller,
    yazarlar_controller,
    personel_controller_instance,
    make_json_compatible
)

# decorators dosyasından yetki kontrollerini çekiyoruz
from decorators import admin_required, admin_or_personel_required

# Blueprint oluşturuluyor
personel_bp = Blueprint('personel', __name__)

@personel_bp.route('/personel_sayfasi') 
@admin_or_personel_required 
#sadece admin veya personel rolundeki kullanıcıların erişmesini saglar
def personel_sayfasi(): 
    # Sayfada gösterilecek veriler veritabanından çekilir
    user_id = g.user_id 
    username = g.username
    role = g.role
    #kategori ve yazarları dbden cekerek html sayfasına gonderiri
    kategoriler=kategoriler_controller.tum_kategorileri_getir_controller()
    yazarlar=yazarlar_controller.tum_yazarlari_getir_controller()
    #eger API formatında istek geldi mi kontrolu
    is_api_request = request.accept_mimetypes.best == "application/json"
    #eger json istegi ise json formatında cikti verir
    if is_api_request:
        return jsonify({
            "success": True,
            "message": "Personel/Admin sayfası erişimi başarılı.",
            "kullanici_adi": username,
            "kullanici_rolu": role,
            "user_id": user_id
        }), 200
      #html istegi ise  
    return render_template('personel.html', 
                           kullanici_adi=username,
                           kullanici_rolu=role,
                           user_id=user_id,
                           kategoriler=kategoriler,
                           yazarlar=yazarlar)


@personel_bp.route("/personel_ekle", methods=["POST"])
@admin_required  # yalnızca admin yetkisine sahip kullanıcılar yapabilsin
def personel_ekle():
    
    # İstek API formatında mı kontrol edilir JSON ise True döner.
    is_api_request = request.is_json or request.accept_mimetypes.best == "application/json"
    
    # JSON isteği geldiyse JSON'dan veri al, değilse formdan alır
    if is_api_request:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form
        
    # Formdan gelen değerler alınır
    ad_soyad = data.get("ad_soyad")
    email = data.get("email")
    sifre = data.get("sifre")
    sifre_tekrar = data.get("sifre_tekrar")

    # Boş alan var mı kontrol edilir
    if not all([ad_soyad, email, sifre, sifre_tekrar]):
        mesaj = "Tüm alanları doldurmalısın!"
        
        # API isteği ise JSON olarak hata döndür
        if is_api_request:
            return jsonify({"success": False, "message": mesaj}), 400
            
        # HTML istek ise flash mesaj göster ve admin ana sayfasına dön
        flash(mesaj, "error")
        return redirect(url_for("admin.admin_anasayfa"))

    try:
        # Controller üzerinden personel oluşturma işlemi yapılır
        sonuc = personel_controller_instance.personel_ekle(
             ad_soyad, email, sifre, sifre_tekrar
        )
        
        basarili_mi = sonuc.get("success", False)
        mesaj = sonuc.get("message", "İşlem tamamlandı.")

        # API isteği ise JSON formatında dönüş yapılır
        if is_api_request:
            status_code = 201 if basarili_mi else 400
            return jsonify(sonuc), status_code
    
        # HTML istek için işlem başarılı mı kontrol edilir
        if basarili_mi:
            flash(mesaj, "success")
        else:
            flash(mesaj, "error")

        # Admin ana sayfasına yönlendirilir
        return redirect(url_for("admin.admin_anasayfa"))

    # İşlem sırasında hata oluşursa yakalanır
    except Exception as e:
        
        mesaj = f"Beklenmeyen bir sistem hatası oluştu: {e}"
        print("PERSONEL EKLE HATA:", e)
        traceback.print_exc() 
        
        # API isteği ise sunucu hatası JSON olarak döndürülür
        if is_api_request:
            return jsonify({"success": False, "message": mesaj}), 500
            
        # HTML isteğinde ise hata mesajı gösterilip ana sayfaya dönülür
        flash(mesaj, "error")
        return redirect(url_for("admin.admin_anasayfa"))

    
@personel_bp.route("/personel_sifre_sifirla", methods=["POST"])
@admin_required
def admin_personel_sifre_sifirla_route():
    # Gelen isteğin JSON formatında olup olmadığını kontrol eder
    # Eğer Accept header veya Content-Type JSON ise API isteği kabul edilir
    is_api_request = request.is_json or request.accept_mimetypes.best == "application/json"
    
    # JSON isteklerde veriyi request.get_json() ile alır
    # Form isteğinde ise request.form kullanır
    form_data = request.get_json(silent=True) if is_api_request else request.form
    
    # Eğer hiçbir veri gelmemişse hata döner
    if not form_data:
        mesaj = "Form verisi eksik."
        
        # API isteğiyse JSON olarak hata döndürür.
        if is_api_request:
            return jsonify({"success": False, "message": mesaj}), 400
        
        # Normal form isteğiyse kullanıcıya mesaj gösterip yönlendirir.
        flash(mesaj, "danger")
        return redirect(url_for('admin.admin_anasayfa'))

    # Controller'a veriyi gönderir ve işlem sonucunu alır
    sonuc = personel_controller_instance.admin_personel_sifre_sifirla_controller(form_data)

    # Controller'dan gelen veriden başarı durumu ve mesajı çekilir
    basarili_mi = sonuc.get("success", False)
    mesaj = sonuc.get("message", "İşlem tamamlandı.")

    # Eğer API isteği yapıldıysa
    if is_api_request:
        # İşlem başarılı ise JSON döner ve personel_id gösterilir
        if basarili_mi:
            return jsonify({
                "success": True,
                "message": mesaj,
                "personel_id": sonuc.get("personel_id")  # controller'dan gelen id
            }), 200
        
        # Başarısız ise hata mesajı döner.
        return jsonify({"success": False, "message": mesaj}), 400

    # API değilse flash mesaj gösterip yönlendirir.
    flash(mesaj, "success" if basarili_mi else "danger")
    return redirect(url_for('admin.admin_anasayfa'))


@personel_bp.route("/personel_liste", methods=["GET"])
@admin_required  # Bu sayfaya erişim sadece yöneticiler icin
def personel_listesi_goster():
    #  İstemci JSON mu bekliyor yoksa HTML mi
    is_api_request = request.accept_mimetypes.best == "application/json"
    
    try:
        # Controller katmanından tüm personel verisini çek
        personel_listesi = personel_controller_instance.tum_personelleri_getir()
        
        # API istegi ise
        if is_api_request:
            # Veriyi JSON formatına uygun hale getir 
            personel_json = make_json_compatible(personel_listesi)
            
            # Başarılı (200 OK) JSON yanıtı döndür
            return jsonify({
                "success": True,
                "personeller": personel_json
            }), 200
        
        # Veriyi HTML şablonuna gönder ve sayfayı oluştur
        return render_template("personel_listesi.html", personeller=personel_listesi)
        
    except Exception as e:
        hata_mesaji = "Personel listesi yüklenirken beklenmeyen bir hata oluştu."
        
        print(f"Personel Listesi Getirme Hatası: {e}")
        traceback.print_exc()
        
        # Eğer istek API ise, hatayı JSON formatında 500 koduyla döndür
        if is_api_request:
            return jsonify({
                "success": False, 
                "message": hata_mesaji
            }), 500
            
        # Eğer web isteği ise, kullanıcıya hata mesajı göster ve anasayfaya yönlendir
        flash(hata_mesaji, "error")
        return redirect(url_for('admin.admin_anasayfa'))

@personel_bp.route("/personel/aktiflik_degistir", methods=["POST"])
@admin_required
def personel_aktiflik_degistir_route():
    # İsteğin JSON  mı yoksa Web Formu mu olduğunu kontrol eder
    is_api_request = request.is_json or request.accept_mimetypes.best == "application/json"
    
    
    # Eğer API isteğiyse JSON body'sini değilse Form verisini al
    if is_api_request:
        # silent=True: JSON bozuksa hata fırlatmak yerine None döner, güvenlidir
        data = request.get_json(silent=True) or {}
    else:
        data = request.form

    try:
        # Verileri sözlükten çeker
        personel_id_str = data.get("personel_id")
        yeni_durum_str = data.get("yeni_durum")
        
        if not personel_id_str or yeni_durum_str is None:
            mesaj = "Personel ID veya yeni durum bilgisi eksik."
            status_code = 400
            
            # API ise JSON dön
            if is_api_request:
                return jsonify({"success": False, "message": mesaj}), status_code
            
            # Web ise hata mesajı göster ve listeye dön
            flash(mesaj, "error")
            return redirect(url_for('personel.personel_listesi_goster'))

        # ID'yi sayıya çevir (Güvenlik ve tutarlılık için)
        personel_id = int(personel_id_str)
        
        yeni_durum = yeni_durum_str in ['1', 1, 'true', True] 
        
        # Controller üzerinden işlemi gerçekleştir
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
            
        # Web kullanıcısı için bildirim oluştur
        flash(mesaj, "success" if basarili_mi else "error")

    except ValueError:
        # ID integer'a çevrilemezse buraya düşer
        mesaj = "Geçersiz personel ID formatı."
        if is_api_request:
            return jsonify({"success": False, "message": mesaj}), 400
        flash(mesaj, "error")

    except Exception as e:
        # Beklenmedik sunucu hataları
        mesaj = "Aktiflik değiştirme işlemi sırasında beklenmeyen bir hata oluştu."
        print(f"Aktiflik Değiştirme Hatası: {e}")
        
        if is_api_request:
            return jsonify({"success": False, "message": mesaj}), 500
        flash(mesaj, "error")

    # Web istekleri işlemin sonunda her zaman listeye yönlendirilir
    return redirect(url_for('personel.personel_listesi_goster'))

@personel_bp.route("/personel_sifre_degistir", methods=["POST"])  
@admin_or_personel_required  # Bu fonksiyon çalışmadan önce kullanıcının Admin veya Personel olup olmadığı kontrol eder
def personel_sifre_degistir_route():
    #  o an giriş yapmış kullanıcının ID'sini alıyoruz.
    personel_id = g.user_id
    
    #  Önce JSON var mı diye bakar (API) yoksa form verisine (HTML Form) bakar
    data = request.get_json(silent=True) or request.form
    
    try:
        # Eğer personel ID'si alınamamışsa  işlem durdurulur
        if not personel_id:
            flash("Yetkiniz yok. Lütfen tekrar giriş yapın.", "danger") # Hata mesajı oluştur.
            return redirect(url_for("genel.anasayfa")) # Kullanıcıyı anasayfaya gönder.
            
        # controller çağırır
        sonuc = personel_controller_instance.personel_sifre_degistir_controller(personel_id, data)
        
        # Controller'dan dönen sözlükten başarı durumu ve mesajı alıyoruz
        basarili_mi = sonuc.get("success", False)
        # Controller'dan dönen mesajı alıyoruz
        mesaj = sonuc.get("message", "İşlem tamamlandı.")
        
        # Eğer gelen istek JSON formatındaysa 
        if request.is_json:
            # JSON yanıtı döndür Başarılıysa 200, değilse 400 HTTP kodu ver
            return jsonify(sonuc), 200 if basarili_mi else 400

        # Eğer istek Web tarayıcısından geliyorsa
        flash(mesaj, "success" if basarili_mi else "danger") # Kullanıcıya bildirim mesajı göster
        return redirect(url_for("personel.personel_sayfasi")) # Personel sayfasına yönlendir

    except Exception as e:
        # Beklenmeyen bir hata oluşursa konsola yazdır
        print(f"PERSONEL ŞİFRE DEĞİŞTİR HATA: {e}")
        
        # API isteği ise JSON hata mesajı dön.
        if request.is_json:
            return jsonify({"success": False, "message": "Beklenmeyen sunucu hatası."}), 500
            
        # Web isteği ise Flash mesajı verip sayfayı yenile.
        flash("Beklenmeyen bir hata oluştu.", "danger")
        return redirect(url_for("personel.personel_sayfasi"))