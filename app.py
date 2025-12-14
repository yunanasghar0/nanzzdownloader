import os
import time
import glob
from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import requests
from flask_cors import CORS

# --- FIX RENDER PATH ---
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
CORS(app)

# === KONFIGURASI ===
DOWNLOAD_FOLDER = '/tmp' 
# PASTIKAN DIGANTI DENGAN TOKEN FONNTE ASLI!
FONNTE_TOKEN = 'wFH9D48iuCAkkdY9h1AV' 
NOMOR_ADMIN = '6281227324594' 

if not os.path.exists(DOWNLOAD_FOLDER):
    try:
        os.makedirs(DOWNLOAD_FOLDER)
    except:
        pass

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def process_download():
    # Bersih-bersih file lama di /tmp (PENTING DI CLOUD GRATIS)
    try:
        now = time.time()
        for f in os.listdir(DOWNLOAD_FOLDER):
            f_path = os.path.join(DOWNLOAD_FOLDER, f)
            if "nanzz_" in f and os.stat(f_path).st_mtime < now - 180: # Hapus file 3 menit lalu
                os.remove(f_path)
    except:
        pass

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
            'cache_dir': False,
            'format': 'bestaudio/best' if format_type == 'mp3' else 'best[ext=mp4]/best',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        list_file = glob.glob(os.path.join(DOWNLOAD_FOLDER, f"{filename_base}*"))
        file_ketemu = [f for f in list_file if not f.endswith('.part')]
        
        if not file_ketemu:
            return jsonify({'status': 'error', 'message': 'Gagal menyimpan file.'}), 500
            
        final_filename = os.path.basename(file_ketemu[0])
        return jsonify({'status': 'success', 'filename': final_filename})

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server Error: {str(e)}'}), 500

@app.route('/get-file/<filename>')
def get_file(filename):
    try:
        # Menghapus file setelah dikirim (biar /tmp tidak penuh)
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        response = send_file(file_path, as_attachment=True)
        # Hapus file setelah response terkirim
        if os.path.exists(file_path):
            os.remove(file_path)
        return response
    except Exception as e:
        return f"File tidak ditemukan: {e}", 404

@app.route('/send-feedback', methods=['POST'])
def send_feedback():
    try:
        data = request.json
        pesan = data.get('message', '')
        
        if 'GANTI_TOKEN' in FONNTE_TOKEN:
            return jsonify({'status': 'error', 'message': 'Token Admin Belum Diisi!'}), 500

        requests.post("https://api.fonnte.com/send", 
                      headers={'Authorization': FONNTE_TOKEN}, 
                      data={'target': NOMOR_ADMIN, 'message': f"WEB FEEDBACK: {pesan}"})
        return jsonify({'status': 'success'})
    except Exception as e:
        # Jika gagal kirim WA (misal token salah), tetap bilang sukses ke user
        return jsonify({'status': 'success'})

# Wajib untuk Render.com
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
