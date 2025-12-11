

import mysql
import database

class kitaplarRepository:
    def __init__(self, db_config=None):
        try:
            self.conn = database.baglanti_olustur(db_config)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print("DB bağlantısı oluşturulamadı:", e)
            self.conn = None

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
   
    def get_by_name(self, isim):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM kitaplar WHERE isim=%s", (isim,))
        return cursor.fetchone()
    
    # Tüm kitapları getirir
    def tum_kitaplari_getir(self):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    k.id,
                    k.isim,
                    y.ad AS yazar_isim,
                    kat.kategori_adi AS kategori_isim,
                    k.stok
                FROM kitaplar k
                LEFT JOIN yazarlar y ON k.yazar_id = y.id
                LEFT JOIN kategoriler kat ON k.kategori_id = kat.id
            """)

            rows = cursor.fetchall()   
            return rows               

        finally:
            cursor.close()          
    def kitap_ara(self, aranan_kitap):
        cursor = self.conn.cursor(dictionary=True)
        try:
            search_term = f"%{aranan_kitap}%"
            cursor.execute("""
                SELECT * FROM kitaplar
                WHERE isim LIKE %s OR yazar LIKE %s OR kategori LIKE %s
            """, (search_term, search_term, search_term))
            return cursor.fetchall()
        finally:
            cursor.close()
    def kitap_ekle(self, kitap_adi, yazar_id, kategori_id, sayfa_sayisi, stok, raf_no, baski_yili, yayinevi):


        try:
            query = """
                INSERT INTO kitaplar 
                (isim, yazar_id, kategori_id, sayfa_sayisi, stok, raf_no, baski_yili, yayinevi)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            val = (kitap_adi, yazar_id, kategori_id, sayfa_sayisi, stok, raf_no, baski_yili, yayinevi)
            self.cursor.execute(query, val)
            self.conn.commit()

        except Exception as e:
            print("!!! HATA OLUŞTU !!!")
            print(f"HATA DETAYI: {e}")
            return False

        finally:
            print("--------------------------------------------------")

    def kitap_sil_db_islemi(self, kitap_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM kitaplar WHERE id=%s", (kitap_id,))
            self.conn.commit()
            if cursor.rowcount == 0:
                return f"Kitap ID {kitap_id} bulunamadı veya silinmiş.", None
            return f"Kitap başarıyla silindi. (ID: {kitap_id})", True
        except mysql.connector.Error as e:
            self.conn.rollback()
            if e.errno == 1451:
                return "Bu kitap ödünç kayıtları içerdiği için silinemiyor.", None
            return f"Veritabanı Hatası: {e.msg}", None
        finally:
            cursor.close()


    def get_by_id(self, kitap_id):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM kitaplar WHERE id=%s", (kitap_id,))
            return cursor.fetchone()
        finally:
            cursor.close()