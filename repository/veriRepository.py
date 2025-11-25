import mysql.connector
from database import baglanti_olustur 
from werkzeug.security import generate_password_hash 
class VeriService:
    def __init__(self, conn):
        self.conn = conn

    def veri_sifirla_delete(self):
        cursor = self.conn.cursor()
        tablolar = ["cezalar", "oduncler", "kitaplar", "kullanicilar", "admin"]
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        for tablo in tablolar:
            try:
                cursor.execute(f"DELETE FROM {tablo}")
                cursor.execute(f"ALTER TABLE {tablo} AUTO_INCREMENT = 1")
            except mysql.connector.Error as err:
                print(f"{tablo} tablosunda hata: {err}")

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        self.conn.commit()
        cursor.close()
        print("Tüm veriler sıfırlandı!")

if __name__ == "__main__":
    conn = baglanti_olustur()
    service = VeriService(conn)
    service.veri_sifirla_delete()

    cursor = conn.cursor()
    # Varsayılan admin
    admin_username = "varsayilan admin"
    admin_email = "infocatlary@gmail.com"
    admin_sifre = ""
    hashed_admin_sifre = generate_password_hash(admin_sifre)

    cursor.execute(
        "INSERT INTO admin (username, email, password) VALUES (%s, %s, %s)",
        (admin_username, admin_email, hashed_admin_sifre)
    )
    
    # Varsayılan kullanıcı
    user_username = "melisa"
    user_email = "taskaramelisa@gmail.com"
    user_sifre = ""
    hashed_user_sifre = generate_password_hash(user_sifre)
    cursor.execute(
        "INSERT INTO kullanicilar (username, email, password) VALUES (%s, %s, %s)",
        (user_username, user_email, hashed_user_sifre)
    )
    
    conn.commit()
    cursor.close()
    conn.close()