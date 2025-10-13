from flask import Flask, jsonify, request, render_template, redirect, url_for
import database
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
#database.db_sil()
database.db_olustur()
database.tablolar_olustur()

@app.route('/')
def anasayfa():
    return render_template("index.html")

@app.route('/girisyap', methods=['POST'])
def giris_yap():
    islem_tipi = request.form.get('islem')
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()

    conn = database.baglanti_olustur()
    cursor = conn.cursor()

    if islem_tipi == "kullanici":
        cursor.execute("SELECT username, password FROM kullanicilar WHERE email=%s", (email,))
        row = cursor.fetchone()
        conn.close()
        if row and check_password_hash(row[1], password):
            return redirect(url_for("kullanici_anasayfa", username=row[0]))
        else:
            return "Email veya şifre yanlış!", 401

    elif islem_tipi == "admin":
        cursor.execute("SELECT username, password FROM admin WHERE email=%s", (email,))
        row = cursor.fetchone()
        conn.close()
        if row and check_password_hash(row[1], password):
            return redirect(url_for("admin_anasayfa", username=row[0]))
        else:
            return "Admin email veya şifre yanlış!", 401

    elif islem_tipi == "yeni":
        yeni_username = request.form.get('username', '').strip()
        yeni_sifre = request.form.get('yeni_sifre', '').strip()
        yeni_sifre_tekrar = request.form.get('yeni_sifre_tekrar', '').strip()

        if not (yeni_username and email and yeni_sifre and yeni_sifre_tekrar):
            return "Lütfen tüm alanları doldurun."

        if yeni_sifre != yeni_sifre_tekrar:
            return "Şifreler eşleşmiyor."

        if len(yeni_sifre) < 6:
            return "Şifre en az 6 karakter olmalı."

        try:
            hashed_password = generate_password_hash(yeni_sifre)
            cursor.execute(
                "INSERT INTO kullanicilar (username, email, password) VALUES (%s, %s, %s)",
                (yeni_username, email, hashed_password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("kullanici_anasayfa", username=yeni_username))
        except Exception as e:
            conn.close()
            return f"Hesap oluşturulamadı! Hata: {str(e)}", 400

@app.route('/kullanici/<username>')
def kullanici_anasayfa(username):
    return render_template("kullanici.html", username=username)

@app.route('/admin/<username>')
def admin_anasayfa(username):
    return render_template("admin.html", username=username)

@app.route('/kitaplari_goruntule/<username>', methods=['GET', 'POST'])
def kitaplari_goruntule(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin WHERE username=%s", (username,))
    admin_mi = cursor.fetchone() is not None
    aranan_kitap = request.form.get('aranacak_kitap', '').strip() if request.method == 'POST' else request.args.get('aranacak_kitap', '').strip()
    
    if aranan_kitap:
        cursor.execute("SELECT isim, yazar, kategori FROM kitaplar WHERE isim LIKE %s", ('%' + aranan_kitap + '%',))
    else:
        cursor.execute("SELECT isim, yazar, kategori FROM kitaplar")
    
    kitaplar = cursor.fetchall()
    conn.close()
    return render_template("kitaplar.html", kitaplar=kitaplar, username=username, aranan_kitap=aranan_kitap, admin_mi=admin_mi)

@app.route('/kullanicisifredegis/<username>', methods=['POST'])
def sifredegis(username):
    try:
        conn = database.baglanti_olustur()
        cursor = conn.cursor()
        yeni_sifre = request.form.get('yeni_sifre', '').strip()
        yeni_sifre_tekrar = request.form.get('yeni_sifre_tekrar', '').strip()
        if not yeni_sifre or not yeni_sifre_tekrar:
            return "Lütfen her iki alanı da doldurun."
        if yeni_sifre != yeni_sifre_tekrar:
            return "Şifreler eşleşmiyor."
        if len(yeni_sifre) < 6:
            return "Şifre en az 6 karakter olmalı."
        hashed = generate_password_hash(yeni_sifre)
        cursor.execute("UPDATE kullanicilar SET password=%s WHERE username=%s", (hashed, username))
        conn.commit()
        if cursor.rowcount == 0:
            return "Böyle bir kullanıcı bulunamadı."
        return redirect(url_for('kullanici_anasayfa', username=username))
    finally:
        cursor.close()
        conn.close()

@app.route('/kitapara/<username>', methods=['GET', 'POST'])
def kitapara(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor()
    aranan_kitap = request.form.get('aranacak_kitap_adi', '').strip() if request.method == 'POST' else request.args.get('aranacak_kitap_adi', '').strip()
    cursor.execute("SELECT isim, yazar, kategori FROM kitaplar WHERE isim LIKE %s", ('%' + aranan_kitap + '%',))
    kitaplar = cursor.fetchall()
    mesaj = f"{len(kitaplar)} kitap bulundu." if kitaplar else "Aradığınız kitap bulunamadı."
    conn.close()
    return render_template("kitaplar.html", kitaplar=kitaplar, mesaj=mesaj, username=username)

@app.route('/kitapekle/<username>', methods=['POST'])
def kitapekle(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor()
    isim = request.form.get('kitap_adi', '').strip()
    yazar = request.form.get('kitap_yazari', '').strip()
    kategori = request.form.get('kitap_turu', '').strip()
    sayfa_sayisi = request.form.get('kitap_sayfa_sayisi', '').strip()
    stok = request.form.get('stok_miktari', '').strip()
    raf_no = request.form.get('raf_no', '').strip()
    baski_yili = request.form.get('baski_yili', '').strip()
    if not (isim and yazar and kategori and sayfa_sayisi and stok and raf_no and baski_yili):
        return "Lütfen tüm alanları doldurun."
    try:
        sayfa_sayisi = int(sayfa_sayisi)
        stok = int(stok)
        raf_no = int(raf_no)
        baski_yili = int(baski_yili)
    except ValueError:
        return "Sayı alanlarına geçerli değer girin."
    cursor.execute(
        "INSERT INTO kitaplar (isim, yazar, kategori, sayfa_sayisi, stok, raf_no, baski_yili) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (isim, yazar, kategori, sayfa_sayisi, stok, raf_no, baski_yili)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('admin_anasayfa', username=username))

@app.route('/kitapsil/<username>', methods=['POST'])
def kitapsil(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor()
    kitap_adi = request.form.get('silinecek_kitap_adi', '').strip()
    if not kitap_adi:
        return "Lütfen kitap ismini girin."
    cursor.execute("DELETE FROM kitaplar WHERE isim=%s", (kitap_adi,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_anasayfa', username=username))

@app.route('/adminekle/<username>', methods=['POST'])
def adminekle(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor()
    try:
        yeni_admin = request.form.get('yeni_admin_adi', '').strip()
        yeni_admin_email = request.form.get('yeni_admin_email', '').strip()
        yeni_admin_sifre = request.form.get('yeni_admin_sifre', '').strip()
        yeni_admin_sifre_tekrar = request.form.get('yeni_admin_sifre_tekrar', '').strip()
        if not (yeni_admin and yeni_admin_email and yeni_admin_sifre and yeni_admin_sifre_tekrar):
            return "Lütfen tüm alanları doldurun."
        if yeni_admin_sifre != yeni_admin_sifre_tekrar:
            return "Şifreler eşleşmiyor!"
        if len(yeni_admin_sifre) < 6:
            return "Şifre en az 6 karakter olmalı."
        cursor.execute("SELECT * FROM admin WHERE username=%s OR email=%s", (yeni_admin, yeni_admin_email))
        if cursor.fetchone():
            return f"'{yeni_admin}' veya '{yeni_admin_email}' zaten kayıtlı!"
        hashed_password = generate_password_hash(yeni_admin_sifre)
        cursor.execute("INSERT INTO admin (username, email, password) VALUES (%s,%s,%s)", (yeni_admin, yeni_admin_email, hashed_password))
        conn.commit()
        mesaj = f"Admin '{yeni_admin}' başarıyla eklendi. <br>ID: {cursor.lastrowid}"
        return f"{mesaj} <br><a href='{url_for('admin_anasayfa', username=username)}'>Geri Dön</a>"
    finally:
        cursor.close()
        conn.close()

@app.route('/adminsil/<username>', methods=['POST'])
def adminsil(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor()
    try:
        silinecek_admin_1 = request.form.get('silinecek_admin_adi', '').strip()
        silinecek_admin_2 = request.form.get('silinecek_admin_adi_tekrar', '').strip()
        if not silinecek_admin_1 or not silinecek_admin_2:
            return "Lütfen her iki alanı da doldurun."
        if silinecek_admin_1 != silinecek_admin_2:
            return "Admin adları eşleşmiyor!"
        cursor.execute("DELETE FROM admin WHERE username=%s", (silinecek_admin_1,))
        conn.commit()
        mesaj = f"Admin '{silinecek_admin_1}' başarıyla silindi." if cursor.rowcount else "Böyle bir admin bulunamadı."
        return f"{mesaj} <br><a href='{url_for('admin_anasayfa', username=username)}'>Geri Dön</a>"
    finally:
        cursor.close()
        conn.close()

@app.route('/kullaniciekle/<username>', methods=['POST'])
def kullaniciekle(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor()
    try:
        yeni_kullanici = request.form.get('yeni_kullanici_adi', '').strip()
        yeni_kullanici_email = request.form.get('yeni_kullanici_email', '').strip()
        yeni_kullanici_sifre = request.form.get('yeni_kullanici_sifre', '').strip()
        yeni_kullanici_sifre_tekrar = request.form.get('yeni_kullanici_sifre_tekrar', '').strip()
        if not (yeni_kullanici and yeni_kullanici_email and yeni_kullanici_sifre and yeni_kullanici_sifre_tekrar):
            return "Lütfen tüm alanları doldurun."
        if yeni_kullanici_sifre != yeni_kullanici_sifre_tekrar:
            return "Şifreler eşleşmiyor!"
        if len(yeni_kullanici_sifre) < 6:
            return "Şifre en az 6 karakter olmalı."
        cursor.execute("SELECT * FROM kullanicilar WHERE username=%s OR email=%s", (yeni_kullanici, yeni_kullanici_email))
        if cursor.fetchone():
            return f"'{yeni_kullanici}' veya '{yeni_kullanici_email}' zaten kayıtlı!"
        hashed_password = generate_password_hash(yeni_kullanici_sifre)
        cursor.execute("INSERT INTO kullanicilar (username, email, password) VALUES (%s,%s,%s)", (yeni_kullanici, yeni_kullanici_email, hashed_password))
        conn.commit()
        return f"Kullanıcı '{yeni_kullanici}' başarıyla eklendi. <br>ID: {cursor.lastrowid} <br><a href='{url_for('admin_anasayfa', username=username)}'>Geri Dön</a>"
    finally:
        cursor.close()
        conn.close()

@app.route('/kullanicisil/<username>', methods=['POST'])
def kullanicisil(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor()
    try:
        silinecek_kullanici_1 = request.form.get('silinecek_kullanici_adi', '').strip()
        silinecek_kullanici_2 = request.form.get('silinecek_kullanici_adi_tekrar', '').strip()
        if not silinecek_kullanici_1 or not silinecek_kullanici_2:
            return "Lütfen her iki alanı da doldurun."
        if silinecek_kullanici_1 != silinecek_kullanici_2:
            return "Kullanıcı adları eşleşmiyor!"
        cursor.execute("DELETE FROM kullanicilar WHERE username=%s", (silinecek_kullanici_1,))
        conn.commit()
        mesaj = f"Kullanıcı '{silinecek_kullanici_1}' başarıyla silindi." if cursor.rowcount else "Böyle bir kullanıcı bulunamadı."
        return f"{mesaj} <br><a href='{url_for('admin_anasayfa', username=username)}'>Geri Dön</a>"
    finally:
        cursor.close()
        conn.close()

@app.route('/adminsifremidegistir/<username>', methods=['POST'])
def adminsifremidegis(username):
    try:
        conn = database.baglanti_olustur()
        cursor = conn.cursor()
        yeni_sifre = request.form.get('yeni_sifre', '').strip()
        yeni_sifre_tekrar = request.form.get('yeni_sifre_tekrar', '').strip()
        if not yeni_sifre or not yeni_sifre_tekrar:
            return "Lütfen her iki alanı da doldurun."
        if yeni_sifre != yeni_sifre_tekrar:
            return "Şifreler eşleşmiyor."
        if len(yeni_sifre) < 6:
            return "Şifre en az 6 karakter olmalı."
        hashed = generate_password_hash(yeni_sifre)
        cursor.execute("UPDATE admin SET password=%s WHERE username=%s", (hashed, username))
        conn.commit()
        if cursor.rowcount == 0:
            return "Böyle bir admin bulunamadı."
        return redirect(url_for('admin_anasayfa', username=username))
    finally:
        cursor.close()
        conn.close()

@app.route('/kitapoduncver/<username>', methods=['POST'])
def kitapoduncver(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor()
    try:
        verilcek_kullanici_id = int(request.form.get("verilcek_kullanici_id", "").strip())
        verilcek_kitap_id = int(request.form.get("verilcek_kitap_id", "").strip())
        verildigi_tarih = request.form.get("verildigi_tarih", "").strip()
        gerekli_iade_tarihi = request.form.get("gerekli_iade_tarihi", "").strip()
        cursor.execute(
            "INSERT INTO oduncler (kullanici_id, kitap_id, odunc_tarihi, gerekli_iade_tarihi) VALUES (%s,%s,%s,%s)",
            (verilcek_kullanici_id, verilcek_kitap_id, verildigi_tarih, gerekli_iade_tarihi)
        )
        conn.commit()
        odunc_id = cursor.lastrowid
        mesaj = f"Kitap başarıyla ödünç verildi. <br>Ödünç ID: {odunc_id} <br>Kullanıcı ID: {verilcek_kullanici_id}, Kitap ID: {verilcek_kitap_id}"
        return render_template("admin.html", username=username, odunc_id=odunc_id, mesaj=mesaj)
    finally:
        cursor.close()
        conn.close()

@app.route('/kitapiadeal/<username>', methods=['POST'])
def kitapiadeal(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor()
    try:
        odunc_id = int(request.form.get("odunc_id", "").strip())
        iade_tarihi = datetime.strptime(request.form.get("iade_tarihi", "").strip(), "%Y-%m-%d")
        cursor.execute("SELECT kullanici_id, kitap_id, odunc_tarihi, gerekli_iade_tarihi, gercek_iade_tarihi FROM oduncler WHERE id=%s", (odunc_id,))
        odunc = cursor.fetchone()
        if not odunc:
            return "Geçersiz ödünç ID."
        kullanici_id, kitap_id, odunc_verilis_tarihi, gerekli_iade_tarihi, mevcut_iade_tarihi = odunc
        if mevcut_iade_tarihi:
            return "Bu ödünç zaten iade edilmiş."
        gecikme_gunu = (iade_tarihi - datetime.strptime(str(gerekli_iade_tarihi), "%Y-%m-%d")).days
        ceza_miktari = gecikme_gunu * 5 if gecikme_gunu > 0 else 0
        if ceza_miktari > 0:
            cursor.execute("INSERT INTO cezalar (kullanici_id, kitap_id, ceza_miktari, odunc_tarihi, iade_tarihi) VALUES (%s,%s,%s,%s,%s)",
                           (kullanici_id, kitap_id, ceza_miktari, odunc_verilis_tarihi, iade_tarihi))
        cursor.execute("UPDATE oduncler SET gercek_iade_tarihi=%s WHERE id=%s", (iade_tarihi, odunc_id))
        cursor.execute("UPDATE kitaplar SET stok=stok+1 WHERE id=%s", (kitap_id,))
        conn.commit()
        mesaj = f"Kitap (ID: {kitap_id}) başarıyla iade edildi."
        if ceza_miktari > 0:
            mesaj += f" {gecikme_gunu} gün gecikme nedeniyle {ceza_miktari} TL ceza eklendi."
        return mesaj + f" <br><a href='{url_for('admin_anasayfa', username=username)}'>Geri Dön</a>"
    finally:
        cursor.close()
        conn.close()
       
# Kullanıcının kendi ödünç geçmişi
@app.route('/oduncalmagecmisim/<username>')
def oduncalmagecmisim(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT o.id, ki.isim AS kitap, o.odunc_tarihi, o.gerekli_iade_tarihi, o.gercek_iade_tarihi
               FROM oduncler o
               JOIN kullanicilar k ON o.kullanici_id = k.id
               JOIN kitaplar ki ON o.kitap_id = ki.id
               WHERE k.username=%s""",
            (username,)
        )
        oduncler = cursor.fetchall()
        return render_template("odunc_gecmisim.html", username=username, oduncler=oduncler)
    finally:
        cursor.close()
        conn.close()


# Admin tüm kullanıcıların ödünç geçmişi
@app.route('/tumkullanicioduncalmagecmisigoster/<username>')
def tumkullanicioduncalmagecmisigoster(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor(dictionary=True)
    try:
        # Admin kontrolü
        cursor.execute("SELECT * FROM admin WHERE username=%s", (username,))
        if not cursor.fetchone():
            return "Yetkisiz erişim!", 403

        cursor.execute(
            """SELECT o.id, k.username AS kullanici, ki.isim AS kitap, 
                      o.odunc_tarihi, o.gerekli_iade_tarihi, o.gercek_iade_tarihi
               FROM oduncler o
               JOIN kullanicilar k ON o.kullanici_id = k.id
               JOIN kitaplar ki ON o.kitap_id = ki.id"""
        )
        oduncler = cursor.fetchall()
        return render_template("tum_odunc_gecmisi.html", username=username, oduncler=oduncler)
    finally:
        cursor.close()
        conn.close()


# Kullanıcının kendi cezaları
@app.route('/cezalarimigoster/<username>')
def cezalarimigoster(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT c.id, ki.isim AS kitap, c.ceza_miktari, c.odunc_tarihi, c.iade_tarihi
               FROM cezalar c
               JOIN kullanicilar k ON c.kullanici_id = k.id
               JOIN kitaplar ki ON c.kitap_id = ki.id
               WHERE k.username=%s""",
            (username,)
        )
        cezalar = cursor.fetchall()
        return render_template("cezalarim.html", username=username, cezalar=cezalar)
    finally:
        cursor.close()
        conn.close()


# Admin tüm cezaları görür
@app.route('/cezatablosunugoster/<username>')
def cezatablosunugoster(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor(dictionary=True)
    try:
        # Admin kontrolü
        cursor.execute("SELECT * FROM admin WHERE username=%s", (username,))
        if not cursor.fetchone():
            return "Yetkisiz erişim!", 403

        cursor.execute(
            """SELECT c.id, k.username AS kullanici, ki.isim AS kitap, 
                      c.ceza_miktari, c.odunc_tarihi, c.iade_tarihi
               FROM cezalar c
               JOIN kullanicilar k ON c.kullanici_id = k.id
               JOIN kitaplar ki ON c.kitap_id = ki.id"""
        )
        cezalar = cursor.fetchall()
        return render_template("tum_cezalar.html", username=username, cezalar=cezalar)
    finally:
        cursor.close()
        conn.close()      
    # Kullanıcının cezasını ID ile göster (JSON)
@app.route('/cezagoster/<int:kullanici_id>', methods=['GET'])
def cezagoster(kullanici_id):
    conn = database.baglanti_olustur()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, ceza_miktari FROM cezalar WHERE kullanici_id=%s", (kullanici_id,))
        ceza = cursor.fetchone()
        if ceza:
            return jsonify({"miktar": ceza["ceza_miktari"], "id": ceza["id"]})
        else:
            return jsonify({"miktar": 0})
    finally:
        cursor.close()
        conn.close()


# Ceza ödeme (ID’ye göre)
@app.route('/cezaode/<int:kullanici_id>', methods=['POST'])
def cezaode(kullanici_id):
    ceza_id = request.form.get("ceza_id")
    if not ceza_id:
        return jsonify({"error": "Ceza ID bulunamadı."})
    conn = database.baglanti_olustur()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("DELETE FROM cezalar WHERE id=%s AND kullanici_id=%s", (ceza_id, kullanici_id))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Ceza bulunamadı veya zaten ödenmiş."})
        return jsonify({"success": "Ceza ödendi."})
    finally:
        cursor.close()
        conn.close()
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
