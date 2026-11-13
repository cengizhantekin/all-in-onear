# Intents teklif önizlemesi — ilk bulgular

## Soruyu daraltma

All in oNEar tezinin bu adımı, tek bir entegrasyonun farklı zincir ailelerinde fiyatlanabilir çıktı isteyebilmesini inceler. Önceki katalog testi listelenen varlıkları gösteriyordu; bu deney gerçek servis yanıtlarında giriş/çıkış tutarı ve rota eşleşmesini kontrol eder. Geliştirme süresi tasarrufu veya tüm bileşenlerin birlikte üstünlüğü ölçülmedi.

## Sabit ölçüm protokolü

- Rotalar: NEAR → Base; Base → Solana; Solana → Ethereum.
- Her rotada 25 ve 250 USDC; zincir başına sabit varlık kimliği, 6 ondalık basamak.
- Aynı POST endpoint, EXACT_INPUT, dry=true, 100 bps tolerans, 3000 ms teklif bekleme ayarı.
- Anahtar olmadan; otomatik tekrar yok, her hücrede tek istek, sırayla altı istek.
- Önce canlı katalogdaki varlık kimliği, zincir, sembol ve ondalık metadata kontrol edilir.
- Public örnek adresler yalnızca önizleme isteğinin biçim kontrolü için kullanıldı. Kullanıcı cüzdanı veya kullanılabilir fonlama hedefi değildir.
- Şema kontrolünde hata veren ön yanıtlar araştırma hazırlığıdır. Sabit matris çalıştırılmadan önce istek yapısı donduruldu.

## Yakalama zamanı ve sonuç

Başlangıç: **10.11.2026 16:21:01 TSİ**. Bitiş: **10.11.2026 16:21:56 TSİ**. UTC zamanları ham kayıtta yer alır.
Toplam ilk canlı çalıştırma yaklaşık **54,8 saniye** sürdü. Altı hücrenin tamamında HTTP 201 ve istekle eşleşen dry quote yapısı alındı.

| Rota | Giriş USDC | Teklif çıkışı USDC | Minimum çıkış USDC | API yanıtı ms | Servis tahmini sn |
|---|---:|---:|---:|---:|---:|
| near → base | 25 | 24.992550 | 24.742624 | 8472 | 22 |
| near → base | 250 | 249.968862 | 247.469173 | 7660 | 22 |
| base → sol | 25 | 24.770058 | 24.522357 | 8152 | 32 |
| base → sol | 250 | 249.750893 | 247.253384 | 8524 | 32 |
| sol → eth | 25 | 24.696694 | 24.449727 | 7686 | 27 |
| sol → eth | 250 | 249.673831 | 247.177092 | 8274 | 27 |

Bu sayılar ilgili yakalama anına aittir. Sonraki çalıştırmada sonuçların veya fiyatların aynı kalması beklenmez. USDC girişleri token tutarıdır; 1 USDC = 1 USD varsayımı yapılmadı.

## Teze katkı

Bu örneklemde aynı istek yapısıyla NEAR, EVM ve Solana kaynaklarından seçilmiş başka zincirlere önizleme alınabildi. Üç ayrı rota için tek entegrasyon yüzeyinin yanıt üretmesi, ağ dışındaki uygulama ve kullanıcı etkinliğine erişim tezine somut bir teknik dayanak ekler. Bunun kalıcı kullanıma, gelir akışına veya NEAR token talebine dönüşmesi ayrıca ölçülmelidir.

## Sınırlar ve hata politikası

- 6/6, yalnızca bu seçilmiş küçük matrisin gözlemidir; hizmetin başarı oranı/SLA ya da bütün piyasa hakkında istatistik değildir.
- API yanıtı istemciden ölçülmüştür. Servis ETA değeri gerçekleşen transfer süresi değildir.
- Teklif çıkışı ile giriş farkı, ayrıştırılmış komisyon, kayma veya fiyat etkisi ölçümü değildir.
- Swap/fonlama gerçekleşmedi. Servisin imza alanı saklandı, kriptografik olarak doğrulanmadı.
- HTTP 2xx tek başına yeterli sayılmaz: echo edilen dry bayrağı, varlık kimlikleri, tutar ve rota türleri; baz birim giriş/çıkış tutarları ve minimum çıktı kontrol edilir.
- HTTP hatası, timeout, bozuk/uyuşmayan yanıt ve katalogdan eksik varlık tabloda kalır. Altı planlı hücre paydadan düşürülmez. Katalog alınamazsa deney hata verir; eski başarı sessizce gösterilmez.
- Kayıt checksum ve kaynak hash ile incelenebilir; bunlar bağımsız kaynak kimliği veya zaman tasdiki değildir.

## Hazırlık denemelerini ayırma

Sabit matristen önce istek yapısını sınamak için 5 teklif isteği yapıldı: 3 HTTP 400 ve 2 HTTP 201. Hatalar sıfır adresin reddi, boş recipient/refund/deadline alanlarının reddi ve ilk NEAR refund örneğinde servisin genel hata yanıtını kapsıyordu. Sonrasında public örnek alanları ve sabit rotalarla yukarıdaki altı hücre birer kez çalıştırıldı. Hazırlık istekleri farklı girdiler kullandığı için matrisin 6/6 paydasına eklenmedi; bunlarla birlikte genel başarı yüzdesi türetilmedi. Hazırlık isteklerinin tam ham gövdeleri bu kayıt dosyasının parçası değildir.

## Tekrar üretme

```powershell
py -3 runner.py quotes --mode replay
```

Canlı yeni bir yakalama için:

```powershell
py -3 runner.py quotes --mode live --record
```

`--record`, mevcut quotes kaydını açıkça yeniler. Arayüzdeki sıradan canlı çalıştırma paket içindeki kaydı değiştirmez.

Kaydedilen evidence SHA-256: `d54e20e5271945e576a414753cc46c383819427a42fafce1797eaf72d07c0c01`
Yakalama analizi kaynak SHA-256: `067c546325c384b8d0a74922d13680b1a7750443e8657cacd7fc81c254adc719`

## Birincil teknik kaynaklar

- [Teklif isteği tanımı](https://docs.near-intents.org/api-reference/oneclick/request-a-swap-quote)
- [Desteklenen token metadata tanımı](https://docs.near-intents.org/api-reference/oneclick/get-supported-tokens)
- [NEAR resmi agent araçları: quote istek alanları](https://github.com/near/agent-skills/blob/main/skills/near-intents/rules/api-quote.md)

Kaynaklar istek şemasını açıklar; tablodaki sayılar kendi kaydımızdan hesaplanmıştır.
