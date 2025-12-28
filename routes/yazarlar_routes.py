from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, g

# dependencies dosyasından controller'ı çekiyoruz
from depencies import yazarlar_controller

# decorators dosyasından login zorunluluğunu çekiyoruz
from decorators import login_required

# Blueprint oluşturuluyor
yazar_bp = Blueprint('yazar', __name__)

@yazar_bp.route("/yazarlar", methods=["GET"]) 
@login_required # Giriş zorunluluğu.
def yazarlar_getir_route():
    # İstemcinin JSON yanıtı isteyip istemediğini kontrol eder
    is_api_request = request.accept_mimetypes.best == "application/json" or request.is_json
    
    # Controller'dan yazarları çeker
    yazarlar = yazarlar_controller.tum_yazarlari_getir_controller()
    
    basarili_mi = True
    mesaj = "Yazarlar listelendi"

    # API isteği için JSON dönüşü.
    if is_api_request:
        return jsonify({
            "success": basarili_mi,
            "message": mesaj,
            "yazarlar": yazarlar
        }), 200

    # Web tarayıcısı için HTML dönüşü.
    return render_template(
        "yazarlar.html",
        yazarlar=yazarlar,
        username=getattr(g, "username", "")
    )

@yazar_bp.route("/yazarekle", methods=["POST"]) 
def yazarekle():
    # Yazar adını alır
    ad = request.form.get("yazar_adi") or (request.json.get("yazar_adi") if request.is_json else None)

    # Controller ile yazarı ekler
    success, msg = yazarlar_controller.yazarekle_controller(ad)

    # Eğer istek JSON formatındaysa JSON dön.
    if request.is_json:
        return jsonify({
            "success": success,
            "message": msg
        }), (200 if success else 400)

    # Değilse Flash mesajı oluştur.
    flash(msg, "success" if success else "danger")

    yazarlar = yazarlar_controller.tum_yazarlari_getir_controller()
    return render_template("yazarlar.html", yazarlar=yazarlar)

@yazar_bp.route("/yazarsil/<int:id>", methods=["POST"]) 
@login_required
def yazar_sil_route(id):
    # API isteği kontrolü
    is_api_request = request.accept_mimetypes.best == "application/json" or request.is_json

    # Controller ile silme işlemi
    basarili, mesaj = yazarlar_controller.yazar_sil_controller(id)

    # API yanıtı
    if is_api_request:
        return jsonify({"success": basarili, "message": mesaj}), (200 if basarili else 400)

    # Web yanıtı ve yönlendirme
    flash(mesaj, "success" if basarili else "danger")
    return redirect(url_for("yazar.yazarlar_getir_route"))