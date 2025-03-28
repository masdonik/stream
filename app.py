import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from datetime import datetime
from models import db, User, Video
from config import Config
from utils import (
    get_system_metrics, 
    download_video_from_drive, 
    start_stream, 
    stop_stream, 
    format_bytes,
    is_video_file
)

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)
db.init_app(app)

# Buat database jika belum ada
with app.app_context():
    db.create_all()

def allowed_file(filename, types=None):
    if types is None:
        types = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in types

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('register'))
    return redirect(url_for('dashboard'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        profile_photo = request.files.get('profile_photo')

        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar', 'error')
            return redirect(url_for('register'))

        user = User(username=username, email=email)
        user.set_password(password)

        if profile_photo and allowed_file(profile_photo.filename):
            filename = secure_filename(profile_photo.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            profile_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.profile_photo = filename

        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        flash('Registrasi berhasil!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('register'))
    
    user = db.session.get(User, session['user_id'])
    videos = Video.query.all()
    metrics = get_system_metrics()
    
    return render_template(
        'dashboard.html',
        user=user,
        videos=videos,
        metrics=metrics
    )

@app.route('/get_metrics')
def get_metrics():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(get_system_metrics())

@app.route('/download_video', methods=['POST'])
def download_video():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    file_id = request.form.get('file_id')
    if not file_id:
        return jsonify({'error': 'File ID tidak ditemukan'}), 400

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"video_{timestamp}.mp4"
    destination_path = os.path.join(app.config['VIDEOS_FOLDER'], filename)

    success, message = download_video_from_drive(file_id, destination_path)
    
    if success:
        # Simpan informasi video ke database
        file_size = os.path.getsize(destination_path)
        video = Video(
            name=filename,
            file_path=destination_path,
            file_size=file_size,
            download_date=datetime.now()
        )
        db.session.add(video)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Video berhasil diunduh',
            'video': {
                'id': video.id,
                'name': video.name,
                'size': format_bytes(video.file_size),
                'download_date': video.download_date.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    
    return jsonify({'error': message}), 500

@app.route('/start_stream', methods=['POST'])
def start_streaming():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    video_id = request.form.get('video_id')
    platform = request.form.get('platform')

    if not video_id or not platform:
        return jsonify({'error': 'Parameter tidak lengkap'}), 400

    video = Video.query.get(video_id)
    if not video:
        return jsonify({'error': 'Video tidak ditemukan'}), 404

    # Pilih URL streaming berdasarkan platform
    stream_url = (
        app.config['FACEBOOK_STREAM_URL']
        if platform == 'facebook'
        else app.config['YOUTUBE_STREAM_URL']
    )

    success, message = start_stream(video.file_path, stream_url)
    
    if success:
        video.is_streaming = True
        video.stream_platform = platform
        video.stream_start_time = datetime.now()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Streaming dimulai',
            'stream_info': {
                'platform': platform,
                'start_time': video.stream_start_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    
    return jsonify({'error': message}), 500

@app.route('/stop_stream', methods=['POST'])
def stop_streaming():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    video_id = request.form.get('video_id')
    if not video_id:
        return jsonify({'error': 'Video ID tidak ditemukan'}), 400

    video = Video.query.get(video_id)
    if not video:
        return jsonify({'error': 'Video tidak ditemukan'}), 404

    success, message = stop_stream()
    
    if success:
        video.is_streaming = False
        video.stream_platform = None
        video.stream_start_time = None
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Streaming dihentikan'
        })
    
    return jsonify({'error': message}), 500

@app.route('/rename_video', methods=['POST'])
def rename_video():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    video_id = request.form.get('video_id')
    new_name = request.form.get('new_name')

    if not video_id or not new_name:
        return jsonify({'error': 'Parameter tidak lengkap'}), 400

    video = Video.query.get(video_id)
    if not video:
        return jsonify({'error': 'Video tidak ditemukan'}), 404

    # Rename file fisik
    old_path = video.file_path
    new_filename = secure_filename(new_name)
    if not new_filename.endswith(os.path.splitext(video.name)[1]):
        new_filename += os.path.splitext(video.name)[1]
    
    new_path = os.path.join(os.path.dirname(old_path), new_filename)
    
    try:
        os.rename(old_path, new_path)
        video.name = new_filename
        video.file_path = new_path
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Video berhasil direname',
            'new_name': new_filename
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_video', methods=['POST'])
def delete_video():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    video_id = request.form.get('video_id')
    if not video_id:
        return jsonify({'error': 'Video ID tidak ditemukan'}), 400

    video = Video.query.get(video_id)
    if not video:
        return jsonify({'error': 'Video tidak ditemukan'}), 404

    try:
        # Hapus file fisik
        if os.path.exists(video.file_path):
            os.remove(video.file_path)
        
        # Hapus dari database
        db.session.delete(video)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Video berhasil dihapus'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('register'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
