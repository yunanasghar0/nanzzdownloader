import os
import time
import glob
import json
from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import requests
from flask_cors import CORS

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# === KONFIGURASI VERCEL ===
# Vercel hanya boleh tulis di folder /tmp
DOWNLOAD_FOLDER = '/tmp'
if not os.path.exists(DOWNLOAD_FOLDER):
    try:
        os.makedirs(DOWNLOAD_FOLDER)
    except:
        pass

# === KONFIGURASI FONNTE ===
# GANTI DENGAN TOKEN ASLI KAMU!
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
        for f in os.listdir(DOWNLOAD_FOLDER):
            f_path = os.path.join(DOWNLOAD_FOLDER, f)
            if "nanzz_" in f and os.stat(f_path).st_mtime < now - 120:
                os.remove(f_path)
    except Exception as e:
        print(f"Gagal bersih-bersih: {e}")

    # 2. PROSES UTAMA
    try:
        data = request.json
        url = data.get('url')
        format_type = data.get('format', 'mp4') 

        if not url: return jsonify({'status': 'error', 'message': 'Link kosong!'}), 400

        timestamp = int(time.time())
        filename_base = f"nanzz_{timestamp}"
        save_path = os.path.join(DOWNLOAD_FOLDER, filename_base)

        ydl_opts = {
            'outtmpl': save_path + '.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'cache_dir': False, # PENTING DI VERCEL
            # User Agent biar tidak dikira bot
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            }
        }

        if format_type == 'mp3':
            ydl_opts.update({'format': 'bestaudio/best'})
        else:
            ydl_opts.update({'format': 'best[ext=mp4]/best'})

        print(f"🔄 Memproses: {url}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        # Cari file hasil
        list_file = glob.glob(os.path.join(DOWNLOAD_FOLDER, f"{filename_base}*"))
        # Ambil file yang bukan .part
        file_ketemu = [f for f in list_file if not f.endswith('.part')]
        
        if not file_ketemu:
            return jsonify({'status': 'error', 'message': 'Download berhasil tapi file tidak tersimpan di /tmp.'}), 500
            
        final_filename = os.path.basename(file_ketemu[0])
        print(f"✅ Sukses: {final_filename}")

        return jsonify({'status': 'success', 'filename': final_filename})

    except Exception as e:
        # INI BAGIAN PENTING: Kirim error asli ke layar user
        error_message = str(e)
        print(f"❌ ERROR FATAL: {error_message}")
        return jsonify({'status': 'error', 'message': f'Server Error: {error_message}'}), 500

@app.route('/get-file/<filename>')
def get_file(filename):
    try:
        return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)
    except Exception as e:
        return f"Gagal ambil file: {e}", 404

@app.route('/send-feedback', methods=['POST'])
def send_feedback():
    try:
        data = request.json
        pesan = data.get('message', '')
        
        # DEBUG: Cek apakah token sudah diisi
        if FONNTE_TOKEN == 'TOKEN_FONNTE_KAMU_DISINI':
            return jsonify({'status': 'error', 'message': 'Token Fonnte Belum Diganti di app.py!'}), 500

        headers = {'Authorization': FONNTE_TOKEN}
        payload = {
            'target': NOMOR_ADMIN, 
            'message': f"*Laporan Web Nanzz:*\n{pesan}"
        }

        response = requests.post("https://api.fonnte.com/send", headers=headers, data=payload)
        
        # Cek respon dari Fonnte
        print(f"Respon Fonnte: {response.text}")
        
        return jsonify({'status': 'success', 'debug': response.text})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Handler Wajib Vercel
app.debug = True
