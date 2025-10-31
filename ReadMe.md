# CATLARY KÜTÜPHANE YÖNETİM SİSTEMİ

Catlary kütüphane yönetim sistemi tamamlanmamış,geliştirilmesi devam eden bir kütüphane otomasyonudur. Mevcut hatalari ve eksiklikleri bulunmaktadır.Güncellemeler eklendikçe dosyalar da güncellenecektir.

### 30.10.2025 tarihine kadar yapılan güncellemelerde özetle şunlar yapılmıştır:

- [Ana sayfa üzerinden admin ve kullanıcı olarak giriş yapma ve kullanıcı olarak yeni hesap açma ](#ana-sayfa)
- [Kullanıcılar için tasarlanmış kullanıcı paneli](#kullanıcı-paneli)
- [Admin için tasarlanmış admin paneli](#admin-paneli)

- CATLARY Kütüphane YÖNETİM Sisteminin güncel ER-Diyagramı:
  ![login](static/images/CatlaryER.png)

```
 Bu kütüphane otomasyonunda;
  -  birden çok admin birden çok kullanıcıyı yönetebilir,
  -  birden fazla kullanıcı birden fazla admin tarafından yönetilebilir,
  -  birden çok admin birden çok kitap ile işlem yapabilir,
  -  birden fazla kitap birden fazla admin tarafından yönetilebilir,
  -  birden çok admin birden çok ödünç üzerinde işlem yapabilir,
  -  birden fazla ödünç birden fazla admin tarafından yönetilebilir,
  -  birden çok admin birden çok ceza üzerinde ile işlem yapabilir,
  -  birden fazla ceza birden fazla admin tarafından yönetilebilir.
```

## Ana-sayfa

Catlary Kütüphane Yönetim sisteminin ana sayfası şuan web üzerinde şu şekilde gözükmektedir:

![login](static/images/Catlary.png)

Giriş yapmak isteyen kullanıcı admin veya kullanıcı olarak giriş yapabilmekte veya yeni kullanıcı oluşturabilmektedir

- Kullanıcı olarak giriş yapmak istenirse:

![login](static/images/Catlary2.png)

- Admin olarak giriş yapmak istenirse:

![login](static/images/Catlary3.png)

- Yeni hesap açıp kaydolmak istenirse:

![login](static/images/Catlary4.png)

\*\* Dikkat! Kayıt olduğunuzda hesabınız askıya alınmış yani pasif haldedir,önce admin tarafından aktifleştirilmeniz gerekmektedir.

![login](static/images/Catlary6.png)

![login](static/images/Catlary7.png)

![login](static/images/Catlary8.png)

## Kullanıcı-Paneli

Kullanıcı panelinde kullanıcılar kütüphanede bulunan kitapları listeleyebilmekte, ödünç alma geçmişini görebilmete ve var olan cezalarını görebilip istedikleri durumda şifre değiştirme özelliklerine sahiptir.

Veri tabanımızda kayıtlı olan kullanıcı Catlary sistemimize giriş yaptığında kullanıcı paneli şu şekilde gözükmektedir:

![login](static/images/Catlary5.png)

Kullanıcı olarak giriş yamak için e-mail ve şifrenizi doğru girmeniz gerekmektedir.

![login](static/images/Catlary9.png)

- Kullanıcı panelinde bulunan 'Kitaplari görüntüle' adlı butona tıkladığımızda kütüphanemizde bulunan kitapları görülmekte ve kitaplar arasında arama yapılabilmektedir.

![login](static/images/Catlary10.png)

Kitabın kütüphanede bulunma durumuna göre çıktı verir:

![login](static/images/Catlary11.png)

![login](static/images/Catlary12.png)

- Kullanıcı panelinde bulunan 'Ödünç Alma Geçmişim' butonuna tıkladığımızda kullanıcının ödünç alma geçmişi görülebilmektedir:

![login](static/images/Catlary13.png)

- Kullanıcı panelinde bulunan ' Cezalarımı Göster' adlı butona tıkladığımızda kullanıcının güncel ve eski cezaları görülebilmektedir:

![login](static/images/Catlary14.png)

- Kullanıcı panelinde bulunan 'Şifre Değiştir' adlı butona tıklayınca kullanıcının şifresi değiştirilebilmektedir.

![login](static/images/Catlary18.png)

![login](static/images/Catlary17.png)

\*\* Eski şifreyi hatasız girmemiz gerektiğini hatırlatmaktan zarar gelmez. :)

![login](static/images/Catlary16.png)

## Admin-Paneli

Admin panelinde kullanıcılar kütüphanede bulunan kitapları listeleyebilmekte,kitap ekleyip silebilmekte,kullanicilarin tamamını gorup yeni kullanici ekleyip var olan kullanicilari pasif hale getirebilmekte, tüm kullanıcıların ödünç alma geçmişini görebilmete,var olan tüm cezalalrı gorebilmekte,kullanıcıların şifrelerini unutma durumunda kullanıcılara mail gonderebilmekte, yani admin ekleyebilmekte veya silebilmekte veistedikleri durumda şifre değiştirebilme özelliklerine sahiptir.

Admin paneli giriş yapıldığında şu sekilde gorünür:

![login](static/images/Catlary19.png)

Kitapları görüntüle butonuna tıkladığımızda:

![login](static/images/Catlary20.png)

Şartları sağlayan kitaplari(Ödüçte olmama gibi) silebilme özelliğie sahiptir.

![login](static/images/Catlary21.png)
![login](static/images/Catlary22.png)

Kitap ekle butonuna tıkladığında:
![login](static/images/Catlary23.png)

Gerekli bilgiler doldurulduğunda :

![login](static/images/Catlary24.png)
![login](static/images/Catlary25.png)

Kitap ödünç ver butonuna tıkladıgında:

![login](static/images/Catlary27.png)
![login](static/images/Catlary28.png)

kullanıcı sayfasında da gözükür:

![login](static/images/Catlary30.png)

Ödünç geçmişini göster butonuna tıklayınca:

![login](static/images/Catlary29.png)

İade al butonuna tıklayınca:

![login](static/images/Catlary31.png)

Gerekli bilgiler eksiksiz doldurulursa:
(Kullanıcı daha önceden iade etmişse ve alanlarda hatalar olursa gerekli hataları verir)

![login](static/images/Catlary32.png)

Tüm kullanıcıların ödünç verme geçmişini görntülemek istenirse:

![login](static/images/Catlary33.png)

Yeni admin eklemek/silmek istenirse:
(Form eksiksiz/hatasız doldurulmalidir.)
![login](static/images/Catlary34.png)

![login](static/images/Catlary35.png)

![login](static/images/Catlary36.png)

![login](static/images/Catlary47.png)

Yeni kullanıcı eklenmek istenirse:

(Gerekli kontroller yapılır(email veya username daha önceden kullanılmaması gibi),Form eksiksiz/hatasız doldurulmalidir.)

![login](static/images/Catlary37.png)

![login](static/images/Catlary38.png)

Kullanıcıların şifresini unutması durumunda kullanıcı şifresini sıfırlamak için gerekli id girilmesi beklenir ve:

![login](static/images/Catlary39.png)
![login](static/images/Catlary40.png)
![login](static/images/Catlary41.png)

Kullanıcı listesi görüntülenme istenirse veya kullanıcıların aktiflik/pasiflikleri değiştirilmek istenirse:

![login](static/images/Catlary42.png)

Adminin kendi şifresini değiştirmek isterse:

![login](static/images/Catlary43.png)

![login](static/images/Catlary44.png)

Tüm kullanıcıların cezaları görüntülenmek istenirse:

![login](static/images/Catlary48.png)

Var olan cezaları ödemek isterse:

![login](static/images/Catlary46.png)

![login](static/images/Catlary50.png)
![login](static/images/Catlary52.png)

Cezalar listesinde ödenen ceza
işaretlenir.

![login](static/images/Catlary51.png)
