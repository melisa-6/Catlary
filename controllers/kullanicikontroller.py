
import traceback
from flask import flash, session, request, jsonify, redirect, url_for
from werkzeug.security import check_password_hash
import jwt
import datetime
from repository.AdminRepository import AdminRepository
from send_mail import send_mail_to_user
from services.kullaniciService import kullaniciService
from services.adminService import adminService
from services.personelService import personelService
db_config = {
    "host": "127.0.0.1",
    "user": "melisa",
    "password": "Mtz0504*",
    "database": "kutuphane_db",
    "port": 3306
#mysql e baglanmak iicn gerekli bilgiler
}
kullanici_service = kullaniciService(db_config)
admin_service = adminService(db_config)
personel_service = personelService(db_config)  

from werkzeug.security import generate_password_hash
class kullanicikontroller:
    def kayit_ol_controller(form, kullanici_service: kullaniciService):
    #ilgili route un yonlendirmesi ile formdan gelen bilgileri alir 
        username = form.get('username')
        email = form.get('email')
        sifre = form.get('yeni_sifre') 
        sifre_tekrar = form.get('yeni_sifre_tekrar') 

        # tum alanlarin dolulugunu kontrol eder
        if not all([username, email, sifre, sifre_tekrar]):
            flash("Tüm alanlar boş bırakılamaz.", "error")
            return redirect(url_for('anasayfa'))
            
        #girilen sifrelerin eslesip eslesmedigini kontrol eder
        if sifre != sifre_tekrar:
            flash("Şifreler eşleşmiyor!", "error")
            return redirect(url_for('anasayfa'))
            
        #sonuc degiskeni ile ilgili service fonksiyonuna yonlendiriyoruz
        sonuc = kullanici_service.kayit_ol(username, email, sifre, sifre_tekrar)

        # İşlem sonucuna göre kullanıcıya uygun mesajı flash ile gösterir
        flash(
            sonuc['message'],  # Service'den dönen mesaj
            "success" if sonuc.get('success') else "error"
        )
        return redirect(url_for('anasayfa'))
        # Kullanıcıyı ana sayfaya yönlendir
  

    def giris_yap_controller(form, SECRET):
        print("\n--- [DEBUG] Giriş işlemi başladı ---")
        try:
            email = form.get('email')
            sifre = form.get('password') or form.get('sifre')
            islem = form.get('islem') # Rol
            is_web = form.get('is_web', False)

            if not all([email, sifre, islem]):
                 mesaj = "Lütfen tüm giriş alanlarını doldurun."
                 if is_web: return {"basarili": False, "mesaj": mesaj} 
                 return jsonify({"basarili": False, "mesaj": mesaj}), 400

            # Rol Bazlı Veri Çeker
            user_data = None
            if islem == 'admin':
                user_data = admin_service.get_admin_by_email(email)
            elif islem == 'personel':
                user_data = personel_service.get_personel_by_email(email)
            else: # islem == 'kullanici'
                user_data = kullanici_service.get_kullanici_by_email(email)

            if not user_data:
                mesaj = "Kullanıcı adı veya şifre hatalı."
                if is_web: return {"basarili": False, "mesaj": mesaj}
                return jsonify({"basarili": False, "mesaj": mesaj}), 404

            password_hash = user_data.get('password') or user_data.get('sifre')
            aktiflik_durumu = 1 
            
            if islem == 'personel':
                aktiflik_durumu = user_data.get('aktif', 0) 
            elif islem == 'kullanici':
                aktiflik_durumu = user_data.get('aktiflik', 0) 
                
            if aktiflik_durumu == 0:
                mesaj = "Hesabınız pasif durumdadır. Lütfen yöneticinizle iletişime geçin."
                if is_web: return {"basarili": False, "mesaj": mesaj} 
                return jsonify({"basarili": False, "mesaj": mesaj}), 403 
            if not check_password_hash(password_hash, sifre):
                mesaj = "Kullanıcı adı veya şifre hatalı."
                if is_web: return {"basarili": False, "mesaj": mesaj}
                return jsonify({"basarili": False, "mesaj": mesaj}), 401

            
            token_data = {
                "user_id": user_data['id'],
                "username": user_data.get('username') or user_data.get('isim'),
                "role": islem,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30) 
            }
            token = jwt.encode(token_data, SECRET, algorithm="HS256")

            # WEB 
            if is_web:
                session['user_id'] = user_data['id']
                session['username'] = token_data["username"]
                session['role'] = islem

                if islem == 'admin':
                    redirect_url = url_for('admin_anasayfa') 
                elif islem == 'personel':
                    redirect_url = url_for('personel_sayfasi') 
                else: # 'kullanici'
                    redirect_url = url_for('kullanici_sayfasi')
                    
                return {
                    "basarili": True, 
                    "mesaj": f"{islem.capitalize()} olarak giriş başarılı.",
                    "redirect_url": redirect_url
                }

            # json
            return jsonify({
                "basarili": True,
                "token": token,
                "username": token_data["username"],
                "role": islem,
                "user_id": user_data['id']
            })

        except Exception as e:
            print(f"\n[HATA] Controller içerisinde bir hata oluştu: {e}")
            traceback.print_exc() 
            mesaj = "Sunucu hatası, lütfen yöneticinize başvurun."
            
            if is_web: return {"basarili": False, "mesaj": mesaj}
            return jsonify({"basarili": False, "mesaj": mesaj}), 500
   
    def tum_kullanicilari_getir():
    #ilgili service fonksiyonuna yonlendirir
        return kullaniciService.tum_kullanicilari_getir()

    def kullanici_sifre_degistir_controller(self, user_id, form_data):
        # formdan gerekli bilgileri alır
        eski_sifre = form_data.get('eski_sifre')
        yeni_sifre = form_data.get('yeni_sifre')
        yeni_sifre_tekrar = form_data.get('yeni_sifre_tekrar')

        sonuc = kullanici_service.sifre_degistir(
            user_id, 
            eski_sifre, 
            yeni_sifre, 
            yeni_sifre_tekrar
        )
        
        return sonuc
    
    
    def kullanici_ekle_controller(form):
        username = form.get('username') or form.get('yeni_kullanici_adi')
        email = form.get('email') or form.get('yeni_kullanici_email')
        sifre = form.get('sifre') or form.get('yeni_kullanici_sifre')
        sifre_tekrar = form.get('sifre_tekrar') or form.get('yeni_kullanici_sifre_tekrar')

        if not username or not email or not sifre or not sifre_tekrar:
            return {"basarili": False, "mesaj": "Tüm alanlar gerekli!"}

        if sifre != sifre_tekrar:
            return {"basarili": False, "mesaj": "Şifreler eşleşmiyor!"}

        hashed_password = generate_password_hash(sifre)

        eklendi_mi = kullanici_service.kullanici_ekle(username, email, hashed_password)

        if eklendi_mi:
            return {"basarili": True, "mesaj": f"Kullanıcı '{username}' başarıyla eklendi."}
        else:
            return {"basarili": False, "mesaj": "Kullanıcı adı veya e-posta zaten kullanımda veya veritabanı hatası oluştu."}

    def get_by_username(username):
        return kullaniciService.get_by_username(username)


    def admin_kullanici_sifre_sifirla_controller(self, form_data):
            try:
                kullanici_id = int(form_data.get("kullanici_id"))
            except (TypeError, ValueError):
                return {"success": False, "message": "Geçersiz kullanıcı ID."}

            user = kullanici_service.get_kullanici_by_id(kullanici_id)
            if not user:
                return {"success": False, "message": "Kullanıcı bulunamadı!"}

            sonuc = kullanici_service.sifre_sifirla_by_user(user)
            if sonuc.get("success"):
                return {
                    "success": True,
                    "message": sonuc.get("message"),
                    "user_id": user["id"],
                    "username": user["username"],
                    "yeni_sifre": sonuc.get("yeni_sifre")
                }
            else:
                return {"success": False, "message": sonuc.get("message")}

    def kullanici_durum_degistir_controller():
    
        if request.method != 'POST':
            return jsonify({"success": False, "message": "Geçersiz istek metodu."}), 405
        # JSON verisini alir
        data = request.get_json()
        
        if not data or 'kullanici_adi' not in data:
            return jsonify({"success": False, "message": "Eksik veri: 'kullanici_adi' gereklidir."}), 400
            
        kullanici_adi = data.get('kullanici_adi')
        # kullanıcıyı kullanıcı adına göre bul ve ID'sini alir
        user_data = kullaniciService.get_by_username(kullanici_adi) 
        if not user_data:
            return jsonify({"success": False, "message": "Kullanıcı bulunamadı!"}), 404

        user_id = user_data['id']
        
        sonuc = kullaniciService.kullanici_aktiflik_durumu_degistir(user_id) 
        #  JSON yanıtı döndür
        if sonuc['success']:
            return jsonify(sonuc), 200
        else:
            return jsonify(sonuc), 400
