from flask import Blueprint, render_template, request, jsonify, g, redirect, url_for
from sqlite3 import DatabaseError, IntegrityError, ProgrammingError

# dependencies klasöründen gerekli fonksiyonları ve sınıfları çekiyoruz
from depencies import ceza_controller_instance, make_json_compatible

from decorators import (admin_required,login_required,
    admin_or_personel_required)
# Blueprint oluşturuluyor
ceza_bp = Blueprint('ceza', __name__)

@ceza_bp.route('/cezatablosunugoster')
@admin_or_personel_required
def ceza_tablosunu_goster():
    username = g.username
    
    try:
        # Veriler controller'dan çekilir
        cezalar = ceza_controller_instance.tum_cezalari_getir()

        # JSON formatı lazım olursa dönüştürülür
        cezalar_json = make_json_compatible(cezalar)

        # JSON response talebi varsa
        if request.accept_mimetypes.best == "application/json":
            return jsonify({
                "username": username, 
                "cezalar": cezalar_json
            }), 200

        # HTML response talebi varsa
        return render_template(
            'tum_cezalar.html',
            username=username,
            role=g.get('role'),
            cezalar=cezalar
        )

    except Exception as e:
        mesaj = f"İşlem Başarısız: Sunucu tarafında beklenmedik bir hata oluştu: {str(e)}"
        print(f"HATA /cezatablosunugoster: {e}")

        if request.accept_mimetypes.best == "application/json":
            return jsonify({"success": False, "message": mesaj}), 500

        return render_template(
            'tum_cezalar.html',
            username=username,
            role=g.get('role'),
            cezalar=[]
        )

@ceza_bp.route('/cezalarimigoster/<username>')   # URL içinde username parametresi alır
@login_required                                # Giriş yapılmış kullanıcı olması şart
def cezalarimigoster(username):
    username = g.username    # Güvenlik için route parametresini değil session bilgisini kullanırız
    
    try:
        # Kullanıcıya ait cezaları servis katmanından çeker
        cezalar = ceza_controller_instance.kullanici_cezalarini_goster(username)

        # JSON formatına uygun hale getirir 
        cezalar_json = make_json_compatible(cezalar)

        # Eğer istek JSON kabul ediyorsa JSON döndürür
        if request.accept_mimetypes.best == "application/json":
            return jsonify({
                "username": username, 
                "cezalar": cezalar_json
            }), 200
        
        # HTML döndürür cezalarim.html template’ine veri gönderir
        return render_template(
            'cezalarim.html', 
            username=username, 
            cezalar=cezalar
        )

    except Exception as e:
        # Hata oluşursa kullanıcıya mesaj verilir
        mesaj = f"İşlem Başarısız: Sunucu tarafında beklenmedik bir hata oluştu: {str(e)}"
        print(f"HATA /cezalarimigoster: {e}")
        
        # JSON isteyen istemciye JSON hatası döndürülür
        if request.accept_mimetypes.best == "application/json":
            return jsonify({
                "success": False, 
                "message": mesaj
            }), 500
        
        # HTML istemciyse kullanıcı ana sayfasına yönlendirilir
        return redirect(url_for('genel.anasayfa'))


@ceza_bp.route('/ceza_sorgula', methods=['POST'])
@admin_or_personel_required   # sadece admin veya personel erişebilir
def ceza_sorgula_api_route():
    
    # Hem JSON hem form isteği için veri alınır
    data = request.get_json(silent=True) or {}
    
    # Ceza ID kullanıcıdan alınır
    ceza_id = data.get("ceza_id")

    # Ceza ID gönderilmemişse hata dön
    if not ceza_id:
        return jsonify({"success": False, "message": "Ceza ID belirtilmedi."}), 400

    # Ceza ID sayı değilse hata dön
    try:
        ceza_id = int(ceza_id)
    except ValueError:
        return jsonify({"success": False, "message": "Geçersiz Ceza ID."}), 400

    # Controller üzerinden ceza bilgileri alınır
    sorgu_sonucu = ceza_controller_instance.ceza_bilgilerini_getir(ceza_id)

    # Bu ID’ye ait ceza yoksa hata dön
    if not sorgu_sonucu:
        return jsonify({"success": False, "message": "Belirtilen ID'ye ait ceza bulunamadı."}), 404

    # Ceza zaten ödenmiş mi kontrol edilir
    if sorgu_sonucu.get('odendi_mi') == 1:
        return jsonify({"success": False, "message": "Bu ceza zaten ödenmiş."}), 400

    # Başarılı ise ilgili bilgiler geri döndürülür
    return jsonify({
        "success": True,
        "borc_miktari": sorgu_sonucu['miktar'],   # Borç tutarı
        "username": sorgu_sonucu['username']      # Kullanıcı adı
    }), 200

@ceza_bp.route('/cezaode', methods=['POST'])
@admin_or_personel_required   # sadece admin/personel yapabilir
def ceza_ode():
    
    # JSON veya form datası alınır
    data = request.get_json(silent=True) or {}
    
    # Kullanıcıdan ceza ID alınır
    ceza_id = data.get("ceza_id")

    # Ceza ID eksikse hata dön
    if not ceza_id:
        return jsonify({"success": False, "message": "Ceza ID belirtilmedi."}), 400

    # Ceza ID sayı mı kontrol edilir
    try:
        ceza_id = int(ceza_id)
    except ValueError:
        return jsonify({"success": False, "message": "Geçersiz Ceza ID."}), 400

    try:
        # Controller üzerinden ceza ödeme işlemi yapılır
        success, message = ceza_controller_instance.ceza_ode(ceza_id)

    # MySQL’den gelebilecek özel veritabanı hataları yakalanır
    except (DatabaseError, IntegrityError, ProgrammingError) as e:
        
        # Kitap iade edilmeden ödeme yapılamaz
        if "1644" in str(e) or "45000" in str(e):
            return jsonify({"success": False, "message": "Kitap iade edilmeden ceza ödenemez."}), 400
        
        # Genel veritabanı hatası
        return jsonify({"success": False, "message": "Veritabanı hatası oluştu."}), 500

    # Herhangi başka bir hata gelirse yakalanır
    except Exception as e:
        print("CEZA ÖDEME HATA:", e)
        return jsonify({"success": False, "message": "Beklenmeyen bir sunucu hatası oluştu."}), 500

    # İşlem başarılı mı değil mi duruma göre yanıt dön
    return jsonify({"success": success, "message": message}), 200 if success else 400