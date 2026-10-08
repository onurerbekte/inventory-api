# Stok REST API / Inventory REST API

**Kurgusal demo proje / Fictional demo project.** Codex desteğiyle geliştirildi / Developed with Codex assistance.

## Türkçe
FastAPI + SQLite ile ürün ekleme, listeleme, güncelleme, silme ve stok özeti. Fiyatlar TL kuruşu olarak tam sayı tutulur. SQL sorguları parametrelidir. Gerçek müşteri verisi içermez.

Python 3.12+ ile bu klasörde:
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000
```
API belgesi: `http://127.0.0.1:8000/docs`. Uçlar: `GET /health`, `GET/POST /products`, `GET/PATCH/DELETE /products/{id}`, `GET /summary`. POST örneği: `{"name":"Latte","price_cents":13000,"stock":2}`. PATCH kısmi güncellemedir; null ve boş değişiklik kabul edilmez. `limit` (1–100), `offset` (0+) listelemeyi sınırlar. Veritabanı `data/inventory.sqlite` içinde; `DATABASE_PATH` ortam değişkeniyle değiştirilebilir. Durdurma: Ctrl+C.

Demo yerel kullanım içindir; kimlik doğrulama ve kullanıcı ayrımı yoktur. İnternete açık üretim servisi olarak yayınlanmadı. `.gitignore` veritabanı, anahtar ve `.env` dosyalarını dışlar.

## English
A FastAPI + SQLite product CRUD service with an inventory summary. Prices are integer TRY cents; queries are parameterized. Use Python 3.12+ and the commands above. Open `/docs` on port 8000 for interactive API documentation. The database path defaults to `data/inventory.sqlite` and can be set through `DATABASE_PATH`. PATCH accepts partial non-null changes. Pagination uses `limit` and `offset`. Stop with Ctrl+C.

This is a local demo with no authentication or user separation; it is not deployed as a public production service. Databases, environment files, and keys are ignored by Git. Tests cover CRUD, invalid data, pagination, query parameterization, and persistence.

## Doğrulama notu / Verification note

Mola sitesi Opera'da elle açılıp görsel olarak kontrol edildi. Telegram botu gerçek botla elle test edildi. Chrome eklentisi Opera'da elle test edildi. Docker projesi Docker Desktop ile çalıştırıldı; GET /health, GET /products ve POST /products elle denendi. OpenAI projesi anahtarsız demo modunda. Mobil cihaz testi yapıldı; yalnızca Android/iOS/web paketleri derlendi.

The Mola website was manually opened and visually checked in Opera. The Telegram bot was manually tested with a real bot. The Chrome extension was manually tested in Opera. The Docker project was run with Docker Desktop; GET /health, GET /products and POST /products were manually exercised. The OpenAI project is in key-free demo mode. Mobile device testing was performed; only Android/iOS/web bundles were built.
