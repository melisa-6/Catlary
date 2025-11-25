import database

class OduncRepository:
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
            # Kitap var mı ve stokta mı kontrolu
            cursor.execute("SELECT stok FROM kitaplar WHERE id=%s", (kitap_id,))
            kitap = cursor.fetchone()
            if not kitap:
                return {"success": False, "message": "Kitap veritabanında bulunamadı."}
            if kitap["stok"] <= 0:
                return {"success": False, "message": "Bu kitabın stokta yeterli miktarı yok."}

            # Kullanıcı var mı ve aktif mi kontrolu
            cursor.execute("SELECT aktiflik FROM kullanicilar WHERE id=%s", (kullanici_id,))
            kullanici = cursor.fetchone()
            if not kullanici:
                return {"success": False, "message": "Kullanıcı veritabanında bulunamadı."}
            if kullanici["aktiflik"] == 0:
                return {"success": False, "message": "Kullanıcı pasif durumda."}

            # Aktif ödünç sayısı kontrolu
            cursor.execute("""
                SELECT COUNT(*) AS kitap_sayisi 
                FROM oduncler 
                WHERE kullanici_id=%s AND gercek_iade_tarihi IS NULL
            """, (kullanici_id,))
            if cursor.fetchone()["kitap_sayisi"] >= 5:
                return {"success": False, "message": "Kullanıcının elinde zaten 5 kitap var."}

            # Aynı kitaptan var mı kontrolu
            cursor.execute("""
                SELECT COUNT(*) AS ayni_kitap 
                FROM oduncler 
                WHERE kullanici_id=%s AND kitap_id=%s AND gercek_iade_tarihi IS NULL
            """, (kullanici_id, kitap_id))
            if cursor.fetchone()["ayni_kitap"] > 0:
                return {"success": False, "message": "Kullanıcı bu kitaptan zaten ödünç aldı."}

            # odunc verir
            cursor.execute("""
                INSERT INTO oduncler (kullanici_id, kitap_id, odunc_tarihi, gerekli_iade_tarihi)
                VALUES (%s, %s, %s, %s)
            """, (kullanici_id, kitap_id, odunc_tarihi, gerekli_iade_tarihi))
            odunc_id = cursor.lastrowid

            conn.commit()

            return {
                "success": True,
                "message": "Kitap başarıyla ödünç verildi.",
                "odunc_id": odunc_id,
            }

        except Exception as e:
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
            
        # Kitabı iade etme işlemi (UPDATE)
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
        # Hata fırlatmak yerine mesajı döndürmek daha kullanıcı dostu olabilir.
        return f"İade işlemi hatası: {e}" 
        # Ya da raise e  (önceki kodunuzdaki gibi)
        
      finally:
        cursor.close()

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
                "SELECT * FROM oduncler WHERE kitap_id=%s AND gercek_iade_tarihi IS NULL",
                (kitap_id,)
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()

#kullanicinin odunc gecmisini getirir   
    def kullanici_odunc_gecmisi_getir(self, kullanici_id):
        cursor = self.conn.cursor(dictionary=True)
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
            
#oduncler tablosundaki tum degerleri ceker
    def tum_kullanici_odunc_gecmisi_getir(self):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT o.id, u.username, k.isim AS kitap_adi, o.odunc_tarihi, o.gerekli_iade_tarihi, o.gercek_iade_tarihi
                FROM oduncler o
                JOIN kullanicilar u ON o.kullanici_id = u.id
                JOIN kitaplar k ON o.kitap_id = k.id
                ORDER BY o.odunc_tarihi DESC
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
