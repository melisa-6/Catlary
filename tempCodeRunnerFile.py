---------------- GIRIS ROUTE -------------------
@app.route('/')
def anasayfa():
    return render_template("anasayfa.html")  # login ve kayıt formu burada

# Kayıt route
@app.route('/kayitol', methods=['POST'])
def kayit_ol():
    form = request.form
    return kullanicikontroller.kayit_ol_controller(form)

# Giriş route
@app.route('/girisyap', methods=['POST'])
def giris_yap():
    form = request.form
    return kullanicikontroller.giris_yap(form, session)

# Admin sayfası
@app.route('/admin/<username>')
@admin_required
def admin_anasayfa(username):
    return render_template("admin.html", username=username)

# Kullanıcı sayfası
@app.route('/kullanici/<username>')
@login_required
def kullanici_sayfasi(username):
    return render_template("kullanici.html", username=username)
