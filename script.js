// Kullanıcı Girişi Butonu
document.getElementById("kullaniciGirisBtn").addEventListener("click", function() {
    document.getElementById("kullaniciGirisFormu").style.display = "block";
    document.getElementById("adminGirisFormu").style.display = "none";
    document.getElementById("hesapFormu").style.display = "none";
});

// Admin Girişi Butonu
document.getElementById("adminGirisBtn").addEventListener("click", function() {
    document.getElementById("adminGirisFormu").style.display = "block";
    document.getElementById("kullaniciGirisFormu").style.display = "none";
    document.getElementById("hesapFormu").style.display = "none";
});

// Hesap Aç Butonu
document.getElementById("hesapAcBtn").addEventListener("click", function() {
    document.getElementById("hesapFormu").style.display = "block";
    document.getElementById("kullaniciGirisFormu").style.display = "none";
    document.getElementById("adminGirisFormu").style.display = "none";
});

// Kullanıcı Giriş Kontrolü
document.getElementById("girisbuton").addEventListener("click", function() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;
/*simdilik cok basit seviyede tek giris kabul ediyor fakat db kısmı eklenince duzeltilecek */
    if (username === "melisa" && password === "1234") {
        alert("Kullanıcı girişi başarılı!");
    } else {
        document.getElementById("login-error").style.display = "block";
    }
});

// Admin Giriş Kontrolü
document.getElementById("adminGirisButon").addEventListener("click", function() {
    let adminname = document.getElementById("adminname").value;
    let adminpassword = document.getElementById("adminpassword").value;
/*simdilik cok basit seviyede tek giris kabul ediyor ama db kısmı eklenince duzeltilecek */
    if (adminname === "admin" && adminpassword === "admin123") {
        alert("Admin girişi başarılı!");
    } else {
        document.getElementById("admin-login-error").style.display = "block";
    }
});

// Hesap Oluşturma
document.getElementById("hesapOlusturButon").addEventListener("click", function() {
    let newUsername = document.getElementById("newUsername").value;
    let newPassword = document.getElementById("newPassword").value;

    if (newUsername && newPassword) {
        alert("Hesap oluşturuldu!");
    } else {
        document.getElementById("hesap-error").style.display = "block";
    }
});
