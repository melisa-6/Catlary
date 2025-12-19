import mysql.connector

class KategoriRepository:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="127.0.0.1",
            user="melisa",
            password="Mtz0504*",
            database="kutuphane_db",
            port=3306
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def tum_kategoriler(self):
        #db den tum kategorileri ceker ve dondurur
        try:
            self.cursor.execute("SELECT * FROM kategoriler")
            return self.cursor.fetchall()
        except Exception as e:
            print("Repository HATA:", e)
            return []

    def kategori_ekle(self, kategori_adi):
        try:
            query = "INSERT INTO kategoriler (kategori_adi) VALUES (%s)"
            self.cursor.execute(query, (kategori_adi,))
            self.connection.commit() 
            return True
        except Exception as e:
            print("Ekleme Hatası:", e)
            return False
    def kategori_bul(self, kategori_adi):
        sql = "SELECT * FROM kategoriler WHERE kategori_adi = %s"
        self.cursor.execute(sql, (kategori_adi,))
        return self.cursor.fetchone()

    def kategori_sil(self, id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM kategoriler WHERE id = %s", (id,))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print("Silme Hatası:", e)
            return False

    def kitap_var_mi(self, kategori_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT COUNT(*) as sayi FROM kitaplar WHERE kategori_id = %s"
            cursor.execute(query, (kategori_id,))
            sonuc = cursor.fetchone()
            cursor.close()
            return sonuc["sayi"] > 0
        except Exception as e:
            print("Kontrol Hatası:", e)
            return True
