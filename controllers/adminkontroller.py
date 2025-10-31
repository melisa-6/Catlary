from flask import request, session, flash, redirect, url_for, render_template
from services.adminService import AdminService


db_config = {
    "host": "localhost",
    "user": "melisa",
    "password": "Mtz0504*",
    "database": "kutuphane_db"
}
admin_service = AdminService(db_config)


def admin_ekle_controller(admin_username):
    #formdan yeni eklencek admin bilgileirni alır 
    username = request.form.get('yeni_admin_adi')
    email = request.form.get('yeni_admin_email')
    sifre = request.form.get('yeni_admin_sifre')
    sifre_tekrar = request.form.get('yeni_admin_sifre_tekrar')
#tum alanların dolulugunu kontrol eder
    if not all([username, email, sifre, sifre_tekrar]):
        flash("Tüm alanları doldurunuz!", "error")
        return redirect(url_for('admin_anasayfa', username=admin_username))
#service de uygun fonksiyona yonlendirerek eklenmesi saglanir
    admin_id = admin_service.admin_ekle(username, email, sifre, sifre_tekrar)
    if admin_id:
        flash(f"Admin başarıyla eklendi. ID: {admin_id}", "success")
    else:
        flash("Admin eklenemedi!", "error")

    return redirect(url_for('admin_anasayfa', username=admin_username))

#silinecek admin adi ni formdan alir ve service e yonlendirir 
#silinme durumuna gore uygun mesajı verir
def admin_sil_controller(admin_username):
    username = request.form.get('silinecek_admin_adi')
    username_tekrar = request.form.get('silinecek_admin_adi_tekrar')

    silinen = admin_service.admin_sil(username, username_tekrar)
    if silinen > 0:
        flash(f"{username} silindi.", "success")
    else:
        flash(f"{username} bulunamadı veya eşleşme hatası.", "error")

    return redirect(url_for('admin_anasayfa', username=admin_username))


def admin_sifre_degistir_controller():
    username = session.get('username')
    if not username:
        flash("Oturum bulunamadı!", "error")
        return redirect(url_for('anasayfa'))
#formdan gelen biligileri alir 
    eski_sifre = request.form.get('eski_sifre')
    yeni_sifre = request.form.get('yeni_sifre')
    yeni_sifre_tekrar = request.form.get('yeni_sifre_tekrar')
#uygun service e yonlendirir
    sonuc = admin_service.sifre_degistir(username, eski_sifre, yeni_sifre, yeni_sifre_tekrar)

    flash(sonuc['message'], "success" if sonuc['success'] else "error")
    return redirect(url_for('admin_anasayfa', username=username))
