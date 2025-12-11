import mysql.connector
from database import baglanti_olustur 

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
def tablolar_olustur():
    conn = baglanti_olustur()
    cursor = conn.cursor()

    # Kullanıcı tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kullanicilar (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        aktiflik BOOLEAN DEFAULT FALSE,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
    );
    """)

    # Yazarlar tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS yazarlar (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ad VARCHAR(255) NOT NULL
    );
    """)

    # Kategoriler tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kategoriler (
        id INT AUTO_INCREMENT PRIMARY KEY,
        kategori_adi VARCHAR(255) NOT NULL
    );
    """)

    # Kitaplar tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kitaplar (
        id INT AUTO_INCREMENT PRIMARY KEY,
        isim VARCHAR(255) NOT NULL,
        yazar_id INT NOT NULL,
        kategori_id INT NOT NULL,
        sayfa_sayisi INT NOT NULL,
        stok INT DEFAULT 0,
        yayinevi VARCHAR(50) NOT NULL,
        raf_no INT DEFAULT 0,
        baski_yili INT DEFAULT 0,
        
        FOREIGN KEY (yazar_id) REFERENCES yazarlar(id) ON DELETE CASCADE,
        FOREIGN KEY (kategori_id) REFERENCES kategoriler(id) ON DELETE CASCADE
    );
    """)

    # Ödünçler tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS oduncler (
        id INT AUTO_INCREMENT PRIMARY KEY,
        kullanici_id INT NOT NULL,
        kitap_id INT NOT NULL,
        odunc_tarihi DATE NOT NULL,
        gerekli_iade_tarihi DATE NULL,
        gercek_iade_tarihi DATE NULL,
        FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(id),
        FOREIGN KEY (kitap_id) REFERENCES kitaplar(id)
    );
    """)

    # Cezalar tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cezalar (
        id INT AUTO_INCREMENT PRIMARY KEY,
        kullanici_id INT NOT NULL,
        kitap_id INT NOT NULL,
        ceza_miktari DECIMAL(10,2) NOT NULL,
        odunc_tarihi DATE NOT NULL,
        iade_tarihi DATE NOT NULL,
        odeme_durumu TINYINT(1) DEFAULT 0,
        ilk_gecikme_mail_tarihi DATETIME NULL,
        son_mail_tarihi DATE NULL,
        FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(id),
        FOREIGN KEY (kitap_id) REFERENCES kitaplar(id)
    );
    """)

    # Admin tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
    );
    """)

    # Personeller tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS personeller (
        id INT AUTO_INCREMENT PRIMARY KEY,
        isim VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        giristarihi DATE NOT NULL,
        aktif BOOLEAN NOT NULL DEFAULT 1
    );
    """)

    # Mail Kuyruğu tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS MailKuyrugu (
        MailId INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
        AliciMail VARCHAR(255) NOT NULL,
        AliciAdi VARCHAR(255) NOT NULL,
        Konu VARCHAR(255) NOT NULL,
        Mesajicerigi TEXT NOT NULL,
        GonderimDurumu ENUM('Beklemede', 'Gonderiliyor', 'Gonderildi', 'Hata olustu') NOT NULL,
        BeklemedeOlusmaZamaniti TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        HataDetaylari TEXT NULL
    );
    """)

    conn.commit()
    conn.close()
    print("Tablolar başarıyla oluşturuldu.")
if __name__ == "__main__":
    conn = None
    try:
        conn = baglanti_olustur() 
        service = Veriservice(conn)
        
        print("Veritabanı sıfırlama işlemi başlatılıyor...")
        service.veri_sifirla_delete() 
        
        print("Sıfırlama ve kurulum tamamlandı.")
        
    except Exception as err:
        print(f"Kritik program hatası: {err}")
    
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("Veritabanı bağlantısı güvenle kapatıldı.")