import database
from datetime import datetime

class CezaRepository:
    def __init__(self, db_config):
        try:
            self.conn = database.baglanti_olustur(db_config)
        except Exception as e:
            print("DB bağlantısı oluşturulamadı:", e)
            self.conn = None

#gelen bilgilere uygun cezayi ekler
    def ceza_ekle(self, kullanici_id, kitap_id, ceza_miktari, odunc_tarihi, iade_tarihi, odeme_durumu=0):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO cezalar (kullanici_id, kitap_id, ceza_miktari, odunc_tarihi, iade_tarihi, odeme_durumu) VALUES (%s,%s,%s,%s,%s,%s)",
                (kullanici_id, kitap_id, ceza_miktari, odunc_tarihi, iade_tarihi, odeme_durumu)
            )
            self.conn.commit()
            return f"Ceza eklendi. ID: {cursor.lastrowid}", cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            return f"Hata olustu: {str(e)}", None
        finally:
            cursor.close()

#id si gelen cezayi siler
    def ceza_sil(self, ceza_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * FROM cezalar WHERE id=%s", (ceza_id,))
            ceza = cursor.fetchone()
            if not ceza:
                return "Ceza bulunamadi.", None

            cursor.execute("DELETE FROM cezalar WHERE id=%s", (ceza_id,))
            self.conn.commit()
            return f"Ceza silindi. ID: {ceza_id}", ceza
        except Exception as e:
            self.conn.rollback()
            return f"Hata olustu: {str(e)}", None
        finally:
            cursor.close()

#kullanicinin cezalarini getirir
    def kullanici_cezalari_getir(self, kullanici_id):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    c.id,
                    c.ceza_miktari,
                    c.odunc_tarihi,
                    c.iade_tarihi,
                    c.odeme_durumu,
                    kit.isim as kitap_adi
                FROM cezalar c
                LEFT JOIN kitaplar kit ON c.kitap_id = kit.id
                WHERE c.kullanici_id = %s
                ORDER BY c.iade_tarihi DESC
            """, (kullanici_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Kullanıcı cezaları getirme hatası: {e}")
            return []
        finally:
            cursor.close()

#tum cezalari tablodan alir
    def tum_cezalari_getir(self):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    c.id,
                    c.ceza_miktari,
                    c.odunc_tarihi,
                    c.iade_tarihi,
                    c.odeme_durumu,
                    u.username,
                    kit.isim
                FROM cezalar c
                LEFT JOIN kullanicilar u ON c.kullanici_id = u.id
                LEFT JOIN kitaplar kit ON c.kitap_id = kit.id
                ORDER BY c.iade_tarihi DESC
            """)
            cezalar = cursor.fetchall()
            print(f"Toplam {len(cezalar)} ceza bulundu")
            return cezalar
        except Exception as e:
            print(f"Tüm cezalar getirme hatası: {e}")
            return []
        finally:
            cursor.close()


    def ceza_odendi_yap(self, kullanici_id, odeme_yapilsin_mi=False):
        cursor = self.conn.cursor(dictionary=True)
        try:
            # Ödenmemiş cezaları alir
            cursor.execute(
                "SELECT * FROM cezalar WHERE kullanici_id=%s AND odeme_durumu=0",
                (kullanici_id,)
            )
            cezalar = cursor.fetchall()
            toplam = sum([ceza['ceza_miktari'] for ceza in cezalar]) if cezalar else 0

            if odeme_yapilsin_mi and toplam > 0:
                cursor.execute(
                    "UPDATE cezalar SET odeme_durumu=1 WHERE kullanici_id=%s AND odeme_durumu=0",
                    (kullanici_id,)
                )#odeme durumunu gunceller
                self.conn.commit()

            return toplam
        except Exception as e:
            self.conn.rollback()
            print("Hata:", e)
            return 0
        finally:
            cursor.close()

#kullanicinin odenmemis cezasi var mi kontrolu yapar
    def odeme_durumu_var_mi(self, kullanici_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM cezalar WHERE kullanici_id=%s AND odeme_durumu=0",
                (kullanici_id,)
            )
            return cursor.fetchone()[0] > 0
        finally:
            cursor.close()