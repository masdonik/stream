import os
import psutil
import subprocess
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import logging
from datetime import datetime

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variabel global untuk menyimpan proses ffmpeg
ffmpeg_process = None

def get_system_metrics():
    """
    Mengambil metrik penggunaan sistem (CPU, Memory, Disk)
    """
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu': cpu_usage,
            'memory': {
                'total': memory.total,
                'used': memory.used,
                'percent': memory.percent
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'percent': disk.percent
            }
        }
    except Exception as e:
        logger.error(f"Error mengambil metrik sistem: {str(e)}")
        return None

def download_video_from_drive(file_id, destination_path):
    """
    Download video dari Google Drive menggunakan API
    """
    try:
        # Inisialisasi layanan Drive
        credentials = service_account.Credentials.from_service_account_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        
        service = build('drive', 'v3', credentials=credentials)
        
        # Membuat request untuk mengambil file
        request = service.files().get_media(fileId=file_id)
        
        # Download file
        fh = io.FileIO(destination_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        
        while not done:
            status, done = downloader.next_chunk()
            if status:
                logger.info(f"Download {int(status.progress() * 100)}%")
        
        return True, "Video berhasil diunduh"
        
    except Exception as e:
        logger.error(f"Error mengunduh video: {str(e)}")
        return False, str(e)

def start_stream(video_path, stream_url):
    """
    Memulai streaming menggunakan ffmpeg tanpa encoding
    """
    global ffmpeg_process
    
    try:
        if ffmpeg_process is not None:
            logger.warning("Streaming sudah berjalan")
            return False, "Streaming sudah berjalan"
        
        # Perintah ffmpeg untuk streaming tanpa encoding
        command = [
            'ffmpeg',
            '-re',  # Membaca input pada kecepatan native
            '-i', video_path,  # File input
            '-c', 'copy',  # Tanpa encoding ulang
            '-f', 'flv',  # Format output
            stream_url  # URL streaming tujuan
        ]
        
        # Memulai proses ffmpeg
        ffmpeg_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        logger.info(f"Streaming dimulai: {video_path} -> {stream_url}")
        return True, "Streaming berhasil dimulai"
        
    except Exception as e:
        logger.error(f"Error memulai streaming: {str(e)}")
        return False, str(e)

def stop_stream():
    """
    Menghentikan proses streaming ffmpeg
    """
    global ffmpeg_process
    
    try:
        if ffmpeg_process is None:
            logger.warning("Tidak ada streaming yang berjalan")
            return False, "Tidak ada streaming yang berjalan"
        
        # Menghentikan proses ffmpeg
        ffmpeg_process.terminate()
        ffmpeg_process.wait(timeout=5)
        ffmpeg_process = None
        
        logger.info("Streaming dihentikan")
        return True, "Streaming berhasil dihentikan"
        
    except Exception as e:
        logger.error(f"Error menghentikan streaming: {str(e)}")
        if ffmpeg_process:
            ffmpeg_process.kill()  # Force kill jika gagal terminate
            ffmpeg_process = None
        return False, str(e)

def format_bytes(size):
    """
    Format ukuran file ke format yang mudah dibaca
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def is_video_file(filename):
    """
    Cek apakah file adalah video berdasarkan ekstensi
    """
    video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv'}
    return os.path.splitext(filename)[1].lower() in video_extensions