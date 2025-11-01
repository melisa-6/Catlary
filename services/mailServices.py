import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class MailService:
    def gonder(self, alici, konu, icerik):
        
        from_email = "infocatlary@gmail.com"
        from_password = ""  # Gmail App Password

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = alici
        msg['Subject'] = konu
        msg.attach(MIMEText(icerik, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)
        server.quit()
