import database


class cezalarRepository:
    def __init__(self, db_config):
        self.db_config = db_config
    def ceza_ode(self, ceza_id):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE cezalar
                SET odeme_durumu = 1
                WHERE id = %s
            """, (ceza_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    def ceza_detaylari_getir(self, ceza_id):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    c.ceza_miktari AS miktar,
                    c.odeme_durumu,
                    u.username,
                    o.gercek_iade_tarihi
                FROM cezalar c
                JOIN kullanicilar u ON u.id = c.kullanici_id
                LEFT JOIN oduncler o
                    ON o.kullanici_id = c.kullanici_id
                    AND o.kitap_id = c.kitap_id
                    AND DATE_FORMAT(o.odunc_tarihi, '%Y-%m-%d %H:%i') = 
                        DATE_FORMAT(c.odunc_tarihi, '%Y-%m-%d %H:%i')
                WHERE c.id = %s
            """, (ceza_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
    def kitap_gercekten_iade_edildi_mi(self, kullanici_id, kitap_id, odunc_tarihi):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id FROM oduncler
                WHERE kullanici_id = %s
                  AND kitap_id = %s
                  AND odunc_tarihi = %s  -- Spesifik tarih kontrolü
                  AND gercek_iade_tarihi IS NULL
            """, (kullanici_id, kitap_id, odunc_tarihi))
            # Eğer o tarihteki kayıt iade edildiyse None döner, iade edilmediyse bir ID döner.
            return cursor.fetchone() is None
        finally:
            cursor.close()
            conn.close()

    def kullanici_cezalari_getir(self, kullanici_id):
            conn = database.baglanti_olustur(self.db_config)
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("""
        SELECT 
            c.id,
            c.ceza_miktari,
            c.odunc_tarihi,
            c.iade_tarihi AS gercek_iade_tarihi,
            c.odeme_durumu,
            k.isim AS kitap_adi,
            k.resim AS kapak_url
        FROM cezalar c
        LEFT JOIN kitaplar k ON k.id = c.kitap_id
        WHERE c.kullanici_id = %s
        ORDER BY c.id DESC
    """, (kullanici_id,))
                return cursor.fetchall()
            except Exception as e:
                print(f"Veritabanı hatası: {e}")
                return []
            finally:
                cursor.close()
                conn.close()
    def ceza_ve_iade_durumu_getir(self, ceza_id):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    c.id,
                    c.odeme_durumu,
                    c.ceza_miktari,
                    o.gercek_iade_tarihi
                FROM cezalar c
                LEFT JOIN oduncler o
                    ON o.kullanici_id = c.kullanici_id
                    AND o.kitap_id = c.kitap_id
                    AND o.odunc_tarihi = c.odunc_tarihi
                WHERE c.id = %s
            """, (ceza_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    
    def cezanin_iade_edilmis_olup_olmadigini_kontrol_et(self, kullanici_id):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor(dictionary=True) 
        try:
            cursor.execute("""
                SELECT COUNT(*) as toplam 
                FROM oduncler
                WHERE kullanici_id = %s
                AND gercek_iade_tarihi IS NULL
            """, (kullanici_id,))
            
            result = cursor.fetchone()
            
            if result and result['toplam'] > 0:
                return True
            return False
        finally:
            cursor.close()
            conn.close()

    

    def odeme_durumu_var_mi(self, kullanici_id):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM cezalar
                    WHERE kullanici_id = %s
                      AND odeme_durumu = 0
                )
            """, (kullanici_id,))
            return bool(cursor.fetchone()[0])
        finally:
            cursor.close()
            conn.close()
    def ceza_odendi_yap(self, kullanici_id, odeme_yapilsin_mi=False):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor(dictionary=True)
        try:
            # Önce kullanıcının toplam borcunu hesapla
            cursor.execute("""
                SELECT SUM(ceza_miktari) as toplam 
                FROM cezalar 
                WHERE kullanici_id = %s AND odeme_durumu = 0
            """, (kullanici_id,))
            
            result = cursor.fetchone()
            toplam_tutar = result['toplam'] if result and result['toplam'] else 0

            # Eğer ödeme onayı geldiyse ve borç varsa güncelle
            if odeme_yapilsin_mi and toplam_tutar > 0:
                cursor.execute("""
                    UPDATE cezalar 
                    SET odeme_durumu = 1 
                    WHERE kullanici_id = %s AND odeme_durumu = 0
                """, (kullanici_id,))
                conn.commit()
                return toplam_tutar, True
            
            return toplam_tutar, False
        finally:
            cursor.close()
            conn.close()
   

    def kullanici_id_getir(self, username):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM kullanicilar WHERE username = %s",
                (username,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            cursor.close()
            conn.close()
            
    def tum_cezalari_getir(self):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    c.id,
                    u.username,
                    k.isim AS kitap_adi,
                    c.ceza_miktari,
                    c.odunc_tarihi,
                    o.gerekli_iade_tarihi,
                    CASE 
                        WHEN c.iade_tarihi = c.odunc_tarihi THEN NULL 
                        ELSE c.iade_tarihi 
                    END AS gercek_iade_tarihi,
                    c.odeme_durumu,
                    k.resim AS kapak_url
                FROM cezalar c
                LEFT JOIN kullanicilar u ON c.kullanici_id = u.id
                LEFT JOIN kitaplar k ON k.id = c.kitap_id
                LEFT JOIN oduncler o ON c.kullanici_id = o.kullanici_id 
                                        AND c.kitap_id = o.kitap_id 
                                        AND c.odunc_tarihi = o.odunc_tarihi
                ORDER BY c.id DESC
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    def cezanin_iade_edilmis_olup_olmadigini_kontrol_et(self, kullanici_id):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT COUNT(*) as toplam FROM oduncler
                WHERE kullanici_id = %s AND gercek_iade_tarihi IS NULL
            """, (kullanici_id,))
            result = cursor.fetchone()
            return result['toplam'] > 0 if result else False
        finally:
            cursor.close()
            conn.close()

    def toplam_borc_getir(self, kullanici_id):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT COALESCE(SUM(c.ceza_miktari), 0) AS toplam
                FROM cezalar c
                JOIN oduncler o ON o.kullanici_id = c.kullanici_id 
                               AND o.kitap_id = c.kitap_id
                               AND DATE_FORMAT(o.odunc_tarihi, '%Y-%m-%d %H:%i') = 
                                   DATE_FORMAT(c.odunc_tarihi, '%Y-%m-%d %H:%i')
                WHERE c.kullanici_id = %s AND c.odeme_durumu = 0
                AND o.gercek_iade_tarihi IS NOT NULL
            """, (kullanici_id,))
            return cursor.fetchone()["toplam"]
        finally:
            cursor.close()
            conn.close()

    def ceza_odendi_yap(self, kullanici_id, odeme_yapilsin_mi=False):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor(dictionary=True)
        try:
            if odeme_yapilsin_mi:
                cursor.execute("""
                    UPDATE cezalar c
                    JOIN oduncler o ON o.kullanici_id = c.kullanici_id 
                                   AND o.kitap_id = c.kitap_id
                                   AND DATE_FORMAT(o.odunc_tarihi, '%Y-%m-%d %H:%i') = 
                                       DATE_FORMAT(c.odunc_tarihi, '%Y-%m-%d %H:%i')
                    SET c.odeme_durumu = 1
                    WHERE c.kullanici_id = %s AND c.odeme_durumu = 0
                    AND o.gercek_iade_tarihi IS NOT NULL
                """, (kullanici_id,))
                conn.commit()
                return {"success": True}, True
            return {"success": False}, False
        finally:
            cursor.close()
            conn.close()