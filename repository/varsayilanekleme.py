# setupRepository.py
from repository.veriRepository import VeriService
from database import baglanti_olustur
from werkzeug.security import generate_password_hash

def setup_database():
    conn = baglanti_olustur()
    cursor=conn.cursor()
    service = VeriService(conn)

    # Varsayılan admin ekler
    admin_username = "admin"
    admin_email = "infocatlary@gmail.com"
    admin_sifre = "123456"
    hashed_admin_sifre = generate_password_hash(admin_sifre)
    cursor.execute(
        "INSERT INTO admin (username, email, password) VALUES (%s, %s, %s)",
        (admin_username, admin_email, hashed_admin_sifre)
    )
   
    # Varsayılan kullanıcı ekle
    user_username = "melisa"
    user_email = "taskaramelisa@gmail.com"
    user_sifre = "666666"
    hashed_user_sifre = generate_password_hash(user_sifre)
    cursor.execute(
        "INSERT INTO kullanicilar (username, email, password) VALUES (%s, %s, %s)",
        (user_username, user_email, hashed_user_sifre)
    )
    conn.commit()
    cursor.close()
    conn.close()

# Script olarak çalıştırıldığında otomatik çalışmasi için
if __name__ == "__main__":
    setup_database()
