import mysql.connector
from database import baglanti_olustur, tablolar_olustur
from repository.varsayilanekleme import setup_database as varsayilan_veriler_ekle
from db_config import db_config
class Veriservice:
    def __init__(self, conn):
        self.conn = conn

    def veri_sifirla_delete(self):
        cursor = self.conn.cursor()
        tablolar = ["cezalar", "oduncler", "kitaplar","kategoriler","yazarlar",
                    "kullanicilar", "yayinevleri","admin", "personeller","mailkuyrugu"] 
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

    def setup_database(self):
        # Tabloları sıfırla
        self.veri_sifirla_delete()
        # Tabloları oluştur
        print("Veritabanı tabloları oluşturuluyor...")
        tablolar_olustur()
        #  Varsayılan verileri ekle
        print("Varsayılan veriler ekleniyor...")
        varsayilan_veriler_ekle()
        print("Veritabanı kurulumu tamamlandı.")
    
if __name__ == "__main__":
    conn = baglanti_olustur(db_config)
    veri_service = Veriservice(conn)
    veri_service.setup_database()  # hem sıfırlama hem tablo oluşturma
    conn.close()
