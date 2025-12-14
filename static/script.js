document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. ANIMASI SALJU & TEKS "NANZZ" ---
    const canvas = document.getElementById('particle-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let width, height, particles = [];
        const resize = () => { width = canvas.width = window.innerWidth; height = canvas.height = window.innerHeight; };
        
        class Particle {
            constructor() { this.reset(true); }
            reset(initial) {
                this.x = Math.random() * width;
                this.y = initial ? Math.random() * height : -20;
                this.speed = Math.random() * 2 + 1;
                this.color = Math.random() > 0.5 ? '#00f2ea' : '#ff0055'; 
                this.opacity = Math.random() * 0.5 + 0.3;
                this.isText = Math.random() < 0.3; 
                this.size = this.isText ? (Math.random() * 10 + 10) : (Math.random() * 3 + 1);
            }
            update() { 
                this.y += this.speed; 
                this.x += Math.sin(this.y * 0.01) * 0.5;
                if (this.y > height) this.reset(); 
            }
            draw() { 
                ctx.globalAlpha = this.opacity;
                ctx.fillStyle = this.color; 
                if (this.isText) {
                    ctx.font = `bold ${this.size}px Arial`; ctx.fillText("Nanzz", this.x, this.y);
                } else {
                    ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2); ctx.fill(); 
                }
                ctx.globalAlpha = 1.0;
            }
        }
        const loop = () => { ctx.clearRect(0, 0, width, height); particles.forEach(p => { p.update(); p.draw(); }); requestAnimationFrame(loop); };
        window.addEventListener('resize', resize); resize();
        for (let i = 0; i < 60; i++) particles.push(new Particle());
        loop();
    }

    // --- 2. LOGIKA DOWNLOAD ---
    const dForm = document.getElementById('downloadForm');
    if (dForm) {
        dForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const url = document.getElementById('urlInput').value.trim();
            const format = document.getElementById('formatSelect').value;
            const btn = document.getElementById('downloadButton');
            const msg = document.getElementById('message');
            const linkBox = document.getElementById('downloadLinkContainer');
            const finalLink = document.getElementById('finalDownloadLink');
            
            if (!url) { alert("Link kosong bro!"); return; }

            linkBox.style.display = 'none';
            msg.style.display = 'none';
            const oldText = btn.innerHTML;
            btn.innerHTML = "SEDANG MEMPROSES... ⏳";
            btn.style.cursor = "wait";

            try {
                const res = await fetch('/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url, format: format })
                });
                if (!res.ok) throw new Error("Gagal menghubungi server.");
                const data = await res.json();

                if (data.status === 'success') {
                    finalLink.href = `/get-file/${data.filename}`;
                    linkBox.style.display = 'block';
                    msg.style.display = 'block';
                    msg.textContent = "Berhasil! Silakan download.";
                    msg.className = "alert alert-success";
                    if (typeof confetti === 'function') confetti();
                } else {
                    msg.style.display = 'block';
                    msg.textContent = "Gagal: " + (data.message || "Unknown error");
                    msg.className = "alert alert-danger";
                }
            } catch (err) {
                console.error(err);
                msg.style.display = 'block';
                msg.textContent = "Error Jaringan / Server.";
                msg.className = "alert alert-danger";
            } finally {
                btn.innerHTML = oldText;
                btn.style.cursor = "pointer";
            }
        });
    }

    // --- 3. LOGIKA FEEDBACK ---
    const fForm = document.getElementById('feedbackForm');
    if (fForm) {
        fForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const txt = document.getElementById('feedbackInput').value;
            const btn = fForm.querySelector('button');
            if(!txt) return;
            btn.innerHTML = "MENGIRIM...";
            try {
                await fetch('/send-feedback', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: txt })
                });
                alert("Pesan Terkirim ke Admin!");
                document.getElementById('feedbackInput').value = "";
            } catch {
                alert("Gagal kirim pesan.");
            } finally {
                btn.innerHTML = "KIRIM PESAN 📧";
            }
        });
    }
});