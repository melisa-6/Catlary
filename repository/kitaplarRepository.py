import mysql.connector # mysql yerine mysql.connector kullanmak daha garantidir
import database

class kitaplarRepository:
    def __init__(self, db_config=None):
        try:
            self.conn = database.baglanti_olustur(db_config)
        except Exception as e:
            print("DB bağlantısı oluşturulamadı:", e)
            self.conn = None

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
    
    def get_by_name(self, isim):
        cursor = self.conn.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute("SELECT * FROM kitaplar WHERE isim=%s", (isim,))
            return cursor.fetchone()
        finally:
            cursor.close()
    
    def tum_kitaplari_getir(self):
        try:
            if self.conn.unread_result:
                self.conn.get_rows()
        except:
            pass

        if self.conn.is_connected():
            self.conn.commit()
            
        cursor = self.conn.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute("""
                SELECT 
                    k.id,
                    k.isim,
                    y.ad AS yazar_isim,
                    kat.kategori_adi AS kategori_isim,
                    yay.yayinevi_adi AS yayinevi_isim,
                    k.stok,
                    k.resim
                FROM kitaplar k
                LEFT JOIN yazarlar y ON k.yazar_id = y.id
                LEFT JOIN kategoriler kat ON k.kategori_id = kat.id
                LEFT JOIN yayinevleri yay ON k.yayinevi_id = yay.id
            """)
            rows = cursor.fetchall()   
            return rows               
        finally:
            cursor.close()

    def kitap_guncelle(self, kitap_id, isim,
                        sayfa_sayisi, stok, raf_no, baski_yili,  yazar_id, kategori_id,yayinevi_id, resim):

        cursor = self.conn.cursor(dictionary=True)
        try:
            sql = """
                UPDATE kitaplar
                SET isim=%s,
                    sayfa_sayisi=%s,
                    stok=%s,
                    raf_no=%s,
                    baski_yili=%s,
                    yazar_id=%s,
                    kategori_id=%s,
                    yayinevi_id=%s,
                    resim=%s
                WHERE id=%s
            """
            cursor.execute(sql, (
                isim, sayfa_sayisi,
                stok, raf_no, baski_yili,yazar_id, kategori_id,  yayinevi_id, resim, kitap_id
            ))
            self.conn.commit()
            return cursor.rowcount > 0 
        except Exception as e:
            print(f"Veritabanı Güncelleme Hatası: {e}")
            self.conn.rollback()
            return False
        finally:
            cursor.close()
            
    def kitap_ara(self, aranan_kitap):
        cursor = self.conn.cursor(dictionary=True, buffered=True)
        try:
            search_term = f"%{aranan_kitap}%"
            cursor.execute("""
                SELECT 
                    k.id,
                    k.isim,
                    y.ad AS yazar_isim,
                    kat.kategori_adi AS kategori_isim,
                    yay.yayinevi_adi AS yayinevi_isim,
                    k.stok,
                    k.resim
                FROM kitaplar k
                LEFT JOIN yazarlar y ON k.yazar_id = y.id
                LEFT JOIN kategoriler kat ON k.kategori_id = kat.id
                LEFT JOIN yayinevleri yay ON k.yayinevi_id = yay.id
                WHERE 
                    k.isim LIKE %s
                    OR y.ad LIKE %s
                    OR kat.kategori_adi LIKE %s
            """, (search_term, search_term, search_term))
            return cursor.fetchall()
        finally:
            cursor.close()


            
    def kitap_ekle(self, kitap_adi, yazar_id, kategori_id,
                sayfa_sayisi, stok, raf_no, baski_yili, yayinevi_id, resim):

        cursor = self.conn.cursor()
        try:
            query = """
                INSERT INTO kitaplar
                (isim, sayfa_sayisi, stok,raf_no,baski_yili,yazar_id,kategori_id
                , yayinevi_id, resim)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            val = (
            kitap_adi, sayfa_sayisi, stok,raf_no,baski_yili,yazar_id,kategori_id
                , yayinevi_id, resim
            )

            cursor.execute(query, val)
            self.conn.commit()
            return True

        except Exception as e:
            self.conn.rollback()
            print("KITAP EKLEME HATASI:", e)
            return False

        finally:
            cursor.close()

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
        cursor = self.conn.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute("SELECT * FROM kitaplar WHERE id=%s", (kitap_id,))
            return cursor.fetchone()
        finally:
            cursor.close()