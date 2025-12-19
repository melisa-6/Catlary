from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, g

# dependencies dosyasından controller'ı çekiyoruz
from depencies import kategoriler_controller

from decorators import (admin_required,login_required,
    admin_or_personel_required)

# Blueprint oluşturuluyor
kategori_bp = Blueprint('kategori', __name__)

@kategori_bp.route("/kategoriler", methods=["GET"]) 
@login_required # Sadece giriş yapmış kullanıcılar görebilsin diye
def kategorileri_getir_route():
    # "Accept" başlığı JSON mu veya istek gövdesi JSON mu kontrol ederek isteğin API olup olmadığını anlar
    is_api_request = request.accept_mimetypes.best == "application/json" or request.is_json

    # Controller katmanından veritabanındaki tüm kategorileri çeker
    kategoriler = kategoriler_controller.tum_kategorileri_getir_controller()
    
    basarili_mi = True 
    mesaj = "Kategoriler listelendi"
    
    # Eğer istek API isteği ise
    if is_api_request:
        # Verileri JSON formatında döndürür
        return jsonify({
            "success": basarili_mi,
            "message": mesaj,
            "kategoriler": kategoriler
        }), 200

    # Eğer istek tarayıcıdan geliyorsa HTML şablonunu kategoriler.html render eder
    # Şablona kategorileri ve kullanıcı adını gönderiyoruz
    return render_template(
        "kategoriler.html",
        kategoriler=kategoriler,
        username=getattr(g, "username", "") # g.username yoksa boş string ver.
    )
    
   
@kategori_bp.route("/kategoriekle", methods=["POST"]) 
def kategoriekle():
    # Önce form verisine bak yoksa JSON verisine bakarak kategori adını alir
    kategori_adi = request.form.get("kategori_adi") or (request.json.get("kategori_adi") if request.is_json else None)

    # Controller'a kategori ekleme emrini verir
    success, msg = kategoriler_controller.kategoriekle_controller(kategori_adi)

    # Eğer istemci JSON yanıtı bekliyorsa (API):
    if request.accept_mimetypes.best == "application/json":
        return jsonify({
            "success": success,
            "message": msg
        }), (200 if success else 400) # Başarılıysa 200 OK, değilse 400 Bad Request.

    # Web tarayıcısı ise kullanıcıya mesaj göster ve listeye geri yönlendir.
    flash(msg, "success" if success else "danger")
    # Blueprint içinde olduğumuz için url_for ile yönlendirmek en doğrusudur
    return redirect(url_for('kategori.kategorileri_getir_route'))


@kategori_bp.route("/kategorisil/<int:id>", methods=["POST"]) 
def kategori_sil_route(id):
    # API isteği kontrolü
    is_api_request = request.accept_mimetypes.best == "application/json" or request.is_json

    # Controller üzerinden silme işlemini yapar
    basarili, mesaj = kategoriler_controller.kategori_sil_controller(id)

    # API yanıtı
    if is_api_request:
        return jsonify({"success": basarili, "message": mesaj}), (200 if basarili else 400)

    # Web yanıtı
    flash(mesaj, "success" if basarili else "danger")
    return redirect(url_for("kategori.kategorileri_getir_route")) # Listeleme sayfasına dön