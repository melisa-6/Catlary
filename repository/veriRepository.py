import mysql.connector
from database import baglanti_olustur 

class VeriService:
    def __init__(self, conn):
        self.conn = conn

    def veri_sifirla_delete(self):
        cursor = self.conn.cursor()
        tablolar = ["cezalar", "oduncler", "kitaplar", "kullanicilar", "admin", "personeller","mailkuyrugu"] 
        
        
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;") 
            
            for tablo in tablolar:
                cursor.execute(f"DELETE FROM {tablo}")
            
            self.conn.commit() 
            print("Tüm veriler sıfırlandı!")
            
        except mysql.connector.Error as err:
            self.conn.rollback() 
            print(f"Sıfırlama sırasında hata: {err}")
            raise
            
        finally:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;") # İlişki kontrolünü aç
            cursor.close()

if __name__ == "__main__":
    conn = None
    try:
        conn = baglanti_olustur() 
        service = VeriService(conn)
        
        print("Veritabanı sıfırlama işlemi başlatılıyor...")
        service.veri_sifirla_delete() 
        
        print("Sıfırlama ve kurulum tamamlandı.")
        
    except Exception as err:
        print(f"Kritik program hatası: {err}")
    
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("Veritabanı bağlantısı güvenle kapatıldı.")