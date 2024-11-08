
# Yazılım Geliştirme Projesi - 1 (Ilk Kısım)

İngilizce aksan tespiti için oluşturulmuş crawler’ la ilgili verilerin toplanması ve daha sonra bu verilerin pre-processing işleminden geçirilip işlenmeye hazır duruma getirilmesi.


## Geliştirme Aşamaları

**1.** Konuyla ilgili bir web crawler geliştirildi ve ilgili veriler YouTube üzerinden toplandı.

**2.** Toplanan veriler işlenip 5 saniyelik parçalara bölündü.

**3.** Veriler işlenmeye hazır duruma getirildi.


## Yapılan Pre-processing Işlemleri

- Ses dosyasi mp3 formatindan wav formatina cevrildi.
- 44.1kHz’ den 16kHz’ e resample edildi.
- Sessiz olan kisimlar filtrelendi.
- Gurultu azaltildi.
- Ses normalizasyonu yapildi.
- 5 saniyelik parcalara bolundu.
- Her bir ses parcasi icin MFCC cikarilip csv olarak kaydedildi.

## Sınıflar

| Sınıf             | Veri Sayısı                                                                |
| ----------------- | ------------------------------------------------------------------ |
| American | 7815 |
| Australian | 6714 |
| British | 5005 |
| Indian | 5252 |
| Scottish | 4985 |


## Veri Linki

[13_Veri](https://drive.google.com/file/d/1OOgX5hOHI6_ZeTWsouNzOCKsyssPX3aQ/view?usp=drive_link)
