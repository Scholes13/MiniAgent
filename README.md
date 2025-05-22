# Crypto Airdrop Analyzer

Sistem analisis airdrop crypto yang mengumpulkan data dari Twitter, menganalisisnya dengan model AI, dan menyimpan hasilnya dalam database.

## Fitur Utama

- **Twitter Scraper**: Mengumpulkan tweet terbaru dengan hashtag terkait crypto
- **Analisis AI**: Menggunakan OpenRouter untuk akses ke berbagai model AI
- **Penyimpanan Database**: Menyimpan hasil analisis untuk referensi
- **Sistem Fallback Model**: Beralih dari model berbayar ke gratis saat kredit habis
- **Manajemen Error**: Penanganan kesalahan yang komprehensif dengan retry
- **Logging yang Jelas**: Log yang informatif dalam bahasa Indonesia
- **Frontend Modern**: Antarmuka pengguna responsif menggunakan Next.js dan Tailwind CSS
- **Integrasi Supabase**: Menggunakan Supabase untuk database dan autentikasi

## Struktur Proyek

```
Crypto
  ├── api/              # API endpoints
  ├── backend/          # Backend core
  │   ├── scraper/      # Twitter scraper
  │   ├── utils/        # Utilitas dan konfigurasi
  │   └── data/         # Data yang dikumpulkan
  ├── database/         # Modul database
  └── frontend/         # Antarmuka pengguna Next.js
      ├── app/          # Pages dan routes
      ├── components/   # Komponen React yang dapat digunakan kembali
      └── lib/          # Hooks dan utilities
  ├── scripts/          # Script untuk setup dan konfigurasi
```

## Penggunaan

1. Pastikan semua dependensi telah diinstal
2. Konfigurasi kredensial Twitter dan OpenRouter
3. Jalankan `python backend/airdrop_pipeline.py` untuk mode pengujian
4. Untuk monitoring berkelanjutan, ubah mode menjadi "continuous"
5. Jalankan frontend dengan `cd frontend && npm run dev`

## Fitur

- Scraping Twitter untuk data proyeksi kripto
- Analisis AI untuk mengevaluasi potensi airdrops
- Dashboard untuk mengelola dan memonitor analisis
- Integrasi dengan OpenRouter untuk dukungan AI yang fleksibel
- Tampilan halaman Airdrops untuk melihat peluang airdrop
- Halaman analisis interaktif untuk mengevaluasi proyek crypto
- Sistem otentikasi melalui Supabase
- Database Supabase untuk penyimpanan data

## Penggunaan Supabase

Untuk mengatur Supabase:

1. Buat akun di [Supabase](https://supabase.com)
2. Buat proyek baru
3. Salin URL dan kunci API Anda ke `.env.local`:

```
NEXT_PUBLIC_SUPABASE_URL=https://your-project-url.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

4. Jalankan script setup untuk menyiapkan tabel dan data contoh:

```bash
node scripts/setup-db.js
```

### Struktur Database

Proyek ini menggunakan dua tabel utama:

1. **projects**: Menyimpan data proyek crypto:
   - id (primary key)
   - project_name
   - token_symbol
   - description
   - website_url
   - twitter_handle
   - discovery_date
   - overall_rating
   - analysis_status

2. **system_logs**: Menyimpan log aktivitas sistem:
   - id (primary key)
   - message
   - level (info, warning, error)
   - source
   - created_at

## Frontend

Frontend dibangun menggunakan Next.js dan Tailwind CSS, menyediakan:

- **Halaman Airdrop**: Menampilkan daftar peluang airdrop dengan detail seperti nilai perkiraan, legitimasi, dan tingkat risiko
- **Detail Airdrop**: Tampilan mendetail untuk setiap peluang airdrop, termasuk analisis AI
- **Halaman Analisis**: Memungkinkan pengguna memasukkan URL Twitter atau nama proyek untuk analisis
- **Navigasi Responsif**: Mendukung tampilan desktop dan mobile dengan menu yang responsif
- **Admin Dashboard**: Menampilkan data proyek dari Supabase dan log aktivitas sistem

### Menjalankan Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend akan berjalan di http://localhost:3000

### Login Admin

Untuk demo/development, gunakan:
- Email: admin@example.com
- Password: password

Atau klik "Demo Login" untuk masuk tanpa kredensial.

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

## Autentikasi

Sistem autentikasi mendukung dua metode login:

1. **Supabase Auth** - Jika Supabase diaktifkan dan terhubung dengan benar
2. **Local Auth** - Sebagai fallback jika Supabase Auth tidak berfungsi

### Kredensial Demo
- **Email:** admin@example.com
- **Password:** password

### Cara Mengatasi Masalah Login

Jika mengalami masalah login:

1. Pastikan halaman login dimuat dengan benar
2. Gunakan kredensial demo yang telah disediakan
3. Jika tombol login tidak merespon, coba reload halaman
4. Jika masih bermasalah, buka Console DevTools dan periksa error

## Pengembangan

### Menjalankan Frontend

```bash
cd frontend
npm run dev
```

Buka [http://localhost:3000](http://localhost:3000)

### Environment Variables

Untuk konfigurasi Supabase, salin file `.env.example` menjadi `.env.local` dan isi kredensial Anda:

```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
``` 