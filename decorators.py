from functools import wraps
from flask import request, jsonify, g, session, redirect, url_for, flash
import jwt

JWT_SECRET = "56925541090436581"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            token = token[7:]
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
                g.user_id = payload.get("user_id")
                g.username = payload.get("username")
                g.role = payload.get("role")
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                msg = "JWT oturumu süresi doldu."
            except jwt.InvalidTokenError:
                msg = "Geçersiz JWT."
            return jsonify({"success": False, "message": msg}), 401

        # SESSION VARSA
        if "user_id" in session:
            g.user_id = session.get("user_id")
            g.username = session.get("username")
            g.role = session.get("role")
            return f(*args, **kwargs)

        # HİÇBİRİ YOKSA
        if request.accept_mimetypes.best == "application/json":
            return jsonify({"success": False, "message": "Giriş yapmanız gerekli."}), 401
        flash("Giriş yapmanız gerekiyor.", "danger")
        return redirect(url_for("anasayfa"))

    return decorated_function

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if getattr(g, "role", None) != "admin":
            if request.accept_mimetypes.best == "application/json":
                return jsonify({"success": False, "message": "Admin yetkisi gerekli."}), 403
            flash("Bu işlem için admin yetkisi gerekiyor.", "danger")
            if g.role == "personel":
                return redirect(url_for("personel_sayfasi"))
            return redirect(url_for("kullanici_sayfasi"))
        return f(*args, **kwargs)
    return decorated

def admin_or_personel_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if getattr(g, "role", None) not in ["admin", "personel"]:
            if request.accept_mimetypes.best == "application/json":
                return jsonify({"success": False, "message": "Admin veya personel yetkisi gerekli."}), 403
            flash("Bu sayfaya erişim yetkiniz bulunmamaktadır.", "danger")
            return redirect(url_for("kullanici_sayfasi"))
        return f(*args, **kwargs)
    return decorated
