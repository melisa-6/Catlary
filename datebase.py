import mysql.connector


# Veritabanı baglantısı olusturmak icin fonksiyon
def baglanti_olustur():
    return mysql.connector.connect(
        host="localhost",    # MySQL host
        user="melisa",         # MySQL kullanıcı adı
        password="Mtz0504*",         # MySQL şifresi
        database="kutuphane_db"  # Kullanılacak DB
    )

# Veritabanı Oluşturmak icin Fonksiyon
def db_olustur():
    conn = mysql.connector.connect(
        host="localhost",
        user="melisa",  # MySQL kullanıcı adı
        password="Mtz0504*"  # MySQL şifresi
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS kutuphane_db")
    conn.close()

# Tabloları oluşturmak fonksiyon
def tablolar_olustur():
    conn = baglanti_olustur()
    cursor = conn.cursor()

    # Kullanıcılar Tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role ENUM('kullanici','admin') NOT NULL DEFAULT 'kullanici'
        )
    """)

    # Kitaplar Tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kitaplar (
            id INT AUTO_INCREMENT PRIMARY KEY,
            isim VARCHAR(255) NOT NULL,
            yazar VARCHAR(255) NOT NULL,
            kategori VARCHAR(255),
            odunc_alindi BOOLEAN DEFAULT FALSE,
            odunc_alan_id INT NULL,
            odunc_tarihi DATE NULL,
            FOREIGN KEY (odunc_alan_id) REFERENCES kullanicilar(id)
        )
    """)

    # Ceza Tablosu
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

    conn.commit()
    conn.close()

if __name__ == "__main__":
    db_olustur()
    tablolar_olustur()
