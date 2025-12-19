

import mysql.connector
import datetime 
import database 

class personelRepository:
    def __init__(self, db_config):
        self.db_config = db_config

   
    def _get_connection(self):
        return mysql.connector.connect(**self.db_config)
    
    def tum_personelleri_getir(self):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, isim, email, giristarihi, aktif FROM personeller") 
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"DB Hatası (tum_personelleri_getir): {err}")
            return []
        finally:
            if conn and conn.is_connected():
                conn.close()

    def get_personel_by_email(self, email):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT id, isim, email, aktif, password FROM personeller WHERE email = %s"
            cursor.execute(sql, (email,))
            return cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"DB Hatası (get_personel_by_email): {err}")
            return None
        finally:
            if conn and conn.is_connected():
                conn.close()

    def personel_getir_username(self, username):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT id, isim, email, aktif, password FROM personeller WHERE isim = %s"
            cursor.execute(sql, (username,))
            return cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"DB Hatası (personel_getir_username): {err}")
            return None
        finally:
            if conn and conn.is_connected():
                conn.close()

    
    def personel_getir_id(self, personel_id):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT id, isim, email, aktif, password FROM personeller WHERE id = %s"
            cursor.execute(sql, (personel_id,))
            return cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"DB Hatası (personel_getir_id): {err}")
            return None
        finally:
            if conn and conn.is_connected():
                conn.close()

    def personel_ekle(self, isim, email, sifre_hash):
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            bugunun_tarihi = datetime.date.today()
            
            sql = "INSERT INTO personeller (isim, email, password, giristarihi) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (isim, email, sifre_hash, bugunun_tarihi))
            
            conn.commit()
            return cursor.lastrowid 
        except mysql.connector.Error as err:
            
            if conn:
                conn.rollback() 
            print(f"DB Hatası (personel_ekle): {err}")
            return 0
        finally:
            if conn and conn.is_connected():
                conn.close()
  
    def sifre_guncelle(self, personel_id, yeni_hash):
        #gelen bilgiler ile sifreti guncelelr
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            sql = "UPDATE personeller SET password = %s WHERE id = %s"
            cursor.execute(sql, (yeni_hash, personel_id))
            
            conn.commit()
            return cursor.rowcount > 0 
        except mysql.connector.Error as err:
            if conn:
                conn.rollback() 
            print(f"DB Hatası (sifre_guncelle): {err}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()

    def personel_aktiflik_degistir(self, personel_id, yeni_durum):
        yeni_aktiflik_degeri = 1 if yeni_durum else 0
        
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            sql = "UPDATE personeller SET aktif = %s WHERE id = %s"
            cursor.execute(sql, (yeni_aktiflik_degeri, personel_id))
            
            conn.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            if conn:
                conn.rollback() 
            print(f"DB Hatası (personel_aktiflik_degistir): {err}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()