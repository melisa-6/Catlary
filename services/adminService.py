from werkzeug.security import generate_password_hash, check_password_hash
from repository.AdminRepository import AdminRepository

class AdminService:
    def __init__(self, db_config):
        self.db_config = db_config 
        
        self.repo = AdminRepository(db_config)
    
    def admin_ekle(self, username, email, sifre, sifre_tekrar):
      #tum alanların dolulugunu kontrol eder
        if not all([username, email, sifre, sifre_tekrar]):
            return None  
        #sifrelerin eslesmesini kontrol eder
        if sifre != sifre_tekrar:
            return None  
#sifreler eslesmisse hashleyerek repositorye gonderir
        sifre_hash = generate_password_hash(sifre)
        admin_id = self.repo.admin_ekle(username, email, sifre_hash)
        return admin_id


    def admin_sil(self, username, username_tekrar):
        # gelen usernamelerin eşleşmesini kontrol eder
        if username != username_tekrar:
            return 0  # Controller mesaj oluşturur

        #  Default admin kontrolü
        if username.lower() == 'admin':  # default adminin usernamei
            return -1  # özel kod, controller bunu yorumlar

        silinen = self.repo.admin_sil(username)
        return silinen
  


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
        admin_repo = AdminRepository(self.db_config)
        
        admin_user = admin_repo.get_by_email(email)
        return admin_user