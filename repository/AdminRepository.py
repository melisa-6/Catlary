import logging
import database
from werkzeug.security import generate_password_hash 

class AdminRepository:

    def __init__(self, db_config):
        self.db_config = db_config
    
    def _get_connection(self):
        """Her çağrıda yeni bir bağlantı oluşturur."""
        try:
            return database.baglanti_olustur(self.db_config)
        except Exception as e:
            raise Exception(f"Admin DB Bağlantı Hatası: {e}")
    
    def admin_sil(self, username):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            sql = "DELETE FROM admin WHERE username = %s"
            cursor.execute(sql, (username,))
            conn.commit()

            silinen_sayi = cursor.rowcount  

            return silinen_sayi  # 1: silindi, 0: bulunamadı olur
        except Exception as e:
            if conn: conn.rollback()
            print(f"Admin silme hatası: {e}")
            return 0
        finally:
            if conn: conn.close()
    
    
    def admin_mi(self, email):
        # E-posta adresi verilen kullanıcının admin tablosunda olup olmadığını kontrol eder
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor() # Dictionary'e gerek yok
            cursor.execute("SELECT 1 FROM admin WHERE email=%s", (email,))
            # Sonuç varsa True, yoksa False döner
            return cursor.fetchone() is not None
        except Exception as e:
            logging.error(f"Admin kontrol hatası: {e}")
            raise e
        finally:
            if conn: conn.close()

    # email ile admini bulur ve getirir
    def get_by_email(self, email):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, username, email, password FROM admin WHERE email=%s", (email,))
            return cursor.fetchone()
        except Exception as e:
            logging.error(f"Admin çekme hatası: {e}")
            raise e
        finally:
            if conn: conn.close()

    # username ile admini getirir
    def get_by_username(self, username):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, username, email, password FROM admin WHERE username=%s", (username,)) 
            
            return cursor.fetchone()
        except Exception as e:
            logging.error(f"Admin username çekme hatası: {e}")
            print(f"DEBUG REPO HATASI: {e}") 
            raise e
        finally:
            if conn: conn.close()
    
    def adminler(self):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True) 
            cursor.execute("SELECT id, username,email FROM admin") 
            
            adminler = cursor.fetchall()
            return adminler
            
        except Exception as e:
            print("-" * 50)
            print(f"!!! KRİTİK VERİTABANI HATASI !!!: {e}") 
            print(f"!!! KOD HATA NEDENİYLE 'None' DÖNDÜRDÜ !!!")
            print("-" * 50)
            
            logging.error(f"Admin listesi çekme hatası: {e}") 
            return None 
            
        finally:
            if conn: conn.close()
            
    def admin_ekle(self, username, email, sifre):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO admin (username, email, password) VALUES (%s,%s,%s)",
                (username, email, sifre)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            if conn: conn.rollback()
            logging.error(f"Admin ekleme hatası: {e}")
            return -1 
        finally:
            if conn: conn.close()
    # gelen bilgiler ile şifreyi günceller
    def sifre_guncelle(self, username, yeni_hash):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE admin SET password = %s WHERE username = %s",
                (yeni_hash, username)
            )
            conn.commit()
            
            return {"success": True, "message": f"{cursor.rowcount} admin kullanıcısının şifresi güncellendi."}
            
        except Exception as e:
            if conn: conn.rollback()
            logging.error(f"Admin şifre güncelleme hatası: {e}")
            raise e
        finally:
            if conn: conn.close()      
    
    def get_first_admin(self):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, email FROM admin LIMIT 1")
            return cursor.fetchone()
        except Exception as e:
            logging.error(f"İlk admin çekme hatası: {e}")
            raise e
        finally:
            if conn: conn.close()