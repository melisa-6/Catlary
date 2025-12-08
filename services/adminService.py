from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash
from repository import AdminRepository
from services.kullaniciService import kullaniciService
from repository.AdminRepository import AdminRepository

class adminService:
    def __init__(self, db_config):
        self.db_config = db_config
        self.repo = AdminRepository(db_config)
        self.kullanici_service = kullaniciService(db_config)
    
        
    def admin_ekle(self, username, email, sifre, sifre_tekrar):
        if not all([username, email, sifre, sifre_tekrar]):
            flash("Tüm alanlar doldurulmalıdır.", "error")
            return None 
        if sifre != sifre_tekrar:
            flash("Şifreler eşleşmiyor!", "error")
            return None 
        if len(sifre) < 6:
            flash("Şifre en az 6 karakter olmalı.", "error")
            return None
        
        if self.kullanici_service.kullanici_var_mi(username) or self.kullanici_service.kullanici_email_var_mi(email):
            print(f"DEBUG: {username} veya {email} zaten KULLANICILAR tablosunda mevcut.")
            flash("Kullanıcı adı veya e-posta zaten kullanımda!", "error")
            return 0 
            
        if self.repo.get_by_username(username) or self.repo.get_by_email(email):
            print(f"DEBUG: {username} veya {email} zaten ADMINLER tablosunda mevcut.")
            flash("Kullanıcı adı veya e-posta zaten kullanımda!", "error")
            return 0 
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
        
    def admin_sil(self, username, username_tekrar):
        if username != username_tekrar:
            return 0  

        if username.lower() == 'admin': 
            return -1 

        silinen = self.repo.admin_sil(username)
        return silinen
    def tum_adminleri_getir(self): 
        adminler = self.repo.adminler() 
        return adminler 
    
    def admin_var_mi(self, username):
        return self.repo.get_by_username(username) is not None

    def sifre_degistir(self, username, eski_sifre, yeni_sifre, yeni_sifre_tekrar):
        if not all([eski_sifre, yeni_sifre, yeni_sifre_tekrar]):
            return {"success": False, "message": "Tüm alanlar doldurulmalıdır."}
        if yeni_sifre != yeni_sifre_tekrar:
            return {"success": False, "message": "Yeni şifreler eşleşmiyor!"}
       
        if len(yeni_sifre) < 6:
            return {"success": False, "message": "Şifre en az 6 karakter olmalı."}

        mevcut_admin = self.repo.get_by_username(username)
        if not mevcut_admin:
            return {"success": False, "message": "Admin bulunamadı!"}
        if check_password_hash(mevcut_admin['password'], yeni_sifre):
           return {"success": False, "message": "Yeni şifre eski şifrenizle aynı olamaz!"}
    
        if not check_password_hash(mevcut_admin['password'], eski_sifre):
            return {"success": False, "message": "Eski şifre yanlış!"}

        yeni_hash = generate_password_hash(yeni_sifre)
        sonuc = self.repo.sifre_guncelle(username, yeni_hash)
        return sonuc
    
    def get_admin_by_email(self, email):
        admin_user = self.repo.get_by_email(email)
        return admin_user