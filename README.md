# Smart Ecommerce Platform (Mikroservis Tabanlı Akıllı E-Ticaret)

Konya Teknik Üniversitesi Bilgisayar Mühendisliği Bölümü Bitirme Projesi.

---

## Mimari ve Port Dağılımı

| Servis | Teknoloji | Port | Açıklama |
| :--- | :--- | :--- | :--- |
| **API Gateway** | ASP.NET Core & YARP | `5000` | Tüm dış isteklerin karşılandığı ters proxy (Reverse Proxy) |
| **Auth Service** | ASP.NET Core Web API (JWT) | `5001` | Kullanıcı kaydı, girişi ve JWT token yönetimi |
| **PostgreSQL** | Docker (postgres:16) | `5432` | İlişkisel veriler (Kullanıcılar, Siparişler) |
| **MongoDB** | Docker (mongo:7) | `27017` | Esnek ürün kataloğu (Scraper ile çekilen ürünler) |
| **Redis** | Docker (redis:7) | `6379` | Sepet yönetimi ve önbellekleme |

---

## Hızlı Başlangıç

### 1. Veritabanı ve Altyapıyı Başlatma (Docker)
```bash
cd infra
docker compose up -d
```

### 2. AuthService'i Çalıştırma
Yeni bir terminalde:
```bash
cd src/Services/AuthService
dotnet run
```
* Tarayıcıdan test arayüzü: [http://localhost:5001/scalar/v1](http://localhost:5001/scalar/v1)

### 3. API Gateway'i Çalıştırma
Yeni bir terminalde:
```bash
cd src/Gateways/ApiGateway
dotnet run
```
* Gateway Sağlık Kontrolü: [http://localhost:5000/](http://localhost:5000/)

---

## API Testleri (Gateway Üzerinden)

API Gateway (`http://localhost:5000`), gelen `/api/auth/*` isteklerini otomatik olarak arka plandaki `AuthService`'e (`http://localhost:5001`) yönlendirir.

### 1. Kayıt Olma (Register)
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "fullName": "Ali İhsan Tosun",
    "email": "ali@example.com",
    "password": "Password123!"
  }'
```

### 2. Giriş Yapma (Login)
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ali@example.com",
    "password": "Password123!"
  }'
```
*Geriye dönen yanıttaki `token` değerini kopyalayın.*

### 3. Yetkili Profil Bilgisini Alma (Authorize / Me)
```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer <BURAYA_JWT_TOKEN_GELECEK>"
```
