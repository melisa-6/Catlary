from email.mime.multipart import MIMEMultipart
from flask import Flask, jsonify, request, render_template, session, redirect, url_for
import database
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import string
from email.mime.text import MIMEText
import smtplib


app = Flask(__name__)
app.secret_key = "Mtz0504*"  
#database.db_sil()
database.db_olustur()
database.tablolar_olustur()

@app.route('/')
def anasayfa():
    return render_template("index.html")

@app.route('/girisyap', methods=['POST'])
def giris_yap():
    islem_tipi = request.form.get('islem')
    
#index HTML dosyasinda kullanici durumumuza gore hangi butona tikladiysak o rolden devam etmemizi saglar

    conn = database.baglanti_olustur()
    cursor = conn.cursor()

    if islem_tipi == "kullanici":
        #eger kullanici giris butonuna basilmissa
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        #kullanicinin girdigi email ve sifreyi alir fomdan
        #şifrenin başında veya sonunda yanlışlıkla boşluk varsa .strip() sayesinde  temizlenir
        cursor.execute("SELECT username, password FROM kullanicilar WHERE email=%s", (email,))
        #kullanicilar tablosundan username ve passwordu secip formdan emaili alinan kullanicilari bulur 
        row = cursor.fetchone()
        #bulunan username ve hashlenmis sifre alinir ve row degiskenine atar 
        # check_password_hash() fonksiyonu ile girilen sifre dogruysa kullanici.html sayfasina yonlendirir
        conn.close()
        if row and check_password_hash(row[1], password):
            # Giris basarili ise session oluşturuyoruz
            # Yani kullanıcı giris yaptıysa onunu otuurm bilgisini hatırlamak için session kullanıyoruz.
            session['username'] = row[0]
            session['role'] = 'user'
            return redirect(url_for("kullanici_anasayfa", username=row[0]))
        else:
            return "Email veya şifre yanlış!", 401

    elif islem_tipi == "admin":
        #eger admin girisi butonuna basilmissa
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        #adminin girdigi email ve sifreyi bosluklari temizleyerek alir 
        cursor.execute("SELECT username, password FROM admin WHERE email=%s", (email,))
        row = cursor.fetchone()
        #admin tabalosunda emaili arar 
        # check_password_hash() fonksiyonu ile girilen sifrenin hashlenmis sifre ile uyusup uyusmadigini kontrol eder uyarsa admin.html sayfasina yonlendirir
        conn.close()
        if row and check_password_hash(row[1], password):
            # admin icin session olusturuyoruz
            session['username'] = row[0]
            session['role'] = 'admin'
            return redirect(url_for("admin_anasayfa", username=row[0]))
        else:
            return "Admin email veya şifre yanlış!", 401
   
    elif islem_tipi == "yeni":
        # eger hemen ac butonuna tiklanmissa da yeni kullanicinin username ve sifrelerini alir
        yeni_username = request.form.get('username', '').strip()
        yeni_email = request.form.get('email', '').strip()  # <-- email burada alındı
        yeni_sifre = request.form.get('yeni_sifre', '').strip()
        yeni_sifre_tekrar = request.form.get('yeni_sifre_tekrar', '').strip()
        # alanlar doldurulmadiysa veya girilen sifreler yanlissa ya da 6 karakterden kisaysa veya bu adda veya mailde farkli biri varsa gerekli uyarilari verir
        if not (yeni_username and yeni_email and yeni_sifre and yeni_sifre_tekrar):
            return "Lütfen tüm alanları doldurun."

        if yeni_sifre != yeni_sifre_tekrar:
            return "Şifreler eşleşmiyor."

        if len(yeni_sifre) < 6:
            return "Şifre en az 6 karakter olmalı."

        try:
            # Aynı username veya email var mı kontrol eder
            cursor.execute(
                "SELECT * FROM kullanicilar WHERE username=%s OR email=%s",
                (yeni_username, yeni_email)
            )
            mevcut = cursor.fetchone()
            if mevcut:
                conn.close()
                return "Bu kullanıcı adı veya email zaten kayıtlı!"
            cursor.execute(
                "SELECT * FROM admin WHERE username=%s OR email=%s",
                (yeni_username, yeni_email)
            )
            mevcut = cursor.fetchone()
            if mevcut:
                conn.close()
                return "Bu kullanıcı adı veya email zaten kayıtlı!"
            # Şifreyi hashleyerek ve ekler tabloya
            hashed_password = generate_password_hash(yeni_sifre)
            cursor.execute(
    "INSERT INTO kullanicilar (username, aktiflik, email, password) VALUES (%s, %s, %s, %s)",
    (yeni_username, 0, yeni_email, hashed_password)
)  # Yeni kullanıcı başlangıçta pasif

            conn.commit()
            conn.close()
            session['username'] = yeni_username
            session['role'] = 'user'
            # hesap olusturduktan sonra kullanici.html sayfasina yonlendirilir
            return redirect(url_for("kullanici_anasayfa", username=yeni_username))
        except Exception as e:
            conn.close()
            return f"Hesap oluşturulamadı! Hata: {str(e)}", 400

@app.route('/kullanici/<username>')
def kullanici_anasayfa(username):
   if 'username' not in session or session.get('role') != 'user':
        return redirect(url_for('anasayfa'))  # giriş yoksa anasayfaya
   username = session['username']
   return render_template("kullanici.html", username=username)

@app.route('/admin/<username>')
def admin_anasayfa(username):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('anasayfa'))
    username = session['username']
    return render_template("admin.html", username=username)

@app.route('/kitaplari_goruntule/<username>', methods=['GET', 'POST'])
def kitaplari_goruntule(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor()

    # bu route kullanici ve admin tarafinda ortak kullanilacagi icin geri don linki sirasinda sorun yasamamak icin her seferinde gelenin kullanici mi admin mi oldugu kontrol edilir
    cursor.execute("SELECT * FROM admin WHERE username=%s", (username,))
    admin_mi = cursor.fetchone() is not None
#eger admin tablosunda boyle bir isim varsa admin olur yoksa da kullanici olur
    # Arama kutusundaki yazıyı alir
    aranan_kitap = request.args.get('aranacak_kitap', '').strip()

    # Eğer arama yapıldıysa sadece o kitapları getirir
    if aranan_kitap:
        cursor.execute("""
    SELECT isim, yazar, kategori FROM kitaplar 
    WHERE isim LIKE %s OR yazar LIKE %s OR kategori LIKE %s
""", (f"%{aranan_kitap}%", f"%{aranan_kitap}%", f"%{aranan_kitap}%"))

    else:
        cursor.execute("SELECT isim, yazar, kategori FROM kitaplar")
#gelenleri kitaplar adinda alir ve kitaplar.html tarafinda bunlari liste halinde gosteririr
    kitaplar = cursor.fetchall()
    conn.close()

    # admin_mi değerini tekrar sayfaya gönderip admşnse admin.html e kllaniciysa da kullanici.html e yonlendirir
    return render_template(
        "kitaplar.html",
        kitaplar=kitaplar,
        username=username,
        aranan_kitap=aranan_kitap,
        admin_mi=admin_mi
    )
    #admin anasayfasinda kullanicinin sifresini unuttugunda sifirlamasi icin buton olusturuldu 
    # ve onclickine bu routeun adi verildi bu sayede girilen degerlere uygun olan kullanicinin sifresi rastgele bir sekilde sifirlanacak ve yeni sifre ekranda gosterilecek 


@app.route('/kullanici_sifre_sifirla/<username>', methods=['POST'])
def sifre_sifirla(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor()
   
    try:
        # admin kontrolu
        cursor.execute("SELECT * FROM admin WHERE username=%s", (username,))
        if cursor.fetchone() is None:
            return "Yetkisiz erişim!", 403

        # formdan gelen kullanici bilgileri
        kullanici_id = request.form.get('sifirla_kullanici_id', '').strip()
        kullanici_email = request.form.get('sifirla_kullanici_email', '').strip()

        if not (kullanici_id and kullanici_email):
            cursor.execute("SELECT id, username, email FROM kullanicilar")
            kullanicilar = cursor.fetchall()
            mesaj = "Lütfen hem kullanıcı ID'si hem e-mailini girin."
            return render_template("admin.html", username=username, kullanicilar=kullanicilar, mesaj=mesaj)

        # kullanicinin tabloda olup olmadigi
        cursor.execute("SELECT id FROM kullanicilar WHERE id=%s AND email=%s", (kullanici_id, kullanici_email))
        kullanici = cursor.fetchone()
        if not kullanici:
            mesaj = "Kullanıcı bulunamadı!"
            cursor.execute("SELECT id, username, email FROM kullanicilar")
            kullanicilar = cursor.fetchall()
            return render_template("admin.html", username=username, kullanicilar=kullanicilar, mesaj=mesaj)

        # yeni sifre olustur
        yeni_sifre = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
        hashed = generate_password_hash(yeni_sifre)
        cursor.execute("UPDATE kullanicilar SET password=%s WHERE id=%s", (hashed, kullanici_id))
        conn.commit()

        # kullanici listesini cek
        cursor.execute("SELECT id, username, email FROM kullanicilar")
        kullanicilar = cursor.fetchall()

        # mail bilgileri
        from_email = session.get('email') or "infocatlary@gmail.com"
        from_password = "gngj tare hkrf yvbf"  # Gmail App Password
        
        # yeni sifreyi mail olarak gonder
        try:
            mesaj_icerik = f"Merhaba,\n\nŞifreniz sıfırlandı. Yeni şifreniz: {yeni_sifre}\n\nGiriş yaptıktan sonra lütfen şifrenizi değiştirin."
            
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = kullanici_email
            msg['Subject'] = 'Şifre Sıfırlama'
            msg.attach(MIMEText(mesaj_icerik, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_email, from_password)
            server.send_message(msg)
            server.quit()

        except Exception as mail_hata:
            mesaj = f"Şifre başarıyla sıfırlandı ama mail gönderilemedi: {str(mail_hata)}"
            return render_template("admin.html", username=username, kullanicilar=kullanicilar, mesaj=mesaj)

        mesaj = "Kullanıcının şifresi başarıyla sıfırlandı ve mail olarak gönderildi."
        return render_template("admin.html", username=username, kullanicilar=kullanicilar, mesaj=mesaj)

    except Exception as e:
        conn.rollback()
        cursor.execute("SELECT id, username, email FROM kullanicilar")
        kullanicilar = cursor.fetchall()
        return render_template("admin.html", username=username, kullanicilar=kullanicilar, mesaj=f"Hata oluştu: {str(e)}")

    finally:
        cursor.close()
        conn.close()
        
@app.route('/kullanicisifredegis/<username>', methods=['POST'])
def sifredegis(username):
    # kullanici sayfasinda kullanicinin kendi sifresini kendi degistirmesi icin
    try:
        conn = database.baglanti_olustur()
        cursor = conn.cursor()
        
        # once kullanicinin eski sifresini cekiyoruz
        cursor.execute("SELECT password FROM kullanicilar WHERE username=%s", (username,))
        eski_sifre_hashed = cursor.fetchone()
        if not eski_sifre_hashed:
            return "Boyle bir kullanici bulunamadi."
        
        # formdan yeni sifre ve tekrarini aliyoruz
        yeni_sifre = request.form.get('yeni_sifre', '').strip()
        yeni_sifre_tekrar = request.form.get('yeni_sifre_tekrar', '').strip()
        
        # her iki alanin da dolu oldugundan emin ol
        if not yeni_sifre or not yeni_sifre_tekrar:
            return "Lutfen her iki alani da doldurun."
        
        # girilen sifreler eslesiyor mu kontrol et
        if yeni_sifre != yeni_sifre_tekrar:
            return "Sifreler eslesmiyor."
        
        # yeni sifre eski sifreyle ayni mi kontrol et
        if check_password_hash(eski_sifre_hashed[0], yeni_sifre):
            return "Yeni sifre eski sifre ile ayni olamaz."
        
        # sifre uzunlugu kontrolu
        if len(yeni_sifre) < 6:
            return "Sifre en az 6 karakter olmali."
        
        # sifreyi hashle ve veritabanina kaydeder
        hashed = generate_password_hash(yeni_sifre)
        cursor.execute("UPDATE kullanicilar SET password=%s WHERE username=%s", (hashed, username))
        conn.commit()
        
        # kullanici yoksa rowcount 0 olur
        if cursor.rowcount == 0:
            return "Boyle bir kullanici bulunamadi."
        
        # sifre degisikligi basariliysa anasayfaya yonlendir
        return redirect(url_for('kullanici_anasayfa', username=username))
    
    finally:
        # kaynaklari her durumda kapat
        cursor.close()
        conn.close()

@app.route('/kitapara/<username>', methods=['GET', 'POST'])
def kitapara(username):
    # kullanan kullanicinin kitap aramasi icin 
    conn = database.baglanti_olustur()
    cursor = conn.cursor()
    
    # aranan kitap adini formdan veya url parametresinden alir
    if request.method == 'POST':
        aranan_kitap = request.form.get('aranacak_kitap_adi', '').strip()
    else:
        aranan_kitap = request.args.get('aranacak_kitap_adi', '').strip()
    
    # kitaplar tablosunda kullanicidan alan isim ile arama yapar
    cursor.execute("""
    SELECT isim, yazar, kategori FROM kitaplar 
    WHERE isim LIKE %s OR yazar LIKE %s OR kategori LIKE %s
""", (f"%{aranan_kitap}%", f"%{aranan_kitap}%", f"%{aranan_kitap}%"))

    kitaplar = cursor.fetchall()
    
    # kitaplarin bulunma durumuna gore mesaj olusturur
    if kitaplar:
        mesaj = f"{len(kitaplar)} kitap bulundu."
    else:
        mesaj = "Aradiginiz kitap bulunamadi."
    
    cursor.close()
    conn.close()
    
    return render_template("kitaplar.html", kitaplar=kitaplar, mesaj=mesaj, username=username)


@app.route('/kullanicilar/<username>', methods=['POST', 'GET'])
def kullanicigoster(username):
    # admin kisminda kullanicilari ve idlerini gostermek icin
    conn = database.baglanti_olustur()
    cursor = conn.cursor()
    # kullanicilar tablosundan aktiflik dahil 4 alan secilir
    cursor.execute("SELECT id, username, email, aktiflik FROM kullanicilar")
    kullanicilar = cursor.fetchall()
    conn.close()

    # sessiondan admin username al
    if "username" in session:
        admin_username = session["username"]
    else:
        admin_username = "admin"

    return render_template(
        "kullanicilar.html",
        username=username,
        kullanicilar=kullanicilar,
        admin_username=admin_username
    )    
    
@app.route('/kitapekle/<username>', methods=['POST'])
def kitapekle(username):
    # Sadece adminler kitap ekleyebilir
    if 'role' not in session or session['role'] != 'admin':
        return "Bu islemi yapmak icin yetkiniz yok.", 403

    conn = database.baglanti_olustur()
    cursor = conn.cursor(buffered=True)  # <-- buffered=True eklendi

    # Degiskenleri baslat
    isim = yazar = kategori = yayinevi = ""
    sayfa_sayisi = stok = raf_no = baski_yili = 0
    mesaj = ""
    kitap_id = None

    try:
        # Formdan verileri al ve bosluklari temizle
        isim = request.form.get('kitap_adi', '').strip()
        yazar = request.form.get('kitap_yazari', '').strip()
        kitap_turleri = request.form.getlist('kitap_turu')
        kategori = ','.join(kitap_turleri)
        yayinevi = request.form.get('kitap_yayini','').strip()
        sayfa_sayisi = request.form.get('kitap_sayfa_sayisi', '').strip()
        stok = request.form.get('stok_miktari', '').strip()
        raf_no = request.form.get('raf_no', '').strip()
        baski_yili = request.form.get('baski_yili', '').strip()

        if not (isim and yazar and kategori and sayfa_sayisi and stok and raf_no and baski_yili and yayinevi):
            return "Lutfen tum alanlari doldurun."

        sayfa_sayisi = int(sayfa_sayisi)
        stok = int(stok)
        raf_no = int(raf_no)
        baski_yili = int(baski_yili)

        # Ayni kitap var mi kontrol et (isim + yayinevi)
        cursor.execute(
            "SELECT * FROM kitaplar WHERE isim=%s AND yayinevi=%s",
            (isim, yayinevi)
        )
        mevcut_kitap = cursor.fetchone()
        if mevcut_kitap:
            mesaj = f"Bu kitap zaten ekli! (ID: {mevcut_kitap[0]})"
            return render_template(
                "kitap_islem.html",
                username=username,
                islem_turu="Kitap Ekleme",
                kitap_id=mevcut_kitap[0],
                isim=mevcut_kitap[1],
                yazar=mevcut_kitap[2],
                kategori=mevcut_kitap[3],
                sayfa_sayisi=mevcut_kitap[4],
                stok=mevcut_kitap[5],
                yayinevi=mevcut_kitap[6],
                raf_no=mevcut_kitap[7],
                baski_yili=mevcut_kitap[8],
                mesaj=mesaj
            )

        # Kitabi veritabanina ekle
        cursor.execute(
            "INSERT INTO kitaplar (isim, yazar, kategori, sayfa_sayisi, stok, raf_no, baski_yili, yayinevi) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (isim, yazar, kategori, sayfa_sayisi, stok, raf_no, baski_yili, yayinevi)
        )

        conn.commit()
        kitap_id = cursor.lastrowid
        mesaj = f"Kitap basariyla eklendi! (ID: {kitap_id})"

    except ValueError:
        return "Sayisal alanlara gecerli deger girin."
    except Exception as e:
        conn.rollback()
        return f"Hata olustu: {str(e)}"
    finally:
        cursor.close()
        conn.close()

    return render_template(
        "kitap_islem.html",
        username=username,
        islem_turu="Kitap Ekleme",
        kitap_id=kitap_id,
        isim=isim,
        yazar=yazar,
        kategori=kategori,
        sayfa_sayisi=sayfa_sayisi,
        stok=stok,
        raf_no=raf_no,
        baski_yili=baski_yili,
        yayinevi=yayinevi,
        mesaj=mesaj
    )

    
@app.route('/kitapsil/<username>', methods=['POST'])
def kitapsil(username):
    # Bu fonksiyon admin tarafindan kitap silmek icin kullanilir
    #  sadece admin islemi yapabilir
    if 'role' not in session or session['role'] != 'admin':
        return "Bu islemi yapmak icin yetkiniz yok.", 403

    conn = database.baglanti_olustur()
    cursor = conn.cursor()

    # Formdan kitap adini al ve bosluklari temizle
    kitap_adi = request.form.get('silinecek_kitap_adi', '').strip()
    if not kitap_adi:
        return "Lutfen kitap ismini girin."

    # Tekrar alanindan dogrulama
    kitap_adi_tekrar = request.form.get('silinecek_kitap_adi_tekrar', '').strip()
    if kitap_adi != kitap_adi_tekrar:
        return "Kitap adlari eslesmiyor!"

    try:
        # Kitabi veritabaninda arayip
        cursor.execute("SELECT * FROM kitaplar WHERE isim=%s", (kitap_adi,))
        kitap = cursor.fetchone()
        #yoksa hata verir
        if not kitap:
            return f"Kitap bulunamadi: {kitap_adi}"

        # varsa kitabi siler
        cursor.execute("DELETE FROM kitaplar WHERE isim=%s", (kitap_adi,))
        conn.commit()
        mesaj = f"Kitap basariyla silindi! (ID: {kitap[0]})"

    except Exception as e:
        conn.rollback()
        return f"Hata olustu: {str(e)}"
    finally:
        cursor.close()
        conn.close()


    return render_template(
        "kitap_islem.html",
        username=username,
        islem_turu="Kitap Silme",
        kitap_id=kitap[0],
        isim=kitap[1],
        yazar=kitap[2],
        kategori=kitap[3],
        sayfa_sayisi=kitap[4],
        stok=kitap[5],
        raf_no=kitap[6],
        baski_yili=kitap[7],
        mesaj=mesaj
    )
    
    
@app.route('/adminekle/<username>', methods=['POST'])
def adminekle(username):
    # Bu fonksiyon admin tarafindan yeni admin eklemek icin kullanilir
    # sadece admin islemi yapabilir
    if 'role' not in session or session['role'] != 'admin':
        return "Bu islemi yapmak icin yetkiniz yok.", 403

   
    conn = database.baglanti_olustur()
    cursor = conn.cursor()
    try:
        # Formdan yeni admin bilgilerini alip ve bosluklari temizler
        yeni_admin = request.form.get('yeni_admin_adi', '').strip()
        yeni_admin_email = request.form.get('yeni_admin_email', '').strip()
        yeni_admin_sifre = request.form.get('yeni_admin_sifre', '').strip()
        yeni_admin_sifre_tekrar = request.form.get('yeni_admin_sifre_tekrar', '').strip()

        # Alanlari kontrol eder
        if not (yeni_admin and yeni_admin_email and yeni_admin_sifre and yeni_admin_sifre_tekrar):
            return "Lutfen tum alanlari doldurun."
        if yeni_admin_sifre != yeni_admin_sifre_tekrar:
            return "Sifreler eslesmiyor!"
        if len(yeni_admin_sifre) < 6:
            return "Sifre en az 6 karakter olmali."

        # Ayni username veya email var mi kontrol edip varsa hata verir
        cursor.execute("SELECT * FROM admin WHERE username=%s OR email=%s", (yeni_admin, yeni_admin_email))
        if cursor.fetchone():
            return f"'{yeni_admin}' veya '{yeni_admin_email}' zaten kayitli!"

        # yoksa Sifreyi hashleyip ve tabloya ekler
        hashed_password = generate_password_hash(yeni_admin_sifre)
        cursor.execute(
            "INSERT INTO admin (username, email, password) VALUES (%s,%s,%s)",
            (yeni_admin, yeni_admin_email, hashed_password)
        )
        conn.commit()
        mesaj = f"Admin '{yeni_admin}' basariyla eklendi. <br>ID: {cursor.lastrowid}"
        return f"{mesaj} <br><a href='{url_for('admin_anasayfa', username=username)}'>Geri Don</a>"

    finally:
        cursor.close()
        conn.close()


@app.route('/adminsil/<username>', methods=['POST'])
def adminsil(username):
    #admin tarafindan admin silmek icin kullanilir
    #rolu konttrol eder
    if 'role' not in session or session['role'] != 'admin':
        return "Bu islemi yapmak icin yetkiniz yok.", 403

    conn = database.baglanti_olustur()
    cursor = conn.cursor()
    try:
        # Formdan silinecek admin bilgilerini alir
        silinecek_admin_1 = request.form.get('silinecek_admin_adi', '').strip()
        silinecek_admin_2 = request.form.get('silinecek_admin_adi_tekrar', '').strip()

        # Alanlari kontrol eder
        if not silinecek_admin_1 or not silinecek_admin_2:
            return "Lutfen her iki alani da doldurun."
        if silinecek_admin_1 != silinecek_admin_2:
            return "Admin adlari eslesmiyor!"

        # Admini siler
        cursor.execute("DELETE FROM admin WHERE username=%s", (silinecek_admin_1,))
        conn.commit()
        mesaj = f"Admin '{silinecek_admin_1}' basariyla silindi." if cursor.rowcount else "Boyle bir admin bulunamadi."
        return f"{mesaj} <br><a href='{url_for('admin_anasayfa', username=username)}'>Geri Don</a>"

    finally:
        cursor.close()
        conn.close()
        
@app.route('/kullaniciekle/<username>', methods=['POST'])
def kullaniciekle(username):
    # admin tarafindan yeni kullanici eklemek icin 
    # Sadece admin islemi yapabilir
    if 'role' not in session or session['role'] != 'admin':
        return "Bu islemi yapmak icin yetkiniz yok.", 403

    conn = database.baglanti_olustur()
    cursor = conn.cursor()
    try:
        # Formdan yeni kullanici bilgilerini alip bosluklari temizler
        yeni_kullanici = request.form.get('yeni_kullanici_adi', '').strip()
        yeni_kullanici_email = request.form.get('yeni_kullanici_email', '').strip()
        yeni_kullanici_sifre = request.form.get('yeni_kullanici_sifre', '').strip()
        yeni_kullanici_sifre_tekrar = request.form.get('yeni_kullanici_sifre_tekrar', '').strip()

        # Alanlari kontrol eder
        if not (yeni_kullanici and yeni_kullanici_email and yeni_kullanici_sifre and yeni_kullanici_sifre_tekrar):
            return "Lutfen tum alanlari doldurun."
        if yeni_kullanici_sifre != yeni_kullanici_sifre_tekrar:
            return "Sifreler eslesmiyor!"
        if len(yeni_kullanici_sifre) < 6:
            return "Sifre en az 6 karakter olmali."

        # Ayni username veya email var mi kontrol eder
        cursor.execute("SELECT * FROM kullanicilar WHERE username=%s OR email=%s", (yeni_kullanici, yeni_kullanici_email))
        if cursor.fetchone():
            return f"'{yeni_kullanici}' veya '{yeni_kullanici_email}' zaten kayitli!"

        #yoksa Sifreyi hashleyip ve tabloya ekler
        hashed_password = generate_password_hash(yeni_kullanici_sifre)
        cursor.execute(
            "INSERT INTO kullanicilar (username, email, password) VALUES (%s,%s,%s)",
            (yeni_kullanici, yeni_kullanici_email, hashed_password)
        )
        conn.commit()
        mesaj = f"Kullanici '{yeni_kullanici}' basariyla eklendi. <br>ID: {cursor.lastrowid}"
        return f"{mesaj} <br><a href='{url_for('admin_anasayfa', username=username)}'>Geri Don</a>"

    finally:
        cursor.close()
        conn.close()
        
@app.route('/kullanicipasif', methods=['POST'])
def kullanici_pasif():
    if 'role' not in session or session['role'] != 'admin':
        return "Bu işlemi yapmak için yetkiniz yok.", 403

    kullanici_adi = request.form.get("kullanici_adi", "").strip()
    if not kullanici_adi:
        return "Lütfen kullanıcı adını girin."

    conn = database.baglanti_olustur()
    cursor = conn.cursor(buffered=True)
    try:
        cursor.execute("SELECT id, aktiflik FROM kullanicilar WHERE username=%s", (kullanici_adi,))
        row = cursor.fetchone()
        if not row:
            return f"Kullanıcı bulunamadı: {kullanici_adi}"

        kullanici_id, aktiflik = row

        # Ödenmemiş ceza kontrolü
        cursor.execute("SELECT * FROM cezalar WHERE kullanici_id=%s AND odeme_durumu=0", (kullanici_id,))
        ceza = cursor.fetchone()
        if ceza:
            return f"Kullanıcının ödenmemiş cezası var! Ceza ID: {ceza[0]}, Miktar: {ceza[2]} TL."

        # İade edilmemiş kitap kontrolü
        cursor.execute("SELECT * FROM oduncler WHERE kullanici_id=%s AND iade_tarihi IS NULL", (kullanici_id,))
        odunc = cursor.fetchone()
        if odunc:
            return f"Kullanıcının iade etmediği kitap(lar) var! Ödünç ID: {odunc[0]}, Kitap ID: {odunc[2]}. Önce kitapları iade etmelidir."

        # Ceza yok ve tüm kitaplar iade edilmişse pasif yapar
        cursor.execute("UPDATE kullanicilar SET aktiflik=0 WHERE id=%s", (kullanici_id,))
        conn.commit()
        return f"Kullanıcı '{kullanici_adi}' artık pasif durumda."

    except Exception as e:
        conn.rollback()
        return f"Hata oluştu: {str(e)}"
    finally:
        cursor.close()
        conn.close()
 
@app.route('/kullanici/aktiflestir/<int:kullanici_id>', methods=['POST'])
def kullanici_aktiflestir(kullanici_id):
    if 'role' not in session or session['role'] != 'admin':
        return "Yetkiniz yok.", 403

    conn = database.baglanti_olustur()
    cursor = conn.cursor()
    cursor.execute("UPDATE kullanicilar SET aktiflik=1 WHERE id=%s", (kullanici_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('kullanicigoster', username=session['username']))
        
@app.route('/adminsifremidegistir/<username>', methods=['POST'])
def adminsifremidegis(username):
    # adminin kendi sifresini degistirmesi icin
    # Formdan gelen yeni sifreyi alir, kontrol eder ve hashleyip veritabani gunceller
    try:
        conn = database.baglanti_olustur()
        cursor = conn.cursor()
        if 'role' not in session or session['role'] != 'admin':
         return "Bu islemi yapmak icin yetkiniz yok.", 403
        # Formdan sifreleri alip ve bosluklari temizler
        yeni_sifre = request.form.get('yeni_sifre', '').strip()
        yeni_sifre_tekrar = request.form.get('yeni_sifre_tekrar', '').strip()

        # Alanlari kontrol eder
        if not yeni_sifre or not yeni_sifre_tekrar:
            return "Lutfen her iki alani da doldurun."
        if yeni_sifre != yeni_sifre_tekrar:
            return "Sifreler eslesmiyor."
        if len(yeni_sifre) < 6:
            return "Sifre en az 6 karakter olmali."

        # Sifreyi hashleyip
        hashed = generate_password_hash(yeni_sifre)

        # Veritabaninda adminin sifresini gunceller
        cursor.execute("UPDATE admin SET password=%s WHERE username=%s", (hashed, username))
        conn.commit()

        # Eğer admin bulunamazsa uyarir
        if cursor.rowcount == 0:
            return "Boyle bir admin bulunamadi."

        # Basarili ise admin anasayfasina yonlendir
        return redirect(url_for('admin_anasayfa', username=username))

    finally:
        cursor.close()
        conn.close()
        
@app.route('/kitapoduncver/<username>', methods=['POST'])
def kitapoduncver(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor(buffered=True)
    
    if 'role' not in session or session['role'] != 'admin':
        return "Bu islemi yapmak icin yetkiniz yok.", 403

    try:
        # Formdan kullanici ve kitapi alir
        kullanici_adi = request.form.get("verilcek_kullanici_adi", "").strip()
        kitap_adi = request.form.get("verilcek_kitap_adi", "").strip()
        verildigi_tarih_str = request.form.get("verildigi_tarih", "").strip()

        if not (kullanici_adi and kitap_adi and verildigi_tarih_str):
            mesaj = "Lutfen tum alanlari doldurun."
            return render_template("odunc.html", username=username, mesaj=mesaj)

        # Kullanıcının aktifliğini kontrol et
        cursor.execute("SELECT id, aktiflik FROM kullanicilar WHERE username=%s", (kullanici_adi,))
        row = cursor.fetchone()
        if not row:
            mesaj = f"Kullanici bulunamadi: {kullanici_adi}"
            return render_template("odunc.html", username=username, mesaj=mesaj)

        kullanici_id, aktiflik = row
        if not aktiflik:
            mesaj = f"Kullanici '{kullanici_adi}' pasif durumda! Önce kullanıcıyı aktifleştirin."
            return render_template("odunc.html", username=username, mesaj=mesaj)

        # string olarak gelen tarihi datetime objesine cevirip
        verildigi_tarih = datetime.strptime(verildigi_tarih_str, "%Y-%m-%d")
        gerekli_iade_tarihi = verildigi_tarih + timedelta(days=15)
        gerekli_iade_tarihi_str = gerekli_iade_tarihi.strftime("%Y-%m-%d")

        # Kitap ID ve stok alir ve tabloda yoksa ya da stokta yoksa uyarir
        cursor.execute("SELECT id, stok FROM kitaplar WHERE isim=%s", (kitap_adi,))
        row = cursor.fetchone()
        if not row:
            mesaj = f"Kitap bulunamadi: {kitap_adi}"
            return render_template("odunc.html", username=username, mesaj=mesaj)
        kitap_id, stok = row
        if stok <= 0:
            mesaj = f"Bu kitap stokta yok! (Kitap: {kitap_adi})"
            return render_template("odunc.html", username=username, mesaj=mesaj)

        # Kullanıcının ödenmemiş cezasını kontrol et
        cursor.execute("""
            SELECT * FROM cezalar 
            WHERE kullanici_id = %s AND odeme_durumu = 0
        """, (kullanici_id,))
        ceza = cursor.fetchone()
        if ceza:
            mesaj = f"Kullanicinin odenmemis cezası var! Ceza ID: {ceza['ceza_id']}, Miktar: {ceza['ceza_miktari']} TL. Önce ceza ödenmeli."
            return render_template("odunc.html", username=username, mesaj=mesaj)

        # Aktif odunc sayisini kontrol eder 5 den fazlaysa hata verir
        cursor.execute("SELECT COUNT(*) FROM oduncler WHERE kullanici_id=%s AND gercek_iade_tarihi IS NULL", (kullanici_id,))
        aktif_oduncler = cursor.fetchone()[0]
        if aktif_oduncler >= 5:
            mesaj = "Kullanici zaten 5 veya daha fazla kitap odunc almis! Once mevcut kitaplari iade edin."
            return render_template("odunc.html", username=username, mesaj=mesaj)

        # kitabi zaten guncel olarak odunc aalmissa kontrol eder
        cursor.execute("SELECT * FROM oduncler WHERE kullanici_id=%s AND kitap_id=%s AND gercek_iade_tarihi IS NULL", (kullanici_id, kitap_id))
        if cursor.fetchone():
            mesaj = "Kullanici bu kitabi henuz iade etmedi! Ayni kitap tekrar verilemez."
            return render_template("odunc.html", username=username, mesaj=mesaj)

        # tum kriterleri sagladiysa kitabin stogunu gunceller
        cursor.execute("UPDATE kitaplar SET stok = stok - 1 WHERE id=%s", (kitap_id,))

        # Odunc kaydi ekler
        cursor.execute("INSERT INTO oduncler (kullanici_id, kitap_id, odunc_tarihi, gerekli_iade_tarihi) VALUES (%s, %s, %s, %s)",
                       (kullanici_id, kitap_id, verildigi_tarih_str, gerekli_iade_tarihi_str))
        conn.commit()

        odunc_id = cursor.lastrowid
        mesaj = (
            f"Kitap basariyla odunc verildi.<br>"
            f"Odunc ID: {odunc_id}<br>"
            f"Kullanici: {kullanici_adi} (ID: {kullanici_id}), Kitap: {kitap_adi} (ID: {kitap_id})<br>"
            f"Gerekli iade tarihi: {gerekli_iade_tarihi_str}"
        )
        return render_template("odunc.html", username=username, mesaj=mesaj)

    except Exception as e:
        conn.rollback()
        return render_template("odunc.html", username=username, mesaj=f"Hata olustu: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.route('/kitapiadeal/<username>', methods=['POST'])
def kitapiadeal(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor()

    # sadece admin yapabilir
    if 'role' not in session or session['role'] != 'admin':
        return "Bu islemi yapmak icin yetkiniz yok.", 403

    try:
        # kullaniciya odunc verirken verdigimiz id yi istiyoruz ve formdan odunc IDi aliyoruz
        odunc_id = int(request.form.get("odunc_id", "").strip())
        # Bugunun tarihini iade tarihi olarak aliyoruz
        iade_tarihi = datetime.now().date()

        # Odunc kaydini verilen bilgilere gore aliyoruz
        cursor.execute(
            "SELECT kullanici_id, kitap_id, odunc_tarihi, gerekli_iade_tarihi, gercek_iade_tarihi "
            "FROM oduncler WHERE id=%s",
            (odunc_id,)
        )
        odunc = cursor.fetchone()
        if not odunc:
            return "Gecersiz odunc ID."

        kullanici_id, kitap_id, odunc_verilis_tarihi, gerekli_iade_tarihi, mevcut_iade_tarihi = odunc

        # Eger kitap zaten iade edilmisse islemi durduruoz
        if mevcut_iade_tarihi:
            return "Bu odunc zaten iade edilmis."

        # degilse odunc kaydini guncellioz gercek_iade_tarihi ile iade edildi olarak isaretle
        cursor.execute(
            "UPDATE oduncler SET gercek_iade_tarihi=%s WHERE id=%s",
            (iade_tarihi, odunc_id)
        )

        # Kitap stokunu geri ekle
        cursor.execute(
            "UPDATE kitaplar SET stok = stok + 1 WHERE id=%s",
            (kitap_id,)
        )

        conn.commit()

        # Kullaniciya mesaj goster
        mesaj = f"Kitap (ID: {kitap_id}) basariyla iade edildi."

        return mesaj + f" <br><a href='{url_for('admin_anasayfa', username=username)}'>Geri Don</a>"

    finally:
        cursor.close()
        conn.close()
 
 
# Kullanıcının kendi odunc gecmisini gormesi icin
@app.route('/oduncalmagecmisim/<username>')
def oduncalmagecmisim(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor(dictionary=True)

    # Sadece kullanici yapabilsin
    if 'role' not in session or session['role'] != 'user':
        return "Bu islemi yapmak icin yetkiniz yok.", 403

    try:
        # Önce username ile kullanici id'sini aliyoruz
        cursor.execute("SELECT id FROM kullanicilar WHERE username=%s", (username,))
        kullanici = cursor.fetchone()
        if not kullanici:
            return "Kullanici bulunamadi."
        kullanici_id = kullanici['id']

        # Odunc gecmisini cekiyoruz, kitap adini ic ice select ile aliyoruz
        cursor.execute("""
            SELECT 
                id,  
                (SELECT isim FROM kitaplar WHERE id = kitap_id) AS kitap, 
                odunc_tarihi, 
                gerekli_iade_tarihi,  
                gercek_iade_tarihi  
            FROM oduncler
            WHERE kullanici_id = %s
        """, (kullanici_id,))
        # WHERE kullanici_id = %s kısmıyla sadece ilgili kullanıcının kayıtları secilip
        # Sorguda id, odunc_tarihi, gerekli_iade_tarihi ve gercek_iade_tarihi ozellikleri direkt tablodan aliniyor
        # kitap adi icin de her odunc kaydindaki kaydındaki kitap_id değerini kitaplar tablosundaki id ile eslestirerek kitabın adını getirir ve bunu kitap olarak adlandırıyor. Böylece, her ödünç kaydı için hem kayıt ID’si hem kitabın adı hem de veriliş ve iade tarihleri tek bir sorguda elde edilebiliyor.

        oduncler = cursor.fetchall()  # Tum oduncler buraya gelir

        #  kullanici kendi odunc gecmisini gorecek
        return render_template("odunc_gecmisim.html", username=username, oduncler=oduncler)

    finally:
        cursor.close()
        conn.close()



#admin icin tum kullanicilarin odunc gecmisini goster 
@app.route('/tumkullanicioduncalmagecmisigoster/<username>')
def tumkullanicioduncalmagecmisigoster(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor(dictionary=True)
    try:
        # admin kontrolu
        cursor.execute("SELECT * FROM admin WHERE username=%s", (username,))
        if not cursor.fetchone():
            return "Yetkisiz erisim!", 403

        # tum odunc gecmisleri aliniyor
        # kullanici adi ve kitap adi ic ice select ile alinio
        cursor.execute("""
            SELECT 
                id,  
                (SELECT username FROM kullanicilar WHERE id = kullanici_id) AS kullanici,
                (SELECT isim FROM kitaplar WHERE id = kitap_id) AS kitap,
                odunc_tarihi,
                gerekli_iade_tarihi,
                gercek_iade_tarihi
            FROM oduncler
        """)
        oduncler = cursor.fetchall()  # Tum odunc gecmisleri liste olarak alinir
        return render_template("tum_odunc_gecmisi.html", username=username, oduncler=oduncler)
    finally:
        cursor.close()
        conn.close()


#  admin icin tum cezalar
@app.route('/cezatablosunugoster/<username>')
def cezatablosunugoster(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor(dictionary=True)
    try:
        # Admin kontrolu
        cursor.execute("SELECT * FROM admin WHERE username=%s", (username,))
        if not cursor.fetchone():
            return "Yetkisiz erisim!", 403

        # Tum cezalar aliniyor
        cursor.execute("""
            SELECT 
                id,
                (SELECT username FROM kullanicilar WHERE id = kullanici_id) AS kullanici,
                (SELECT isim FROM kitaplar WHERE id = kitap_id) AS kitap,
                ceza_miktari,
                odunc_tarihi,
                iade_tarihi,
                odeme_durumu
            FROM cezalar
        """)
        cezalar = cursor.fetchall()

        # odeme_durumu integer olarak cevirioruz
        for ceza in cezalar:
            ceza['odeme_durumu'] = int(ceza['odeme_durumu'])

        return render_template("tum_cezalar.html", username=username, cezalar=cezalar)
    finally:
        cursor.close()
        conn.close()



# Kullaniciya ozel cezalar
@app.route('/cezalarimigoster/<username>')
def cezalarimigoster(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor(dictionary=True)
    try:
        # Kullanici id'si aliniyor
        cursor.execute("SELECT id FROM kullanicilar WHERE username=%s", (username,))
        kullanici = cursor.fetchone()
        if not kullanici:
            return "Kullanici bulunamadi."
        kullanici_id = kullanici['id']

        # Cezalar cekiliyor, kitap adi ic ice select ile aliniyor
        cursor.execute("""
            SELECT 
                id,
                (SELECT isim FROM kitaplar WHERE id = kitap_id) AS kitap,
                ceza_miktari,
                odunc_tarihi,
                iade_tarihi
            FROM cezalar
            WHERE kullanici_id = %s
        """, (kullanici_id,))
        cezalar = cursor.fetchall()  # Tum cezalar listeleniyor
        return render_template("cezalarim.html", username=username, cezalar=cezalar)
    finally:
        cursor.close()
        conn.close()

@app.route('/cezaode', methods=['POST'])
def ceza_ode():

    # Formdan ya da JSON'dan veri alma
    if request.is_json:
        veri = request.get_json()  # Eger istek JSON formatindaysa veriyi JSON olarak al
    else:
        veri = request.form        # Degilse form verisini al

    # Kullanici ID ve odeme istegi
    kullanici_id = veri.get('kullanici_id')  # Kullanici ID
    odeme_yapilsin_mi = veri.get('odeme_yapilsin_mi', True)  # Eger gonderilmezse True varsayiyoruz

    #  Kullanici ID bossa hata dondur
    if not kullanici_id or kullanici_id.strip() == "":
        return jsonify({
            'success': False,
            'message': 'Kullanici ID gereklidir!'
        }), 400

    #  Veritabani baglantisini olustur
    conn = database.baglanti_olustur()
    cursor = conn.cursor(dictionary=True)

    try:
        #  Kullanicinin odenmemis tum cezalarini sorgula
        cursor.execute("""
    SELECT COUNT(*) as toplam_ceza, IFNULL(SUM(ceza_miktari), 0) as toplam_tutar
    FROM cezalar
    WHERE kullanici_id = %s AND odeme_durumu = 0
""", (kullanici_id,))

        ceza_bilgisi = cursor.fetchone()

        #  Eger kullaniciya ait odenmemis ceza yoksa uygun mesaji  verir
        if ceza_bilgisi['toplam_ceza'] == 0 or ceza_bilgisi['toplam_tutar'] is None:
            return jsonify({
                'success': False,
                'message': 'Bu kullanicinin odenecek cezasi bulunmamaktadir!'
            }), 404

        #  Eger sadece ceza bilgisini almak istiyorsak (odeme yapilmayacaksa)
        if not odeme_yapilsin_mi:
            return jsonify({
                'success': True,
                'toplam_tutar': ceza_bilgisi['toplam_tutar']
            })

        # tum cezalari odenmis olarak isaretle
        cursor.execute("""
            UPDATE cezalar 
            SET odeme_durumu = True
            WHERE kullanici_id = %s AND odeme_durumu = 0
        """, (kullanici_id,))
        conn.commit()

        # Islem sonucu mesaji
        return jsonify({
            'success': True,
            'message': f"{cursor.rowcount} ceza basariyla odendi! Toplam tutar: {ceza_bilgisi['toplam_tutar']} TL"
        })

    except Exception as hata:
        #  Hata durumunda mesaj
        conn.rollback()
        return jsonify({
            'success': False,
            'message': f'Database hatasi: {str(hata)}'
        }), 500

    finally:
        cursor.close()
        conn.close()
   
@app.route('/cezamailleri', methods=['POST'])
def ceza_mailleri():
    # Yetki kontrolü
    if 'role' not in session or session['role'] != 'admin':
        return "Yetkiniz yok.", 403

    from_email = session.get('email') or "InfoCatlary@gmail.com"
    from_password = "txap mmnt wimh cxtb"  # Gmail App Password

    conn = database.baglanti_olustur()
    cursor = conn.cursor(dictionary=True)

    hatali_mailler = []
    basarili_mailler = []

    try:
        bugun = datetime.today().date()
        cursor.execute("SELECT * FROM oduncler WHERE gercek_iade_tarihi IS NULL")
        oduncler = cursor.fetchall()
        print(f"Toplam iade edilmemiş kitap: {len(oduncler)}")

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, from_password)
            print("SMTP girişi başarılı")

            for odunc in oduncler:
                try:
                    gerekli_iade = odunc['gerekli_iade_tarihi']

                    # Tarih formatını kontrol et
                    if isinstance(gerekli_iade, str):
                        try:
                            gerekli_iade = datetime.strptime(gerekli_iade, "%Y-%m-%d").date()
                        except ValueError:
                            gerekli_iade = datetime.strptime(gerekli_iade, "%Y-%m-%d %H:%M:%S").date()

                    ara_gun = (bugun - gerekli_iade).days

                    # Gecikme varsa işlem yap
                    if ara_gun > 0:
                        ceza_miktari = ara_gun * 5
                        print(f"Ödünç ID {odunc['id']}: ara_gun = {ara_gun}, ceza = {ceza_miktari}")

                        # Kullanıcı bilgileri
                        cursor.execute(
                            "SELECT username, email FROM kullanicilar WHERE id=%s",
                            (odunc['kullanici_id'],)
                        )
                        kullanici = cursor.fetchone()
                        if not kullanici:
                            print(f"Kullanıcı ID {odunc['kullanici_id']} bulunamadı.")
                            continue
                        if not kullanici['email']:
                            print(f"Kullanıcı {kullanici['username']} e-mail adresi yok.")
                            hatali_mailler.append(f"{kullanici['username']} (e-mail yok)")
                            continue

                        username = kullanici['username']
                        email = kullanici['email']

                        # Kitap bilgisi
                        cursor.execute("SELECT isim FROM kitaplar WHERE id=%s", (odunc['kitap_id'],))
                        kitap_satir = cursor.fetchone()
                        kitap = kitap_satir['isim'] if kitap_satir else "Bilinmiyor"

                        # Ceza kaydı ekle/güncelle
                        cursor.execute("""
                            SELECT id FROM cezalar 
                            WHERE kullanici_id=%s AND kitap_id=%s
                        """, (odunc['kullanici_id'], odunc['kitap_id']))
                        ceza_var_mi = cursor.fetchone()

                        if ceza_var_mi:
                            cursor.execute("""
                                UPDATE cezalar
                                SET ceza_miktari=%s, iade_tarihi=%s
                                WHERE id=%s
                            """, (ceza_miktari, bugun, ceza_var_mi['id']))
                        else:
                            cursor.execute("""
                                INSERT INTO cezalar (kullanici_id, kitap_id, ceza_miktari, odunc_tarihi, iade_tarihi)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (odunc['kullanici_id'], odunc['kitap_id'], ceza_miktari, odunc['odunc_tarihi'], bugun))
                        conn.commit()

                        # Mail içeriği
                        konu = f"Kitap iade gecikmesi (ID: {odunc['id']}): {kitap}"
                        icerik = (
                            f"Merhaba {username},\n\n"
                            f"{kitap} isimli kitabın (Ödünç ID: {odunc['id']}) "
                            f"{gerekli_iade} tarihinde iade edilmesi gerekiyordu.\n"
                            f"Bugün: {bugun}\n"
                            f"Gecikme süresi: {ara_gun} gün\n"
                            f"Ceza miktarı: {ceza_miktari} TL\n\n"
                            f"Lütfen kitabı en kısa sürede iade ediniz.\n\n"
                            f"Saygılarımızla,\nKutuphane Yönetimi"
                        )

                        basarili = send_mail(server, from_email, email, konu, icerik)
                        if basarili:
                            basarili_mailler.append({
                                "username": username,
                                "email": email,
                                "kitap": kitap,
                                "ceza": ceza_miktari,
                                "odunc_id": odunc['id']
                            })
                        else:
                            hatali_mailler.append(email)

                except Exception as e:
                    print(f"Ödünç ID {odunc['id']} için hata: {e}")
                    continue

        # Sonuç mesajı
        sonuc_mesaji = f"Toplam {len(basarili_mailler)} mail başarıyla gönderildi.\n\n"
        if basarili_mailler:
            sonuc_mesaji += "📧 Gönderilen mailler:\n"
            for m in basarili_mailler:
                sonuc_mesaji += f"- {m['username']} ({m['email']}) → {m['kitap']} (Ceza: {m['ceza']} TL, Ödünç ID: {m['odunc_id']})\n"
        if hatali_mailler:
            sonuc_mesaji += f"\nHatalı gönderimler: {', '.join(hatali_mailler)}"

        print(sonuc_mesaji)
        return sonuc_mesaji

    except Exception as e:
        print(f"Genel hata: {e}")
        return f"Sistem hatası: {e}", 500

    finally:
        cursor.close()
        conn.close()

def send_mail(server, from_email, to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        server.send_message(msg)
        return True
    except Exception as e:
        print(f"Mail gonderilemedi: {e}")
        return False


if __name__ == "__main__":
    app.run(debug=True)
