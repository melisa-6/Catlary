import mysql.connector
from werkzeug.security import generate_password_hash

#Veritabanı bağlantısı oluşturmak
def baglanti_olustur():
    return mysql.connector.connect(
        host="localhost",
        user="melisa",
        password="Mtz0504*",
        database="kutuphane_db"
    )

# Veritabanını silmek
def db_sil():
    conn = mysql.connector.connect(
        host="localhost",
        user="melisa",
        password="Mtz0504*"
    )
    cursor = conn.cursor()
    cursor.execute("DROP DATABASE IF EXISTS kutuphane_db")
    conn.close()

# Veritabanını oluşturmak
def db_olustur():
    conn = mysql.connector.connect(
        host="localhost",
        user="melisa",
        password="Mtz0504*"
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS kutuphane_db")
    conn.close()
def tablolar_olustur():
    conn = baglanti_olustur()
    cursor = conn.cursor()

    # Kullanıcı tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kullanicilar (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
    )
    """)

    # Admin tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
    )
    """)

    # Kitaplar tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kitaplar (
        id INT AUTO_INCREMENT PRIMARY KEY,
        isim VARCHAR(255) NOT NULL,
        yazar VARCHAR(255) NOT NULL,
        kategori VARCHAR(255),
        sayfa_sayisi INT NOT NULL,
        stok INT DEFAULT 0,
        raf_no INT DEFAULT 0,
        baski_yili INT DEFAULT 0
    )
    """)

    # Ödünç tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS oduncler (
        id INT AUTO_INCREMENT PRIMARY KEY,
        kullanici_id INT NOT NULL,
        kitap_id INT NOT NULL,
        odunc_tarihi DATE NOT NULL,
        gerekli_iade_tarihi DATE,
        gercek_iade_tarihi DATE,
        FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(id),
        FOREIGN KEY (kitap_id) REFERENCES kitaplar(id)
    )
    """)

    # Ceza tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cezalar (
        id INT AUTO_INCREMENT PRIMARY KEY,
        kullanici_id INT NOT NULL,
        kitap_id INT NOT NULL,
        ceza_miktari DECIMAL(10,2) NOT NULL,
        odunc_tarihi DATE NOT NULL,
        iade_tarihi DATE NOT NULL,
        FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(id),
        FOREIGN KEY (kitap_id) REFERENCES kitaplar(id)
    )
    """)

    # Varsayılan admin eklemek (kütüphane e-postası)
    hashed1 = generate_password_hash('123456')
    hashed2 = generate_password_hash('1234567')

    cursor.execute("""
    INSERT IGNORE INTO admin (username, email, password)
    VALUES ('admin', 'info@catlarykutuphane.com', %s)
    """, (hashed1,))

    cursor.execute("""
    INSERT IGNORE INTO admin (username, email, password)
    VALUES ('admin2', 'admin2@catlarykutuphane.com', %s)
    """, (hashed2,))
    
    cursor.execute("""
INSERT IGNORE INTO kullanicilar (username, email, password)
VALUES ('Melisa', 'taskaramelisa@gmail.com', %s)
""", (generate_password_hash('666666'),))
    cursor.execute("""
    INSERT IGNORE INTO kitaplar (isim, yazar, kategori, sayfa_sayisi, stok, raf_no, baski_yili)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, ("Tutunamayanlar", "Oğuz Atay", "Roman", 540, 5, 1, 1971))

    conn.commit()
    conn.close()
