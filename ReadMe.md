#Catlary Kütüphane Yönetim Sistemi Youtube kanalı: www.youtube.com/@Catlaryy


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

### 25.11.2025 tarihinde;

\*Kullanıcı kitap ödünç aldığında

![login](static/images/Catlary53.png)

\*Kullanıcıda ödünç durumunda olup gerekli iade tarihi geldiğinde

![login](static/images/Catlary57.png)

\*Gerekli iade tarihinde iade edilmediğinde oluşacak cezaları bildirmek için

![login](static/images/Catlary55.png)

\*İade edilmeyen her gün cezanın arttığını belirtmek için

![login](static/images/Catlary56.png)

\*Kitap iade edildiğinde onaylandığını göstermek için

![login](static/images/Catlary58.png)

\*Ceza ödemenin gerçekleştiğini belirten

![login](static/images/Catlary59.png)

\* Yetkili admine günlük rapor

![login](static/images/Catlary59.png)

' trigger ve stored procedureler eklenmiştir.

### 8.12.20205 tarihinde atılan commit ile;

\* Catlary Kütüphane Yönetim Sistemine Personel/Çalışan rolü ekledim,JWT tabanlı şifrelemeye geçiş yaptım ve Postman testleri ile uyumlu hale getirdim;

Güncel olarak anasayfa

![login](static/images/Catlaryguncelanasayfa.png)

personellerin de giriş yapabileceği şekilde güncellendi.

\* Personel rolü eklendikten sonra Admin anasayfasında bazı değişiklikler yapıldı;

İlk olarak admin yetkileri personelleri yönetilecek şekilde değiştirildi.

![login](static/images/gunceladminsayfasi.png)

\* Bulunan personel ekle , personel Listesi ve Yönetimi ,Sistem Yöneticilerini Gör butonları ile

Gerekli bilgiler ile (Mail ve username kontrolu yapılarak) personel ekleyebilir

![login](static/images/personelekle.png)

![login](static/images/varsayilanpersonelekleme.png)

![login](static/images/personeleklemebasarili.png)

Personel listesini görebilir
![login](static/images/personellistesi.png)

Personellerin Aktiflik /Pasiflik durumlarını değiştirebilir

![login](static/images/personelaktiflik.png)

Personellerin Şifrelerini unutma durumunda şifrelerini sıfırlayabilir

![login](static/images/personelsifresifirlamaonayi.png)

![login](static/images/sifresifirlamaonayi.png)

Bu şifre sıfırlanırken aynı zamanda admine de mail gider

![login](static/images/adminmail.png)

![login](static/images/personelmail.png)

![login](static/images/personelsifremailgonderildi.png)

Bu değişiklikler yapılırken kullanıcı listesi görünümü ve kitap listesi de güncellendi

![login](static/images/personelkitaplistesi.png)

![login](static/images/personelkitapsilonay.png)
Kitap ödünç durumuna göre;

![login](static/images/kitapsilhata.png)

![login](static/images/kitapsilindi.png)

Kullanıcı Listesi Aktiflik/Pasiflik durumu ve şifre sıfırlama bir araya getirildi

![login](static/images/guncelkullanicilistesi.png)

![login](static/images/sifresifirlaonay.png)

![login](static/images/sifirlabasarili.png)

\* Sistem Yöneticilerini gör butonu ile sistemdeki yöneticileri görebilir, eskisi gibi ekleyebilir silebilir.

![login](static/images/adminlistesi.png)

!!! Varsayilan admin kontrolu eklendi
Artık Default admin silinemez!

![login](static/images/Defaultadmin.png)

\* Diğer roller gibi gerekli kontrolleri sağladıktan sonra giriş yapabilir.

![login](static/images/personelhataligiris.png)

\* Personel doğru bilgiler ile giriş yaptıktan sonra personel anasayfası:

![login](static/images/personelgirisbasarilipng.png)
' bu şekilde görünmektedir.

Eklenen Personel rolü anasayfasında ise Admin gibi ama daha az yetkileri bulunuyor.
Adminlerin de görebileceği gibi güncel admin anasayfasında da olduğu gibi kitap Listesini görebilir ve yönetebilir ve kullanıcı Listesini görebilir ve yönetimini yapabilmektedir.

Ekstra olarak kendi şifrelerini istedikleri gibi değiştirebilmektedir.

![login](static/images/personelsifredeis.png)

![login](static/images/sifredeisbasarili.png)

Duruma göre hata verir;

![login](static/images/sifredeishata.png)

Admin ve personel sayfasinda bulunan ceza ödeme kısmı da güncellendi;

![login](static/images/cezaode.png)

![login](static/images/cezaodeonay.png)

Duruma göre kitap iade edilmişse ceza başarıyla ödenir veya hata verir;

![login](static/images/cezaodeonaylandi.png)

![login](static/images/cezaodehata.png)

Aynı zamanda kullanıcı anasayfası da güncellendi;

![login](static/images/guncelkullanıcı.png)

Duruma göre güncel borcunu görür, ödeme yapar veya hata verir
(Ödeme sistemi entegre etmeyi denedim fakat yapamadım dolayısıyla sadece basit bir html sayfası ile bilgileri alıp hiçbir kontrol yapmadan oanyalıyor şuanlık :(( )

![login](static/images/borc.png)

![login](static/images/borcvar.png)

![login](static/images/borcodehata2.png)

Eklenen ilgili Trigger ile yeni bir üye eklendiğinde mail gitmektedir;

![login](static/images/uyeoldun.png)

Yapılan değişiklikler dolayısıyla ER Diyagramları da güncellendi;

![login](static/images/erguncel.png)

![login](static/images/tablolar.png)

### 11.12.2025 tarihinde atılan commit ile ;

\* Catlary Kütüphane Yönetim Sistemine Kategori ve Yazarlar kısmını ekledim.Sadece Admin rolündeki kullamıcılar bunları yönetebilir;

\*Admin rolundeki kullanıcıların anasayfasında bulunan Kategori Yönetimi yazılı butona tıklandığında tüm kategorilerin bulunduğu bir sayfa gelir ve belirli şartlar dahilinde kategori ekleyip silebiliriz;

![login](static/images/kategoriyonetimiveekleme.png)

![login](static/images/kategorisil.png)

\* Admin rolundeki kullanıcıların anasayfasında bulunan Yazar Yönetimi yazılı butona tıklandığında tüm yazarların bulunduğu bir sayfa gelir ve belirli şartlar dahilinde yazar ekleyip silebiliriz;

![login](static/images/yazaryonetimi.png)

![login](static/images/yazarekleme.png)

![login](static/images/yazareklehata.png)

![login](static/images/yazarsilme.png)

![login](static/images/yazarsilmebasarilipng.png)

![login](static/images/yazarsilmehata.png)

\* Yapılan bu değişiklikler sonucunda hem admin hem de personel rolündeki kullanıcılar kitap eklemesi ekranında ufak değişiklik yapıldı;

![login](static/images/guncelkitapekle.png)

![login](static/images/guncelkitapekle2.png)

\* Kategori ve Yazarların da eklenmesi ile birlikt ER diyagramı da güncellendi;

![login](static/images/GUNCELER.png)

![login](static/images/GUNCELER2.png)

### 13.12.2025 traihinde yapılan güncellemeler ile;

Admin ve personel ana sayfasında sadeleştirilmelere gidildi ve bazı işlemler taşındı;

![login](static/images/engunceladmin.png)

![login](static/images/guncelpersonelanasayfa.png)

Sistem yöneticileri sayfası;

![login](static/images/gunceladminler.png)

Güncel ceza tablosu;

![login](static/images/guncelcezalar.png)

![login](static/images/guncelcezalarfiltrele.png)

Güncel tüm kullanıcıların ödünç geçmişi tablosu;

![login](static/images/gunceloduncgecmisitum.png)

Güncel kitap ödünç verme sayfası;

![login](static/images/guncelodunc.png)

![login](static/images/guncelodunckitap.png)

![login](static/images/guncelouncmail.png)

Ve PayTR odeme sistemi entegre edilmeye çalışıldı.
