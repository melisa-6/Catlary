import mysql.connector

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

# Tabloları oluşturmak
def tablolar_olustur():
    conn = baglanti_olustur()
    cursor = conn.cursor()

    # Kullanıcı tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)

    #  Admin tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)

    #  Kitaplar tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kitaplar (
            id INT AUTO_INCREMENT PRIMARY KEY,
            isim VARCHAR(255) NOT NULL,
            yazar VARCHAR(255) NOT NULL,
            kategori VARCHAR(255),
            stok INT DEFAULT 0
        )
    """)

    #  Ödünç tablosu (kimin hangi kitabı aldığı)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS oduncler (
            id INT AUTO_INCREMENT PRIMARY KEY,
            kullanici_id INT NOT NULL,
            kitap_id INT NOT NULL,
            odunc_tarihi DATE NOT NULL,
            iade_tarihi DATE,
            FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(id),
            FOREIGN KEY (kitap_id) REFERENCES kitaplar(id)
        )
    """)

    #  Ceza tablosu
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

    # kontroller için Varsayılan admin eklemek 
    cursor.execute("""
        INSERT IGNORE INTO admin (username, password)
        VALUES ('admin', '1234')
    """)

    conn.commit()
    conn.close()
