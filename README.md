# Aplikasi Live Streaming Manager

Aplikasi web untuk mengelola live streaming ke Facebook/YouTube menggunakan ffmpeg tanpa encoding dan video looping. Aplikasi ini mendukung download video dari Google Drive dan manajemen video streaming.

## Fitur Utama

- Registrasi user dengan foto profil
- Dashboard dengan tampilan dark theme
- Monitoring penggunaan sistem (CPU, Memory, Disk)
- Download video dari Google Drive
- Live streaming ke Facebook/YouTube tanpa encoding
- Manajemen video (rename, delete)
- Monitoring status streaming

## Persyaratan Sistem

- Python 3.8+
- FFmpeg
- SQLite3
- Google Drive API Key
- Facebook/YouTube Stream Key

## Instalasi

1. Clone repository ini
```bash
git clone <repository-url>
cd streaming-manager
```

2. Buat virtual environment dan aktifkan
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Buat file .env dan isi dengan konfigurasi yang diperlukan
```env
SECRET_KEY=your-secret-key
GOOGLE_DRIVE_API_KEY=your-google-drive-api-key
FACEBOOK_STREAM_URL=your-facebook-rtmp-url
YOUTUBE_STREAM_URL=your-youtube-rtmp-url
```

5. Inisialisasi database
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
```

## Penggunaan

1. Jalankan aplikasi
```bash
python app.py
```

2. Buka browser dan akses `http://localhost:5000`

3. Registrasi user baru dengan mengisi form dan upload foto profil

4. Setelah login, Anda dapat:
   - Melihat metrik sistem di header
   - Download video dari Google Drive dengan memasukkan File ID
   - Memulai streaming ke Facebook/YouTube
   - Mengelola video yang sudah didownload

## Struktur Direktori

```
streaming-manager/
├── app.py              # File utama aplikasi Flask
├── config.py           # Konfigurasi aplikasi
├── models.py           # Model database
├── utils.py           # Fungsi-fungsi utilitas
├── requirements.txt    # Dependensi Python
├── static/
│   ├── css/
│   │   └── style.css  # Custom CSS
│   ├── js/
│   │   └── script.js  # Custom JavaScript
│   ├── uploads/       # Direktori untuk foto profil
│   └── videos/        # Direktori untuk video
└── templates/
    ├── register.html  # Halaman registrasi
    └── dashboard.html # Halaman dashboard
```

## Endpoints API

- `POST /register` - Registrasi user baru
- `GET /dashboard` - Halaman dashboard
- `GET /get_metrics` - Mendapatkan metrik sistem
- `POST /download_video` - Download video dari Google Drive
- `POST /start_stream` - Memulai streaming
- `POST /stop_stream` - Menghentikan streaming
- `POST /rename_video` - Mengubah nama video
- `POST /delete_video` - Menghapus video

## Keamanan

- Gunakan HTTPS di production
- Simpan kredensial di environment variables
- Validasi input user
- Hashing password
- Manajemen session

## Troubleshooting

1. Jika streaming tidak dimulai:
   - Periksa FFmpeg sudah terinstall
   - Pastikan stream key valid
   - Cek log error di terminal

2. Jika download gagal:
   - Verifikasi Google Drive API key
   - Pastikan File ID valid dan dapat diakses
   - Cek kuota API

3. Jika metrik sistem tidak update:
   - Refresh halaman
   - Periksa koneksi browser
   - Cek log error di console browser

## Kontribusi

Silakan buat issue atau pull request untuk kontribusi.

## Lisensi

MIT License