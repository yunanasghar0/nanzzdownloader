import os
import time
import glob
from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import requests
from flask_cors import CORS

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# === KHUSUS VERCEL: GUNAKAN FOLDER /tmp ===
# Vercel hanya mengizinkan tulis file di folder sementara /tmp
DOWNLOAD_FOLDER = '/tmp'

# Pastikan folder ada (walaupun /tmp biasanya selalu ada)
if not os.path.exists(DOWNLOAD_FOLDER):
    try:
        os.makedirs(DOWNLOAD_FOLDER)
    except:
        pass

# KONFIGURASI WA & TOKEN
FONNTE_TOKEN = 'wFH9D48iuCAkkdY9h1AV' 
NOMOR_ADMIN = '6281227324594' 

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def process_download():
    # BERSIH-BERSIH FILE LAMA (PENTING DI VERCEL)
    # Hapus file di /tmp yang umurnya lebih dari 5 menit biar storage gak penuh
    try:
        now = time.time()
        for f in os.listdir(DOWNLOAD_FOLDER):
            f_path = os.path.join(DOWNLOAD_FOLDER, f)
            if os.path.isfile(f_path) and "nanzz_" in f:
                if os.stat(f_path).st_mtime < now - 300:
                    os.remove(f_path)
    except:
        pass

    data = request.json
    url = data.get('url')
    format_type = data.get('format', 'mp4') 

    if not url: return jsonify({'status': 'error', 'message': 'Link kosong bro!'}), 400

    timestamp = int(time.time())
    filename_base = f"nanzz_{timestamp}"
    save_path = os.path.join(DOWNLOAD_FOLDER, filename_base)

    ydl_opts = {
        'outtmpl': save_path + '.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        # Cache dimatikan biar hemat memori di Vercel
        'cache_dir': False, 
    }

    if format_type == 'mp3':
        ydl_opts.update({'format': 'bestaudio/best'})
    else:
        ydl_opts.update({'format': 'best[ext=mp4]/best'})

    try:
        print(f"🔄 Memproses di Vercel: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        list_file = glob.glob(os.path.join(DOWNLOAD_FOLDER, f"{filename_base}*"))
        file_ketemu = [f for f in list_file if not f.endswith('.part') and not f.endswith('.ytdl')]
        
        if not file_ketemu:
            return jsonify({'status': 'error', 'message': 'Gagal menyimpan file.'}), 500
            
        final_filename = os.path.basename(file_ketemu[0])
        print(f"✅ Sukses: {final_filename}")

        return jsonify({'status': 'success', 'filename': final_filename})

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'status': 'error', 'message': 'Gagal download. Link Private/Error.'}), 500

@app.route('/get-file/<filename>')
def get_file(filename):
    try:
        return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)
    except:
        return "File hilang/kadaluarsa", 404

@app.route('/send-feedback', methods=['POST'])
def send_feedback():
    try:
        data = request.json
        pesan = data.get('message', '')
        if pesan:
            requests.post("https://api.fonnte.com/send", 
                          headers={'Authorization': FONNTE_TOKEN}, 
                          data={'target': NOMOR_ADMIN, 'message': f"FEEDBACK: {pesan}"})
        return jsonify({'status': 'success'})
    except:
        return jsonify({'status': 'success'})

# Handler wajib buat Vercel Serverless
app.debug = True