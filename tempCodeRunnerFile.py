    basarili_mi = sonuc.get("basarili", False) 

    
    #  JSON yanıtı
    if is_api_request:
        status_code = 201 if basarili_mi else 400
        return jsonify(sonuc), status_code
    
    if basarili_mi:
        flash(sonuc.get("mesaj", "Kayıt başarılı."), "success")
    else:
        flash(sonuc.get("mesaj", "Kayıt başarısız."), "error")
        
    return redirect(url_for('anasayfa'))

@app.route("/girisyap", methods=["POST"])
def girisyap():
    SECRET2 = SECRET 
    if request.is_json:
        form = request.get_json()
        form['is_web'] = False
    else:
        form = request.form.to_dict()
        form['is_web'] = True
    
    controller_sonuc = kullanicikontroller.giris_yap_controller(form, SECRET2)
    
    # json kontrolu
    if isinstance(controller_sonuc, tuple) or hasattr(controller_sonuc, 'get_data'):
        return controller_sonuc
    
    # WEB Kontrolü
    if isinstance(controller_sonuc, dict):
        # Başarısız ise
        if controller_sonuc.get("basarili") is False:
            mesaj = controller_sonuc.get("mesaj", "Giriş başarısız.")
            flash(mesaj, "error") 
            return redirect(url_for('anasayfa'))
        
        # Başarılı ise
        if controller_sonuc.get("redirect_url"):
            flash(controller_sonuc.get("mesaj", "Giriş başarılı."), "success")
            return redirect(controller_sonuc['redirect_url'])
        
        return redirect(url_for('anasayfa'))
    
    return "Beklenmeyen sunucu yanıtı.", 500

@app.route('/admin_anasayfasi')
@admin_required
def admin_anasayfa():
    username = g.username 
    
    if request.accept_mimetypes.best == "application/json":
        return jsonify({"username": username, "message": "Admin sayfası erişimi başarılı"}), 200
        
    return render_template("admin.html", username=username)

@app.route('/kullanici_sayfasi')
@login_required
def kullanici_sayfasi():
    username = g.username 
    
    if 