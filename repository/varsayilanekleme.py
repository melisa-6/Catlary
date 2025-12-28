import hashlib
from datetime import date
from database import baglanti_olustur
from werkzeug.security import generate_password_hash

def frontend_hash_simule_et(sifre):
    return hashlib.sha256(sifre.encode('utf-8')).hexdigest()

def setup_database():
    conn = baglanti_olustur()
    cursor = conn.cursor(dictionary=True)

    try:
        print("Veritabanı tamamen sıfırlanıyor...")
        
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        tablolar = ["kitaplar", "yazarlar", "kategoriler","mailkuyrugu", "yayinevleri", "personeller", "admin", "kullanicilar", "oduncler", "cezalar"]
        for tablo in tablolar:
            cursor.execute(f"TRUNCATE TABLE {tablo}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        kategoriler = ["Roman", "Din", "Edebiyat","Çocuk","Yetişkin","Psikoloji",]
        kategori_map = {}
        for kat in kategoriler:
            cursor.execute("INSERT INTO kategoriler (kategori_adi) VALUES (%s)", (kat,))
            kategori_map[kat] = cursor.lastrowid

        yazarlar_listesi = [
            "Oğuz Atay", "Jack LONDON", "Stefen Zweig", "İmam Gazali", "Zülfü Livaneli",
            "Sabahattin Ali", "Luis Martin-Santos", "Paulo Coelho", "Joanne Greenberg",
            "Attilâ İlhan", "Jane Austen", "Fyodor Dostoyoevski", "Lev Tolstoy",
            "Yu Hua", "Charlotte Perkins Gilman", "José Saramago", "Emily Brontë"
        ]
        yazar_map = {}
        for yazar in yazarlar_listesi:
            cursor.execute("INSERT INTO yazarlar (ad) VALUES (%s)", (yazar,))
            yazar_map[yazar] = cursor.lastrowid

        yayinevleri_listesi = [
            "MaviBulut", "Modern Klasikler Dizisi", "Nesil", "Can", "YapıKredi",
            "Türkiye İş Bankası", "Sel", "METİS YAYINLARI", "Hasan Ali Yücel Klasikleri"
        ]
        yayinevi_map = {}
        for yayi in yayinevleri_listesi:
            cursor.execute("INSERT INTO yayinevleri (yayinevi_adi) VALUES (%s)", (yayi,))
            yayinevi_map[yayi] = cursor.lastrowid

        print("Kullanıcılar ekleniyor...")
        bugun = date.today()
        
        # Adminler
        hashed_admin1 = generate_password_hash(frontend_hash_simule_et('123456'))
        hashed_admin2 = generate_password_hash(frontend_hash_simule_et('1234567'))
        cursor.execute("INSERT INTO admin (username, email, password) VALUES (%s, %s, %s)", ('admin', 'infocatlary@gmail.com', hashed_admin1))
        cursor.execute("INSERT INTO admin (username, email, password) VALUES (%s, %s, %s)", ('admin2', 'admin2@catlarykutuphane.com', hashed_admin2))

        # Personeller
        hashed_pers_std = generate_password_hash(frontend_hash_simule_et('123456'))
        personeller = [
            ('Mustafa Gül', 'mustafa.gul@catlarykutuphane.com', generate_password_hash(frontend_hash_simule_et('sifrepersonel1')), bugun),
            ('Ayşe Demir', 'ayse.demir@catlarykutuphane.com', generate_password_hash(frontend_hash_simule_et('sifrepersonel2')), date(2024, 5, 20)),
            ('varsayilanpersonel', 'infocatlarykutuphane@gmail.com', hashed_pers_std, bugun)
        ]
        cursor.executemany("INSERT INTO personeller (isim, email,password, giristarihi) VALUES (%s, %s, %s, %s)", personeller)

        hashed_melisa = generate_password_hash(frontend_hash_simule_et('666666'))
        cursor.execute("INSERT INTO kullanicilar (username, email, password) VALUES (%s, %s, %s)", ('Melisa', 'taskaramelisa@gmail.com', hashed_melisa))

        print("Kitaplar yeni şemaya göre ekleniyor...")
        
        kitap_listesi = [
    (60, "Tutunamayanlar", 18, "Oğuz Atay", "Roman", "MaviBulut", 879, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSb97o4HtnPtVx58id2swXVjM02GrAoEz2GWulPLg1PgZ4NS0fFWO79ZDDT9RAtmXfxft8uvA8AXK-F6ubZ69jGxPS7S_Ulywy-2R4AA3o4DA&s=10"),
    (61, "Martin Eden", 21, "Jack LONDON", "Roman", "Modern Klasikler Dizisi", 456, "https://i.dr.com.tr/cache/600x600-0/originals/0000000608697-1.jpg"),
    (62, "Bilinmeyen bir kadinin mektubu", 25, "Stefen Zweig", "Roman", "Modern Klasikler Dizisi", 123, "https://img.kitapyurdu.com/v1/getImage/fn:11582931/wi:220/wh:85a72ad57"),
    (65, "Tehlikeli Oyunlar", 15, "Oğuz Atay", "Roman", "MaviBulut", 546, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTB1Ey2URCgGN9AMICP9mbAM-raCwB3aGr2JOtR4dOhNTh-z5up7aO3u1Eb6U55kB5JDjq4l7fBQvCp65e-r0HVcpRVDBpi-YNCa2QaYFu5xA&s=10"),
    (66, "Dil Belası", 40, "İmam Gazali", "Din", "Nesil", 245, "https://i.dr.com.tr/cache/600x600-0/originals/0002140367001-1.jpg"),
    (67, "Bekle Beni", 22, "Zülfü Livaneli", "Roman", "Can", 230, "https://m.media-amazon.com/images/I/81dh4439xEL._AC_UF350,350_QL50_.jpg"),
    (68, "Kürk Mantolu Madonna", 16, "Sabahattin Ali", "Roman", "YapıKredi", 245, "https://i.dr.com.tr/cache/600x600-0/originals/0000000058245-1.jpg"),
    (70, "Sessizlik Zamanı", 35, "Luis Martin-Santos", "Roman", "Türkiye İş Bankası", 235, "https://www.selyayincilik.com/kapaklar/opt/sessizlik-zamani.jpg"),
    (71, "Simyacı", 35, "Paulo Coelho", "Roman", "Can", 231, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRp2HyTefqpllN78mDMogSzL2oYyBIT_DvUDDkwAoiNiSGEPyJAB7d6RbO1Tkdp9ZGREw0CIsUY6CG7tHYpKXy-KJpgK2tbbRYBS8mZrRjZ&s=10"),
    (72, "Fareler ve İnsanlar", 26, "Paulo Coelho", "Roman", "Sel", 196, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR3Uak-R2aQxCBXW2_T1rzqdsuIOSTvXGW1pawN6SoFhnJUXECVqXOSqzSbK2tqW3WKrfKG3oBzArwybelpQ6mRXxWticfmiun-trhQ8w&s=10"),
    (73, "Sana Gül Bahçesi Vadetmedim", 26, "Joanne Greenberg", "Roman", "METİS YAYINLARI", 265, "https://img.kitapyurdu.com/v1/getImage/fn:11708981/wi:220/wh:f61fba353"),
    (75, "Bir Zanaatla Beklenmedik Karşılaşma", 31, "Stefen Zweig", "Roman", "Modern Klasikler Dizisi", 120, "https://img.iskultur.com.tr/webp/2021/03/Bir-Zanaatla-Beklenmedik-Karsilasma-Sert-Kapak-254x420.png"),
    (76, "Ben Sana Mecburum", 26, "Attilâ İlhan", "Edebiyat", "Türkiye İş Bankası", 245, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT3s4oUD7rWNKw0gn_A3syMaqv4n49z_dQyXzsK441KAls8NnxZ1N1g6h-5HkOJNtdzreyZ3BMafdWNBKlI3c1tjKnUE8iDdNhgWcXN7l5vHQ&s=10"),
    (77, "Gurur ve Önyargı", 45, "Jane Austen", "Roman", "Hasan Ali Yücel Klasikleri", 345, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSdvtndsysFXvp5RSB2FDKxtK42EvIunuRg_7DzaIGwOQTd0eNVrtlzvYDEnidzj_q2Z-fkrK1YNS-IUKkpnYw5yaVJkvoIe9ncGURD-Xy7Fw&s=10"),
    (78, "Suç ve Ceza", 49, "Fyodor Dostoyoevski", "Roman", "Hasan Ali Yücel Klasikleri", 687, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRT3YcpMh-NNwn5zlO9EtDYVJnxwrLJ_lbXYuGrtTovyZbDbQ5ZNCZXGS-6ikXGmm8OFfhlea2fjt4h3YBiMsqsDR1KzbrW51rGp6U1xVvL9w&s=10"),
    (79, "İnsan Ne ile Yaşar?", 13, "Lev Tolstoy", "Roman", "Hasan Ali Yücel Klasikleri", 123, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ8Pk1nGn8KE-82MlsD174gsJISm1j3RwKu4_sJFfsUoOM5qZ8Lk_P6f6ccsuUq2i__hTWtp7cJ413Ujxg2pLFaJwdfNZbux_UyezGxue_B&s=10"),
    (80, "Yaşamak", 35, "Yu Hua", "Roman", "Can", 123, "https://img.kitapyurdu.com/v1/getImage/fn:1177782/wi:220/wh:6892eba02"),
    (81, "Kadınlar Ülkesi", 22, "Charlotte Perkins Gilman", "Roman", "Modern Klasikler Dizisi", 342, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSBD_OF_kTIE34UNfozl47IH_XZTm9coo923z8VUF12FymQJnq2qFZ-PqvYXzzoGM-99kbq0v99pDVbu4BcOEXO_AqQ6Q0HPGfsLRAxLw&s=10"),
    (82, "Körlük", 24, "José Saramago", "Roman", "MaviBulut", 342, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRp2HyTefqpllN78mDMogSzL2oYyBIT_DvUDDkwAoiNiSGEPyJAB7d6RbO1Tkdp9ZGREw0CIsUY6CG7tHYpKXy-KJpgK2tbbRYBS8mZrRjZ&s=10"),
    (83, "Karışık Duygular", 19, "Stefen Zweig", "Roman", "Modern Klasikler Dizisi", 245, "https://img.iskultur.com.tr/webp/2015/06/karmasik-duygular-3.jpg"),
    (84, "Uğultulu Tepeler", 89, "Emily Brontë", "Roman", "Can", 408, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRqKkVPero9mqC7wow4lGCBRxAwtHOzAHRfdw&s")
]  

        for b_id, isim, stok, yazar_ad, kat_ad, yayi_ad, sayfa, kapak in kitap_listesi:
            raf_no = 0
            baski_yili = 2024 
            
            cursor.execute("""
                INSERT INTO kitaplar 
                (id, isim, sayfa_sayisi, stok, raf_no, baski_yili, yazar_id, kategori_id, yayinevi_id, resim)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                b_id, 
                isim, 
                sayfa, 
                stok, 
                raf_no, 
                baski_yili, 
                yazar_map[yazar_ad], 
                kategori_map[kat_ad], 
                yayinevi_map[yayi_ad], 
                kapak
            ))

        conn.commit()
    except Exception as e:
        print(f"\nHATA OLUŞTU: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_database()