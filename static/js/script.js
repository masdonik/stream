// Fungsi untuk memformat angka dengan pemisah ribuan
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Fungsi untuk memformat bytes ke format yang mudah dibaca
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Fungsi untuk memformat waktu
function formatDate(date) {
    return new Date(date).toLocaleString('id-ID', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// Fungsi untuk menampilkan loading spinner
function showLoading(element) {
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    element.appendChild(spinner);
}

// Fungsi untuk menyembunyikan loading spinner
function hideLoading(element) {
    const spinner = element.querySelector('.loading-spinner');
    if (spinner) {
        spinner.remove();
    }
}

// Fungsi untuk menampilkan alert
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} fade-enter`;
    alertDiv.textContent = message;
    
    document.body.appendChild(alertDiv);
    
    // Trigger animation
    setTimeout(() => alertDiv.classList.remove('fade-enter'), 100);
    
    // Hapus alert setelah 3 detik
    setTimeout(() => {
        alertDiv.classList.add('fade-exit');
        setTimeout(() => alertDiv.remove(), 200);
    }, 3000);
}

// Fungsi untuk memperbarui metrik sistem
async function updateSystemMetrics() {
    try {
        const response = await fetch('/get_metrics');
        if (!response.ok) throw new Error('Failed to fetch metrics');
        
        const metrics = await response.json();
        
        // Update CPU usage
        const cpuElement = document.getElementById('cpu-usage');
        if (cpuElement) {
            cpuElement.textContent = `${metrics.cpu}%`;
            // Tambah warna berdasarkan penggunaan
            cpuElement.className = metrics.cpu > 80 ? 'text-red-500' : 
                                 metrics.cpu > 60 ? 'text-yellow-500' : 
                                 'text-green-500';
        }
        
        // Update Memory usage
        const memoryElement = document.getElementById('memory-usage');
        if (memoryElement) {
            memoryElement.textContent = `${metrics.memory.percent}%`;
            memoryElement.className = metrics.memory.percent > 80 ? 'text-red-500' : 
                                    metrics.memory.percent > 60 ? 'text-yellow-500' : 
                                    'text-green-500';
        }
        
        // Update Disk usage
        const diskElement = document.getElementById('disk-usage');
        if (diskElement) {
            diskElement.textContent = `${metrics.disk.percent}%`;
            diskElement.className = metrics.disk.percent > 80 ? 'text-red-500' : 
                                  metrics.disk.percent > 60 ? 'text-yellow-500' : 
                                  'text-green-500';
        }
    } catch (error) {
        console.error('Error updating metrics:', error);
    }
}

// Fungsi untuk menangani download video
async function handleDownload(event) {
    event.preventDefault();
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const fileId = form.querySelector('#file-id').value;
    
    if (!fileId) {
        showAlert('Mohon masukkan File ID Google Drive', 'error');
        return;
    }
    
    try {
        submitButton.disabled = true;
        showLoading(submitButton);
        
        const response = await fetch('/download_video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `file_id=${encodeURIComponent(fileId)}`
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Video berhasil diunduh');
            location.reload();
        } else {
            showAlert(result.error || 'Gagal mengunduh video', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Terjadi kesalahan saat mengunduh video', 'error');
    } finally {
        submitButton.disabled = false;
        hideLoading(submitButton);
    }
}

// Fungsi untuk memulai streaming
async function startStream(videoId, platform) {
    const button = event.target;
    
    try {
        button.disabled = true;
        showLoading(button);
        
        const response = await fetch('/start_stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `video_id=${videoId}&platform=${platform}`
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(`Streaming ke ${platform} dimulai`);
            location.reload();
        } else {
            showAlert(result.error || 'Gagal memulai streaming', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Terjadi kesalahan saat memulai streaming', 'error');
    } finally {
        button.disabled = false;
        hideLoading(button);
    }
}

// Fungsi untuk menghentikan streaming
async function stopStream(videoId) {
    const button = event.target;
    
    try {
        button.disabled = true;
        showLoading(button);
        
        const response = await fetch('/stop_stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `video_id=${videoId}`
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Streaming dihentikan');
            location.reload();
        } else {
            showAlert(result.error || 'Gagal menghentikan streaming', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Terjadi kesalahan saat menghentikan streaming', 'error');
    } finally {
        button.disabled = false;
        hideLoading(button);
    }
}

// Fungsi untuk menangani rename video
async function handleRename(videoId, newName) {
    try {
        const response = await fetch('/rename_video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `video_id=${videoId}&new_name=${encodeURIComponent(newName)}`
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Nama video berhasil diubah');
            location.reload();
        } else {
            showAlert(result.error || 'Gagal mengubah nama video', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Terjadi kesalahan saat mengubah nama video', 'error');
    }
}

// Fungsi untuk menangani delete video
async function handleDelete(videoId) {
    if (!confirm('Apakah Anda yakin ingin menghapus video ini?')) {
        return;
    }
    
    try {
        const response = await fetch('/delete_video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `video_id=${videoId}`
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Video berhasil dihapus');
            const videoRow = document.getElementById(`video-row-${videoId}`);
            if (videoRow) {
                videoRow.classList.add('fade-exit');
                setTimeout(() => videoRow.remove(), 200);
            }
        } else {
            showAlert(result.error || 'Gagal menghapus video', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Terjadi kesalahan saat menghapus video', 'error');
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Inisialisasi update metrik sistem
    updateSystemMetrics();
    setInterval(updateSystemMetrics, 5000); // Update setiap 5 detik
    
    // Event listener untuk form download
    const downloadForm = document.getElementById('download-form');
    if (downloadForm) {
        downloadForm.addEventListener('submit', handleDownload);
    }
    
    // Event listener untuk drag and drop
    const dropZone = document.querySelector('.border-dashed');
    if (dropZone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            dropZone.classList.add('border-blue-500');
        }

        function unhighlight(e) {
            dropZone.classList.remove('border-blue-500');
        }

        dropZone.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        }

        function handleFiles(files) {
            const fileInput = document.getElementById('profile_photo');
            if (fileInput) {
                fileInput.files = files;
                fileInput.dispatchEvent(new Event('change'));
            }
        }
    }
});