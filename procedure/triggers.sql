DELIMITER // CREATE TRIGGER stok_azaltma
AFTER
INSERT ON oduncler FOR EACH ROW BEGIN
UPDATE kitaplar
SET stok = stok - 1
WHERE id = NEW.kitap_id;
END;
// CREATE TRIGGER stok_arttir
AFTER
UPDATE ON oduncler FOR EACH ROW BEGIN IF OLD.gercek_iade_tarihi IS NULL
    AND NEW.gercek_iade_tarihi IS NOT NULL THEN
UPDATE kitaplar
SET stok = stok + 1
WHERE id = NEW.kitap_id;
END IF;
END;
// DELIMITER;
DELIMITER // CREATE TRIGGER uyeolmabilgilendirmesi
AFTER
INSERT ON kullanicilar FOR EACH ROW BEGIN IF NEW.username IS NOT NULL THEN
INSERT INTO MailKuyrugu (AliciMail, AliciAdi, Konu, MesajIcerigi)
VALUES (
        NEW.email,
        NEW.username,
        'Aramıza Hoş Geldiniz!',
        CONCAT(
            'Sayın ',
            NEW.username,
            ', kütüphanemize üyeliğiniz başarıyla oluşturulmuştur.'
        )
    );
END IF;
END;
// DELIMITER;
DELIMITER // CREATE TRIGGER odunc_mail
AFTER
INSERT ON oduncler FOR EACH ROW BEGIN
DECLARE v_email VARCHAR(255);
DECLARE v_username VARCHAR(255);
DECLARE v_kitap_adi VARCHAR(255);
SELECT email,
    username INTO v_email,
    v_username
FROM kullanicilar
WHERE id = NEW.kullanici_id;
SELECT kitap_adi INTO v_kitap_adi
FROM kitaplar
WHERE id = NEW.kitap_id;
INSERT INTO MailKuyrugu (AliciMail, AliciAdi, Konu, MesajIcerigi)
VALUES (
        v_email,
        v_username,
        'Kitap Ödünç Alma İşlemi',
        CONCAT(
            'Sayın ',
            v_username,
            ', "',
            v_kitap_adi,
            '" adlı kitabı ödünç aldınız. Son iade tarihi: ',
            NEW.iade_tarihi
        )
    );
END;
// DELIMITER;
DELIMITER // CREATE TRIGGER iademaili
AFTER
UPDATE ON oduncler FOR EACH ROW BEGIN
DECLARE v_email VARCHAR(255);
DECLARE v_username VARCHAR(255);
DECLARE v_kitap_adi VARCHAR(255);
IF OLD.gercek_iade_tarihi IS NULL
AND NEW.gercek_iade_tarihi IS NOT NULL THEN
SELECT email,
    username INTO v_email,
    v_username
FROM kullanicilar
WHERE id = NEW.kullanici_id;
SELECT kitap_adi INTO v_kitap_adi
FROM kitaplar
WHERE id = NEW.kitap_id;
INSERT INTO MailKuyrugu (AliciMail, AliciAdi, Konu, MesajIcerigi)
VALUES (
        v_email,
        v_username,
        'Kitap İade İşlemi Başarılı',
        CONCAT(
            'Sayın ',
            v_username,
            ', "',
            v_kitap_adi,
            '" adlı kitabı iade ettiğiniz için teşekkür ederiz.'
        )
    );
END IF;
END;
// DELIMITER;
DELIMITER // CREATE TRIGGER tr_ceza_odendi_mail
AFTER
UPDATE ON cezalar FOR EACH ROW BEGIN
DECLARE v_email VARCHAR(255);
DECLARE v_username VARCHAR(255);
IF OLD.odeme_durumu = 0
AND NEW.odeme_durumu = 1 THEN
SELECT email,
    username INTO v_email,
    v_username
FROM kullanicilar
WHERE id = NEW.kullanici_id;
INSERT INTO MailKuyrugu (AliciMail, AliciAdi, Konu, MesajIcerigi)
VALUES (
        v_email,
        v_username,
        'Ceza Ödeme Onayı',
        CONCAT(
            'Sayın ',
            v_username,
            ', ',
            NEW.ceza_miktari,
            ' TL tutarındaki gecikme cezası ödemeniz alınmıştır.'
        )
    );
END IF;
END;
// DELIMITER;
DELIMITER // CREATE TRIGGER trg_ceza_odeme_kontrol BEFORE
UPDATE ON cezalar FOR EACH ROW BEGIN
DECLARE v_iade_tarihi DATE;
IF NEW.odeme_durumu = 1
AND OLD.odeme_durumu = 0 THEN
SELECT gercek_iade_tarihi INTO v_iade_tarihi
FROM oduncler
WHERE id = NEW.odunc_id;
IF v_iade_tarihi IS NULL THEN SIGNAL SQLSTATE '45000'
SET MESSAGE_TEXT = 'HATA: Kitap iade edilmeden ceza ödemesi yapılamaz! Önce kitabı teslim alın.';
END IF;
END IF;
END;
// DELIMITER;