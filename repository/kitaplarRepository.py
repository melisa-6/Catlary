
import database

class KitaplarRepository:
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
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM kitaplar WHERE isim=%s", (isim,))
        return cursor.fetchone()
    
    #tum kitaplari getirir
    def tum_kitaplari_getir(self):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM kitaplar")
            return cursor.fetchall()
        finally:
            cursor.close()

    #parametre gelen kitabi arar
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

    #parametre gelen bilgileri alarak kitabi ekler
    def kitap_ekle(self, isim, yazar, kategori, yayinevi, sayfa_sayisi, stok, raf_no, baski_yili):
        cursor = self.conn.cursor(buffered=True)
        try:
            cursor.execute(
                "SELECT * FROM kitaplar WHERE isim=%s AND yayinevi=%s",
                (isim, yayinevi)
            )
            mevcut = cursor.fetchone()
            if mevcut:
                return f"Bu kitap zaten ekli! (ID: {mevcut[0]})", mevcut[0]

            cursor.execute(
                "INSERT INTO kitaplar (isim, yazar, kategori, sayfa_sayisi, stok, raf_no, baski_yili, yayinevi) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (isim, yazar, kategori, sayfa_sayisi, stok, raf_no, baski_yili, yayinevi)
            )
            self.conn.commit()
            return f"Kitap başarıyla eklendi! (ID: {cursor.lastrowid})", cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            return f"Hata oluştu: {str(e)}", None
        finally:
            cursor.close()


    #parametre gelen id ile kitabi siler
    def kitap_sil_by_id(self, kitap_id):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM kitaplar WHERE id=%s", (kitap_id,))
            kitap = cursor.fetchone()
            if not kitap:
                return f"Kitap bulunamadi: ID {kitap_id}", None

            cursor.execute("DELETE FROM kitaplar WHERE id=%s", (kitap_id,))
            self.conn.commit()
            return f"Kitap basariyla silindi! (ID: {kitap_id})", kitap
        except Exception as e:
            self.conn.rollback()
            return f"Hata olustu: {str(e)}", None
        finally:
            cursor.close()
    def get_by_id(self, kitap_id):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM kitaplar WHERE id=%s", (kitap_id,))
            return cursor.fetchone()
        finally:
            cursor.close()