from datetime import date
from services.veriservice import Veriservice
from database import baglanti_olustur
from werkzeug.security import generate_password_hash

def setup_database():
    conn = baglanti_olustur()
    cursor = conn.cursor()
    service = Veriservice(conn)

    try:
        # Varsayılan şifreler 
        hashed1 = generate_password_hash('123456')
        hashed2 = generate_password_hash('1234567')
        personel1_sifre_hash = generate_password_hash('sifrepersonel1')
        personel2_sifre_hash = generate_password_hash('sifrepersonel2')
        kullanici_sifre = generate_password_hash('666666')
        bugunun_tarihi = date.today()

        cursor.execute("INSERT INTO yazarlar (ad) VALUES (%s)", ("Fyodor Dostoyevski",))
        cursor.execute("INSERT INTO yazarlar (ad) VALUES (%s)", ("J. K. Rowling",))

        cursor.execute("INSERT INTO kategoriler (kategori_adi) VALUES (%s)", ("Roman",))
        cursor.execute("INSERT INTO kategoriler (kategori_adi) VALUES (%s)", ("Fantastik",))

        cursor.execute("""
        INSERT INTO personeller (isim, email, password, giristarihi)
        VALUES (%s, %s, %s, %s)
        """, ('Mustafa Gül', 'mustafa.gul@catlarykutuphane.com', personel1_sifre_hash, bugunun_tarihi))

        cursor.execute("""
        INSERT INTO personeller (isim, email, password, giristarihi)
        VALUES (%s, %s, %s, %s)
        """, ('Ayşe Demir', 'ayse.demir@catlarykutuphane.com', personel2_sifre_hash, '2024-05-20'))

        cursor.execute("""
        INSERT INTO admin (username, email, password)
        VALUES (%s, %s, %s)
        """, ('admin', 'infocatlary@gmail.com', hashed1))

        cursor.execute("""
        INSERT INTO admin (username, email, password)
        VALUES (%s, %s, %s)
        """, ('admin2', 'admin2@catlarykutuphane.com', hashed2))

        cursor.execute("""
        INSERT INTO kullanicilar (username, email, password)
        VALUES (%s, %s, %s)
        """, ('Melisa', 'taskaramelisa@gmail.com', kullanici_sifre))

        # Commit
        conn.commit()
        print("Varsayılan veriler başarıyla eklendi!")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    setup_database()
