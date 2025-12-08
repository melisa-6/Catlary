import mysql.connector
from database import baglanti_olustur 
from werkzeug.security import generate_password_hash # Kullanılmasa bile kalabilir
# from repository.varsayilanekleme import setup_database # Bu satır main'e taşınacak

# VeriService, sıfırlama mantığını içerir
class VeriService:
    def __init__(self, conn):
        self.conn = conn

    # DÜZELTİLMİŞ METOT: Sınıfın içine ve `self` ile tanımlandı.
    def veri_sifirla_delete(self):
        cursor = self.conn.cursor()
        tablolar = ["cezalar", "oduncler", "kitaplar", "kullanicilar", "admin", "personeller"] 
        # "mailkuyrugu" tablosunu bu örnekte çıkarttım, ekleyebilirsiniz.
        
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;") # İlişki kontrolünü kapat
            
            for tablo in tablolar:
                cursor.execute(f"DELETE FROM {tablo}")
                # ALTER TABLE AUTO_INCREMENT = 1 komutunu da ekleyebilirsiniz
            
            self.conn.commit() # Değişiklikleri kaydet
            print("Tüm veriler sıfırlandı!")
            
        except mysql.connector.Error as err:
            self.conn.rollback() # Hata durumunda geri al
            print(f"Sıfırlama sırasında hata: {err}")
            raise # Hatayı yukarı fırlat
            
        finally:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;") # İlişki kontrolünü aç
            cursor.close()


# __main__ BLOĞU: Akışı yöneten, global kapsamda (sınıf veya fonksiyon dışında) yer almalıdır.
if __name__ == "__main__":
    conn = None
    try:
        # 1. BAĞLANTIYI OLUŞTUR
        conn = baglanti_olustur() 
        service = VeriService(conn)
        
        # 2. SIFIRLAMA İŞLEMİNİ YAP
        print("Veritabanı sıfırlama işlemi başlatılıyor...")
        service.veri_sifirla_delete() 
        
        # 3. TABLOLARI OLUŞTUR VE VERİ EKLE
        # from tablolar import tablolar_olustur 
        # from setup import setup_database
        # tablolar_olustur(conn) 
        # setup_database(conn)
        
        print("Sıfırlama ve kurulum tamamlandı.")
        
    except Exception as err:
        # mysql.connector hatası dahil tüm hataları yakala
        print(f"Kritik program hatası: {err}")
    
    finally:
        # 4. BAĞLANTIYI GÜVENLİ KAPAT
        if conn and conn.is_connected():
            conn.close()
            print("Veritabanı bağlantısı güvenle kapatıldı.")