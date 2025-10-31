from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify

#kullanilan route da giris yapilmak zorunda
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_ajax = request.accept_mimetypes.accept_json or request.is_json
        
        if 'logged_in' not in session:
            if is_ajax:
        
                return jsonify({"success": False, "message": "Oturum süresi doldu."}), 401
            
            flash("Lütfen bu sayfaya erişmek için giriş yapınız.", "error")
            return redirect(url_for('anasayfa'))
        return f(*args, **kwargs)
    return decorated_function

#kullanilan route da rol admin olmak zorunda
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        
        is_ajax = request.accept_mimetypes.accept_json or request.is_json
        
        # Admin yetkisi kontrolü
        if 'logged_in' not in session or session.get('role') != 'admin':
            
            if is_ajax:
                
                return jsonify({
                    "success": False,
                    "message": "Yetkisiz erişim. Lütfen tekrar giriş yapın."
                }), 401 
            
        
            flash("Bu sayfaya erişim yetkiniz yok veya oturumunuz sona erdi.", "error")
            return redirect(url_for('anasayfa'))
        return f(*args, **kwargs)
    return decorated_function
