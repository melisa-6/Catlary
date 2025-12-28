from flask import Blueprint, flash, render_template, request, jsonify, g, redirect, url_for
from sqlite3 import DatabaseError, IntegrityError, ProgrammingError

# dependencies klasöründen gerekli fonksiyonları ve sınıfları çekiyoruz
from depencies import  make_json_compatible,yayinevi_controller

from decorators import (admin_required,login_required,
    admin_or_personel_required)
# Blueprint oluşturuluyor
yayinevi_bp = Blueprint('yayinevi', __name__)
@yayinevi_bp.route("/yayinevleri", methods=["GET"])
@login_required
def yayinevleri_getir():
    # Controller'dan veriyi çek
    yayinevleri = yayinevi_controller.yayinevleri_getir_controller()
    
    # API isteği mi kontrol et (JSON isteniyorsa)
    if request.accept_mimetypes.best == "application/json" or request.is_json:
        return jsonify(yayinevleri), 200
        
    # HTML Sayfasını render et
    return render_template("yayinevleri.html", yayinevleri=yayinevleri)


@yayinevi_bp.route("/yayineviekle", methods=["POST"])  # DİKKAT: 'methods' çoğul olmalı
@login_required
def yayinevi_ekle():
    data = request.get_json(silent=True) or request.form
    ad = data.get("yayinevi_adi")

    # Controller'a gönder
    success, msg = yayinevi_controller.yayinevi_ekle(ad) # Controller'da bu metodun olduğundan emin ol

    # JSON İsteği ise
    if request.is_json or request.accept_mimetypes.best == "application/json":
        return jsonify({"success": success, "message": msg}), (200 if success else 400)

    # HTML Form İsteği ise
    flash(msg, "success" if success else "danger")
    
    # İşlem bitince listeye geri dön
    return redirect(url_for('yayinevi.yayinevleri_getir'))


@yayinevi_bp.route("/yayinevisil", methods=["POST"])
@admin_required 
def yayinevi_sil():
    
    # Silinecek ID'yi al
    data = request.get_json(silent=True) or request.form
    yayinevi_id = data.get("id")

    success, msg = yayinevi_controller.yayinevi_sil(yayinevi_id)

    # JSON Dönüşü
    if request.is_json or request.accept_mimetypes.best == "application/json":
         return jsonify({"success": success, "message": msg}), (200 if success else 400)

    # HTML Dönüşü
    flash(msg, "success" if success else "danger")
    return redirect(url_for('yayinevi.yayinevleri_getir'))