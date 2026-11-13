# All in oNEar — Geniş tez ve kanıt haritası

Güncelleme: 10 Kasım 2026. Esas belge: NEAR_Investment_Thesis_Hazirlik_2026-11-09.md, bölüm 5 ve 6. İlk belge 13 tez (A–M), 20 test/analiz adayı (T01–T20) içeriyor. Bu harita kapsam değerlendirmesidir; yeni canlı kaynak taraması veya yeni deney sonucu değildir. İlk belgedeki dinamik ürün ve yol haritası bilgileri yayıma alınırken tekrar doğrulanmalıdır.

## Ana anlatı

**All in oNEar:** NEAR'ın uzun vadeli fırsatı; esnek hesaplar, zincirler arası erişim, ödeme, settlement ve gizli AI hizmetlerinin birlikte yeni uygulamalar kurmayı kolaylaştırmasıdır. Bileşenlerin aynı kullanıcı görevinde nasıl birleştiği ana hikâyedir. Kullanımın gelir ve token etkisine dönüşmesi ayrıca araştırılmalıdır.

Bir özellik testi, bütün ekosistemin üstünlüğünü veya gelecekteki getiriyi kanıtlamaz. Pozitif anlatı, gösterilebilen kabiliyetten ekonomik fırsata ilerler; beklenti ile gerçekleşen bulgu ayrı sunulur.

## Sunum biçimleri

- **Teknik deney:** Sabit kod, gerçek giriş, ham çıktı ve yeniden hesaplanabilir sonuç.
- **Veri analizi:** Belirli tarih ve kapsamda gözlem; hesap kodu ve kaynakla birlikte.
- **Senaryo:** Kullanıcının görebildiği varsayımlardan hesaplanan olası sonuç.
- **Kaynaklı konsept:** Ürün/mimari açıklaması, kullanım örneği ve ekonomik gerekçe; deney sonucu olarak etiketlenmez.
- **Yol haritası:** Gelecek özellik veya hedef; canlı ürün durumundan ayrı gösterilir.

Bir tez birden fazla sunum biçimi taşıyabilir. Konsept anlatısında kaynak ve ekonomik gerekçe bulunur; gelecek başarısı kanıtlanmış gibi yazılmaz.

## 13 tezin tam eşlemesi

| ID | Tez / sunum başlığı | Bugünkü kanıtımız | Genişletme ve sunum biçimi |
|---|---|---|---|
| A | Çok zincirli dünyaya ortak erişim | Intents varlık kataloğu ve üç rota × iki tutarlık dry teklif matrisi | Teknik gözlem + konsept. İleride tarihsel rota çeşitliliği ve kullanım. Teklif, gerçekleşmiş dış zincir transferi değildir. |
| B | Kullanıcının bulunduğu yerde dağıtım | Uygulamada ayrı modül yok; ilk belgede partner kaynakları var | Önce kaynaklı konsept: ürün → entegrasyon → kullanıcı görevi. Partnerlerin kendi duyuruları yeniden kontrol edilecek. Kullanıcı tabanı aktif kullanım olarak sayılmayacak. |
| C | Likidite ile dağıtımın birbirini güçlendirmesi | Tek bir zamandaki altı teklif, teklif elverişliliğine dar kanıt | Konsept + çok zamanlı sabit teklif analizi. Ağ etkisi uzun vadeli hipotez; altı teklif solver rekabetini veya kullanıcı devamlılığını kanıtlamaz. |
| D | Ajanlara sınırlı ve iptal edilebilir ekonomik yetki | Kullanıcının WSL ortamındaki gerçek Sandbox 2.14.0 kaydı: 8/8 kontrol. Yeniden kayıt ve UI replay doğrulandı | Teknik deney + kullanıcı senaryosu. Mevcut test gerçek LLM agentı içermez; yetki yapıtaşını gösterir. |
| E | Küçük ve sık işlemler için maliyet yapısı | Ayrı karşılaştırmalı deney yok | Global kontrat dağıtımı ile normal dağıtımın aynı iş yükünde storage/kurulum farkı; gas keys paralelliği ayrı deney adayı. Uygulanana kadar kaynaklı konsept. |
| F | Gizli AI için doğrulanabilir hizmet | Opsiyonel AI adaptörü var; gerçek model çağrısı ve attestation henüz doğrulanmadı | Konsept şimdi; erişim uygunsa attestation ve bozulmuş veri kontrolü sonra. API anahtarı açılması bu planla yetkilendirilmiş sayılmaz. |
| G | Finansal gizlilikle yeni kullanım alanları | İlk belgedeki Confidential Intents kaynakları; bağımsız deney yok | Kaynaklı konsept ve görünürlük/güven modeli. Özel shard iç hacmi kamu verisinden ölçülmüş gibi sunulmaz. |
| H | Talebe uyarlanabilen yürütme kapasitesi | Public RPC blok/protokol gözlemi | Teknik bağlam + sınırları belirli blok/işlem analizi. Mevcut blok yüksekliği okuması ölçekleme kapasitesi testi değildir. Büyük benchmark ve yol haritası kaynaklı ayrı bağlamdır. |
| I | Kullanımdan ürün gelirine | Varsayımlı ekonomi hesaplayıcısı; gerçekleşmiş gelir serisi yok | Kaynaklı ücret akışı + senaryo; veri erişirse dönemsel hacim/ücret/net gelir uzlaştırması. Hacim × varsayılan komisyon gerçekleşmiş gelir değildir. |
| J | Ürün başarısının NEAR'a ekonomik katkısı | Senaryo modülü mevcut; alım/yakım serisi uzlaştırılmadı | Gas/storage/staking ile ürün geliri aktarımını ayrı açıklayan konsept; uygun veriyle gerçek hareket analizi. Alım, elde tutma ve yakım birbirine eklenmez. |
| K | Staking ile AI hesaplama arasında bağ | Ayrı modül yok | Önce kaynaklı konsept; sonra stake, fiyat, getiri, compute birim fiyatı ve tahsis oranıyla senaryo. Getiri dış gelir veya risksiz ücretsiz compute diye sunulmaz. |
| L | Güvenlik ve değişen ihtiyaçlara uyarlanabilirlik | Hesap anahtarı iptal/owner kontrol testi dar destek veriyor | Kaynaklı konsept: anahtar rotasyonu, araç izolasyonu ve kriptografik uyarlanabilirlik ayrı alt konular. Uygun ortamda ML-DSA testi eklenebilir; mevcut yetki testi bunları kanıtlamaz. |
| M | Birleşik yapıdan yeni uygulamalar üretmek | Bileşen modülleri ayrı ayrı var; bütünleşik görev testi yok | Ana sentez: kullanıcının veya ajanın tek işi boyunca kullanılan bileşenleri gösteren kaynaklı anlatı. Gelecekte aynı görevde yetki + doğrulanabilir imza + teklif akışı; ölçülmeden daha az entegrasyon maliyeti iddiası sayısallaştırılmaz. |

## 20 adayın mevcut durumla ilişkisi

| Aday | Durum / karar |
|---|---|
| T01 veri kalitesi | Modüllerde ham yanıt ve hash var; tarihsel veri kalite karnesi henüz yok. |
| T02 tarihsel Intents kullanımı | Yapılmadı; veri erişimi gerekli. |
| T03 büyüme devamlılığı | Yapılmadı; yeterli tarihsel seri gerekli. |
| T04 rota çeşitliliği | Katalog ve teklif rotaları gözlendi; gerçekleşmiş ekonomik rota dağılımı ölçülmedi. |
| T05 kullanıcı devamlılığı | Yapılmadı; uygun sabit kimlik gerekli. |
| T06 ücret/net katkı | Yapılmadı; doğrulanabilir ücret ve gelir kapsamı gerekli. |
| T07 gerçekleşmiş token etkisi | Yapılmadı; etiketli adres ve muhasebe uzlaştırması gerekli. |
| T08 ekonomik senaryolar | Temel hesaplayıcı mevcut; gerçekleşmiş seri değildir. |
| T09 kullanım bileşimi | Yapılmadı; blok konfigürasyonu gözlemi bu analizin yerine geçmez. |
| T10 maliyet/sonuç süresi | Tanımlı karşılaştırmalı iş yüküyle yapılmadı. |
| T11 dry teklifler | İlk 3×2 matris tamamlandı; çok zamanlı örneklem yapılmadı. |
| T12 yetki kısıtlaması | Gerçek yerel node üzerinde 8/8; kullanıcı UI replay doğruladı. |
| T13 gas keys | Yapılmadı; önce kaynak/sürüm ve SDK desteği kontrol edilecek. |
| T14 global kontratlar | Yapılmadı; sıradaki yerel deney adayımız. |
| T15 Chain Signatures | Kontrat yapılandırma gözlemi mevcut; türetme/gerçek imza doğrulama henüz yok. |
| T16 gizli AI doğrulama | Yapılmadı; uygun kanıt ve erişim gerekli. |
| T17 gizli işlemler | İlk kaynak incelemesi var; ürünün güncel durumu tekrar kontrol edilerek konsept sunulabilir. |
| T18 staking/compute | Yapılmadı; ayrı varsayımlı hesaplayıcı adayı. |
| T19 güvenlik bütçesi/dağılım | Yapılmadı; ekonomik senaryodan ayrı validator analizi gerekli. |
| T20 geleceğe uyarlanabilir hesap | Yapılmadı; protokol/sürüm desteği kontrolü sonrası dar test veya kaynaklı konsept. |

## Açılış ve gezinme

Why NEAR ana sayfası 13 uzun kartla doldurulmayacak. Beş anlaşılır grup altında A–M başlıklarına erişim sağlanacak:

1. **Reach across chains:** A, B, C; MPC/Chain Signatures burada açıklanır.
2. **Build for people and agents:** D, E.
3. **Keep sensitive work private:** F, G.
4. **Scale and adapt:** H, L.
5. **Connect usage to value:** I, J, K.

M, sayfanın açılışındaki All in oNEar ana sentezi ve grupları birleştiren kullanıcı görevidir. Böylece 13 tez sunulur; başlık sayısını artırmak için tekrar üretilmez.

Her detay sayfası: iddia → neden önemli → kaynaklı açıklama → varsa ilgili deney/veri/senaryo → bulgu → ekonomik bağlantı → sınır ve sonraki adım.

Deneyi olan detaylarda Evidence Lab bağlantısı bulunur. Konsept detayında kod çalıştırma düğmesi zorunlu değildir; kaynak ve uygulama senaryosu gösterilir. Kayıtlı sonuç, canlı sonuç, senaryo ve yol haritası görünür biçimde ayrılır. Gerçek AI bağlantısı kurulana kadar yerel rehber model agentı olarak tanıtılmaz.

## Önerilen uygulama sırası

1. A–M kapsamını siteye taşımak için kaynakları güncelle, konsept metinlerini ve mevcut deney bağlantılarını hazırla. Bu belge henüz site arayüzünü değiştirmedi.
2. **T14 global kontrat ekonomisi:** Mevcut WSL/Sandbox kurulumu kullanılabildiği takdirde normal/global aynı kodun kurulum ve storage farkını ölç. Önce sabit sürümde desteği doğrula. E için bağımsız yeni teknik bulgu hedeflenir.
3. **T15 MPC:** Halka açık gerçek imza kaydıyla payload ve türetilmiş anahtar doğrulamasının mümkün olup olmadığını araştır; mümkünse bozulmuş payload testi ekle. Yeni anahtar veya ücretli işlem otomatik başlatılmaz.
4. **T18 staking/compute:** Güncel formülü kontrol et, açık varsayımlı hesaplayıcı ekle.
5. **T11 teklif tekrarları ve ekonomik veri erişimi:** Sabit örnekleme planı kur; erişebildiğimiz veri kadar tarihsel analizi genişlet.
6. Gizli AI doğrulaması, gas keys, validator dağılımı ve kriptografik uyarlanabilirlik için erişim ve süreye göre teknik deney seç. Konsept sunumu bu deneyleri beklemez.

MPC tek olası sonraki adım değildir. Önce kapsamın tamamı görünür olur; yeni deneylerde yerel olarak tekrarlanabilir ve açık sonuç veren işler öne alınır.

## Kaynaklar

Ana harita, 9 Kasım tarihli hazırlık belgesinin A–M ve T01–T20 kayıtlarını korur. Aşağıdaki adresler tekrar kontrol edilecek birincil kaynak girişleridir; bu belge bunların bugün yeniden açıldığını iddia etmez.

- Hesap/yetki: https://docs.near.org/protocol/accounts-contracts/access-keys
- Global kontratlar: https://docs.near.org/smart-contracts/global-contracts
- Gas keys: https://docs.near.org/protocol/accounts-contracts/gas-keys
- Chain Signatures: https://docs.near.org/chain-abstraction/chain-signatures
- Intents: https://docs.near-intents.org/getting-started/what-are-intents
- AI doğrulama: https://docs.near.ai/cloud/verification/index
- Staking for Inference: https://docs.near.ai/cloud/staking-for-inference/overview
- Confidential Intents: https://near.org/blog/how-confidential-intents-works
- Ekonomik çerçeve: https://near.org/blog/evolving-near-tokenomics
- Yol haritası: https://roadmap.near.org/

Tam 51 kaynak kaydı ve ilgili açıklamalar ilk hazırlık belgesindedir. Yeni kanıtlar için modüllerin ham kayıtları, kullanıcıdan gelen iki sandbox çıktısı ve SANDBOX_FINDINGS_TR.md esas alınmıştır. İlk belgedeki eski 'deney yapılmadı' ve PLAN.md içindeki 'ilk capture bekleniyor' ifadeleri güncel sandbox durumunu yansıtmaz; bu harita ilgili başlıkta onları günceller.
