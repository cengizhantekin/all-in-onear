# Yerel NEAR Sandbox kurulumu ve gerçek çalıştırma

## Mevcut durum

Araç hazır, **gerçek node deneyi henüz tamamlanmadı**. Çalışma ortamının sabit açık dosya limiti 16.384; resmi Sandbox 2.14.0 ikilisi 65.535 istiyor. Bu sınır nedeniyle ne node ne izin testleri çalışmış sayılır. Uygulamada kaydedilmiş bir sandbox sonucu yok; test dosyalarındaki yapay örnekler arayüze veri olarak verilmez.

40 Python testi ve ayrı bir Node.js çevrimdışı kontrolü geçti. Bunlar sonuç ayrıştırıcısı, kaynak/mod ayrımı, yanlış sonucun reddi, kontratın WebAssembly'ye derlenmesi ve imzalı işlem kodlamasını kontrol eder. NEAR'ın bu işlemleri kabul veya reddettiğini kanıtlamaz.

## 1. Windows'ta WSL/Ubuntu

Microsoft'un resmi yönergesi: https://learn.microsoft.com/en-us/windows/wsl/install

Windows 10 2004/build 19041 ve sonrası veya Windows 11'de PowerShell'i **Yönetici olarak çalıştır** ve şunu gir:

```powershell
wsl --install -d Ubuntu
```

Kurulum isterse bilgisayarı yeniden başlat. Başlat menüsünden **Ubuntu** aç; Linux kullanıcı adı/parolasını oluştur. Bu parola cüzdan anahtarı değildir. Sonra PowerShell'de kontrol edebilirsin:

```powershell
wsl -l -v
```

Bu aşamaya gelince Ubuntu'nun açıldığını bildir; proje klasörünü ve Node kurulumunu birlikte kontrol edeceğiz. Anahtar veya gerçek bakiye oluşturma.

## 2. Ubuntu içindeki ön kontroller

```sh
python3 --version
node --version
npm --version
ulimit -Hn
```

Python 3.11+, Node **22.22.2 veya üstü** gerekli. Sandbox için açık dosya hard limiti en az **65535** olmalı. Hard limit yeterliyse soft limit düşük olduğunda resmi binary bunu yükseltebilir; hard limit sabitse sistemi aşmaya çalışma, bu ortam uygun değildir.

Node'u Ubuntu içinde kur; Windows Node kurulumunu Linux kurulumunun yerine kullanma. Resmi indirme/kurulum seçenekleri: https://nodejs.org/en/download

## 3. Proje klasöründe çalıştırma

Ubuntu'dan Windows diskindeki mevcut proje klasörüne erişilebilir. Örneğin `C:\Users\Cengizhan\Desktop\near-evidence-lab`, `/mnt/c/Users/Cengizhan/Desktop/near-evidence-lab` olur. Bu yalnız örnek; gerçek klasör yolunu kullan.

Proje kökünde:

```sh
npm --prefix sandbox ci --ignore-scripts --no-audit --no-fund
node sandbox/check.mjs
python3 runner.py access --mode sandbox --record
```

İlk komut kilitli bağımlılıkları kurar; npm lifecycle scriptleri çalıştırılmaz. İkinci komut yalnız çevrimdışı hazırlık kontrolüdür. Üçüncü komut resmi 2.14.0 binary'sini indirir/önbelleğe alır, gerçek node başlatır ve deneyi çalıştırır.

İlk indirme yaklaşık 36 MB; başarılı bir capture'dan sonra `data/recordings/access.json` oluşur. Bu dosyada özel anahtar olmamalıdır. Uygulamada **Bounded keys, retained control → Recorded sandbox · recompute** seçeneği açılır. Windows'taki Python sunucusunu yeniden başlat / sayfayı yenile.

Node hatası, indirme hatası veya zaman aşımı başarıya çevrilmez. `--record` olmadan arayüzde çalıştırmak mevcut kaydı yenilemez.

## Sekiz planlı kontrol

| Durum | Beklenen gözlem |
|---|---|
| Full-access anahtarla `blocked` | Kontrat metodu var ve çalışır; `blocked` durumu yazılır |
| Sınırlı anahtarla `allowed` | Metot çalışır; `allowed` yazılır; gas allowance azalır |
| Sınırlı anahtarla `blocked` | Node `MethodNameMismatch` döndürür |
| Sınırlı anahtarla başka kontrat | Node `ReceiverMismatch` döndürür |
| Sınırlı anahtarla 1 yerel yoctoNEAR depozito | Node `DepositWithFunctionCall` döndürür |
| Sınırlı anahtarla transfer eylemi | Node `RequiresFullAccess` döndürür |
| Anahtar silindikten sonra `allowed` | Node `AccessKeyNotFound` döndürür |
| İptal sonrasında sahibin full-access anahtarı | `allowed` çağrısı çalışır; yönetim anahtarı korunur |

Bunlar **beklentidir**, bu sürümün gerçek gözlemleri değildir. Her satırda node yanıtı ve kontratların çağrı sonrası durumu birlikte kontrol edilecektir. Farklı hata veya durum olursa satır `Mismatch` olur.

Full-access/sınırlı anahtarlar geçici ve rastgele üretilir. Node yalnız 127.0.0.1 RPC kullanır. Anahtar ekleme/silme normal yerel işlemlerle yapılır; anahtar davranışı state patch ile taklit edilmez. Kontratların halka açık `get_last` view sorguları anahtar sınırlarının testi değildir.

## Teknik kaynaklar

- https://docs.near.org/protocol/accounts-contracts/access-keys
- https://github.com/near/near-sandbox-js
- https://github.com/near/near-api-js
- Sabit binary kaynağı: https://s3-us-west-1.amazonaws.com/build.nearprotocol.com/nearcore/Linux-x86_64/2.14.0/near-sandbox.tar.gz
