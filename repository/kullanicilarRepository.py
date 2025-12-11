import logging
import database
from werkzeug.security import generate_password_hash, check_password_hash

class kullanicilarRepository:
  

    def __init__(self, db_config=None):
        self.db_config = db_config
    def kullanici_ekle(self, username, email, hashed_password):
        conn = None
        cursor = None
        try:
            conn = database.baglanti_olustur(self.db_config)
            cursor = conn.cursor()

            # Çakışma kontrolü
            cursor.execute(
                "SELECT id FROM kullanicilar WHERE username=%s OR email=%s",
                (username, email)
            )
            if cursor.fetchone():
                return False

            # Kullanıcı ekle
            cursor.execute(
                "INSERT INTO kullanicilar (username, email, password) VALUES (%s,%s,%s)",
                (username, email, hashed_password)
            )
            conn.commit()
            return True

        except Exception as e:
            if conn:
                conn.rollback()
            logging.error(f"Kullanıcı kayıt hatası (Repo): {e}")
            return False

        finally:
            if cursor: cursor.close()
            if conn: conn.close()
    def kullanici_by_email(self, email):
        conn = None
        cursor = None
        try:
            conn = database.baglanti_olustur(self.db_config)
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT id, username, email, password, aktiflik FROM kullanicilar WHERE email=%s",
                (email,)
            )
            return cursor.fetchone()
        except Exception as e:
            logging.error(f"Kullanıcı çekme hatası (email): {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

#id ile kullaniciyi getirir
    def kullanici_by_id(self, user_id):
        conn = None
        cursor = None
        try:
            conn = database.baglanti_olustur(self.db_config)
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT id, username, email, password, aktiflik FROM kullanicilar WHERE id=%s",
                (user_id,)
            )
            return cursor.fetchone()
        except Exception as e:
            logging.error(f"Kullanıcı çekme hatası (id): {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

#username ile kullaniciyi getirir
    def kullanici_by_username(self, username):
        conn = None
        cursor = None
        try:
            conn = database.baglanti_olustur(self.db_config)
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT id, username, email, aktiflik FROM kullanicilar WHERE username=%s",
                (username,)
            )
            return cursor.fetchone()
        except Exception as e:
            logging.error(f"Kullanıcı adına göre çekme hatası: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

#tum kullanicilari getirir
    def tum_kullanicilari_getir(self):
        conn = None
        cursor = None
        try:
            conn = database.baglanti_olustur(self.db_config)
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT id, username, email, aktiflik FROM kullanicilar")
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"Tüm kullanıcıları çekme hatası: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

# sifreyi gunceller
    def sifre_guncelle(self, user_id, yeni_sifre):
        conn = None
        cursor = None
        try:
            conn = database.baglanti_olustur(self.db_config)
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE kullanicilar SET password=%s WHERE id=%s",
                (yeni_sifre, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0 # Güncelleme başarılıysa True doner

        except Exception as e:
            if conn:
                conn.rollback()
            logging.error(f"Şifre güncelleme hatası: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    #gelen id bilgisi ile aktiflik gunceller
    def aktiflik_durumu_guncelle_by_id(self, user_id, aktiflik_degeri):
        conn = None
        cursor = None
        try:
            conn = database.baglanti_olustur(self.db_config)
            cursor = conn.cursor()

            sorgu = "UPDATE kullanicilar SET aktiflik = %s WHERE id = %s"
            cursor.execute(sorgu, (aktiflik_degeri, user_id))
            conn.commit()
            return cursor.rowcount 

        except Exception as e:
            if conn:
                conn.rollback()
            logging.error(f"Aktiflik güncelleme hatası: {e}")
            return 0
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
        