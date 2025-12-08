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
        # 1. İlk Kontroller
        if not all([username, email, sifre, sifre_tekrar]):
            flash("Tüm alanlar doldurulmalıdır.", "error")
            return None 
        if sifre != sifre_tekrar:
            flash("Şifreler eşleşmiyor!", "error")
            return None 
        if len(sifre) < 6:
            flash("Şifre en az 6 karakter olmalı.", "error")
            return None
        
        # Kullanıcılar tablosunda kontrol
        if self.kullanici_service.kullanici_var_mi(username) or self.kullanici_service.kullanici_email_var_mi(email):
            print(f"DEBUG: {username} veya {email} zaten KULLANICILAR tablosunda mevcut.")
            flash("Kullanıcı adı veya e-posta zaten kullanımda!", "error")
            return 0 
            
        # Adminler tablosunda kontrol
        if self.repo.get_by_username(username) or self.repo.get_by_email(email):
            print(f"DEBUG: {username} veya {email} zaten ADMINLER tablosunda mevcut.")
            flash("Kullanıcı adı veya e-posta zaten kullanımda!", "error")
            return 0 

        # 3. Şifreyi hashle
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
        # gelen usernamelerin eşleşmesini kontrol eder
        if username != username_tekrar:
            return 0  # Controller mesaj oluşturur

        #  Default admin kontrolü
        if username.lower() == 'admin':  # default adminin usernamei
            return -1  # özel kod, controller bunu yorumlar

        silinen = self.repo.admin_sil(username)
        return silinen
    # Bu metot AdminService.py içinde olmalı ve Repository'ye yönlendirmeli
    def tum_adminleri_getir(self): # <--- HATA: Bu metot repo'yu yanlış çağırıyor.
        """Tüm adminleri AdminService üzerinden çeker ve döndürür."""
        # adminler = admin_service.tum_adminleri_getir() kısmı Controller'da zaten var.
        # Service katmanındaki doğru çağırma:
        adminler = self.repo.adminler() # Repo'daki adminler() metodunu çağırmalı.
        return adminler # Çekilen listeyi döndürmeli.
    # belirtilen isimde admin var mi ogrenmek icin repoya yonlendirir
    def admin_var_mi(self, username):
        return self.repo.get_by_username(username) is not None

    # adminin sifresini degistirmek icin ilgili kontrolleri yapar 
    def sifre_degistir(self, username, eski_sifre, yeni_sifre, yeni_sifre_tekrar):
       #tum alanlarin dolulugunu kontrol eder
        if not all([eski_sifre, yeni_sifre, yeni_sifre_tekrar]):
            return {"success": False, "message": "Tüm alanlar doldurulmalıdır."}
        #yeni sifre ve eski sifrenin eslesimini kontrol eder
        if yeni_sifre != yeni_sifre_tekrar:
            return {"success": False, "message": "Yeni şifreler eşleşmiyor!"}
       #yeni sifrenin uzunlugunu kontrol eder
        if len(yeni_sifre) < 6:
            return {"success": False, "message": "Şifre en az 6 karakter olmalı."}
        #adminin mevcut olup olmadıgını kontrol eder
        mevcut_admin = self.repo.get_by_username(username)
        if not mevcut_admin:
            return {"success": False, "message": "Admin bulunamadı!"}
        #yeni sifre ve eski sifrenin ayni olma durumunu kontrool eder
        if check_password_hash(mevcut_admin['password'], yeni_sifre):
           return {"success": False, "message": "Yeni şifre eski şifrenizle aynı olamaz!"}
    #eski sifrenin dogrulugu kontrol edilir
        if not check_password_hash(mevcut_admin['password'], eski_sifre):
            return {"success": False, "message": "Eski şifre yanlış!"}

        # Yeni şifreyi hashler ve günceller
        yeni_hash = generate_password_hash(yeni_sifre)
        sonuc = self.repo.sifre_guncelle(username, yeni_hash)
        return sonuc
    
    def get_admin_by_email(self, email):
    #repository dosyasina emaili parametre alarak gonderir
    
        
        admin_user = self.repo.get_by_email(email)
        return admin_user