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
