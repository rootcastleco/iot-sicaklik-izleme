# IoT Sıcaklık İzleme Projesi

Bu proje, IoT tabanlı bir sıcaklık izleme sisteminin kurulumu ve yönetimini kapsamaktadır. Sistem, farklı ortamlardan elde edilen sıcaklık verilerinin gerçek zamanlı olarak toplanmasını, analiz edilmesini ve izlenmesini sağlar.

## Özellikler

- Gerçek zamanlı veri takibi
- Sensör simülatörü (gerçek IoT cihazları gibi çalışır)
- SQLite veritabanı ile veri saklama
- Gerçek zamanlı uyarı sistemi
- Çoklu cihaz desteği
- Thread tabanlı asenkron veri toplama
- 5 saniyede bir otomatik veri toplama
- Eşik değerlerini aşan durumlar için otomatik uyarılar
- Sıcaklık ve nem takibi
- İstatistiksel raporlama
- Thread-safe veri işleme
- Kolay genişletilebilir yapı
- MQTT veya HTTP API entegrasyonuna hazır
- Gerçek sensörlere (DHT11, DHT22 vb.) kolayca adapte edilebilir

## Kurulum

1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/rootcastleco/iot-sicaklik-izleme.git
   cd iot-sicaklik-izleme
   ```

2. Gerekli kütüphaneleri kurun:
   Proje dosyasındaki gereksinimler bölümüne göre gerekli bağımlılıkları yükleyiniz.

   ```bash
   # Örneğin:
   pip install -r requirements.txt
   ```

3. Sensörleri bağlayın ve yapılandırın:
   Kullandığınız IoT cihazının modeline göre uygun bağlantıları ve yapılandırmaları tamamlayın.

## Kullanım

Projeyi başlatmak için:

```bash
python iot_project.py
```

- Sistem başlatıldığında otomatik olarak sensörlerden veri çekmeye başlayacaktır.
- Web arayüzünden güncel sıcaklık değerlerini ve geçmiş veri kayıtlarını görebilirsiniz. (Mevcutsa)
- Eşik değerlerini ayarlayabilirsiniz.

## Katkı Sağlama

Projenin gelişimine katkıda bulunmak isterseniz, fork'layabilir ve pull request gönderebilirsiniz. Hatalar ve geliştirmeler için issue oluşturabilirsiniz.

## Lisans

Bu proje MIT lisansı ile lisanslanmıştır. Daha fazla bilgi için LICENSE dosyasını inceleyiniz.

---
Daha fazla bilgi için [proje sayfasına](https://github.com/rootcastleco/iot-sicaklik-izleme) göz atabilirsiniz.
