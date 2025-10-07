from flask import Flask, request, render_template, redirect, url_for
import database  # database.py dosyasındaki fonksiyonları kullanabilmek için

app = Flask(__name__)

# Veritabanı oluşturuluyor
#database.db_sil()
database.db_olustur()
database.tablolar_olustur()

@app.route('/')
def anasayfa():
    return render_template("index.html")

@app.route('/girisyap', methods=['POST'])
def giris_yap():
    islem_tipi = request.form.get('islem')
    username = request.form.get('username')
    password = request.form.get('password')

    conn = database.baglanti_olustur()
    cursor = conn.cursor()

    if islem_tipi == "kullanici":
        cursor.execute("SELECT * FROM kullanicilar WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            return redirect(url_for("kullanici_anasayfa", username=username))
        else:
            return "Kullanıcı adı veya şifre yanlış!", 401

    elif islem_tipi == "admin":
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s ", (username, password))
        admin = cursor.fetchone()
        conn.close()
        if admin:
            return redirect(url_for("admin_anasayfa", username=username))
        else:
            return "Admin adı veya şifre yanlış!", 401

    elif islem_tipi == "yeni":
        try:
            cursor.execute("INSERT INTO kullanicilar (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for("kullanici_anasayfa", username=username))
        except Exception as e:
            conn.close()
            return f"Hesap oluşturulamadı! Hata: {str(e)}", 400

@app.route('/kullanici/<username>')
def kullanici_anasayfa(username):
    return render_template("kullanici.html", username=username)

@app.route('/admin/<username>')
def admin_anasayfa(username):
    return render_template("admin.html", username=username)

@app.route('/kitaplari_goruntule/<username>')
def kitaplari_goruntule(username):
    conn = database.baglanti_olustur()
    cursor = conn.cursor()
    cursor.execute("SELECT isim, yazar, kategori FROM kitaplar")
    kitaplar = cursor.fetchall()
    conn.close()
    return render_template("kitaplar.html", kitaplar=kitaplar, username=username)


@app.route('/sifredegis/<username>')
def sifredegis(username):
    return ("sifre degisti")


@app.route('/kitapara/<username>')
def kitapara(username):
    return ("kitap arandi")

@app.route('/kitapekle/<username>')
def kitapekle(username):
    return ("kiap eklendi")


@app.route('/kitapsil/<username>')
def kitapsil(username):
    return ("kiap silindi")


@app.route('/kullaniciekle/<username>')
def kullaniciekle(username):
    return ("kullanıcı eklendi")


@app.route('/kullanicisil/<username>')
def kullanicisil(username):
    return ("kullanıcı silindi")


@app.route('/adminekle/<username>')
def adminekle(username):
    return ("admin eklendi")

@app.route('/adminsil/<username>')
def adminsil(username):
    return ("admin silindi")

@app.route('/adminsifremidegistir/<username>')
def adminsifremidegistir(username):
    return ("admin sifre degistirildi")


@app.route('/kullanicisifremidegistir/<username>')
def kullanicisifremidegistir(username):
    return ("kullanici sifre degistirildi")

@app.route('/kitapoduncver/<username>')
def kitapoduncver(username):
    return ("kitap odunc verildi")

@app.route('/kitapiadeal/<username>')
def kitapiadeal(username):
    return ("kitap iade alindi")

@app.route('/oduncalmagecmisim/<username>')
def oduncalmagecmisi(username):
    return ("odunc alma gecmisi")   

@app.route('/tumkullanicioduncalmagecmisigoster/<username>')
def tumkullanicioduncalmagecmisigoster(username):
    return ("odunc alma gecmisi gosterildi")

@app.route('/cezatablosunugoster/<username>')
def cezatablosunugoster(username):
    return ("ceza tablosu gosterildi")


@app.route('/cezalarimigoster/<username>')
def cezalarimigoster(username):
    return ("cezalarin gosterildi")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
