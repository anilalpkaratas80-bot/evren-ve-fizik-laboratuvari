# Evren ve Fizik Laboratuvarı

Türkçe, etkileşimli bir uzay ve fizik öğrenme uygulaması.

## Mevcut sürüm

Bu depo, Windows üzerinde Python ve Tkinter ile çalışan masaüstü sürümünün kaynak kodunu içerir. Android uygulaması veya Google Play yayını henüz değildir; Windows `.exe` dosyası doğrudan Play Store'a yüklenemez.

Özellikler:

- Sürükleyerek döndürülebilen kara delik modeli; Sgr A*, M87* ve TON 618 profilleri
- Beş aşamalı gözlem/test rehberi ve metin raporu
- Dolaşıklık, çift yarık ve spin olasılığı laboratuvarları
- Altı bilimsel deney için şematik çizimler
- Makaleler, terimler, anlatımlar, Nobel ödülleri ve kaynaklar

Kara delik çizimi ve kuantum deneyleri eğitim amaçlı modellerdir. Çizim tam relativistik ışın izleme, teleskop verisi analizi veya laboratuvar ölçümü değildir. TON 618 uzaklık değeri kozmoloji varsayımına dayalı yaklaşık model girdisidir; EHT halka ölçümü olarak sunulmaz.

## Çalıştırma

Python ve Tkinter kurulu Windows ortamında:

```powershell
python alp_expo.py
```

Bağımsız Windows uygulaması oluşturmak için PyInstaller:

```powershell
python -m PyInstaller --onefile --windowed --name "Evren-ve-Fizik-Laboratuvari" alp_expo.py
```

## Giriş ve yayın durumu

Bu masaüstü sürümünde Google veya telefon numarasıyla giriş yoktur. Doğrulama eklemek için veli tarafından yönetilen bir kimlik sağlayıcısı, uygulama yapılandırması ve gizlilik incelemesi gerekir. E-posta, parola, SMS kodu veya API gizlisi kaynak dosyalara eklenmemelidir. Android uygulaması veya Google Play yayını henüz değildir; Windows `.exe` dosyası doğrudan Play Store'a yüklenemez.

Kaynak MIT lisansı altındadır. Bu sürüm ücretsiz kullanılabilir ve dağıtılabilir kalır; ilerideki ayrı sürümlerin fiyatı ve lisansı ayrıca belirlenebilir.

## Lisans

MIT lisansı için `LICENSE` dosyasına bakın.
