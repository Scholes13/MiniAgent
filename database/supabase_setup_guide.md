# Panduan Setup Supabase untuk Crypto Airdrop Analyzer

## Langkah 1: Masuk ke Supabase

1. Buka browser dan navigasi ke [https://supabase.com](https://supabase.com)
2. Login ke akun Anda
3. Akses project "Crypto Airdrop Analyzer" yang telah dibuat

## Langkah 2: Menjalankan SQL Script

1. Di dashboard Supabase, klik menu "SQL Editor" di sidebar kiri
2. Klik tombol "New Query" untuk membuat query baru
3. Copy seluruh isi dari file `schema.sql` yang ada di folder `database`
4. Paste ke editor SQL
5. Klik tombol "Run" untuk mengeksekusi script

## Langkah 3: Verifikasi Tabel

Setelah script berhasil dijalankan, Anda dapat memverifikasi tabel-tabel berikut telah dibuat:

1. Buka menu "Table Editor" di sidebar kiri
2. Verifikasi bahwa tabel-tabel berikut ada:
   - projects
   - twitter_data
   - ai_analysis
   - tokenomics
   - market_data
   - user_watchlist

## Langkah 4: Verifikasi RLS (Row Level Security)

1. Klik pada tabel "user_watchlist"
2. Klik tab "Authentication"
3. Verifikasi bahwa RLS (Row Level Security) telah diaktifkan
4. Pastikan policy-policy berikut telah dibuat:
   - "Users can view their own watchlist"
   - "Users can insert to their own watchlist"
   - "Users can update their own watchlist"
   - "Users can delete from their own watchlist"

## Catatan Tambahan

- Jika ada error saat menjalankan script, pastikan Anda menjalankannya dalam satu operasi (tidak parsial)
- Jika tabel sudah ada sebelumnya, Anda mungkin perlu menghapusnya terlebih dahulu atau menggunakan `CREATE TABLE IF NOT EXISTS` 