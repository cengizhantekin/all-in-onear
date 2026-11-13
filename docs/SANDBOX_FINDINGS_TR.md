# Yerel erişim anahtarı deneyi — doğrulanmış ilk kayıt

Kullanıcının WSL ortamında ürettiği ve inceleme için paylaştığı ham JSON kaydı:
10 Kasım 2026, 16:39:00.503–16:39:03.430 UTC. Node: NEAR Sandbox 2.14.0,
protokol 88. Bu inceleme ortamında yeni bir NEAR node çalıştırılmadı;
paylaşılan gerçek kayıt Python analizinden geçirildi ve 8/8 eşleşme bulundu.

| Kontrol | Gözlenen sonuç |
| --- | --- |
| Tam yetkili anahtarla blocked çağrısı | Başarılı; durum blocked |
| Sınırlı anahtarla allowed çağrısı | Başarılı; durum allowed |
| İzin verilmeyen metot | MethodNameMismatch |
| Başka alıcı sözleşme | ReceiverMismatch |
| Çağrıya 1 yoctoNEAR eklenmesi | DepositWithFunctionCall |
| Transfer eylemi | RequiresFullAccess |
| İptal edilen anahtarla çağrı | AccessKeyNotFound |
| İptalden sonra sahibin çağrısı | Başarılı; durum allowed |

Beş reddedilen işlemden sonra hedef durum allowed, diğer sözleşmenin durumu
none kaldı. Sahibin anahtarı FullAccess olarak kaldı. Sınırlı anahtarın gaz
bütçesi başarılı çağrının ardından azaldı.

Bu bulgu protokol düzeyindeki sınırlı ve iptal edilebilir yetki mekanizmasını
destekler. Mainnet performansı, kullanıcı benimsemesi, token talebi veya gerçek
bir LLM agent davranışı hakkında sonuç üretmez. Tüm bakiyeler yerel test
bakiyeleridir. Allowance genel bir varlık harcama limiti değildir.

## v0.5.2 düzeltmeleri

- İşlem nonce değeri, sorgudaki ve süreçte kullanılan son değerin büyüğünden ilerler.
- Anahtar ve sözleşme durumu sorguları optimistic kullanır; finality gecikmesi
  yeni anahtarları ve durum değişikliklerini gizlemez. Bu durum okumaları final
  kesinleşme ölçümü olarak sunulmaz.
- Sayı ve tam sayı metni nonce değerleri kayıpsız BigInt ile işlenir.
- Eski result.error sorgu zarfı tanınır. İptal kontrolünde hata metni tam olarak
  ilgili anahtarla eşleşmelidir; rastgele sorgu hatası başarı sayılmaz.
- Ayrıntılı yerel RPC hata mesajları korunur.

Doğrulama: 41 Python testi, JavaScript sözdizimi kontrolü, çevrimdışı WAT ve
imzalı işlem kodlama kontrolü geçti. Kullanıcının gerçek kaydı analiz edildi.
Güncellenmiş harness ile yeni uçtan uca çalıştırma kullanıcı ortamında yapılmalıdır.

## Uygulama

Güncellemedeki near-evidence-lab klasörünün içeriğini Ubuntu proje klasörünün
üzerine kopyalayın. Yeniden npm kurulumu gerekmez. Çalışan Python sunucusunu
dosyalar değiştikten sonra yeniden başlatın.

```bash
cd ~/near-evidence-lab
python3 runner.py access --mode sandbox --record
```

Başarılı çalıştırma data/recordings/access.json oluşturur. Recorded sandbox
bu kaydı kullanır. Bu güncelleme yapay veya yeniden oluşturulmuş bir kayıt içermez.
