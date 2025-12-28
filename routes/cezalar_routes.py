from flask import Blueprint, render_template, request, jsonify, g, redirect, session, url_for
from sqlite3 import DatabaseError, IntegrityError, ProgrammingError

# dependencies klasöründen gerekli fonksiyonları ve sınıfları çekiyoruz
from depencies import ceza_controller_instance, make_json_compatible

from decorators import (admin_required, login_required,
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
@ceza_bp.route('/cezalarimigoster/<username>')
@login_required
def cezalarimigoster(username):
    # Güvenlik için session'daki kullanıcıyı alıyoruz
    current_username = g.username 
    
    try:
        cezalar = ceza_controller_instance.kullanici_cezalarini_goster(current_username)

        # JSON uyumluluğu için formatla
        cezalar_json = make_json_compatible(cezalar)

        # Postman veya API istekleri için JSON döndür
        if request.accept_mimetypes.best == "application/json" or request.is_json:
            return jsonify({
                "status": "success",
                "username": current_username, 
                "total_count": len(cezalar),
                "cezalar": cezalar_json
            }), 200
        
        # Tarayıcı için HTML döndür
        return render_template(
            'cezalarim.html', 
            username=current_username, 
            cezalar=cezalar
        )

    except Exception as e:
        mesaj = f"Sunucu hatası: {str(e)}"
        if request.accept_mimetypes.best == "application/json" or request.is_json:
            return jsonify({"status": "error", "message": mesaj}), 500
        
        print(f"HATA /cezalarimigoster: {e}")
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
@admin_or_personel_required
def ceza_ode():
    data = request.get_json(silent=True) or {}
    ceza_id = data.get("ceza_id")
    
    if not ceza_id:
        return jsonify({"success": False, "message": "Ceza ID belirtilmedi."}), 400

    try:
        ceza_id = int(ceza_id)
        mevcut_ceza = ceza_controller_instance.ceza_bilgilerini_getir(ceza_id)

        if not mevcut_ceza:
            return jsonify({"success": False, "message": "Ceza kaydı bulunamadı."}), 404

        asıl_borclu = mevcut_ceza.get('username') 

        if mevcut_ceza.get('gercek_iade') is None:
            return jsonify({
                "success": False, 
                "message": f"DİKKAT: {asıl_borclu} isimli kullanıcı bu kitabı henüz iade etmemiş!"
            }), 400
        
        # Ödeme Durumu Kontrolü
        if mevcut_ceza.get('odendi_mi') == 1:
             return jsonify({"success": False, "message": "Bu ceza zaten ödenmiş."}), 400

        # Servis katmanından ödemeyi yap
        success, message = ceza_controller_instance.ceza_ode(ceza_id)
        
        # Her zaman JSON döndür
        return jsonify({"success": success, "message": message}), 200 if success else 400

    except Exception as e:
        print(f"CEZA ÖDEME HATASI: {e}")
        # Hata durumunda da JSON döndür (HTML değil!)
        return jsonify({"success": False, "message": f"Sunucu hatası: {str(e)}"}), 500