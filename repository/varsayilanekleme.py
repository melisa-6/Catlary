import hashlib
from datetime import date
from database import baglanti_olustur
from werkzeug.security import generate_password_hash


def frontend_hash_simule_et(sifre):
    return hashlib.sha256(sifre.encode('utf-8')).hexdigest()

def setup_database():
    conn = baglanti_olustur()
    cursor = conn.cursor()

    try:
        print("Varsayılan veriler hazırlanıyor...")

        sifre_admin1 = frontend_hash_simule_et('123456')
        hashed_admin1 = generate_password_hash(sifre_admin1)

        sifre_admin2 = frontend_hash_simule_et('1234567')
        hashed_admin2 = generate_password_hash(sifre_admin2)


        sifre_pers1 = frontend_hash_simule_et('sifrepersonel1')
        hashed_pers1 = generate_password_hash(sifre_pers1)

        
        sifre_pers2 = frontend_hash_simule_et('sifrepersonel2')
        hashed_pers2 = generate_password_hash(sifre_pers2)

        
        sifre_kullanici = frontend_hash_simule_et('666666')
        hashed_kullanici = generate_password_hash(sifre_kullanici)
        
        bugunun_tarihi = date.today()

        cursor.execute("INSERT INTO yazarlar (ad) VALUES (%s)", ("Fyodor Dostoyevski",))
        cursor.execute("INSERT INTO yazarlar (ad) VALUES (%s)", ("J. K. Rowling",))


        cursor.execute("INSERT INTO kategoriler (kategori_adi) VALUES (%s)", ("Roman",))
        cursor.execute("INSERT INTO kategoriler (kategori_adi) VALUES (%s)", ("Fantastik",))

        
        cursor.execute("""
        INSERT INTO personeller (isim, email, password, giristarihi)
        VALUES (%s, %s, %s, %s)
        """, ('Mustafa Gül', 'mustafa.gul@catlarykutuphane.com', hashed_pers1, bugunun_tarihi))

        cursor.execute("""
        INSERT INTO personeller (isim, email, password, giristarihi)
        VALUES (%s, %s, %s, %s)
        """, ('Ayşe Demir', 'ayse.demir@catlarykutuphane.com', hashed_pers2, '2024-05-20'))

        
        cursor.execute("""
        INSERT INTO admin (username, email, password)
        VALUES (%s, %s, %s)
        """, ('admin', 'infocatlary@gmail.com', hashed_admin1))

        cursor.execute("""
        INSERT INTO admin (username, email, password)
        VALUES (%s, %s, %s)
        """, ('admin2', 'admin2@catlarykutuphane.com', hashed_admin2))

    
        cursor.execute("""
        INSERT INTO kullanicilar (username, email, password)
        VALUES (%s, %s, %s)
        """, ('Melisa', 'taskaramelisa@gmail.com', hashed_kullanici))

        
        conn.commit()
        print("Varsayılan veriler başarıyla eklendi!")

    except Exception as e:
        print(f"Hata oluştu: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_database()