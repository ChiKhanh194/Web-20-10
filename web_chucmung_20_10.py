"""
Web chúc mừng 20/10 - Single-file Flask app
Lưu file này thành: web_chucmung_20_10.py
Chạy:
  1. Tạo virtualenv (khuyến nghị): python -m venv venv
  2. Kích hoạt: (Windows) venv\\Scripts\\activate  (Mac/Linux) source venv/bin/activate
  3. Cài dependencies: pip install flask
  4. Chạy: python web_chucmung_20_10.py
  5. Mở trình duyệt: http://127.0.0.1:5000

Tính năng:
 - Trang chủ với lời chúc tiếng Việt cho ngày 20/10 (Ngày Phụ nữ Việt Nam)
 - Form nhập tên để cá nhân hóa lời chúc
 - Nút "Gửi lời chúc" tạo hiệu ứng confetti và hiển thị thiệp
 - Giao diện responsive, hoạt động offline (không cần internet)

Bạn có thể chỉnh nội dung trong biến MESSAGE_HTML hoặc template trong mã.
"""

from flask import Flask, request, render_template_string, redirect, url_for
import datetime

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Chúc mừng 20/10</title>
  <style>
    :root{--bg:#fff7fb;--card:#ffffff;--accent:#ff67a1;--muted:#6b6b6b}
    *{box-sizing:border-box}
    body{margin:0;font-family:Inter, Ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; background:linear-gradient(180deg,var(--bg),#fff);color:#222}
    header{padding:28px 20px;text-align:center}
    .container{max-width:900px;margin:0 auto;padding:16px}
    .card{background:var(--card);border-radius:16px;box-shadow:0 6px 18px rgba(0,0,0,0.08);padding:20px}
    h1{margin:6px 0 8px;font-size:28px;color:var(--accent)}
    p.lead{margin:0 0 12px;color:var(--muted)}
    .two-col{display:flex;gap:18px;flex-wrap:wrap;align-items:center}
    .left{flex:1;min-width:240px}
    .right{width:320px;min-width:240px}
    input[type=text]{width:100%;padding:12px;border-radius:10px;border:1px solid #eee;font-size:16px}
    button{display:inline-block;padding:10px 16px;border-radius:10px;border:0;background:var(--accent);color:white;font-weight:600;cursor:pointer}
    .postcard{margin-top:16px;padding:18px;border-radius:12px;background:linear-gradient(135deg,#fff,#fff0f7);text-align:center}
    .postcard h2{margin:6px 0;font-size:22px}
    .postcard p{margin:4px 0;color:#333}
    footer{text-align:center;margin:18px 0;color:#888;font-size:13px}
    @media(max-width:720px){.two-col{flex-direction:column}.right{width:100%}}
    /* small confetti canvas */
    #confetti-canvas{position:fixed;pointer-events:none;top:0;left:0;right:0;bottom:0;z-index:9999}
  </style>
</head>
<body>
  <canvas id="confetti-canvas"></canvas>
  <header>
    <div class="container">
      <div class="card">
        <h1>🎉 Chúc mừng 20/10</h1>
        <p class="lead">Đừng xúc động nhé bà.</p>
        <div class="two-col">
          <div class="left">
            <form method="POST" action="/">
              <label for="name">Gõ tên bà vô đây nhé (Tran Phuong Anh):</label>
              <input id="name" name="name" type="text" placeholder="Tên người nhận" value="{{ name|e }}">
              <div style="margin-top:12px">
                <button id="sendBtn" type="submit">Gửi lời chúc</button>
                <button id="randomBtn" type="button" style="margin-left:8px;background:#6c6cff">Gợi ý</button>
              </div>
            </form>

            <div class="postcard" id="postcard" style="display:{{ 'block' if show_postcard else 'none' }}">
              <h2>Chúc mừng ngày 20/10, {{ name_display|e }}!</h2>
              <p>Chúc bà học rỏi, lĩnh học bổng.</p>
              <p>Và tôi mún tờ 500K bà nhé :3.</p>
              <div style="margin-top:10px;font-size:12px;color:#666">— Nguyen Chi Khanh siu cute</div>
            </div>
          </div>
          <div class="right">
            <img src="data:image/svg+xml;utf8,{{ svg|safe }}" alt="thiệp" style="width:100%;border-radius:10px;display:block">
          </div>
        </div>
      </div>
      <footer>Ngày Phụ nữ Việt Nam — 20/10 </footer>
    </div>
  </header>

  <script>
    // small list of name suggestions
    const samples = ["Tran Phuong Anh"];
    document.getElementById('randomBtn').addEventListener('click', ()=>{
      const n = samples[Math.floor(Math.random()*samples.length)];
      document.getElementById('name').value = n;
    });

    // confetti implementation (lightweight)
    (function(){
      const canvas = document.getElementById('confetti-canvas');
      const ctx = canvas.getContext('2d');
      let W = canvas.width = window.innerWidth;
      let H = canvas.height = window.innerHeight;
      window.addEventListener('resize', ()=>{W=canvas.width=window.innerWidth;H=canvas.height=window.innerHeight});

      function Confetti(){
        this.x = Math.random()*W; this.y = -10 - Math.random()*H; this.r = 6+Math.random()*8; this.d = Math.random()*40+10;
        this.color = `hsl(${Math.floor(Math.random()*360)}, 85%, 60%)`;
        this.tilt = Math.random()*10-10; this.tiltAngleIncrement = Math.random()*0.07+0.05; this.tiltAngle = 0;
      }
      Confetti.prototype.draw = function(){ ctx.beginPath(); ctx.fillStyle=this.color; ctx.save(); ctx.translate(this.x,this.y); ctx.rotate(this.tiltAngle); ctx.fillRect(0,0,this.r, this.r*0.6); ctx.restore(); };

      let confs = [];
      function launch(count){ for(let i=0;i<count;i++) confs.push(new Confetti()); animate(); }
      let animId=null;
      function animate(){ if(animId) cancelAnimationFrame(animId); animId = requestAnimationFrame(step); }
      function step(){ ctx.clearRect(0,0,W,H); for(let i=confs.length-1;i>=0;i--){ let c=confs[i]; c.tiltAngle += c.tiltAngleIncrement; c.y += Math.cos(c.d) + 3 + c.r/2; c.x += Math.sin(c.d); c.draw(); if(c.y>H+50){confs.splice(i,1);} } if(confs.length>0) animId=requestAnimationFrame(step); }

      // run confetti if postcard is visible (server rendered)
      const show = {{ 'true' if show_postcard else 'false' }};
      if(show){ launch(80); }

      // also intercept form submission to show confetti without reload (progressive enhancement)
      const form = document.querySelector('form');
      form.addEventListener('submit', (e)=>{
        // allow normal POST to show server postcard; but for nicer UX, we'll show confetti quickly
        // show confetti immediately
        launch(60);
      });
    })();
  </script>
</body>
</html>
"""

SVG_THIEP = '''<svg xmlns='http://www.w3.org/2000/svg' width='800' height='520' viewBox='0 0 800 520'>
  <defs>
    <linearGradient id='g' x1='0' x2='1' y1='0' y2='1'>
      <stop offset='0' stop-color='%23fff0f7'/>
      <stop offset='1' stop-color='%23ffeef7'/>
    </linearGradient>
  </defs>
  <rect width='800' height='520' rx='24' fill='url(#g)' stroke='%23ffd6ec' stroke-width='6'/>
  <g transform='translate(40,40)'>
    <text x='0' y='40' font-size='34' font-family='Arial' font-weight='700' fill='%23ff5a9e'>Chúc mừng 20/10</text>
    <text x='0' y='90' font-size='20' fill='%23333'>Gửi đến Tran Phuong Anh</text>
    <g transform='translate(0,140)'>
      <rect x='0' y='0' width='720' height='260' rx='14' fill='%23fff' stroke='%23ffdcee' stroke-width='2'/>
      <text x='40' y='60' font-size='22' fill='%23000'>Nhớ viết tâm thư cảm ơn nhé.</text>
      <text x='40' y='100' font-size='16' fill='%23666'>Chúc bà tất cả hihi.</text>
    </g>
  </g>
</svg>'''

@app.route('/', methods=['GET','POST'])
def index():
    name = ''
    show_postcard = False
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        if name:
            show_postcard = True
        else:
            name = ''
    # safe display name
    name_display = name if name else 'Người thân'
    today = datetime.date.today().strftime('%d/%m/%Y')
    # encode svg for embedding (basic escaping of hashes and newlines)
    svg = SVG_THIEP.replace('\n','').replace('#','%23')
    return render_template_string(TEMPLATE, name=name, name_display=name_display, today=today, svg=svg, show_postcard=show_postcard)

if __name__ == '__main__':
    app.run(debug=True)
