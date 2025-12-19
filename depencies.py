# ------------------- CONTROLLER IMPORTLARI -------------------
from controllers.yazarController import YazarController
from controllers.kategoriController import KategoriController
from controllers.personelController import personelController
from controllers.adminkontroller import adminkontroller 
from controllers.kitapController import kitapController
from controllers.kullanicikontroller import kullanicikontroller
from controllers.odunccontroller import odunccontroller
from controllers.cezaController import cezaController

# ------------------- SERVICE IMPORTLARI -------------------
from services.veriservice import Veriservice
from services.adminService import adminService
from services.kullaniciService import kullaniciService
from services.kitapService import kitapService
from services.cezaService import cezaService
from services.oduncService import oduncService
from services.personelService import personelService
from database import baglanti_olustur,tablolar_olustur
# ------------------- VERİTABANI AYARLARI -------------------
db_config = {
    "host": "127.0.0.1",
    "user": "melisa",
    "password": "Mtz0504*",
    "database": "kutuphane_db",
    "port": 3306
}

ceza_service_instance = cezaService(db_config) # Değişken adını karışıklık olmasın diye güncelledim
kitap_islemleri = kitapService(db_config)
odunc_islemleri = oduncService(db_config)
kullanici_islemleri = kullaniciService(db_config)
admin_service = adminService(db_config)
personel_service = personelService(db_config)

ceza_controller_instance = cezaController(db_config)
kullanici_controller_instance = kullanicikontroller()
personel_controller_instance = personelController(db_config)
yazarlar_controller = YazarController()
kitap_controller = kitapController(db_config)
kategoriler_controller = KategoriController(db_config)

odunc_controller_instance = odunccontroller(db_config)
def setup_database():
    print("Veritabanı kurulumu başlatılıyor...")
    tablolar_olustur()
    print("Veritabanı kurulumu tamamlandı.")

def make_json_compatible(obj):
#donebilecek her veri tipini json formatına uyarlamak için
    if isinstance(obj, set):
        #eger gelen obje set veri tipinde ise gelen nesneyi listeye cevirir 
        return list(obj)
    #eger gelen obje dict turunde ise
    elif isinstance(obj, dict):
        #dicti tek tek gezer ve deger kısmına rekursif olarak tekrar aynı fonksiyonu uygular
        return {k: make_json_compatible(v) for k, v in obj.items()}
    #eger gelen obje liste veya tuple ise 
    elif isinstance(obj, (list, tuple)):
        #named tuple olup olmadıgını fields ozelligi olup olmadıgına bakarak kontrol eder 
        if hasattr(obj, "_fields"):  
            #eger named tuple ise dicte cevirir
            return {k: make_json_compatible(v) for k, v in obj._asdict().items()}
        else:
            #deilse her elemana uygulayarak cevirir
            return [make_json_compatible(i) for i in obj]
    else:
        #yukardaki turlerden hicbiri deilse zaten json formatına uygundur bu yuzden aynen geri dondurur
        return obj
