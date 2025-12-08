
from repository.personelRepository import personelRepository
from send_mail import send_mail_to_user
from services.adminService import adminService
from services.kullaniciService import kullaniciService
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
class personelService:
    def __init__(self, db_config):
        self.repo = personelRepository(db_config)
        self.admin_service = adminService(db_config)
        self.kullanici_service = kullaniciService(db_config)

    def personel_ekle(self, ad_soyad, email, sifre, sifre_tekrar):

        if not all([ad_soyad, email, sifre, sifre_tekrar]):
            return {"success": False, "message": "Tüm alanlar doldurulmalıdır."}

        if sifre != sifre_tekrar:
            return {"success": False, "message": "Şifreler eşleşmiyor!"}
        
        if self.admin_service.repo.get_by_username(ad_soyad) or \
        self.admin_service.repo.get_by_email(email):
            return {"success": False, "message": "Bu isim veya email ADMIN tablosunda zaten kayıtlı!"}
        
        if self.repo.personel_getir_username(ad_soyad) or self.repo.get_personel_by_email(email):
            return {"success": False, "message": "Bu isim veya email PERSONEL tablosunda zaten kayıtlı!"}
        
        if self.kullanici_service.kullanici_var_mi(ad_soyad) or \
        self.kullanici_service.kullanici_email_var_mi(email):
            return {"success": False, "message": "Bu isim veya email KULLANICI tablosunda zaten kayıtlı!"}
        
        sifre_hash = generate_password_hash(sifre)
        sonuc = self.repo.personel_ekle(ad_soyad, email, sifre_hash)
        if sonuc:
            return {"success": True, "message": "Personel başarıyla eklendi!"}
        else:
            return {"success": False, "message": "Personel eklenirken hata oluştu."}


    def tum_personelleri_getir(self):
        return self.repo.tum_personelleri_getir()

    def personel_aktiflik_degistir(self, personel_id, yeni_durum):
        return self.repo.personel_aktiflik_degistir(personel_id, yeni_durum)


    def get_personel_by_email(self, email):
        personel = self.repo.get_personel_by_email(email)
            
        return personel

    def sifre_sifirla_by_email(self, personel_email):
        personel = self.repo.get_personel_by_email(personel_email)
        
        if not personel:
            return {"success": False, "message": "Bu e-posta adresine sahip personel bulunamadı."}
        yeni_sifre = ''.join(secrets.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(10))
        yeni_hash = generate_password_hash(yeni_sifre)

        personel_id = personel['id']
        guncellendi = self.repo.sifre_guncelle(personel_id, yeni_hash) 
        
        if not guncellendi:
            return {"success": False, "message": "Şifre veritabanına güncellenirken hata oluştu."}

        mail_gonderim_durumu = "başarılı"
        yeni_sifre_mesajda = f"Yeni şifre: {yeni_sifre}" 

        try:
            personel_konu = "Personel Şifre Sıfırlama"
            personel_icerik = f"Merhaba {personel['isim']},\nŞifreniz sıfırlandı. Yeni geçici şifreniz: {yeni_sifre}"
            send_mail_to_user(personel_email, personel_konu, personel_icerik) 
            admin_user = self.admin_service.repo.get_first_admin()
            if admin_user:
                admin_konu = "Personel Şifre Sıfırlama Bildirimi"
                admin_icerik = f"{personel['isim']} personelinin şifresi sıfırlanmıştır."
                send_mail_to_user(admin_user['email'], admin_konu, admin_icerik)

        except Exception as mail_err:
            mail_gonderim_durumu = f"başarısız"
            print(f"KRİTİK MAİL HATASI: {mail_err}")
            yeni_sifre_mesajda = f"Yeni şifre: {yeni_sifre}. Mail Hata Mesajı: {mail_err}"
        
        mesaj = f"Şifre başarıyla sıfırlandı. Mail gönderimi: {mail_gonderim_durumu}."
        if mail_gonderim_durumu == "başarısız":
            mesaj = f"Şifre DB'ye yazıldı, ancak mail gönderilemedi. Yönetici olarak şifreyi not alın. {yeni_sifre_mesajda}"
        return {
            "success": True, 
            "message": mesaj, 
            "yeni_sifre": yeni_sifre,
            "personel_id": personel["id"], 
            "username": personel["email"]  
        }
    def personel_sifre_degistir(self, personel_id, data):
        eski_sifre = data.get("eski_sifre")
        yeni_sifre = data.get("yeni_sifre")
        yeni_sifre_tekrar = data.get("yeni_sifre_tekrar")

        if not all([eski_sifre, yeni_sifre, yeni_sifre_tekrar]):
            return {"success": False, "message": "Tüm şifre alanları doldurulmalıdır."}

        if yeni_sifre != yeni_sifre_tekrar:
            return {"success": False, "message": "Yeni şifreler birbiriyle eşleşmiyor."}
            
        personel = self.repo.personel_getir_id(personel_id)
        
        if not personel:
            return {"success": False, "message": "Personel bulunamadı."}

        if not check_password_hash(personel['password'], eski_sifre):
            return {"success": False, "message": "Eski şifreniz hatalı. Lütfen kontrol edin."}

        yeni_hash = generate_password_hash(yeni_sifre)
        guncellendi = self.repo.sifre_guncelle(personel_id, yeni_hash) 
        if guncellendi:
            return {"success": True, "message": "Şifreniz başarıyla güncellendi!"}
        else:
            return {"success": False, "message": "Veritabanına kaydederken hata oluştu."}