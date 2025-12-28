from flask import Flask, session, g

# dependencies klasöründen gerekli fonksiyonları ve sınıfları çekiyoruz
from database import baglanti_olustur, tablolar_olustur
from services.veriservice import Veriservice
from db_config import db_config
# ------------------- BLUEPRINT IMPORTLARI -------------------
from routes.ortak_routes import genel_bp
from routes.admin_routes import admin_bp
from routes.personel_routes import personel_bp
from routes.kullanicilar_routes import kullanici_bp
from routes.kitaplar_routes import kitap_bp
from routes.yazarlar_routes import yazar_bp
from routes.kategoriler_routes import kategori_bp
from routes.cezalar_routes import ceza_bp 
from routes.oduncler_routes import odunc_bp
from routes.yayinevleri_routes import yayinevi_bp
from repository.varsayilanekleme import setup_database
# ------------------- FLASK APP -------------------
app = Flask(__name__)
SECRET = "56925541090436581"
app.secret_key = "56925541090436582"  

# Route dosyalarını uygulamaya tanıtıyoruz
app.register_blueprint(genel_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(personel_bp)
app.register_blueprint(kullanici_bp)
app.register_blueprint(kitap_bp)
app.register_blueprint(yazar_bp)
app.register_blueprint(kategori_bp)
app.register_blueprint(ceza_bp)
app.register_blueprint(odunc_bp)
app.register_blueprint(yayinevi_bp)

#Kullanıcı giriş yaptıysa session içindeki bilgileri alıp her sayfada otomatik olarak kullanılabilir hale getirir
#boyle olunca diger dosyalarda g.username gibi kullanabiliriz
@app.before_request
def load_user_data():
    g.user_id = session.get('user_id')
    g.username = session.get('username')
    g.role = session.get('role')
    g.user_email = session.get('email') 

# db sifirlamak ve varsayilan admin eklemek icin
#if __name__ == "__main__":
    # Veritabanı bağlantısı oluştur
#    conn = baglanti_olustur(db_config)
    # Veriservice instance oluştur
#    veri_service = Veriservice(conn)
    # Tabloları sıfırla ve veritabanını kur
#    veri_service.setup_database()
    # DB bağlantısını kapat
#    conn.close()
# Uygulama ana bloğu
if __name__ == "__main__":
    app.run(debug=True)