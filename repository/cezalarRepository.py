import database

class cezalarRepository:
    def __init__(self, db_config):
       
        self.db_config = db_config

#ceza detylarını verir
    def ceza_detaylari_getir(self, ceza_id):
        
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT c.ceza_miktari AS miktar, c.odeme_durumu, u.username
                FROM cezalar c
                JOIN kullanicilar u ON c.kullanici_id = u.id
                WHERE c.id=%s
            """, (ceza_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
    def kullanici_cezalari_getir(self, kullanici_id):
    
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT c.id, c.ceza_miktari, c.odunc_tarihi, c.iade_tarihi, c.odeme_durumu, k.isim AS kitap_adi
                FROM cezalar c
                LEFT JOIN kitaplar k ON c.kitap_id = k.id
                WHERE c.kullanici_id=%s
                ORDER BY c.iade_tarihi DESC
            """, (kullanici_id,))
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()
            conn.close()

    def tum_cezalari_getir(self):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT c.id, c.ceza_miktari, c.odunc_tarihi, c.iade_tarihi, c.odeme_durumu,
                        u.username, k.isim AS kitap_adi
                FROM cezalar c
                LEFT JOIN kullanicilar u ON c.kullanici_id = u.id
                LEFT JOIN kitaplar k ON c.kitap_id = k.id
                ORDER BY c.iade_tarihi DESC
            """)
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()
            conn.close()
    
    def iade_edilmemis_kitap_var_mi(self, kullanici_id):
       
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor()
        query = """
            SELECT EXISTS (
                SELECT 1 FROM oduncler 
                WHERE kullanici_id=%s AND gercek_iade_tarihi IS NULL
            )
        """
        try:
            cursor.execute(query, (kullanici_id,))
            sonuc = cursor.fetchone()
            
            raw_result = sonuc[0] if sonuc and len(sonuc) > 0 else 0
            final_bool = bool(raw_result)
            return final_bool
        finally:
            cursor.close()
            conn.close()
 
    def cezanin_iade_edilmis_olup_olmadigini_kontrol_et(self, kullanici_id):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT iade_tarihi
                FROM cezalar
                WHERE kullanici_id = %s
            """
            cursor.execute(query, (kullanici_id,))
            result = cursor.fetchall()

            if not result:
                # Bu kullanıcıya ait ceza yok
                return None  

            # Tüm kayıtları tarar iade_tarihi NULL olan var mı?
            for ceza in result:
                if ceza.get("iade_tarihi") is None:
                    # Halen iade edilmeyen kitap var → ödeme yapılamaz
                    return False

            # Tüm cezalar iade edilmiş → ödeme yapılabilir
            return True

        finally:
            cursor.close()
            conn.close()

    def toplam_borc_getir(self, kullanici_id):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT SUM(ceza_miktari) AS toplam
                FROM cezalar
                WHERE kullanici_id=%s AND odeme_durumu=0
            """, (kullanici_id,))
            result = cursor.fetchone()
            return result['toplam'] or 0
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
                    WHERE kullanici_id=%s AND odeme_durumu=0
                )
            """, (kullanici_id,))
            sonuc = cursor.fetchone()
            return bool(sonuc[0]) if sonuc and len(sonuc) > 0 else False
        finally:
            cursor.close()
            conn.close()


    def ceza_durumu_getir(self, ceza_id):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT odeme_durumu, iade_tarihi
                FROM cezalar
                WHERE id=%s
            """, (ceza_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def ceza_ode(self, ceza_id):
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE cezalar SET odeme_durumu=1 WHERE id=%s", (ceza_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def kullanici_id_getir(self, username):
       
        conn = database.baglanti_olustur(self.db_config)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM kullanicilar WHERE username=%s", (username,))
            result = cursor.fetchone()
            print(f"DEBUG: kullanici_id_getir('{username}') => {result}")
            return result[0] if result else None
        finally:
            cursor.close()
            conn.close()
            
    def ceza_odendi_yap(self, kullanici_id, odeme_yapilsin_mi):
        conn = None
        cursor = None
        try:
            conn = database.baglanti_olustur(self.db_config)
            cursor = conn.cursor()
#odeme yapılmasını isterse odeme durumunu gınceller
            if odeme_yapilsin_mi:
                cursor.execute("""
                    UPDATE cezalar
                    SET odeme_durumu = 1
                    WHERE kullanici_id = %s
                    AND odeme_durumu = 0
                    AND ceza_miktari > 0
                """, (kullanici_id,))

                etkilenen_satir = cursor.rowcount 
                conn.commit()

                return etkilenen_satir, True

            return 0, False

        except Exception as e:
            print(f"Repo hata (ceza_odendi_yap_repo): {e}")
            return str(e), False

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
