import mysql.connector

from database import baglanti_olustur

class YazarRepository:
    def __init__(self):
        self.conn = baglanti_olustur()

    def tum_yazarlar(self):
        #yazarlar tablosundan tum yazarları ceker
        try:
            cursor = self.conn.cursor(dictionary=True)
            #sonucları dict formatında dondurmesi icin 
            cursor.execute("SELECT * FROM yazarlar")
            sonuc = cursor.fetchall()
            cursor.close()
            return sonuc
        except Exception as e:
            print("Repository HATA:", e)
            return []

    def yazar_bul(self, ad):
        try:
            cursor = self.conn.cursor(dictionary=True)
            sql = "SELECT * FROM yazarlar WHERE ad = %s"
            cursor.execute(sql, (ad,))
            sonuc = cursor.fetchone()
            cursor.close()
            return sonuc
        except Exception as e:
            print("Yazar Bul Hatası:", e)
            return None

    def yazar_ekle(self, yazar_adi):
        try:
            cursor = self.conn.cursor()
            query = "INSERT INTO yazarlar (ad) VALUES (%s)"
            cursor.execute(query, (yazar_adi,))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print("Ekleme Hatası:", e)
            return False

    def yazar_sil(self, id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM yazarlar WHERE id = %s", (id,))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print("Silme Hatası:", e)
            return False

    def kitap_var_mi(self, yazar_id):
        try:
            cursor = self.conn.cursor(dictionary=True)
            query = "SELECT COUNT(*) AS sayi FROM kitaplar WHERE yazar_id = %s"
            cursor.execute(query, (yazar_id,))
            sonuc = cursor.fetchone()
            cursor.close()
            if sonuc is None:
                return True  
            return int(sonuc.get("sayi", 0)) > 0
        except Exception as e:
            print("Kontrol Hatası:", e)
            return True  
