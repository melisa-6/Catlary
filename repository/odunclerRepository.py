import mysql
import database
class odunclerRepository:
    def __init__(self, db_config):
        self.db_config = db_config  
        try:
            self.conn = database.baglanti_olustur(db_config)
        except Exception as e:
            print("DB bağlantısı oluşturulamadı:", e)
            self.conn = None

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def _get_conn(self):

        return database.baglanti_olustur(self.db_config)

    
    def odunc_ver(self, kullanici_id, kitap_id, odunc_tarihi, gerekli_iade_tarihi):
        conn = self._get_conn()
        cursor = conn.cursor(dictionary=True)
        try:
            # Kitap veritabanında var mı ve stok yeterli mi kontrolu
            cursor.execute("SELECT stok FROM kitaplar WHERE id=%s", (kitap_id,))
            kitap = cursor.fetchone()
            if not kitap:
                return {"success": False, "message": "Kitap veritabanında bulunamadı."}

            # Eğer stok 0 veya altındaysa ödünç verilemez
            if kitap["stok"] <= 0:
                return {"success": False, "message": "Bu kitabın stokta yeterli miktarı yok."}

            # Kullanıcı veritabanında var mı ve aktif mi kontrolu
            cursor.execute("SELECT aktiflik FROM kullanicilar WHERE id=%s", (kullanici_id,))
            kullanici = cursor.fetchone()
            if not kullanici:
                return {"success": False, "message": "Kullanıcı veritabanında bulunamadı."}

            # aktiflik = 0 ise kullanıcı pasif demektir işlem iptal olur
            if kullanici["aktiflik"] == 0:
                return {"success": False, "message": "Kullanıcı pasif durumda."}

            # Eğer aktif ödünç sayısı 5’ten fazlaysa yeni kitap verilemez
            cursor.execute("""
                SELECT COUNT(*) AS kitap_sayisi 
                FROM oduncler 
                WHERE kullanici_id=%s AND gercek_iade_tarihi IS NULL
            """, (kullanici_id,))
            if cursor.fetchone()["kitap_sayisi"] >= 5:
                return {"success": False, "message": "Kullanıcının elinde zaten 5 kitap var."}

            # Kullanıcı aynı kitabı teslim etmeden tekrar alamaz
            cursor.execute("""
                SELECT COUNT(*) AS ayni_kitap 
                FROM oduncler 
                WHERE kullanici_id=%s AND kitap_id=%s AND gercek_iade_tarihi IS NULL
            """, (kullanici_id, kitap_id))
            if cursor.fetchone()["ayni_kitap"] > 0:
                return {"success": False, "message": "Kullanıcı bu kitaptan zaten ödünç aldı."}

            # Bütün kontroller geçtiyse ödünç kaydı oluşturulur
            cursor.execute("""
    INSERT INTO oduncler (kullanici_id, kitap_id, odunc_tarihi, gerekli_iade_tarihi, gercek_iade_tarihi)
    VALUES (%s, %s, %s, %s, %s)
""", (kullanici_id, kitap_id, odunc_tarihi, gerekli_iade_tarihi, None))

            # Eklenen kaydın ID'sini al
            odunc_id = cursor.lastrowid

            # Veritabanına işlemleri kaydet
            conn.commit()

            # Başarılı yanıt döndür
            return {
                "success": True,
                "message": "Kitap başarıyla ödünç verildi.",
                "odunc_id": odunc_id,
            }

        except Exception as e:
            # Herhangi bir hata olursa işlemi geri alır
            conn.rollback()
            return {"success": False, "message": f"Hata oluştu: {e}"}

        finally:
            cursor.close()
            conn.close()

            
    def odunc_iade(self, odunc_id, gercek_iade_tarihi):
      cursor = self.conn.cursor(dictionary=True)
      try:
        # Ödünç kaydını kontrol et
        cursor.execute("SELECT * FROM oduncler WHERE id=%s", (odunc_id,))
        odunc = cursor.fetchone()

        if not odunc:
            return "Geçersiz ödünç ID."
            
        #  İade edilip edilmediğini kontrol et
        if odunc['gercek_iade_tarihi'] is not None:
            return "Bu ödünç zaten iade edilmiş!"
            
        # Kitabı iade eder
        cursor.execute(
            "UPDATE oduncler SET gercek_iade_tarihi = %s WHERE id = %s",
            (gercek_iade_tarihi, odunc_id)
        )
        
        # Değişiklikleri kaydet
        self.conn.commit()
        
        #  Başarılı mesajı döndür
        return f"Ödünç ID: {odunc_id} başarıyla iade edildi."

      except Exception as e:
        self.conn.rollback()
        return f"İade işlemi hatası: {e}" 
        
      finally:
        cursor.close()
        
    def cezanin_iade_edilmis_olup_olmadigini_kontrol_et(self, ceza_id):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                SELECT iade_tarihi
                FROM cezalar
                WHERE id=%s
            """
            cursor.execute(query, (ceza_id,))
            result = cursor.fetchone()
            
            return result is not None and result.get('iade_tarihi') is not None
        finally:
            cursor.close()
            conn.close()
   #odunc id nin olup olmadigini ceker
    def get_odunc_by_id(self, odunc_id):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM oduncler WHERE id=%s", (odunc_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    #kullanicinin kitabi aktif olarak odunc alıp almadigini kontrol eder
    def kitap_oduncte_mi_kullaniciye(self, kitap_id, kullanici_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM oduncler WHERE kitap_id=%s AND kullanici_id=%s AND gercek_iade_tarihi IS NULL",
                (kitap_id, kullanici_id)
            )
            return cursor.fetchone()[0] > 0
        finally:
            cursor.close()

   #kullanicinin toplam iade edilmemis kitaplarinin sayisini kontrol eder
    def aktif_odunc_sayisi(self, kullanici_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM oduncler WHERE kullanici_id=%s AND gercek_iade_tarihi IS NULL",
                (kullanici_id,)
            )
            return cursor.fetchone()[0]
        finally:
            cursor.close()

    #kitap oduncte mi kontrol eder
    def kitap_oduncte_mi(self, kitap_id):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM oduncler WHERE kitap_id=%s",
                (kitap_id,)
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()

#kullanicinin odunc gecmisini getirir   
    def kullanici_odunc_gecmisi_getir(self, kullanici_id):
        
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
                SELECT o.id, k.isim AS kitap_adi, o.odunc_tarihi, o.gerekli_iade_tarihi, o.gercek_iade_tarihi
                FROM oduncler o
                JOIN kitaplar k ON o.kitap_id = k.id
                WHERE o.kullanici_id=%s
                ORDER BY o.odunc_tarihi DESC
            """, (kullanici_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
    def tum_kullanici_odunc_gecmisi_getir(self):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    o.id,
                    u.username,
                    k.isim AS kitap_adi,
                    o.odunc_tarihi,
                    o.gerekli_iade_tarihi,
                    o.gercek_iade_tarihi,
                    k.resim AS kapak_url     
                FROM oduncler o
                LEFT JOIN kullanicilar u ON o.kullanici_id = u.id
                LEFT JOIN kitaplar k ON o.kitap_id = k.id
                ORDER BY o.id DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"SQL Hatası oluştu: {e}")
            return []
        finally:
            cursor.close()
            conn.close()


    def kullanici_aktif_odunc_detaylari_getir_repo(self, kullanici_id):
       
        conn = self._get_conn()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    o.id, o.kitap_id, o.odunc_tarihi, o.gerekli_iade_tarihi
                FROM 
                    oduncler o
                WHERE 
                    o.kullanici_id=%s AND o.gercek_iade_tarihi IS NULL
                """, (kullanici_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    def cezalar_odendi_yap_repo(self, kullanici_id):
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            query = """
                UPDATE cezalar
                SET odeme_durumu = 1
                WHERE kullanici_id = %s AND odeme_durumu = 0
            """

            cursor.execute(query, (kullanici_id,))
            conn.commit()

            return True

        except Exception as e:
            conn.rollback()
            print("Repo hata (cezalar_odendi_yap_repo):", e)
            return False

        finally:
            cursor.close()
            conn.close()

    def kullanici_odenecek_cezalarini_getir_repo(self, kullanici_id):
       
        conn = self._get_conn()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
    id AS ceza_id,         
    ceza_miktari, 
    odunc_tarihi 
                FROM 
                    cezalar 
                WHERE 
                    kullanici_id=%s AND odeme_durumu=0
                """, (kullanici_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    def get_kullanici_id_by_username_repo(self,username):
        conn = self._get_conn()
        cursor = conn.cursor()
        kullanici_id = None
        
        try:
            cursor.execute("SELECT id FROM kullanicilar WHERE username = %s", (username,))
            result = cursor.fetchone()
            
            if result:
                kullanici_id = result[0] 
                
        except Exception as e:
            print(f"Kullanıcı ID çekilirken hata oluştu: {e}")
        finally:
            cursor.close()
            conn.close()
            
        return kullanici_id
    def get_odunc_by_id(self, odunc_id):
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM oduncler WHERE id=%s", (odunc_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
            