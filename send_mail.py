import smtplib
from email.mime.text import MIMEText
import mysql.connector

SMTP_USER = "infocatlary@gmail.com"
SMTP_PASS = "" 

def send_mail_to_user(to_email, subject, content):
    """Tek bir kullanıcıya mail gönderir"""
    try:
        msg = MIMEText(content)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = to_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        server.quit()
        print(f"Mail gönderildi: {to_email}")
    except Exception as e:
        print(f"Mail gönderilemedi: {to_email} - {e}")


def send_pending_mails():
    """Veritabanındaki bekleyen mailleri gönderir"""
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="melisa",
        password="Mtz0504*",
        database="kutuphane_db",
        port=3306
    )
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM MailKuyrugu WHERE GonderimDurumu = 'Beklemede'")
    mailler = cursor.fetchall()

    if not mailler:
        print("Gönderilecek mail yok.")
        cursor.close()
        db.close()
        return

    for mail in mailler:
        try:
            cursor.execute(
                "UPDATE MailKuyrugu SET GonderimDurumu='Gonderiliyor' WHERE MailId=%s",
                (mail['MailId'],)
            )
            db.commit()

            send_mail_to_user(mail['AliciMail'], mail['Konu'], mail['Mesajicerigi'])

            cursor.execute(
                "UPDATE MailKuyrugu SET GonderimDurumu='Gonderildi' WHERE MailId=%s",
                (mail['MailId'],)
            )
            db.commit()

        except Exception as e:
            cursor.execute(
                "UPDATE MailKuyrugu SET GonderimDurumu='Hata olustu', HataDetaylari=%s WHERE MailId=%s",
                (str(e), mail['MailId'])
            )
            db.commit()
            print(f"Hata oluştu: {mail['AliciMail']} - {e}")

    cursor.close()
    db.close()
if __name__ == "__main__":
    send_pending_mails()        
    