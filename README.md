# Crypto Airdrop Analyzer

Sistem analisis untuk mengidentifikasi airdrops kripto yang potensial

## Fitur

- Scraping Twitter untuk data proyeksi kripto
- Analisis AI untuk mengevaluasi potensi airdrops
- Dashboard untuk mengelola dan memonitor analisis
- Integrasi dengan OpenRouter untuk dukungan AI yang fleksibel

## Penggunaan OpenRouter

Sistem ini memanfaatkan OpenRouter API untuk akses ke berbagai model AI dengan strategi fallback cerdas:

### Model Utama (Berbayar)
- Claude 3 Haiku/Sonnet/Opus untuk berbagai tingkat analisis
- GPT-3.5 Turbo untuk operasi standar
- GPT-4 Turbo untuk analisis kompleks

### Model Fallback (Gratis)
Jika terjadi pembatasan API atau kredit tidak mencukupi, sistem akan otomatis fallback ke model gratis:
- Mistral 7B Instruct untuk analisis umum
- Llama 3.1 8B Instruct untuk scraping dan ekstraksi
- Gemma untuk tugas ringan

Model gratis memerlukan pengaturan Data Policy khusus pada header API:
```
Data-Policy-1: on  # Allow prompt to be used for improvement of OpenRouter
Data-Policy-2: on  # Allow prompt to be shared with model providers
Data-Policy-3: on  # Allow responses to be used for improvement of OpenRouter
Data-Policy-4: on  # Allow responses to be shared with model providers
```

Sistem akan mencoba menggunakan model berbayar terlebih dahulu, dan hanya fallback ke model gratis jika terjadi error atau batasan API.

### Mengubah Preferensi Model

Jika Anda ingin memaksa penggunaan model gratis sebagai default (misalnya untuk pengujian atau hemat biaya), Anda dapat mengubah konfigurasi di panel admin atau langsung di kode:

```python
# Di kode
manager = OpenRouterManager(prefer_free=True)  # Gunakan model gratis

# Melalui API
POST /openrouter/preference
Body: {"prefer_free": true}
```

## Mengatur

1. Clone repositori
2. Setup lingkungan virtual dengan `python -m venv backend/venv`
3. Aktifkan lingkungan dan install dependensi dengan `pip install -r backend/requirements.txt`
4. Atur konfigurasi API di `backend/utils/openrouter_config.py`
5. Jalankan server backend dengan `cd backend && uvicorn api.main:app --reload`
6. Untuk frontend, jalankan `cd frontend && npm install && npm run dev`

## Struktur Proyek

- `backend/`: API dan layanan backend
  - `api/`: Endpoints FastAPI 
  - `data/`: Penyimpanan dan cache data
  - `scraper/`: Modul scraping media sosial
  - `utils/`: Utilitas umum dan integrasi
- `frontend/`: Aplikasi Next.js
  - `app/`: Komponen dan halaman
  - `public/`: Aset statis
- `database/`: Schema dan utilitas database

## Setup

### Backend

1. Buat virtual environment Python:

```bash
cd backend
python -m venv venv
```

2. Aktifkan virtual environment:

```bash
# Windows
venv\Scripts\activate

# Unix/MacOS
source venv/bin/activate
```

3. Install dependensi:

```bash
pip install -r requirements.txt
```

4. Setup Supabase:

Baca panduan di `database/supabase_setup_guide.md` untuk langkah-langkah setup Supabase.

5. Update kredensial:

Edit file `backend/utils/supabase_config.py` dan `backend/utils/twitter_config.py` dengan kredensial Anda.

### Menjalankan API

```bash
cd backend/api
uvicorn main:app --reload
```

API akan berjalan di http://localhost:8000.

## Endpoints API

- `GET /health` - Health check
- `GET /projects/latest` - Mendapatkan proyek terbaru
- `GET /projects/top` - Mendapatkan proyek dengan rating tertinggi
- `GET /projects/{project_id}` - Mendapatkan detail proyek
- `POST /projects/` - Membuat proyek baru
- `POST /scrape/twitter` - Memulai scraping Twitter

## Pengujian

### Test Supabase Connection

```bash
cd backend
python test_supabase.py
```

### Test Twitter Scraper

```bash
cd backend
python test_scraper.py
```

### Test API

```bash
cd backend
python test_api.py
```

## Pengembangan Selanjutnya

- Menambahkan analisis AI lanjutan untuk tokenomics
- Fitur pelacakan harga token
- Integrasi data on-chain
- Analisis sentimen dari data media sosial

## Kontribusi

Kontribusi selalu diterima. Silakan buat Issue atau Pull Request untuk berkontribusi.

## Lisensi

[MIT](LICENSE) 