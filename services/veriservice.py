import mysql.connector
from database import baglanti_olustur, tablolar_olustur 
from repository.varsayilanekleme import setup_database
class Veriservice:
    def __init__(self, conn):
        self.conn = conn
        
    def veri_sifirla_delete(self):
        cursor = self.conn.cursor()
        tablolar = ["cezalar", "oduncler", "kitaplar","kategoriler","yazarlar", "kullanicilar", "admin", "personeller","mailkuyrugu"] 
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
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;") 
            cursor.close()
    
    def setup_database():
        """Veritabanı kurulumunu tetikleyen yardımcı fonksiyon"""
        print("Veritabanı kurulumu başlatılıyor...")
        tablolar_olustur()
        print("Veritabanı kurulumu tamamlandı.")
    
    if __name__ == "__main__":
        conn = None
        veri_sifirla_delete()
        tablolar_olustur()
        setup_database