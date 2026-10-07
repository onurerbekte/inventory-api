# Doğrulama / Verification
`python -m pytest -q`: **9 passed**. API uçları TestClient ile, geçici gerçek SQLite dosyalarında test edildi / API endpoints tested with TestClient using actual temporary SQLite files.

CRUD, geçersiz giriş, kısmi güncelleme, sayfalama, parametreli SQL ve yeniden açılışta kalıcılık geçti / CRUD, invalid input, partial updates, pagination, parameterized SQL, and persistence passed.

Gerçek tarayıcı ve uzak sunucu yayını denenmedi / Rendered browser and remote deployment were not tested.
