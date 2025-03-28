# Streaming Manager

Aplikasi manajemen streaming video ke Facebook/YouTube menggunakan FFmpeg tanpa encoding.

## Fitur

- Registrasi user dengan foto profil
- Dashboard dengan tampilan dark mode
- Monitoring penggunaan sistem (CPU, Memory, Disk)
- Download video dari Google Drive
- Live streaming ke Facebook/YouTube tanpa encoding
- Manajemen video (rename, delete)
- Tabel status streaming dan daftar video

## Persyaratan Sistem

- Python 3.8+
- FFmpeg
- Ubuntu VPS
- Google Drive API Key
- Facebook/YouTube Stream URL

## Instalasi di VPS Ubuntu

1. Update sistem dan install dependensi
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv ffmpeg
```

2. Clone repository
```bash
git clone https://github.com/yourusername/stream.git
cd stream
```

3. Buat virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

4. Install dependensi Python
```bash
pip install -r requirements.txt
```

5. Konfigurasi environment variables
```bash
# Copy file .env.example ke .env
cp .env.example .env

# Edit file .env dengan konfigurasi yang sesuai
nano .env
```

6. Setup Google Drive API
- Buat project di Google Cloud Console
- Aktifkan Google Drive API
- Buat API Key
- Tambahkan API Key ke file .env

7. Inisialisasi database
```bash
python3
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

## Menjalankan Aplikasi

1. Menggunakan Gunicorn (Direkomendasikan untuk Production)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

2. Menggunakan Flask Development Server (Untuk Development)
```bash
python3 app.py
```

## Penggunaan

1. Buka browser dan akses `http://your-vps-ip:8000`
2. Registrasi user baru dengan username, email, password, dan foto profil
3. Login ke dashboard
4. Download video dari Google Drive dengan memasukkan File ID
5. Mulai streaming dengan memilih platform (Facebook/YouTube)
6. Monitor status streaming dan kelola video di dashboard

## Monitoring

- CPU Usage: Ditampilkan di header dashboard
- Memory Usage: Ditampilkan di header dashboard
- Disk Usage: Ditampilkan di header dashboard
- Status Streaming: Tabel status streaming aktif
- Daftar Video: Tabel manajemen video

## Troubleshooting

1. Jika port 8000 sudah digunakan:
```bash
sudo lsof -i :8000  # Cek proses yang menggunakan port 8000
sudo kill -9 PID    # Matikan proses (ganti PID dengan ID proses)
```

2. Jika FFmpeg error:
```bash
# Cek log FFmpeg
tail -f /var/log/syslog | grep ffmpeg
```

3. Jika streaming gagal:
- Pastikan URL streaming valid
- Cek koneksi internet
- Verifikasi format video compatible

## Keamanan

1. Ganti SECRET_KEY di file .env
2. Gunakan HTTPS di production
3. Batasi akses ke port yang tidak digunakan
4. Update sistem dan dependensi secara regular
5. Backup database secara regular

## Maintenance

1. Backup Database
```bash
cp instance/database.db backup/database_$(date +%Y%m%d).db
```

2. Update Aplikasi
```bash
git pull
source venv/bin/activate
pip install -r requirements.txt
```

3. Restart Aplikasi
```bash
sudo systemctl restart streaming-manager
```

## Support

Untuk bantuan dan pertanyaan, silakan buat issue di repository GitHub.