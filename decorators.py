from functools import wraps
from flask import request, jsonify, g, session, redirect, url_for, flash
import jwt

# JWT  imzalama ve çözme işlemleri için kullanılan gizli anahtar
JWT_SECRET = "56925541090436581"

def login_required(f):
    
    #Bir rotaya erişmek için kullanıcının giriş yapmış olmasını zorunlu kılar
    #Hem JWT (Token) hem de Session (Oturum) kontrolü yapar.
    
    @wraps(f)  
    def decorated_function(*args, **kwargs):
        # İstek başlıklarından 'Authorization' verisini alir
        token = request.headers.get("Authorization")
        
        # Eğer token varsa ve "Bearer " ile başlıyorsa 
        if token and token.startswith("Bearer "):
            token = token[7:]  # "Bearer " kısmını (ilk 7 karakter) atar ve sadece token kalır
            try:
                # Token'ı gizli anahtar ile çözmeye çalışır
                payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
                
                # Token geçerliyse içindeki verileri Flask'ın global 'g' nesnesine kaydet.
                # Böylece bu verilere (user_id, role vb.) diğer fonksiyonlardan erişilebilir olur
                g.user_id = payload.get("user_id")
                g.username = payload.get("username")
                g.role = payload.get("role")
                
                # Her şey tamamsa orijinal fonksiyonu çalışır
                return f(*args, **kwargs)
                
            except jwt.ExpiredSignatureError:
                # Token'ın süresi dolmuşsa
                msg = "JWT oturumu süresi doldu."
            except jwt.InvalidTokenError:
                # Token formatı bozuksa veya imza geçersizse
                msg = "Geçersiz JWT."
            
            # Token hatası varsa JSON olarak 401 (Unauthorized) hatası dön
            return jsonify({"success": False, "message": msg}), 401

        # Eğer Header'da token yoksa, sunucu taraflı session'a bak
        if "user_id" in session:
            # Session'daki verileri 'g' nesnesine aktar.
            g.user_id = session.get("user_id")
            g.username = session.get("username")
            g.role = session.get("role")
            
            # Orijinal fonksiyonu çalıştır
            return f(*args, **kwargs)

        # giriş yapılmamışşsaa
        if request.accept_mimetypes.best == "application/json":
            return jsonify({"success": False, "message": "Giriş yapmanız gerekli."}), 401
        
        # Eğer istek tarayıcıdan geliyorsa:
        flash("Giriş yapmanız gerekiyor.", "danger")
        return redirect(url_for("anasayfa")) # Giriş sayfasına yönlendir

    return decorated_function

# -------------------------------------------------------------------------
# SADECE ADMIN YETKİSİ (ADMIN REQUIRED)
# -------------------------------------------------------------------------
def admin_required(f):

#    Sadece rolü 'admin' olan kullanıcıların erişmesine izin verir.

    @wraps(f)
    @login_required 
    def decorated(*args, **kwargs):
        if getattr(g, "role", None) != "admin":
            
            # Yetki yoksa ve istek API ise 403 (Forbidden) döner
            if request.accept_mimetypes.best == "application/json":
                return jsonify({"success": False, "message": "Admin yetkisi gerekli."}), 403
            
            # Web tarayıcısı ise hata mesajı verir
            flash("Bu işlem için admin yetkisi gerekiyor.", "danger")
            
            # Kullanıcıyı rolüne göre uygun sayfaya geri gönder
            if g.role == "personel":
                return redirect(url_for("personel_sayfasi"))
            return redirect(url_for("kullanici_sayfasi"))
            
        # Admin ise fonksiyonu çalıştır.
        return f(*args, **kwargs)
    return decorated

def admin_or_personel_required(f):
    
    #Rolü 'admin' VEYA 'personel' olanların erişmesine izin verir.
    #Normal kullanıcılar erişemez.

    @wraps(f)
    @login_required  # Önce giriş kontrolü.
    def decorated(*args, **kwargs):
        # Rol, izin verilenler listesinde mi kontrolu
        if getattr(g, "role", None) not in ["admin", "personel"]:
            
            # Yetki yoksa API yanıtı 
            if request.accept_mimetypes.best == "application/json":
                return jsonify({"success": False, "message": "Admin veya personel yetkisi gerekli."}), 403
            
            # Web yanıtı.
            flash("Bu sayfaya erişim yetkiniz bulunmamaktadır.", "danger")
            return redirect(url_for("kullanici_sayfasi"))
            
        # Yetki varsa fonksiyonu çalıştır.
        return f(*args, **kwargs)
    return decorated