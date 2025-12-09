import mysql.connector
from werkzeug.security import generate_password_hash
from datetime import date 

def baglanti_olustur(db_config=None):
    cfg = db_config or {
        "host": "localhost",
        "user": "melisa",
        "password": "Mtz0504*",
        "database": "kutuphane_db"
    }    
    
    return mysql.connector.connect(
        host=cfg["host"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"]
    )

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

    # Kitaplar tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kitaplar (
        id INT AUTO_INCREMENT PRIMARY KEY,
        isim VARCHAR(255) NOT NULL,
        yazar VARCHAR(255) NOT NULL,
        kategori SET('Roman','Bilim','Tarih','Felsefe','Macera','Korku','Fantastik') DEFAULT 'Roman',
        sayfa_sayisi INT NOT NULL,
        stok INT DEFAULT 0,
        yayinevi VARCHAR(50) NOT NULL,
        raf_no INT DEFAULT 0,
        baski_yili INT DEFAULT 0
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
    print("Tablolar oluşturuldu.")
