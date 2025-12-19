import smtplib
from email.mime.text import MIMEText
import sys
import os

# Ana dizindeki database.py dosyasına erişebilmek için yol ayarı
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Veritabanı bağlantısını merkezi dosyadan alıyoruz
try:
    from database import baglanti_olustur
except ImportError:
    print("UYARI: database.py import edilemedi. Veritabanı bağlantısı kurulamayabilir.")
    def baglanti_olustur(): return None

# Mail Ayarları
SMTP_USER = "infocatlary@gmail.com"
SMTP_PASS =

def send_mail_to_user(to_email, subject, content):
    """Tek bir kullanıcıya mail gönderir ve (Basari, Mesaj) döner"""
    try:
        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = to_email

        # Gmail sunucusuna bağlan
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        server.quit()
        
        print(f"Mail başarıyla gönderildi: {to_email}")
        return True, "Başarılı" 
        
    except Exception as e:
        print(f"Mail gönderilemedi: {to_email} - {e}")
        return False, str(e)    


def send_pending_mails():
    """Veritabanındaki bekleyen mailleri gönderir"""
    
    # Bağlantıyı merkezi dosyadan al
    conn = baglanti_olustur()
    
    if conn is None:
        print("Veritabanı bağlantısı kurulamadı.")
        return

    cursor = conn.cursor(dictionary=True)

    try:
        # 1. Bekleyen mailleri çek
        cursor.execute("SELECT * FROM MailKuyrugu WHERE GonderimDurumu = 'Beklemede'")
        mailler = cursor.fetchall()

        if not mailler:
            return

        for mail in mailler:
            cursor.execute(
                "UPDATE MailKuyrugu SET GonderimDurumu='Gonderiliyor' WHERE MailId=%s",
                (mail['MailId'],)
            )
            conn.commit()

            basarili_mi, sonuc_mesaji = send_mail_to_user(mail['AliciMail'], mail['Konu'], mail['Mesajicerigi'])

            if basarili_mi:
                cursor.execute(
                    "UPDATE MailKuyrugu SET GonderimDurumu='Gonderildi' WHERE MailId=%s",
                    (mail['MailId'],)
                )
            else:
                cursor.execute(
                    "UPDATE MailKuyrugu SET GonderimDurumu='Hata olustu', HataDetaylari=%s WHERE MailId=%s",
                    (sonuc_mesaji, mail['MailId'])
                )
            
            conn.commit()

    except Exception as e:
        print(f"Genel Mail Döngüsü Hatası: {e}")
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    send_pending_mails()