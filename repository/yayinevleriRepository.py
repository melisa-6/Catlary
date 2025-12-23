import mysql.connector

class YayinevleriRepository:
    def __init__(self, db_config):
        self.db_config = db_config
        self.baglanti_kur()

    def baglanti_kur(self):
        if not hasattr(self, 'connection') or not self.connection.is_connected():
            self.connection = mysql.connector.connect(**self.db_config)

    def tum_yayinevleri(self):
        try:
            self.baglanti_kur()
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM yayinevleri ORDER BY id DESC")
            sonuc = cursor.fetchall()
            cursor.close()
            return sonuc
        except Exception as e:
            print("Repository HATA (Listeleme):", e)
            return []

    def yayinevi_bul_isme_gore(self, ad):
        try:
            self.baglanti_kur()
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT * FROM yayinevleri WHERE yayinevi_adi = %s"
            cursor.execute(query, (ad,))
            kayit = cursor.fetchone()
            cursor.close()
            return kayit
        except Exception as e:
            print("Repository HATA (Bulma):", e)
            return None

    def yayinevi_ekle(self, ad):
        try:
            self.baglanti_kur()
            cursor = self.connection.cursor()
            query = "INSERT INTO yayinevleri (yayinevi_adi) VALUES (%s)"
            cursor.execute(query, (ad,))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print("Repository HATA (Ekleme):", e)
            raise e 

    def yayinevi_sil(self, id):
        try:
            self.baglanti_kur()
            cursor = self.connection.cursor()
            query = "DELETE FROM yayinevleri WHERE id = %s"
            cursor.execute(query, (id,))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print("Repository HATA (Silme):", e)
            raise e
    
    def yayinevine_ait_kitap_sayisi(self, yayinevi_id):
        try:
            self.baglanti_kur()
            cursor = self.connection.cursor()
            sql_sorgusu = "SELECT COUNT(*) FROM kitaplar WHERE yayinevi_id = %s"
            cursor.execute(sql_sorgusu, (yayinevi_id,))
            
            sonuc = cursor.fetchone() 
            sayi = sonuc[0]
            
            cursor.close()
            return sayi
        except Exception as e:
            print("Hata:", e)
            return 0
    
    def isme_gore_getir(self, ad):
        try:
            self.baglanti_kur()
            cursor = self.connection.cursor(dictionary=True)
            
            query = "SELECT * FROM yayinevleri WHERE yayinevi_adi = %s"
            cursor.execute(query, (ad.strip(),)) 
            
            kayit = cursor.fetchone()
            cursor.close()
            
            return kayit 
        except Exception as e:
            print("Repo Hata (İsim Kontrol):", e)
            return None