import hashlib
import logging
from werkzeug.security import check_password_hash, generate_password_hash
import database
from repository.kullanicilarRepository import kullanicilarRepository
from repository.AdminRepository import AdminRepository 
from send_mail import send_pending_mails, send_mail_to_user

from database import baglanti_olustur 
import secrets
import string

from db_config import db_config

class kullaniciService:
    def __init__(self, db_config=None):
        self.db_config = db_config
        self.repo = kullanicilarRepository(db_config)
        
#kullanicinin username i ile kullaniciyi almak icin repoya yonlendirir
    def get_by_username(self, username):
        return self.repo.kullanici_by_username(username)
    
#kullanicinin  email i ile kullaniciyi almak icin repoya yonlendirir
    def get_kullanici_by_email(self, email):
        return self.repo.kullanici_by_email(email)
    
    def kullanici_email_var_mi(self, email):
    #repositorydeki ilgili kısma yonlendirir
        return self.repo.kullanici_by_email(email) is not None
    
    def sifre_dogrula(self, user_data, sifre):
        if not user_data or 'password' not in user_data:
            return False
        #check_password_hash ile sifreyi kontrol eder 
        return check_password_hash(user_data['password'], sifre)
    def kullanici_var_mi(self, username):
        
    #repositorydeki ilgili kısma yonlendirir
        return self.repo.kullanici_by_username(username) is not None 
    
    def tum_kullanicilari_getir(self):
    #repositorydeki ilgili kısma yonlendirir
        return self.repo.tum_kullanicilari_getir()
    
    def kullanici_ekle(self, username, email, hashed_password):
        #kilgili parametrler ile ilgili repoya yonlendirir
        return self.repo.kullanici_ekle(username, email, hashed_password)
    
    def sifre_degistir(self, user_id, eski_sifre, yeni_sifre, yeni_sifre_tekrar):
        if yeni_sifre != yeni_sifre_tekrar:
            return {"success": False, "message": "Yeni şifreler eşleşmiyor!"}
 #kullanicinin id si ile kullaniciyi almak icin repoya yonlendirir
        user = self.repo.kullanici_by_id(user_id)
        if not user:
            return {"success": False, "message": "Kullanıcı bulunamadı!"}

        if not check_password_hash(user['password'], eski_sifre):
            return {"success": False, "message": "Eski şifre yanlış!"}
  #yeni sifreyi hashleyerek repoya yonlendirir
        yeni_hash = generate_password_hash(yeni_sifre)
        self.repo.sifre_guncelle(user_id, yeni_hash)

        return {"success": True, "message": "Şifre başarıyla değiştirildi!"}

    def kullanici_aktiflik_durumu_degistir(self, user_id):
        #gelen kullanici idsine gore mevcut aktiflik durumunu tersine çevirir
        try:
            #krepositoryden ullanici bilgilerini id ile alir
            user = self.repo.kullanici_by_id(user_id) 

            if not user:
                return {"success": False, "message": "Kullanıcı bulunamadı!"}
            #mevcut aktifligi alir
            mevcut_aktiflik = user.get('aktiflik', 1)
            #aktifse pasif pasifse aktif yapmasi gerektigini belirler 
            yeni_durum = 0 if mevcut_aktiflik == 1 else 1
            durum_mesaji = "Aktif" if yeni_durum == 1 else "Pasif"

            # Repository'e güncelleme komutunu gönderir
            guncellendi = self.repo.aktiflik_durumu_guncelle_by_id(user_id, yeni_durum) 
            
            if guncellendi:
                return {"success": True, "message": f"Kullanıcı başarıyla {durum_mesaji} hale getirildi. Yeni Durum: {yeni_durum}"}
            else:
                return {"success": False, "message": "Kullanıcı durumu güncellenirken bir veritabanı hatası oluştu."}
        
        except Exception as e:
            # Beklenmedik veritabanı veya sunucu hatası olursa
            print(f"Kullanıcı aktiflik durumu değiştirme hatası: {e}")
            return {"success": False, "message": "Durum değiştirme sırasında beklenmedik bir hata oluştu."}
            
    def get_kullanici_by_id(self, user_id):
        #reponun ilgili fonksiyonuna yonlendirir
        return self.repo.kullanici_by_id(user_id)

    def sifre_sifirla_by_user(self, user):
        # Kullanıcıya mail ile gönderilecek olan Rastgele 10 karakterlik yeni şifre oluştur

        yeni_sifre = ''.join(secrets.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(10))
        
        # Yeni şifreyi önce SHA256 ile hashliyoruz
        simule_edilmis_hash = hashlib.sha256(yeni_sifre.encode('utf-8')).hexdigest()
        
        # SHA256 ile hashlenen şifreyi tekrar daha güvenli hale getirmek için
        # generate_password_hash fonksiyonuyla ikinci bir hash üretiyoruz
        yeni_db_hash = generate_password_hash(simule_edilmis_hash)

        # Daha sonra veritabanında şifreyi güncelliyoruz
        guncellendi = self.repo.sifre_guncelle(user['id'], yeni_db_hash)
        
        # Güncelleme başarısız olursa hata döndürülüyor
        if not guncellendi:
            return {"success": False, "message": "Şifre veritabanına güncellenemedi."}

        # Kullanıcıya yeni şifre mail ile gönderiliyor
        konu = "Şifre Sıfırlama"
        icerik = f"Merhaba {user['username']},\nYeni şifreniz: {yeni_sifre}"
        send_mail_to_user(user['email'], konu, icerik)
        
        # Admin'e bildirim maili gönderiliyor 
        admin_repo = AdminRepository(self.db_config)
        admin_user = admin_repo.get_first_admin()
        if admin_user:
            admin_konu = "Kullanıcı Şifre Sıfırlama Bildirimi"
            admin_icerik = f"{user['username']} kullanıcısının şifresi sıfırlanmıştır."
            send_mail_to_user(admin_user['email'], admin_konu, admin_icerik)

        # İşlem başarılı ise yeni şifre geri döndürülüyor
        return {
            "success": True, 
            "message": f"Kullanıcının şifresi sıfırlandı: {user['email']}", 
            "yeni_sifre": yeni_sifre
        }

   
    def kayit_ol(self, username: str, email: str, sifre: str, sifre_tekrar: str) -> dict:
      #aldigi parametreler ile her zaman dict dondurur
        # gelen sifrelerin eslesip eslesmedigini kontrol eder
        if sifre != sifre_tekrar:
            return {
                "success": False, 
                "message": "Şifreler eşleşmiyor. Lütfen tekrar kontrol edin."
            }
        admin_repo = AdminRepository(self.db_config)
        # kullanıcı tablosunda ayni username ya da mailden bir kullanıccı daha var mı kontrol eder 
        kullanici_username_var = self.repo.kullanici_by_username(username)
        kullanici_email_var = self.repo.kullanici_by_email(email)
        # admin tablosunda ayni username ya da mailden bir kullanıccı daha var mı kontrol eder 
        admin_username_var = admin_repo.get_by_username(username) 
        admin_email_var = admin_repo.get_by_email(email)
        if kullanici_username_var or admin_username_var:
            return {
                "success": False, 
                "message": f"'{username}' kullanıcı adı zaten kullanımda."
            }
        
        if kullanici_email_var or admin_email_var:
            return {
                "success": False, 
                "message": f"'{email}' e-posta adresi zaten kullanımda."
            }
        try:
            # gelen sifreyi hashler
            hashed_sifre = generate_password_hash(sifre)
            #repository e eklemesi icin gonderir
            eklendi = self.repo.kullanici_ekle(username, email, hashed_sifre)
            #eklenip eklenmemesine gore de mesaj dondurur
            if eklendi:
                return {
                    "success": True, 
                    "message": "Tebrikler! Kayıt işleminiz başarıyla tamamlandı."
                }
            else:
                return {
                    "success": False, 
                    "message": "Kayıt sırasında veritabanı hatası oluştu. Lütfen tekrar deneyin."
                }
                
        except Exception as e:
            return {
                "success": False, 
                "message": "Kayıt sırasında beklenmeyen bir hata oluştu. Lütfen daha sonra tekrar deneyin."
            }