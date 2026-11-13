# Why NEAR? — Çalışma planı

Kararlar: Local geliştirme, VPS yok, GitHub'dan yeniden çalıştırma. Çalışma adı **All in oNEar**; test alanı **Evidence Lab**. Kullanıcı yaklaşımı: bütünleşik NEAR kabiliyetlerini testlerle açan, kodu gösteren ve sonuçları açıklayan rehber/ajan arayüzü.

## 1. İlk çalışan sürüm — başladı

- [x] Why NEAR? açılışı, tez kartları, tam kod ve komut gösterimi.
- [x] Public RPC üzerinden blok ve sabitlenmiş protokol konfigürasyonu gözlemi.
- [x] MPC kontratı için salt okunur yapılandırma incelemesi.
- [x] Intents varlık kataloğu analizi.
- [x] Sabit Intents dry teklif matrisi: ham yanıt, zaman, tutar ve hata sınıflaması; çevrimdışı replay.
- [x] Varsayımları açık ekonomik senaryo hesaplayıcısı.
- [x] Gerçek kayıtlı veri ve internet gerektirmeyen yeniden hesaplama.
- [x] Capture/çalıştırma zamanı, kaynak/evidence hash'leri ve JSON indirme.
- [x] Windows ve evaluator kurulum talimatları.
- [x] Opsiyonel NEAR AI açıklama adaptörü; model bağlantısı henüz gerçek anahtarla sınanmadı.

## 2. Tezi kanıtlayacak deneyleri seçme

İlk üç gözlem altyapıyı görünür kılıyor; all-in-one avantajını tek başına ispatlamıyor. Bir sonraki hedef, parçaları birlikte kullanan dar ve sonuçlu bir deney tasarlamak. Aday: sınırlandırılmış hesap yetkisi + çok zincirli imza/teklif + doğrulanabilir AI açıklaması. Bütün katmanları tek akışa zorlamadan önce her birinin erişimini doğrulayacağız.

| Modül | Sonraki iş | Tamamlanma ölçütü |
|---|---|---|
| Hesap / yetki | v0.5: sekiz durum için gerçek-node aracı hazır; kullanıcı WSL ortamında ilk capture bekleniyor | Bu çalışma ortamındaki FD limiti nedeniyle gerçek runtime henüz doğrulanmadı; sahte kayıt eklenmedi |
| MPC | Gerçek test destekli imza ve payload doğrulaması | Yetkili ortamda doğrulanmış imza; yalnız mock sonuç sayılmaz |
| Intents | v0.4: ilk dry:true matris tamamlandı; sonraki iş çok zamanlı örneklem / teklif imzası doğrulaması | 3 rota × 2 tutar; ilk kayıtta 6/6 önizleme; tekrarların tüm hata ve sonuçları saklanmalı |
| AI / privacy | Attestation ve uygun yanıt doğrulaması | Güncel doğrulama politikasına göre doğrulanan kanıtlar |
| Ekonomi | Tarihsel kullanım, gelir ve token akışı | Kaynakları uzlaştırılmış seriler; senaryodan ayrı gerçek veri |
| Bütünleşme | Ortak kullanıcı görevi | Birden çok bileşenin birlikte yarattığı avantajı ölçen sonuç |

## 3. Gerçek AI rehberi

v0.3'te soru → deney önerisi → kaynak inceleme → kullanıcı düğmesiyle çalıştırma → sonuç → sonraki soru akışı eklendi. Yerel authored rehber gerçek AI olarak sunulmuyor. Opsiyonel NEAR AI modu aynı katalogdan tek bir deney öneriyor; yanıt şeması backend'de doğrulanıyor. HTTP ve model yanıtı sınırları mock ile test edildi; gerçek anahtarla bağlantı ve TEE doğrulaması henüz yapılmadı. Bu adım tamamlanana kadar gerçek AI agent entegrasyonu kısmen hazır sayılır. Model yalnız allowlist'teki araçları seçebilecek; ölçümleri sabit scriptler üretecek. İlk sürümün scripted guide modu açıkça belirtiliyor. Anahtar olmadan bütün testler çalışacak; AI anlatımı opsiyonel kalacak. Model yanıtı, doğrulanmış ölçümün yerine geçmeyecek.

## 4. Araştırma ve teslim kalitesi

- Canlı/kayıtlı/senaryo/sandbox ayrımı her modülde.
- Karşılaştırma ancak eş iş yükü, tarih ve koşulla; genel üstünlük iddiası yok.
- Her deneyde teknik sonuç, yatırım teziyle bağlantı ve yorum sınırı.
- Geniş tezden dar deneylere bağlantı; yalnız özellik kataloğuyla kalmamak.
- Temiz ortamda kurulum ve yeniden çalıştırma; Windows kontrolü kullanıcı ortamında tamamlanacak.
- Sonraki adımda GitHub repository adresi belirlenip kaynaklar taşınacak.
- Sonraki paketlerde kayıtlı veriyi ve sonuçları analiz eden görseller genişletilecek.

Bu pakette hesap oluşturma, para harcama, işlem imzalama, GitHub'a push veya yarışma başvurusu yapılmadı.
