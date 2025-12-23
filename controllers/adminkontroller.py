from flask import request, session, flash, redirect, url_for, render_template
from services.adminService import adminService


db_config = {
    "host": "localhost",
    "user": "melisa",
    "password": "",
    "database": "kutuphane_db"
}
admin_service = adminService(db_config)

class adminkontroller:
    def tum_adminleri_getir():
        #Tüm adminleri AdminService üzerinden çeker ve döndürür
        try:
            adminler = admin_service.tum_adminleri_getir() 
            return adminler
        except Exception as e:
            print(f"HATA: Adminleri Getirme Başarısız: {e}")
            return []
    
    def admin_ekle_controller(username, email, sifre, sifre_tekrar):
        # Tüm alanların doluluğunu kontrol eder
        if not all([username, email, sifre, sifre_tekrar]):
            return {"success": False, "message": "Tüm alanları doldurunuz!"}
        #eklemek icin ilgili service fonksiyonuna yonlendirir
        admin_id = admin_service.admin_ekle(username, email, sifre, sifre_tekrar)
        if admin_id:
            return {"success": True, "message": f"Admin başarıyla eklendi. ID: {admin_id}"}
        else:
            return {"success": False, "message": "Admin eklenemedi!"}

    #silinecek admin adi ni formdan alir ve service e yonlendirir 
    #silinme durumuna gore uygun mesajı verir
    def admin_sil_controller(username, username_tekrar):
        
        if not all([username, username_tekrar]):
            return {"success": False, "message": "Tüm alanları doldurunuz!"}
#servicein ilgili fonksiyonuna yonlendirir
        silinen = admin_service.admin_sil(username, username_tekrar)

        if silinen == -1:
            return {"success": False, "message": "Default admin silinemez!"}
        elif silinen > 0:
            return {"success": True, "message": f"{username} başarıyla silindi."}
        else:
            return {"success": False, "message": f"{username} bulunamadı veya eşleşme hatası."}

    def admin_sifre_degistir_controller(data):
        # Oturumdaki admin kullanıcı adını alır 
        # Eğer session'da yoksa API üzerinden gelen admin_username kullanılır
        admin_username = session.get('username') or data.get('admin_username')

        # Form veya JSON içinden şifre bilgilerini alır
        eski_sifre = data.get("eski_sifre")
        yeni_sifre = data.get("yeni_sifre")
        yeni_sifre_tekrar = data.get("yeni_sifre_tekrar")
        
        # Eğer admin session'da yoksa işlem yapılmaz
        if not admin_username:
            return {"success": False, "message": "Admin oturumu bulunamadı!"}

        # Yeni şifre ile tekrar şifresi eşleşmiyorsa hata döner
        if yeni_sifre != yeni_sifre_tekrar:
            return {"success": False, "message": "Yeni şifreler eşleşmiyor!"}

        # Şifre güncelleme işlemi service katmanına gönderilir
        sonuc = admin_service.sifre_degistir(admin_username, eski_sifre, yeni_sifre, yeni_sifre_tekrar)

        # Service başarılı dönerse işlem tamamlanır
        if sonuc.get("success", False):
            return {"success": True, "message": "Şifre başarıyla değiştirildi."}

        # Başarısızsa hata mesajı döner
        return {"success": False, "message": sonuc.get("message", "Şifre değiştirilemedi.")}
