import os
import time
import glob
from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import requests
from flask_cors import CORS

# Setup Path Absolut (Supaya tidak nyasar folder)
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
CORS(app)

# === KONFIGURASI FOLDER (HUGGING FACE/DOCKER) ===
DOWNLOAD_FOLDER = '/app/downloads'

# Buat folder jika belum ada
if not os.path.exists(DOWNLOAD_FOLDER):
    try:
        os.makedirs(DOWNLOAD_FOLDER)
    except:
        pass

# === KONFIGURASI WA (DATA KAMU) ===
FONNTE_TOKEN = 'wFH9D48iuCAkkdY9h1AV' 
NOMOR_ADMIN = '6281227324594' 

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def process_download():
    # 1. BERSIH-BERSIH FILE LAMA
    try:
        now = time.time()
        if os.path.exists(DOWNLOAD_FOLDER):
            for f in os.listdir(DOWNLOAD_FOLDER):
                f_path = os.path.join(DOWNLOAD_FOLDER, f)
                # Hapus file yang umurnya lebih dari 5 menit
                if os.stat(f_path).st_mtime < now - 300:
                    os.remove(f_path)
    except Exception as e:
        print(f"Warning Cleanup: {e}")

    # 2. PROSES DOWNLOAD
    try:
        data = request.json
        url = data.get('url')
        format_type = data.get('format', 'mp4') 

        if not url: return jsonify({'status': 'error', 'message': 'Link kosong!'}), 400

        # Nama file unik
        timestamp = int(time.time())
        filename_base = f"nanzz_{timestamp}"
        
        # Path lengkap tujuan simpan
        save_path_template = os.path.join(DOWNLOAD_FOLDER, filename_base)

        ydl_opts = {
            'outtmpl': f"{save_path_template}.%(ext)s",
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
        }

        if format_type == 'mp3':
            ydl_opts.update({'format': 'bestaudio/best'})
        else:
            ydl_opts.update({'format': 'best[ext=mp4]/best'})

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        # 3. CARI FILE HASIL
        search_pattern = os.path.join(DOWNLOAD_FOLDER, f"{filename_base}*")
        list_file = glob.glob(search_pattern)
        
        file_ketemu = [f for f in list_file if not f.endswith('.part') and not f.endswith('.ytdl')]
        
        if not file_ketemu:
            return jsonify({'status': 'error', 'message': 'File gagal tersimpan di server.'}), 500
            
        final_filename = os.path.basename(file_ketemu[0])
        
        return jsonify({'status': 'success', 'filename': final_filename})

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server Error: {str(e)}'}), 500

@app.route('/get-file/<filename>')
def get_file(filename):
    try:
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return "File tidak ditemukan (Mungkin kadaluarsa)", 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"Gagal mengambil file: {e}", 404

@app.route('/send-feedback', methods=['POST'])
def send_feedback():
    try:
        data = request.json
        pesan_user = data.get('message', '')
        
        if not pesan_user:
            return jsonify({'status': 'error', 'message': 'Pesan kosong'})

        # Kirim WA via Fonnte
        pesan_lengkap = f"*📢 FEEDBACK WEB NANZZ*\n\nIsi: {pesan_user}"
        
        requests.post(
            "https://api.fonnte.com/send", 
            headers={'Authorization': FONNTE_TOKEN}, 
            data={
                'target': NOMOR_ADMIN, 
                'message': pesan_lengkap
            }
        )
        return jsonify({'status': 'success'})
    except:
        return jsonify({'status': 'success'})

if __name__ == '__main__':
    # Port 7860 wajib untuk Hugging Face
    app.run(debug=True, host='0.0.0.0', port=7860)
