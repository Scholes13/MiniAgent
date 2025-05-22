# Crypto Airdrop Pipeline

Sistem otomatis untuk memonitoring, menganalisis, dan menyimpan peluang airdrop cryptocurrency dari Twitter.

## Arsitektur Sistem

Sistem ini terdiri dari 3 komponen utama:

1. **Twitter Scraper** - Mengumpulkan data terbaru dari Twitter berdasarkan hashtag dan keyword terkait cryptocurrency
2. **AI Processor** - Menganalisis tweet menggunakan AI untuk menentukan legitimasi dan nilai dari peluang airdrop
3. **Supabase Database** - Menyimpan hasil analisis untuk diakses melalui aplikasi web

## Alur Proses

```
Twitter API → Twitter Scraper → AI Processor → Supabase → Web Application
```

1. **Pengumpulan Data**: 
   - Scraper Twitter mengumpulkan tweet terbaru berdasarkan hashtag seperti #airdrop, #solana, #sol, $sol
   - Data difilter berdasarkan relevansi dan skor engagement
   - URL tweet diambil untuk referensi

2. **Analisis AI**:
   - Setiap tweet dianalisis oleh AI
   - Model AI menentukan legitimasi, risk level, dan potensi nilai
   - Panduan langkah-langkah untuk mengklaim airdrop dihasilkan

3. **Penyimpanan Data**:
   - Hasil analisis disimpan di database Supabase
   - Tabel `crypto_airdrops` menyimpan semua informasi
   - View `v_promising_opportunities` menampilkan peluang paling menjanjikan

## Komponen-komponen

### Twitter Scraper (`twitter_scraper.py`)

- Menggunakan library `twikit` untuk mengakses Twitter tanpa API key
- Mengambil tweet terbaru berdasarkan hashtag tertentu
- Melakukan penilaian awal berdasarkan engagement dan kredibilitas

### Airdrop Pipeline (`airdrop_pipeline.py`)

- Mengoordinasikan seluruh proses dari scraping hingga penyimpanan
- Mengelola autentikasi dan koneksi ke layanan eksternal
- Menjadwalkan eksekusi berkala

### Konfigurasi (`utils/config.py`)

- Menyimpan konfigurasi untuk Twitter dan Supabase
- Mengelola variabel lingkungan dan kredensial
- Konfigurasi interval monitoring

### Database Schema (`database/supabase_schema.sql`)

- Definisi struktur tabel untuk menyimpan data airdrop
- Pengaturan keamanan dan akses
- Indeks untuk optimasi query

## Setup dan Penggunaan

### Prasyarat

- Python 3.9+
- Akun Twitter
- Project Supabase

### Instalasi

1. Clone repositori
   ```bash
   git clone https://github.com/username/crypto-airdrop-pipeline.git
   cd crypto-airdrop-pipeline
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Setup variabel lingkungan (atau edit `utils/config.py`)
   ```bash
   export TWITTER_USERNAME="your_twitter_username"
   export TWITTER_EMAIL="your_twitter_email"
   export TWITTER_PASSWORD="your_twitter_password"
   export SUPABASE_URL="https://your-project.supabase.co"
   export SUPABASE_KEY="your_supabase_anon_key"
   ```

4. Setup database Supabase
   - Jalankan SQL dari `database/supabase_schema.sql` di SQL Editor Supabase

### Menjalankan Pipeline

Mode test (satu kali):
```bash
python airdrop_pipeline.py
```

Mode continuous (24/7 monitoring):
```bash
# Edit file airdrop_pipeline.py
# Ubah mode = "test" menjadi mode = "continuous"
python airdrop_pipeline.py
```

## Diagram Alur

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│             │    │             │    │             │    │             │
│   Twitter   │───>│   Scraper   │───>│ AI Analysis │───>│  Supabase   │
│             │    │             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                          │                                      │
                          │                                      │
                          ▼                                      ▼
                  ┌─────────────┐                       ┌─────────────┐
                  │             │                       │             │
                  │  JSON File  │                       │     Web     │
                  │   Backup    │                       │ Application │
                  │             │                       │             │
                  └─────────────┘                       └─────────────┘
```

## Pengembangan Lanjutan

- **Frontend Admin**: Untuk melihat dan mengelola data airdrop
- **Notifikasi**: Integrasi Telegram/Discord untuk notifikasi real-time
- **Analisis Lanjutan**: Pemfilteran scam yang lebih canggih
- **Multi-platform**: Menambahkan sumber data selain Twitter 