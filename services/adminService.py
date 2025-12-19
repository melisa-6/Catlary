import hashlib
import secrets
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash
from repository import AdminRepository
from send_mail import send_mail_to_user
from services.kullaniciService import kullaniciService
from repository.AdminRepository import AdminRepository

class adminService:
    def __init__(self, db_config):
        self.db_config = db_config
        self.repo = AdminRepository(db_config)
        self.kullanici_service = kullaniciService(db_config)
    
        
    def admin_ekle(self, username, email, sifre, sifre_tekrar):
        #alan doluluklarını kontrol eder
        if not all([username, email, sifre, sifre_tekrar]):
            flash("Tüm alanlar doldurulmalıdır.", "error")
            return None 
        #sifre uyusmasını kontrol eder
        if sifre != sifre_tekrar:
            flash("Şifreler eşleşmiyor!", "error")
            return None 
        #sifre uzunluunu kontrol eder
        if len(sifre) < 6:
            flash("Şifre en az 6 karakter olmalı.", "error")
            return None
        #isimde veya mailde kullanıcının olup olmadıgını kontrol eder
        if self.kullanici_service.kullanici_var_mi(username) or self.kullanici_service.kullanici_email_var_mi(email):
            print(f"DEBUG: {username} veya {email} zaten KULLANICILAR tablosunda mevcut.")
            flash("Kullanıcı adı veya e-posta zaten kullanımda!", "error")
            return 0 
            
        if self.repo.get_by_username(username) or self.repo.get_by_email(email):
            print(f"DEBUG: {username} veya {email} zaten ADMINLER tablosunda mevcut.")
            flash("Kullanıcı adı veya e-posta zaten kullanımda!", "error")
            return 0 
        #sifreyi hashler ve ilgili repoya yonlendirir
        sifre_hash = generate_password_hash(sifre)
        
        
        try:
            admin_id = self.repo.admin_ekle(username, email, sifre_hash)

            if admin_id > 0:
                return admin_id
            else:
                flash("Admin, admin tablosuna kaydedilemedi!", "error")
               
                return -1
                
        except Exception as e:
            print(f"AdminService admin_ekle HATA: {e}")
            flash("Admin eklenirken beklenmeyen bir hata oluştu.", "error")
            return -1
    def sifre_sifirla_by_admin_user(self, admin_user):
        yeni_sifre = ''.join(secrets.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(10))
        
        simule_edilmis_hash = hashlib.sha256(yeni_sifre.encode('utf-8')).hexdigest()
        
        yeni_db_hash = generate_password_hash(simule_edilmis_hash)

        guncellendi = self.repo.sifre_guncelle(admin_user['username'], yeni_db_hash)
        try:
            admin_id = int(admin_user['id']) 
        except ValueError:
            return {"success": False, "message": "HATA: Admin ID'si sayı değil, veri bozuk geldi!"}

        # Güncellemeyi sayı olan ID ile yap
        guncellendi = self.repo.sifre_guncelle(admin_id, yeni_db_hash)
        if not guncellendi:
            return {"success": False, "message": "Admin şifresi veritabanına yazılamadı."}

        konu = "Admin Şifre Sıfırlama"
        icerik = f"Merhaba Sayın Yönetici ({admin_user['username']}),\n\nŞifreniz sıfırlandı.\nYeni Şifreniz: {yeni_sifre}\n\nLütfen güvenliğiniz için giriş yaptıktan sonra değiştiriniz."
        
        try:
            send_mail_to_user(admin_user['email'], konu, icerik)
        except:
            print(f"Mail gönderilemedi. Yeni şifre: {yeni_sifre}")

        return {
            "success": True, 
            "message": f"Admin şifresi sıfırlandı. Mail: {admin_user['email']}",
            "yeni_sifre": yeni_sifre
        }   
    def admin_sil(self, username, username_tekrar):
        #eslesme kontrolu
        if username != username_tekrar:
            return 0  

        if username.lower() == 'admin': 
            return -1 
#reponun ilgili fonksiyonun ayonlendirir
        silinen = self.repo.admin_sil(username)
        return silinen
    
    def tum_adminleri_getir(self): 
        #reponun ilgili fonksiyonunu cagirir
        adminler = self.repo.adminler() 
        return adminler 
    
    def admin_var_mi(self, username):
        return self.repo.get_by_username(username) is not None

    def sifre_degistir(self, username, eski_sifre, yeni_sifre, yeni_sifre_tekrar):
        # 3 şifrenin de gönderilmiş olması gerekiyor. Eksik varsa hata verir
        if not all([eski_sifre, yeni_sifre, yeni_sifre_tekrar]):
            return {"success": False, "message": "Tüm alanlar doldurulmalıdır."}

        # Yeni şifre ile tekrar girilen şifre kontrol edilir
        if yeni_sifre != yeni_sifre_tekrar:
            return {"success": False, "message": "Yeni şifreler eşleşmiyor!"}
       
        # Yeni şifrenin minimum uzunluk kontrolü
        if len(yeni_sifre) < 6:
            return {"success": False, "message": "Şifre en az 6 karakter olmalı."}

        # Veritabanından admin bilgisi alınır
        mevcut_admin = self.repo.get_by_username(username)
        if not mevcut_admin:
            return {"success": False, "message": "Admin bulunamadı!"}

        # Yeni şifre eski şifreyle aynı mı kontrol edilir
        if check_password_hash(mevcut_admin['password'], yeni_sifre):
           return {"success": False, "message": "Yeni şifre eski şifrenizle aynı olamaz!"}
    
        # Kullanıcıdan alınan eski şifre doğru mu diye kontrol edilir
        if not check_password_hash(mevcut_admin['password'], eski_sifre):
            return {"success": False, "message": "Eski şifre yanlış!"}

        # Yeni şifre hashlenir
        yeni_hash = generate_password_hash(yeni_sifre)

        # Şifre veritabanında güncellenir
        sonuc = self.repo.sifre_guncelle(username, yeni_hash)

        # repo sonucu doğrudan döndürülür (success veya error)
        return sonuc

    
    def get_admin_by_email(self, email):
        admin_user = self.repo.get_by_email(email)
        return admin_user