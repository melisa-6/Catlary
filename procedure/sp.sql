END CREATE DEFINER = `root` @`localhost` PROCEDURE `ceza`() BEGIN
DECLARE v_gunluk_ceza DECIMAL(10, 2) DEFAULT 5.00;
DECLARE v_islem_tarihi DATE;
SET v_islem_tarihi = CURDATE();
INSERT INTO cezalar (
        kullanici_id,
        kitap_id,
        ceza_miktari,
        odunc_tarihi,
        iade_tarihi,
        odeme_durumu,
        ilk_gecikme_mail_tarihi,
        son_mail_tarihi
    )
SELECT O.kullanici_id,
    O.kitap_id,
    (
        DATEDIFF(v_islem_tarihi, O.gerekli_iade_tarihi) * v_gunluk_ceza
    ),
    O.odunc_tarihi,
    O.gerekli_iade_tarihi,
    0,
    v_islem_tarihi,
    v_islem_tarihi
FROM oduncler O
WHERE O.gercek_iade_tarihi IS NULL
    AND O.gerekli_iade_tarihi < v_islem_tarihi
    AND NOT EXISTS (
        SELECT 1
        FROM cezalar C
        WHERE C.kullanici_id = O.kullanici_id
            AND C.kitap_id = O.kitap_id
    );
UPDATE cezalar C
    JOIN oduncler O ON C.kullanici_id = O.kullanici_id
    AND C.kitap_id = O.kitap_id
SET C.ceza_miktari = (
        DATEDIFF(v_islem_tarihi, O.gerekli_iade_tarihi) * v_gunluk_ceza
    ),
    C.son_mail_tarihi = v_islem_tarihi
WHERE O.gercek_iade_tarihi IS NULL
    AND O.gerekli_iade_tarihi < v_islem_tarihi;
INSERT INTO mailkuyrugu (
        AliciMail,
        AliciAdi,
        Konu,
        Mesajicerigi,
        GonderimDurumu,
        OlusmaZamani
    )
SELECT U.email,
    U.username,
    'HATIRLATMA: Gecikmiş Kitap Borcunuz Arttı',
    CONCAT(
        'Sayın ',
        U.username,
        ', gecikme devam etmektedir. Güncel borcunuz: ',
        C.ceza_miktari,
        ' TL. Lütfen kitabınızı iade ediniz.'
    ),
    'Beklemede',
    NOW()
FROM cezalar C
    JOIN kullanicilar U ON C.kullanici_id = U.id
    JOIN oduncler O ON C.kullanici_id = O.kullanici_id
    AND C.kitap_id = O.kitap_id
WHERE C.son_mail_tarihi = v_islem_tarihi
    AND O.gercek_iade_tarihi IS NULL;
END CREATE DEFINER = `root` @`localhost` PROCEDURE `iadebugunhatirlatmasi`() BEGIN
INSERT INTO mailkuyrugu(AliciMail, AliciAdi, Konu, MesajIcerigi)
SELECT U.email,
    U.username,
    'HATIRLATMA: Kitap Teslim Tarihi BUGÜN!',
    CONCAT(
        'Sayın ',
        U.username,
        ', Kitabı teslim etmeniz gereken son tarih BUGÜNDÜR. Lütfen gecikme cezası almamak için kitabı iade ediniz.'
    )
FROM oduncler O
    INNER JOIN kullanicilar U ON O.kullanici_id = U.id
WHERE O.gercek_iade_tarihi IS NULL
    AND O.gerekli_iade_tarihi = CURDATE();
END CREATE DEFINER = `root` @`localhost` PROCEDURE `AdminRaporMailiOlustur`() BEGIN
DECLARE v_odunc INT;
DECLARE v_iade INT;
DECLARE v_ceza_mail INT;
DECLARE v_rapor_tarihi DATE;
DECLARE v_mesaj TEXT;
DECLARE v_admin_mail VARCHAR(255) DEFAULT 'infocatlary@gmail.com';
SET v_rapor_tarihi = CURDATE();
SELECT COUNT(*) INTO v_odunc
FROM oduncler
WHERE odunc_tarihi = v_rapor_tarihi;
SELECT COUNT(*) INTO v_iade
FROM oduncler
WHERE gercek_iade_tarihi = v_rapor_tarihi;
SELECT COUNT(*) INTO v_ceza_mail
FROM MailKuyrugu
WHERE DATE(OlusmaZamani) = v_rapor_tarihi
    AND Konu LIKE '%Ceza Başlatıldı%';
SET v_mesaj = CONCAT(
        '--- KÜTÜPHANE GÜNLÜK ÖZET RAPORU (',
        v_rapor_tarihi,
        ') ---\n\n',
        '1. Bugün Yapılan Yeni Ödünç Sayısı: ',
        v_odunc,
        '\n',
        '2. Bugün Yapılan Kitap İade Sayısı: ',
        v_iade,
        '\n',
        '3. Sistem Tarafından Başlatılan Yeni Ceza Sayısı: ',
        v_ceza_mail,
        '\n\n',
        'Bu rapor, otomasyon sistemi tarafından otomatik oluşturulmuştur.'
    );
INSERT INTO MailKuyrugu (AliciMail, AliciAdi, Konu, MesajIcerigi)
VALUES (
        v_admin_mail,
        'Kütüphane Yöneticisi',
        CONCAT('GÜNLÜK RAPOR ÖZETİ - ', v_rapor_tarihi),
        v_mesaj
    );
END CREATE DEFINER = `root` @`localhost` PROCEDURE `AdminRaporMailiOlustur`() BEGIN
DECLARE v_odunc INT;
DECLARE v_iade INT;
DECLARE v_ceza_mail INT;
DECLARE v_rapor_tarihi DATE;
DECLARE v_mesaj TEXT;
DECLARE v_admin_mail VARCHAR(255) DEFAULT 'infocatlary@gmail.com';
SET v_rapor_tarihi = CURDATE();
SELECT COUNT(*) INTO v_odunc
FROM oduncler
WHERE odunc_tarihi = v_rapor_tarihi;
SELECT COUNT(*) INTO v_iade
FROM oduncler
WHERE gercek_iade_tarihi = v_rapor_tarihi;
SELECT COUNT(*) INTO v_ceza_mail
FROM MailKuyrugu
WHERE DATE(OlusmaZamani) = v_rapor_tarihi
    AND Konu LIKE '%Ceza Başlatıldı%';
SET v_mesaj = CONCAT(
        '--- KÜTÜPHANE GÜNLÜK ÖZET RAPORU (',
        v_rapor_tarihi,
        ') ---\n\n',
        '1. Bugün Yapılan Yeni Ödünç Sayısı: ',
        v_odunc,
        '\n',
        '2. Bugün Yapılan Kitap İade Sayısı: ',
        v_iade,
        '\n',
        '3. Sistem Tarafından Başlatılan Yeni Ceza Sayısı: ',
        v_ceza_mail,
        '\n\n',
        'Bu rapor, otomasyon sistemi tarafından otomatik oluşturulmuştur.'
    );
INSERT INTO MailKuyrugu (AliciMail, AliciAdi, Konu, MesajIcerigi)
VALUES (
        v_admin_mail,
        'Kütüphane Yöneticisi',
        CONCAT('GÜNLÜK RAPOR ÖZETİ - ', v_rapor_tarihi),
        v_mesaj
    );
END CREATE DEFINER = `root` @`localhost` EVENT `SabahOtomasyonu` ON SCHEDULE EVERY 1 DAY STARTS '2025-11-09 08:00:00' ON COMPLETION NOT PRESERVE ENABLE DO CALL AnaKontrol() CREATE DEFINER = `root` @`localhost` EVENT `AksamRaporlama` ON SCHEDULE EVERY 1 DAY STARTS '2025-11-09 17:00:00' ON COMPLETION NOT PRESERVE ENABLE DO BEGIN CALL AdminRaporMailiOlustur();
END