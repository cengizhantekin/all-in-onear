# NEAR Investment Thesis — Kaynaklar, geniş tez ve teknik araştırma planı

Hazırlanma tarihi: **9 Kasım 2026, Türkiye saati**. Sürüm: 1.0.

Bu belge ilk dört hazırlık adımını kapsar: kaynak toplama, kaynaklardan öğrenme, pozitif yatırım tezi oluşturma ve teknik incelemeleri tasarlama. **Henüz deney yapılmadı, tarihsel veri seti indirilmedi, model çalıştırılmadı ve uygulama geliştirilmedi.** Buradaki deneyler plan, ekonomik çıkarımlar ise sınanacak hipotezdir. Belge tamamlanmış ampirik araştırma veya nihai yarışma teslimi değildir.

Kullanıcının kararı: VPS yenilenmeyecek. Çalışma localde geliştirilecek; kod, analiz ve paylaşılabilir veri GitHub üzerinden yeniden çalıştırılabilir olacak. Büyük uygulama geliştirmesine geçmeden kapsam birlikte seçilecek.

## 1. Araştırmanın çerçevesi

Pozitif yaklaşımımız, NEAR'ın güçlü özelliklerinden başlayıp bunların ekonomik fırsata nasıl dönüşebileceğini açıklamak. Ölçüm sonucunu önceden seçmiyoruz. Olumlu bulguları öne çıkarırken ölçülemeyen alanları, karşı bulguları ve varsayımları ayrı göstereceğiz. Bu yaklaşım, tezin güvenilirliğini ve jüri önünde savunulabilirliğini artırır.

Üç ayrı soruyu birlikte cevaplamak istiyoruz:

1. **Ürün:** NEAR hangi somut sorunları çözüyor ve bunu teknik olarak gösterebiliyor muyuz?
2. **Benimsenme:** Bu özellikler tekrar eden, çeşitli ve ekonomik anlam taşıyan kullanıma dönüşüyor mu?
3. **Token:** Kullanım ve ürün gelirleri NEAR için hangi ölçülebilir talep, yakım veya arz etkisini yaratıyor?

Bir ürünün başarısı, o ürünle ilişkili tokenın yatırım performansını tek başına belirlemez. Bu nedenle uzun vadeli tezde ürün kalitesi, ekonomik aktarım ve piyasa değerlemesi ayrı ele alınacak. Bu hazırlıkta alım önerisi veya fiyat hedefi üretmiyoruz.

Resmî Investment Thesis örneği, yeniden üretilebilir veri analizini merkeze alıyor. İddiayı destekleyen kanıtla birlikte karşı kanıtı ve görüşü değiştirecek sonucu yazmayı öneriyor. Örnekteki BigQuery, SQL ve statik dashboard bir başlangıç yaklaşımı; zorunlu teknoloji listesi değil. [S01–S02]

## 2. Kaynak toplama: kalıcı kaynak dizini

Aşağıdaki 51 kayıt, bu hazırlığın kaynak haritasıdır. İlgili teknik bölümler, açıklamalar ve erişim koşulları incelendi. **S34 yalnız arama motorunun gösterdiği birincil kaynak özeti üzerinden görülebildi; tam sayfa erişimi başarısız oldu.** Diğer kayıtlarda sayfa veya ilgili bölümler açıldı. Depoların README ve ilgili sayfalarının incelenmesi, bütün kodlarının veya audit raporlarının denetlendiği anlamına gelmez.

Tüm kayıtlarda erişim tarihi 2026-11-09. Yayın tarihi belirtilmeyen teknik belgeler canlı belgedir; uygulama aşamasında sürüm/commit ve ağ durumu ayrıca sabitlenecek. Bu dizin kaynak içeriklerinin birebir arşivi değildir; URL, öğrenilen bilgi ve kullanım amacı kaydıdır.

### 2.1. Yarışma ve protokol

| ID | Kaynak | Araştırmada kullanım |
|---|---|---|
| S01 | [HACKATHON.md](https://nearhackathon.com/HACKATHON.md) | Uygunluk, teslim, yerel demo ve yeniden çalıştırılabilirlik |
| S02 | [Investment Thesis kategori örneği](https://github.com/nearai/near-hackathon-prompt-examples/blob/main/tracks/02-thesis.md) | Kategori beklentisi ve araştırma yaklaşımı |
| S03 | [Architectural Overview](https://docs.near.org/protocol/network/architecture) | Shard, hesap, işlem ve receipt ilişkisi |
| S04 | [NEAR Accounts](https://docs.near.org/protocol/accounts-contracts/account-model) | Hesap ile anahtarın ayrılması |
| S05 | [Access Keys](https://docs.near.org/protocol/accounts-contracts/access-keys) | Sınırlı yetki, anahtar rotasyonu ve imza şemaları |
| S06 | [Meta Transactions](https://docs.near.org/protocol/transactions/meta-tx) | Kullanıcıdan gas yönetimini kaldıran relayer akışı |
| S07 | [Gas Keys](https://docs.near.org/protocol/accounts-contracts/gas-keys) | Paralel nonce kanalları ve ayrı gas bütçesi |
| S08 | [Global Contracts](https://docs.near.org/smart-contracts/global-contracts) | Ortak kod, bağımsız durum ve dağıtım maliyeti |
| S09 | [Storage Staking](https://docs.near.org/protocol/storage/storage-staking) | Veri saklama karşılığında ayrılan NEAR |
| S10 | [NEAR Native Token](https://docs.near.org/protocol/network/tokens) | Gas, storage ve staking kullanım alanları |
| S11 | [Gas / Execution Fees](https://docs.near.org/protocol/transactions/gas) | Gerçek işlem maliyeti, iade ve yakım ayrımı |
| S12 | [Validators](https://docs.near.org/protocol/network/validators) | Konsensüs, ödül bütçesi ve stake yoğunlaşması |
| S13 | [Chain Signatures](https://docs.near.org/chain-abstraction/chain-signatures) | NEAR'dan başka zincirlerde imza üretimi |
| S14 | [near/mpc](https://github.com/near/mpc) | İmzalama ağı, güven varsayımları ve audit dizini |

### 2.2. Intents, likidite ve gizlilik

| ID | Kaynak | Araştırmada kullanım |
|---|---|---|
| S15 | [What are Intents?](https://docs.near-intents.org/getting-started/what-are-intents) | Kullanıcının sonuç belirtmesi ve solver rekabeti |
| S16 | [Verifier Contract](https://docs.near-intents.org/integration/verifier-contract/introduction) | intents.near bakiyeleri, settlement ve bridge sınırı |
| S17 | [Intents Fees](https://docs.near-intents.org/resources/fees) | Protokol/API/kanal ücretlerinin ayrılması |
| S18 | [Request a Swap Quote](https://docs.near-intents.org/api-reference/oneclick/request-a-swap-quote) | dry:true ile işlem yapmadan teklif incelemesi |
| S19 | [Explorer API](https://docs.near-intents.org/integration/distribution-channels/1click-api/explorer/introduction) | Tarihsel 1Click verisi, JWT ve hız sınırı |
| S20 | [Explorer Get Transactions](https://docs.near-intents.org/api-reference/get-transactions) | Örnek işlem şeması ve USD alanları |
| S21 | [Intents Security](https://docs.near-intents.org/security-compliance/security) | Audit ve bug bounty kaynaklarına erişim |
| S22 | [Treasury Addresses](https://docs.near-intents.org/security-compliance/treasury-addresses) | Resmî adres etiketleri; operasyonel fonları ayırma |
| S23 | [Confidential Swaps](https://docs.near-intents.org/integration/distribution-channels/1click-api/quickstart/confidential-swaps) | Gizli swap entegrasyon biçimi |
| S24 | [How Confidential Intents Works](https://near.org/blog/how-confidential-intents-works) | 27 Mayıs 2026; private shard mimarisi ve erişim sınırları |

### 2.3. AI, ajanlar ve dağıtım kanalları

| ID | Kaynak | Araştırmada kullanım |
|---|---|---|
| S25 | [NEAR AI Private Inference](https://docs.near.ai/cloud/private-inference) | CPU/GPU TEE ile gizli inference tasarımı |
| S26 | [NEAR AI Verification](https://docs.near.ai/cloud/verification/index) | Attestation, TLS ve yanıt imzası doğrulama ayrımı |
| S27 | [NEAR AI Cloud Verifier](https://github.com/nearai/nearai-cloud-verifier) | Python/TypeScript doğrulayıcı uygulamalar |
| S28 | [Staking for Inference](https://docs.near.ai/cloud/staking-for-inference/overview) | Stake getirisinin compute kredisine dönüşmesi |
| S29 | [IronClaw](https://github.com/nearai/ironclaw) | WASM araç izolasyonu ve credential koruması |
| S30 | [NEAR AI Agent Market](https://market.near.ai/) | Ajan hizmet pazarı ve ekonomik kullanım alanı |
| S31 | [Brave: Browser AI TEE](https://brave.com/blog/browser-ai-tee/) | 20 Kasım 2025; erken entegrasyonun partner doğrulaması |
| S32 | [Brave: Browser AI E2EE](https://brave.com/blog/browser-ai-e2ee/) | 15 Ekim 2026; daha güncel gizlilik ve dağıtım uygulaması |
| S33 | [Ledger: NEAR Intents via Swapkit](https://www.ledger.com/blog-near-intents-joins-ledger-wallet-via-swapkit) | Ledger tarafında entegrasyonun doğrulanması |
| S34 | [Talos: NEAR Intents solver integration](https://www.talos.com/insights/talos-connects-liquidity-from-near-intents-solver-network) | 9 Kasım 2026; kurumsal RFQ entegrasyonu, yalnız kaynak özeti görüldü |

### 2.4. Ekonomi, yönetişim, ölçekleme ve veri

| ID | Kaynak | Araştırmada kullanım |
|---|---|---|
| S35 | [Evolving NEAR Tokenomics](https://near.org/blog/evolving-near-tokenomics) | 24 Şubat 2026; ürün gelirleri, geri alım ve yönetişim takdiri |
| S36 | [The State of NEAR: Q2 2026](https://near.org/blog/the-state-of-near-q-2-2026) | 8 Temmuz 2026; strateji ve tarihsel durum anlatısı |
| S37 | [NEAR Revenue Dashboard](https://revenue.near.org/) | Gelir tanımları ve izlenebilecek adres adayları; rakamlar doğrulanmadı |
| S38 | [House of Stake](https://houseofstake.org/home) | Ekonomik politika ve yönetişim süreci |
| S39 | [HSP-027: Remove Developer Gas Rebate](https://gov.near.org/t/hsp-027-remove-the-near-developer-gas-rebate/42213) | Gas rebate değişikliğinin gerekçesi ve karar metni |
| S40 | [nearcore Releases](https://github.com/near/nearcore/releases) | 2.14.0 değişiklikleri; uygulamada sabit tag kullanılmalı |
| S41 | [Introducing Dynamic Resharding](https://near.org/blog/introducing-dynamic-resharding) | 20 Mayıs 2026; otomatik shard bölünmesi tasarımı |
| S42 | [Near One: Scaling NEAR to 1M TPS](https://blog.nearone.org/announcement/2025/12/11/scaling-near-to-1m-tps.html) | Benchmark kurulumu ve ölçüm sınırları |
| S43 | [SPICE: Separation of Consensus and Execution](https://near.org/blog/separation-of-consensus-and-execution) | 22 Haziran 2026; gelecek protokol geliştirmesi |
| S44 | [Preparing NEAR for the Quantum Era](https://near.org/blog/making-near-protocol-post-quantum-safe) | 6 Mayıs 2026; kriptografik geçiş stratejisi |
| S45 | [NEAR Roadmap](https://roadmap.near.org/) | Intents, AI ve protokolün ortak yönü |
| S46 | [BigQuery Public Dataset](https://docs.near.org/data-infrastructure/big-query) | Tarihsel sorgular, maliyet ve Lake uyarısı |
| S47 | [NEAR Public Lakehouse](https://github.com/near/near-public-lakehouse) | Tablo yapıları ve veri işleme kodu |
| S48 | [NEAR Data Services](https://docs.near.org/data-infrastructure/data-services) | Alternatif veri sağlayıcıları |
| S49 | [FastNear NEAR Data API](https://docs.fastnear.com/neardata) | Yakın dönem blok/shard erişimi ve auth koşulları |
| S50 | [Protocol RPC](https://docs.near.org/api/rpc/protocol) | Blok bazında gerçek protokol konfigürasyonu |
| S51 | [Sandbox Integration Tests](https://docs.near.org/smart-contracts/testing/integration-test) | Yerel kontrat davranışlarını test etme |

## 3. Kaynakları tarama: NEAR hakkında öğrenilenler

### 3.1. Temel mimari ve ekonomik anlamı

NEAR, işlemleri farklı shard'larda paralel işleyebilen bir proof-of-stake ağı. Hesaplar arasında işlem yapılırken receipt adı verilen iç mesajlar oluşuyor. Bir kullanıcı işlemi birden çok receipt ve kontrat çağrısı doğurabilir. Bu yüzden receipt sayısını işlem, işlem sayısını da kullanıcı sayısı yerine koyamayız. Paralel yapı büyüme kapasitesi sunarken, uygulama düzeyindeki tam sonuç gecikmesini ayrıca ölçmemizi gerektiriyor. [S03]

Token; işlem yürütme, zincirde veri saklama ve ağ güvenliği için kullanılıyor. Storage için ayrılan NEAR veri silinince serbest kalabiliyor. Bu, kullanım ile token talebi arasında incelenebilir bir bağ; kalıcı yakım anlamına gelmiyor. Ortak kod ve verimlilik iyileştirmeleri aynı kullanıcı sayısının daha az storage gerektirmesini de sağlayabilir. [S09–S10]

### 3.2. Hesap ve yetkilendirme avantajı

Bir hesap birden fazla anahtar taşıyabiliyor. Function-call anahtarı belirli kontrat ve yöntemlere sınırlandırılabiliyor; normal anahtardaki allowance gas bütçesidir. Bunu bütün token harcamalarını otomatik sınırlayan genel bir bütçe sanmamalıyız: çağrılan kontratın yetkileri ayrıca incelenir. Hesap kimliğinin anahtardan ayrı olması rotasyon ve yeni imza şemalarına geçiş açısından esneklik sağlıyor. [S04–S05]

Meta transaction akışında gas ücretini relayer ödeyebiliyor. Kullanıcı deneyimi açısından başlangıç engelini azaltır; maliyet sistemden kaybolmaz, ödeyen taraf değişir. [S06]

Gas keys ayrı ön ödemeli gas bakiyesi ve paralel nonce kanalları sunuyor. Bu özellik bot, relayer ve çok sayıda ajan işlemi için değerlendirilebilir. Global contracts ise birçok hesabın aynı kodu paylaşmasına ve kendi durumunu korumasına izin veriyor. İkisi farklı sorunları çözüyor: işlem paralelliği ve kod dağıtım maliyeti. [S07–S08]

### 3.3. Intents ve Chain Signatures birbirinden farklıdır

Intents, kullanıcının istediği sonucu belirtmesi ve çözüm sağlayıcıların teklif üretmesi yaklaşımıdır. Verifier kontratı bakiyeleri ve uygun intent gruplarının yürütülmesini yönetir. Dış zincir giriş/çıkışları bridge ve diğer bileşenler üzerinden gerçekleşir. İç settlement atomikliği, bütün dış zincir adımlarının aynı anda ve aynı güven varsayımıyla kesinleştiği anlamına gelmez. [S15–S16]

Chain Signatures, bir NEAR hesabının farklı zincirler için imza üretmesini sağlayan MPC altyapısıdır. Tek bir anahtar yöneticisine bağımlılığı azaltan bir tasarım sunar; imzacı çoğunluğu, kullanılan yazılım ve hedef zincir gibi varsayımlar devam eder. İmza üretmek ve karşı zincirdeki bir olayı doğrulamak ayrı kabiliyetlerdir. Repo yeni okuma/doğrulama bileşenleri de anlatıyor; bunların canlı ağ kapsamı ayrıca saptanmalı. [S13–S14]

### 3.4. Gizlilik iki ayrı üründe iki ayrı mimariye dayanıyor

NEAR AI tarafında TEE tabanlı inference ve doğrulama akışları bulunuyor. Gateway attestation, model attestation, TLS bağlama ve varsa yanıt imzası farklı kanıtlar sağlıyor. Modelin doğru cevap verdiğini veya bir işletmenin kârlı olduğunu kanıtlamazlar. Gizlilik iddiasının kapsamı seçilen model, istek yolu ve doğrulama politikasına bağlıdır. [S25–S27]

Confidential Intents belgesi, permissioned bağımsız doğrulayıcılarla çalışan private shard ve bridge bağlantısını tarif ediyor. İç hareketler için herkese açık RPC ve explorer bulunmadığını söylüyor. Bu nedenle kamuya açık zincir verisiyle bütün gizli akışı yeniden kurabileceğimizi varsayamayız. Public giriş/çıkış gözlemi iç işlem hacmine eşit değildir. [S23–S24]

### 3.5. Ajanlar, ödeme ve dağıtım

IronClaw; araç izolasyonu, izin verilen endpoint'ler ve credential koruması gibi kontroller anlatıyor. Bunlar ajanların gerçek iş yapabilmesi için gerekli güven katmanlarına aday. Repo açıklaması sistemin bütün saldırıları engellediğinin bağımsız kanıtı değildir. Agent Market ise ajan hizmetlerinin satın alınabileceği bir ürün yüzeyi sunuyor; görülen ana sayfa USD/USDC ile ödemeden söz ediyor. Buradan her hizmet alımının NEAR token satın alımı yarattığı sonucu çıkmaz. [S29–S30]

Brave ve Ledger kendi kanallarından NEAR tabanlı entegrasyonlarını açıklıyor. Bu, yalnız NEAR'ın kendi ortaklık listesinden daha sağlam bir ürünleşme işareti. Fakat erişilebilen toplam kullanıcı kitlesi, aktif kullanıcıya veya NEAR gelirine eşit değildir. Talos duyurusu kurumsal dağıtım için ek aday kanıttır; bu belgede tam sayfa doğrulanamadığı için ikincil önemdedir. [S31–S34]

### 3.6. Ekonomi: güncellik zorunlu

NEAR'ın ürün gelirlerini token ekonomisine bağlamaya yönelik resmî açıklamaları var. Geri alım, elde tutma, stake etme ve yakımın farklı arz sonuçları bulunur. Yönetişim kararıyla uygulanabilecek bir araç ile gerçekleşmiş zincir üstü hareket ayrı kaydedilecek. [S35, S38]

Güncel validator belgesi yıllık ödül bütçesini toplam arzın %2,5'i olarak tanımlıyor; bunun %10'unu protokol hazinesine ayırıyor. Bu oranı kullanırken veri tarihindeki gerçek ağ ayarını doğrulayacağız. Güncel gas belgeleri ve 2.14.0 sürüm notları developer gas rebate'in kaldırılmasını anlatıyor. Daha eski %5 emisyon veya genel %70 yakım/%30 rebate anlatılarını bugüne otomatik taşımayacağız. [S11–S12, S39–S40]

## 4. Kaynaklarda saptanan kritik ayrımlar

| Konu | Bulgu | Çalışmaya etkisi |
|---|---|---|
| NEAR Lake | Resmî belge AWS S3 Lake kaynağının 24 Mart 2026'da yeni blok indekslemeyi bıraktığını belirtiyor; BigQuery'nin de aynı gün durduğunu söylemiyor. | Her tablonun son tarihini ayrı kontrol edeceğiz. [S46] |
| Lakehouse README | Eski ingestion mimarisini hâlâ tarif ediyor. | README'den güncel veri kapsamını varsaymayacağız. [S47] |
| Explorer API | JWT istiyor; partner başına beş saniyede bir istek sınırı anlatılıyor; kapsamı tarihsel 1Click işlemleri. | Anahtar, kapsam ve indirme süresi veri kapısıdır. Bütün Intents evreni olarak sunulamaz. [S19] |
| API ücreti | HACKATHON.md anahtarsız %0,2 diyor; güncel ücret belgesi anahtarsız non-ANY_INPUT tekliflerde ek %0,25 tanımlıyor. | Ekonomik hesapta güncel ücret politikası ve gerçek yanıt kullanılacak. [S01, S17] |
| Revenue dashboard | Sayfa bazı alanları 0 gösteriyor ve alt notunda rakamların illustrative olduğunu belirtiyor; farklı açılışlarda görünen bazı değerler de değişti. | Bu gözlem tek başına hata veya sahte veri kanıtı değildir; ekrandaki rakamlar ölçüm tabanımıza alınmadı. Ham veri ve tanım doğrulaması gerekli. [S37] |
| Gas rebate | 2.14.0 notu ve canlı doküman 30% rebate'in kaldırılmasını tarif ediyor. | Dönemler farklı kurallarla hesaplanmalı; mainnet aktivasyon bloğu ayrıca doğrulanmalı. [S11, S40] |
| 1 milyon TPS | Mühendislik benchmark'ı 70 shard ve özel ağ kurulumu kullanıyor. | Bunu mainnet'teki günlük kullanım veya bizim ölçümümüz olarak yazmayacağız. [S42] |
| SPICE | İncelenen yazı gelecek sürüm geliştirmesi olarak anlatıyor. | 200 ms hedefi şu anda bütün mainnet işlemleri için ölçülmüş sonuç sayılamaz. [S43] |
| Post-quantum | Hesap anahtarları ve imza doğrulama ilerlemesi var; bütün konsensüs/bridge/hedef zincir sisteminin korunması ayrı mesele. | Tam ekosistem kuantum güvenliği iddiası kurmayacağız. [S05, S40, S44] |
| Partner entegrasyonu | Ürünün dağıtımını gösteriyor. | Duyuru tarihini, aktif kullanım ve geliri birbirine karıştırmayacağız. [S32–S34] |

## 5. Geniş kapsamlı pozitif tez

### 5.1. Ana iddia

**NEAR'ın uzun vadeli fırsatı; kullanıcıların ve ajanların farklı zincirlerdeki para ve hizmetlere erişimini kolaylaştıran, gizli hesaplama ile ekonomik işlemleri birlikte sunan bir altyapıya dönüşmesidir. Ölçeklenebilir yürütme, esnek hesaplar, Intents dağıtımı ve doğrulanabilir AI bir araya geldikçe NEAR, kendi zincirine taşınmayan ekonomik faaliyetten de fayda sağlayabilir. Bu fırsatın token yatırım tezine dönüşmesi, tekrar eden kullanımın ölçülebilir net gelir ve NEAR'a ekonomik katkı üretmesine bağlıdır.**

Bu, kaynaklardan oluşturduğumuz araştırmacı sentezidir. Gelecek başarısı doğrulanmış bir olgu değildir. Yol haritası iki tamamlayıcı alanı — zincirler arası finans ve otonom ajanları — ortak bir stratejiye bağlıyor. Biz bu stratejinin hangi bölümünün bugün kanıtlanabildiğini, hangi bölümünün opsiyon değeri taşıdığını inceleyeceğiz. [S45]

### 5.2. Tez A — Büyüyen çok zincirli dünyaya ortak erişim

Varlıkların tek zincirde toplanmasını beklemek yerine, farklı zincirlerdeki varlıkları ortak bir işlem deneyimine bağlamak önemli bir fırsat. NEAR, kullanıcıyı cüzdan, gas ve rota ayrıntılarından uzaklaştırabildiği ölçüde daha büyük bir kullanım alanına ulaşabilir. [S15]

Pozitif çıkarımımız: diğer ekosistemlerin büyümesi NEAR için de erişilebilir işlem akışı yaratabilir. Bu iddianın dayanağı yalnız desteklenen zincir sayısı olamaz; farklı rotalarda tekrar eden hacim, rekabetçi net çıktı ve gerçek kullanıcı talebi görmeliyiz. Ana ağdaki hesap sayısına sığmayan bir dağıtım modeli, NEAR'ı değerlendirmek için daha geniş ölçüm gerektirir.

### 5.3. Tez B — Kullanıcının zaten bulunduğu yerde dağıtım

Her kullanıcıya yeni cüzdan veya yeni uygulama yükletmek yerine mevcut ürünlerin içine altyapı olarak girmek büyümeyi kolaylaştırabilir. Ledger/Swapkit bağlantısı bu modelin somut bir örneği. [S33]

Bizim çıkarımımız: partnerlerin arayüz, güven ve müşteri edinimi avantajlarından yararlanan bir altyapı, tek bir markalı uygulamanın büyüme hızını aşabilir. Sağlam kanıt; kaç partner duyurulduğundan çok, kanalların ne kadar kullanıldığı ve ekonomik katkılarının nasıl dağıldığıdır. Partner yoğunlaşmasını da ölçmek, büyümenin birkaç kanala bağlı kalıp kalmadığını anlamamızı sağlar.

### 5.4. Tez C — Likidite ve dağıtımın birbirini güçlendirmesi

Solver'ların teklif verdiği yapı, kullanılabilir varlıklar ile işlem taleplerini buluşturmaya çalışıyor. [S15] Araştırma hipotezimiz şu: daha çok dağıtım kanalı daha çok talep getirebilir; daha çok talep likidite sağlayıcısını çekebilir; daha iyi teklifler kullanıcıların tekrar gelmesini destekleyebilir.

Bu olası ağ etkisinin varlığını fiyat teklifleri, rota kapsaması, hacim devamlılığı ve elde edilebilirse solver yoğunlaşmasıyla araştırabiliriz. API'nin sunduğu en iyi tekliften kaç bağımsız solver'ın rekabet ettiğini çıkaramayız. Gözlenemeyen rekabet parametreleri raporda açık kalır.

### 5.5. Tez D — Ajanlar için programlanabilir ekonomik kimlik

Bir ajanın hizmet satın alması, bütçe kullanması ve görev yürütmesi için kalıcı kimlik, yetki sınırları ve işlem araçları gerekir. Çok anahtarlı hesaplar, function-call yetkileri ve anahtar iptali bu ihtiyaçlarla uyumlu bileşenlerdir. [S04–S05]

Pozitif çıkarım: bu özelliklerin protokol düzeyinde bulunması, ajan uygulamalarında tekrar yazılan bazı altyapı işlerini azaltabilir. Kanıtımız, gerçek bir ajan kullanıcısının ödemesi yerine önce dar ve kontrollü bir yetkilendirme deneyi olabilir. Bu deney teknik elverişliliği gösterir; gelecekte kaç işletmenin kullanacağını göstermez.

### 5.6. Tez E — Küçük ve sık işlemler için maliyet yapısı

Ajanların ekonomik faaliyetleri, insanlardan farklı işlem sıklıkları yaratabilir. Ön ödemeli gas bütçesi ve paralel nonce kanalları, tek hesaptan yoğun işlem üreten sistemlere uygun tasarım seçenekleridir. [S07] Ortak kontrat kodu kullanımı da tekrar eden dağıtımlardaki saklama yükünü azaltabilir. [S08]

Bizim araştırma yönümüz, bir işin tamamlanma maliyetini ölçmek: bir anahtar ekleme, bir çağrı zinciri veya bir kullanıcı örneği başlatma. Yalnız en ucuz transferi seçmek yerine iş yükünü tanımlayıp bütün receipt ve storage etkilerini hesaba katmak daha ikna edici olur.

### 5.7. Tez F — Gizli AI için doğrulanabilir hizmet katmanı

NEAR AI, TEE tabanlı inference için doğrulama yolları sunuyor. [S25–S26] Brave'ın daha güncel yazısı, NEAR AI tabanlı gizli inference'ı tarayıcıdaki uçtan uca şifreleme ve OHTTP akışıyla birleştirdiğini anlatıyor. Bu, bir gizlilik özelliğinin kullanıcı ürününe ulaşmasına örnek. [S32]

Pozitif çıkarımımız: hassas verilerle çalışan kuruluşlar ve kullanıcılar, yalnız sözleşmesel gizlilik vaadi yerine inceleyebilecekleri teknik kanıt isteyebilir. Bunun ekonomik büyüklüğünü bugünden varsaymayacağız. Önce hangi kanıtın doğrulanabildiğini gösterebilir; ücretli talep ve gelir verisi yoksa o kısmı geleceğe yönelik fırsat olarak bırakabiliriz.

### 5.8. Tez G — Finansal gizlilik profesyonel kullanımı genişletebilir

Public order flow bazı kullanıcıların pozisyon ve stratejilerini açığa çıkarır. Confidential Intents bu görünürlüğü azaltmaya yönelik farklı bir işlem ortamı sunuyor. [S23–S24]

Pozitif hipotez: daha kontrollü görünürlük, belirli kurumsal ve profesyonel işlemlerin NEAR altyapısına gelmesini kolaylaştırabilir. Burada teknik gizlilik özelliği ile gerçekleşmiş kurumsal hacmi ayıracağız. Seçili akışın görünürlüğünü incelemek mümkün olabilir; kamuya kapalı bütün shard faaliyetini bağımsız yeniden üretmek şu an planlanamaz. Bu özelliği ana nicel tez yerine destekleyici ürün tezi olarak kullanmak daha uygulanabilir.

### 5.9. Tez H — İşlem kapasitesinin talebe uyarlanması

Sharding ve otomatik shard bölünmesi tasarımı, talep büyüdükçe daha çok paralel işlem alanı açmayı hedefliyor. [S03, S41] Mühendislik benchmark'ı yüksek kapasite için önemli kanıt sunuyor; fakat native transfer ağırlıklı özel kurulumu gerçek kullanım karmasından ayrılmalı. [S42]

Pozitif çıkarımımız: kullanıcı deneyimi ve ekonomik kullanım büyürse, kapasitenin genişleyebilmesi talebin ücret artışı veya gecikmeyle bastırılmasını azaltabilir. Biz localde bu büyük benchmark'ı tekrar etmiş gibi davranmayacağız. Gerçek blok zamanları, işlem sonuçları ve maliyet dağılımı daha erişilebilir bir analiz sağlar; yüksek kapasite iddiası kaynaklı teknik bağlam olur.

### 5.10. Tez I — Kullanımın ürün gelirine dönüşebilmesi

Intents ekonomisinde protokol, API ve dağıtım kanalı ücretleri farklı katmanlar. Güncel ücret belgesi farklı rota ve kimlik doğrulama koşullarını ayırıyor. [S17] Bu yapı, yalnız temel gas ücretine dayalı bir gelir incelemesinden daha geniş bir araştırma gerektiriyor.

Pozitif çıkarım: aynı işlem hacmi, dağıtım karışımı ve ürün koşullarına göre farklı ekonomik katkı yaratabilir. Bu nedenle en değerli grafiklerden biri hacim ile toplam ücret ve elde tutulan gelir arasındaki dönüşüm olabilir. Bir işlem tutarına tek sabit komisyon uygulayıp sonucu gerçekleşmiş gelir diye sunmayacağız.

### 5.11. Tez J — NEAR'a ekonomik katkının ölçülebilmesi

Ürün geliri NEAR satın alımı, elde tutma, stake etme veya yakım gibi farklı uygulamalarla ilişkilendirilebilir. Resmî ekonomik çerçeve yönetişim takdirini açık bırakıyor. [S35] Tokenın gas, storage ve staking işlevleri ise ayrı kullanım alanları. [S10]

Hipotezimiz: tekrar eden gelir ve gözlenebilir token hareketleri birlikte büyürse uzun vadeli ekonomik dayanak güçlenir. Bunu araştırırken işletmenin geliri, token alımına harcanan tutar, yakılmış NEAR ve dolaşımdan geçici ayrılmış NEAR için ayrı seriler gerekir. Böylece “ekonomik katkı” gibi geniş bir ifadenin hangi somut mekanizmaya dayandığını gösterebiliriz.

### 5.12. Tez K — Staking ile compute arasında yeni bir kullanım bağı

Staking for Inference belgesi, staking getirisinin AI kullanım kredisine çevrildiği bir model anlatıyor. NEAR fiyatı, stake miktarı ve getiri oranı kullanılabilecek compute bütçesini etkiliyor. [S28]

Bizim çıkarımımız: bu tasarım token elde tutma ile hizmet tüketimini bağlayan ilginç bir kullanım yolu sunuyor. Senaryo hesaplayıcısıyla hangi koşullarda ne kadar compute karşılanabildiğini gösterebiliriz. Ancak getiri dış gelirle aynı şey değildir; fırsat maliyeti ve token fiyat değişimi hesaba katılmalı. Ürünün varlığı ile ne kadar kullanıldığı ayrıca değerlendirilir.

### 5.13. Tez L — Güvenlik ve uyarlanabilirlik uzun vadeli kullanımın ön koşulu

IronClaw'ın araç ve credential kontrolleri, ajanların güvenli çalışmasına yönelik bir katman. [S29] Hesap anahtarlarının değiştirilebilmesi ve yeni imza şemaları eklenebilmesi de uzun ömürlü hesap tasarımı açısından avantaj sağlayabilir. [S44]

Pozitif çıkarım: altyapının güvenlik gereksinimlerine uyarlanabilmesi, ürünlerin ve kurumların kullanım kararını destekleyebilir. Kuantum sonrası bir anahtarı doğrulamak tüm ekosistemin kuantum güvenliğini ispatlamaz. Güvenlik incelememiz belirli davranış ve tehdit modeliyle sınırlı kalacak. Bu başlık ekonomik ana tezin yanında teknik dayanıklılık kanıtı olarak kullanılabilir.

### 5.14. Tez M — Birleşik ürün yapısı, yeni kullanım alanlarını daha ucuz açabilir

AI, kimlik, imza, ödeme ve settlement bileşenleri birlikte çalışabildiğinde yeni ürünler mevcut parçaları kullanarak daha hızlı kurulabilir. Bu sentez, yol haritasındaki finans ve ajan birlikteliğinin ekonomik gerekçesidir. [S45]

Stablecoin taşıma, hizmet ödemeleri, ajan pazarı, gizli işlemler ve zincirler arası finans, bu bütünleşmenin farklı kullanım alanlarıdır. Her birine aynı gelir beklentisini yüklemeyeceğiz. Veriyle desteklenebilen bugünkü ürünler ana senaryoya; erken ürünler ve gelecek özellikleri ise ayrı büyüme seçeneklerine konulacak.

### 5.15. Zaman ufku ve değerleme yaklaşımı

Aşağıdaki ufuklar organizatör beklentisi veya fiyat tahmini değil, bizim modelleme tercihimizdir:

| Ufuk | Araştırma odağı | Tezi güçlendirecek gelişme |
|---|---|---|
| Önümüzdeki 12 ay | Mevcut ürünlerin kullanımı ve ücret aktarımı | Devam eden kullanım, daha iyi gelir dönüşümü, gözlenebilir token katkısı |
| 1–3 yıl | Daha fazla dağıtım ve ajan iş yükü | Çeşitli kanallardan tekrar eden ekonomik faaliyet |
| 3–5 yıl | Finans ve gizli AI altyapısının daha geniş yerleşmesi | Ürünlerin birlikte kullanımının kalıcı talep ve gelir yaratması |

Bir ileriki aşamada piyasa değerini de modele katabiliriz. Bunun için aynı tarihe ait token fiyatı, dolaşım/total arz tanımı ve ekonomik katkı serisi gerekir. Tokenı otomatik olarak şirket hissesi gibi değerlendirip bütün ürün gelirinin token sahibine nakit olarak aktığını varsaymayacağız.

## 6. Teknik test ve analiz haritası

Bu bölüm **çalıştırılmış deney sonuçlarını içermez**. Öncelik ve emek tahminleri, veri erişimi henüz doğrulanmadığı için başlangıç değerlendirmesidir. P0 temel araştırma, P1 destekleyici kanıt, P2 isteğe bağlı genişlemedir. Tek bir teslimde bütün satırları gerçekleştirmek hedeflenmiyor.

| ID | İncelenecek tez | Yöntem ve veri | Üretilecek çıktı | Erişim / sınır | Öncelik |
|---|---|---|---|---|---|
| T01 | Verinin güvenilirliği | Şema, son blok/tarih, örnek kayıt ve eksik gün kontrolü | Veri kalite karnesi | BigQuery/Explorer erişimi sınanacak | P0 |
| T02 | Intents kullanımı | Başarılı işlemleri tekilleştir; haftalık sayı ve hacim | Kullanım ve büyüme grafikleri | 1Click kapsamı açık yazılacak | P0 |
| T03 | Büyümenin devamlılığı | 7/30/90 günlük pencereler, medyan ve sıçrama günlerini çıkarma | Büyüme dayanıklılığı paneli | Yeterli tarih geçmişi gerekli | P0 |
| T04 | Ekonomik rota çeşitliliği | Zincir/varlık çifti ve stablecoin rotaları | Yoğunlaşma ve rota haritası | İç yeniden dengeleme ayrımı gerekli | P0 |
| T05 | Kullanıcı devamlılığı | Sabit gözlenebilir kimlik varsa kohort ve geri dönüş | Kullanım devamlılığı analizi | Adres insan değildir; kimlik yoksa yapılamaz | P1 |
| T06 | Ücret → net katkı | Sözleşme/kanal tanımıyla ücret serilerini uzlaştırma | Ekonomik aktarım tablosu | Hacim × varsayılan ücret yeterli değil | P0 |
| T07 | Gerçekleşmiş token etkisi | Etiketli adres hareketlerini işlem bazında sınıflama | Alım/elde tutma/yakım ayrı serileri | Treasury girişi tek başına gelir veya yakım değil | P0 |
| T08 | Uzun vadeli senaryolar | Hacim, efektif gelir oranı, tahsis ve fiyat varsayımları | Duyarlılık ve başa baş hesaplayıcısı | Senaryo ile gerçekleşmiş veri ayrı | P0 |
| T09 | Temel ağ kullanım kalitesi | Kontrat, signer, işlem ve receipt ayrımı | Kullanım bileşimi paneli | Bot/relayer ayrımı kesin olmayabilir | P1 |
| T10 | İşlem maliyeti ve sonuç süresi | Sabit iş yükü; final durum, receipt zinciri, RPC süreleri | p50/p95 maliyet ve gecikme | RPC gecikmesi konsensüs gecikmesi değildir | P1 |
| T11 | Teklif kalitesi | Sabit rota/tutar/saatte dry:true teklifleri | Teklif kapsaması ve net çıktı dağılımı | Gerçekleşmiş işlem başarısı göstermez | P1 |
| T12 | Ajan yetki sınırlaması | Sandbox'ta izinli/yasak kontrat-metot ve anahtar iptali | Başarılı/engellenen eylem kayıtları | Genel harcama güvenliği iddiası kurulmaz | P1 |
| T13 | Gas keys yararı | Sabit sürümde tek nonce / çoklu lane karşılaştırması | Yerel iş yükü tamamlanma dağılımı | Mainnet kapasite benchmark'ı değildir | P2 |
| T14 | Ortak kontrat ekonomisi | Aynı uygulamanın normal/global dağıtımı | Storage ve kurulum farkı | Kod/veri büyüklüğü sabit tutulacak | P1 |
| T15 | Chain Signatures elverişliliği | Türetme ve imza doğrulaması; uygun test ortamı | İmza/geçersiz payload testleri | Yerel mock canlı MPC'nin yerini tutmaz | P2 |
| T16 | Gizli AI doğrulanabilirliği | Nonce, attestation, TLS ve mevcut yanıt imzası kontrolü | Doğrulama raporu ve bozulmuş veri testi | Canlı endpoint/anahtar/ücret koşulları doğrulanacak | P1 |
| T17 | Gizli işlem ürünü | Doküman ve public giriş/çıkış sınırlarını inceleme | Görünürlük ve güven modeli haritası | Private shard içi bağımsız sayım yapılamaz | P2 |
| T18 | Staking → compute | Stake, fiyat, APY ve kullanım fiyatı senaryoları | Compute bütçe hesaplayıcısı | Getiri ve fiyat oynaktır; tasarruf kanıtı değildir | P2 |
| T19 | Güvenlik bütçesi ve dağılım | Validator stake payları ve ödül/gelir karşılaştırması | Yoğunlaşma ve güvenlik finansmanı | Aynı operatörün çoklu hesapları olabilir | P2 |
| T20 | Geleceğe uyarlanabilir hesap | Desteklenen ağda ML-DSA doğrulaması/rotasyon | Başarılı ve bozulmuş imza sonuçları | Tam kuantum güvenliği kanıtlanmaz | P2 |

### 6.1. Önerilen ana araştırma ekseni

Geniş tezi koruyup ilk teknik ürünü **“Kullanımdan NEAR'a Ekonomik Katkıya”** sorusu etrafında kurmayı öneriyorum. Bu henüz kullanıcı tarafından seçilmiş nihai isim veya kapsam değildir.

Birbirine bağlanan dört bölüm yeterince güçlü bir araştırma omurgası oluşturabilir:

1. **Talep:** Kullanım hangi rotalarda, ne kadar sürekli ve ne kadar çeşitli?
2. **Dönüşüm:** Bu kullanım hangi ücretleri ve hangi tanımla net ekonomik katkıyı yaratıyor?
3. **Token etkisi:** Gerçekleşen token alımı, yakım ve geçici arz ayrılması nasıl ayrışıyor?
4. **Gelecek koşulları:** Farklı büyüme ve ekonomik tahsis varsayımları sonucu nasıl değiştiriyor?

Bu eksen T01–T04 ve T06–T08'e dayanır. Bir küçük teknik gösterim ekleyeceksek, veriyle destekleyebildiğimiz iddiaya en yakın olanı seçeriz. Çok sayıda bağımsız özellik demosu ana araştırmayı dağıtabilir.

### 6.2. Ekonomik modelin ilk taslağı

Aşağıdaki denklemler araştırma tasarımıdır; NEAR'ın bütün ekonomik akışını kapsayan doğrulanmış muhasebe modeli değildir.

| Sembol | Tanım |
|---|---|
| V | Aynı dönemde, seçilen kapsamda tekilleştirilmiş swap hacmi |
| F | Aynı hacim kapsamından doğan brüt ücretler |
| R | Belgelenmiş tanıma göre ekosistem/protokol tarafından elde tutulan gelir |
| A | O gelirden token alımına gerçekten tahsis edilen para |
| P | Gerçek alımların ağırlıklı fiyatı veya senaryo fiyatı |
| B | Kalıcı olarak yakıldığı doğrulanan NEAR |
| I | Dönemde yeni üretilen NEAR |

Efektif ücret oranı = F / V. Gelir tutma oranı = R / F. Alınan NEAR için senaryo yaklaşımı = A / P; gerçekleşmiş miktar varsa işlem kayıtlarından ölçülür. Net arz değişimi, model kapsamındaki diğer arz olayları da uzlaştırılarak hesaplanır. Yalnız yeni üretim ve yakım varsa I − B olur.

**Çifte sayım kontrolü:** Aynı gelirle alınan NEAR daha sonra yakıldıysa, alım ve yakımı iki bağımsız gelir katkısı gibi toplamayacağız. Alınan fakat hazinede duran NEAR toplam arzı azaltmaz. Storage/staking kilitleri de kalıcı yakımla toplanmaz. Kullanıcı mevduatı veya bridge likiditesi gelir değildir.

Gelecek senaryosunda A = V × efektif net gelir oranı × alıma ayrılan pay olarak modellenebilir. Bütün bu parametreler görünür olacak. Emisyon karşılaştırması hem NEAR cinsinden hem aynı dönemin fiyat yöntemiyle USD cinsinden gösterilecek; yalnız tek günün fiyatıyla tarihsel karşılaştırma yapılmayacak.

### 6.3. Deney tasarımının kanıt standardı

- Araştırma sorusu, tarih aralığı, kapsam ve hariç tutulan kayıtlar sonuçları görmeden tanımlanacak.
- Başarısız/iptal/iade işlemleri hacim hesabına gelişigüzel eklenmeyecek; kaynak statüleri eşlenecek.
- Bir swap'ın giriş ve çıkış değeri toplanarak hacim ikiye katlanmayacak.
- USD tutarının kaynağı, fiyat zamanı ve token decimals dönüşümü belirtilecek.
- Kullanıcı, signer, relayer, kontrat ve receipt ölçümleri ayrı tutulacak.
- Eğilim ile nedensellik ayrılacak. Korelasyon geleceği öngörme başarısı olarak sunulmayacak.
- Olumlu bulunan rota ve günler seçilip diğerleri gizlenmeyecek. Tam örnekleme planı ve başarısız sorgular kaydedilecek.
- Her grafiğin hesap kodu, veri özeti ve yorum sınırı bulunacak.
- Bir ölçüm yapılamazsa sebebi ve kullanılabilecek daha dar ölçüm gösterilecek.

## 7. Veri erişimi ve çalışma ortamı

Bu aşamada erişilebilirlik **doküman düzeyinde** incelendi. Hesap, anahtar, kota, güncel veri aralığı veya ücretsiz kullanım için başarılı canlı veri denemesi henüz yok.

| Kaynak / ortam | Sağlayabileceği veri veya deney | İlk kontrol |
|---|---|---|
| BigQuery | Tarihsel işlem, receipt ve outcome analizleri | Şema, MAX tarih ve partition kapsamı; dry-run byte tahmini |
| 1Click Explorer | Tarihsel swap ve statüler | JWT erişimi, global/partner görünümü ve sayfalama |
| NEAR RPC | Protokol sürümü, blok ve kontrat durumu | Public endpoint'in erişimi, tarihsel saklama ve hız sınırı |
| FastNear | Yakın dönem blok/shard dilimleri | API anahtarı, ücretsiz kapsam ve geçmiş derinliği |
| NEAR AI | Attestation ve seçili model çağrısı | İstek yolu, güncel model, anahtar ve küçük kullanım maliyeti |
| Sandbox | Hesap ve kontrat davranışları | Sabit sürüm, Windows/WSL/Docker desteği ve kurulabilirlik |

BigQuery'nin bulutta sorgulanması VPS kiralamayı gerektirmez; yerel program bu hizmeti kullanabilir. Fakat veri erişimi/sorgu maliyeti devam edebilir. Güncel fiyat ve kotalar bu hazırlıkta ayrıca doğrulanmadı; 2023 fiyatını bugünkü bütçe olarak kullanmıyoruz. [S46]

Yerel geliştirme için ilk tercih önerim: Python ile toplama/analiz, SQL ile sorgular, Parquet/CSV ile paylaşılabilir veri, DuckDB gibi yerel bir analiz katmanı ve statik web dashboard. Bu bir mimari öneridir; henüz bağımlılık veya sürüm seçilmedi. Kontrat deneyi seçilirse ayrı Rust/Sandbox bölümü eklenebilir.

## 8. GitHub'dan yeniden çalıştırılabilir teslim tasarımı

Amaç, değerlendiren kişinin kendi sandbox veya container ortamında açık talimatlarla aynı araştırma sonuçlarını üretebilmesi. Her olası sandbox'ın internet ve işletim sistemi kısıtları için koşulsuz çalışma garantisi veremeyiz; desteklenen ortamları açıkça belirleyip temiz kurulumda sınayacağız.

| Çalıştırma modu | Beklenen davranış |
|---|---|
| Kayıtlı veriyle analiz | Anahtar ve yeni veri çekimi olmadan, sabit veri setinden ana grafik ve tabloları üretir |
| Güncel veri yenileme | Kullanıcının kendi anahtarlarıyla kaynağa gider; yeni tarih/sürümle ayrı çıktı üretir |
| Yerel teknik deney | Seçilen Sandbox veya verifier deneyini açık ön koşullarla çalıştırır |

Teslim paketinde veri sözlüğü, kaynak URL'leri, veri alma zamanı, kapsam, sorgu/commit sürümü ve SHA-256 özetleri tutulacak. API anahtarları `.env` içinde kalacak; `.env.example` yalnız değişken isimlerini içerecek. Kod ve veri lisansları ayrı değerlendirilecek. Kamuya açık bir verinin otomatik olarak yeniden dağıtım izni verdiğini varsaymayacağız.

Tek komut hedefi, bağımlılık kurulumu ve desteklenen ortam hazırlandıktan sonra araştırmayı yeniden üretmektir. İlk kurulum paket indirmesi gerektirebilir; tam çevrimdışı kurulum ayrı bir teslim kapsamıdır. Statik dashboard tarayıcıda hazır sonuçları gösterebilir. Ana sonuçlar yalnız bize ait ücretli anahtara bağlı olmayacak.

## 9. Beşinci adıma geçiş için önerilen sıra

Bu bölüm bir uygulama başlangıcı değil, çalışma sırası önerisidir:

1. Ana ekonomik araştırma sorusunu ve başarı ölçütlerini birlikte seçmek.
2. Küçük veri erişim kontrolleriyle yeterli tarih ve alan bulunduğunu doğrulamak.
3. Veriyi tanımlamak, kalite raporu hazırlamak ve ilk temel serileri çıkarmak.
4. Ekonomik aktarım analizini üretmek; veri izin verirse token hareketleriyle uzlaştırmak.
5. Bir destekleyici teknik deneyi seçmek veya tamamen ekonomik analize odaklanmak.
6. Dashboard, tez metni ve senaryo hesaplayıcısını aynı kanıt yapısına bağlamak.
7. Temiz ortamda yeniden çalıştırma, README, kaynak/lisans kontrolü ve demo videosu.

Resmî son teslim 14 Kasım 2026 23:59 UTC, Türkiye saatiyle **15 Kasım 02:59**. [S01] Bu nedenle geniş tez araştırma haritamız olabilir; teknik teslim kapsamını veri erişimi görüldükten sonra daraltmalıyız. Genişlik, her başlık için ayrı uygulama geliştirme yükümlülüğü yaratmamalı.

## 10. Hazırlığın sonucu ve açık kalanlar

İlk dört adım için kaynak haritası, güçlü yönlerin teknik açıklaması, 13 ana temalı pozitif tez ve 20 test/analiz adayı hazırlandı. Bu çalışmanın en güçlü özgün katkı fırsatı, teknik kabiliyetleri doğrudan ekonomik sonuçlarla ilişkilendirip **hangi kullanımın NEAR'a ne tür katkı ürettiğini** görünür kılmak olabilir. Bu bir seçim önerisi; henüz kanıtlanmış sonuç değil.

Henüz bilinmeyenler: veri kaynaklarının bize açık gerçek kapsamı; güncel tarihsel veri sürekliliği; gelir adreslerinin tam ve doğru sınıflaması; ücretlerin partner bazında fiilî dağılımı; geri alım/yakım muhasebesinin tam uzlaştırılması; hedef ortamda kurulabilirlik; modelin bulacağı sonuçlar. Bunları çözmeden kesin rakam, fiyat hedefi, bütün sistem için güvenlik garantisi veya kazanma olasılığı sunulmayacak.

Bu belge sonraki çalışmalarda başvuru kaynağı olarak kullanılabilir. Dinamik rakamlar, ücretler, model listeleri ve ağ sürümleri kullanılacakları tarihte yeniden kontrol edilmelidir.
