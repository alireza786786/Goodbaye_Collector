import os
import datetime

def generate_web_page():
    output_html = "index.html"
    repo_raw_url = "https://raw.githubusercontent.com/alireza786786/Goodbaye_Collector/main"
    pages_base_url = "https://alireza786786.github.io/Goodbaye_Collector"
    
    # ۳ پروتکل اختصاصی و اضطراری جدید
    emergency_proxies = [
        {"name": "socks5.txt", "title": "⚡ ساکس ۵ (SOCKS5 Ultra Clean)", "icon": "fa-bolt", "desc": "مخصوص v2rayNG و Nekoray با پینگ تاییدشده", "badge": "SOCKS5"},
        {"name": "telegramProxys.txt", "title": "✈️ پروکسی مستقیم تلگرام (Direct TG)", "icon": "fa-paper-plane", "desc": "اتصال مستقیم تلگرام بدون نیاز به فیلترشکن", "badge": "TELEGRAM"},
        {"name": "https.txt", "title": "🔒 پروکسی امن HTTPS via TLS", "icon": "fa-lock", "desc": "ارتباط رمزنگاری‌شده و مقاوم در برابر اینترنت ملی", "badge": "HTTPS"}
    ]

    # فایل‌های اصلی و فرمت‌های V2Ray (دست‌نخورده و کامل)
    core_files = [
        {"name": "Goodbaye_Sub.txt", "title": "⭐ سابسکرایب اصلی (تست‌شده و زنده)", "icon": "fa-bolt-lightning", "type": "txt"},
        {"name": "Goodbaye_Light.txt", "title": "⚡ سابسکرایب لایت (۲ ساعت اخیر)", "icon": "fa-clock", "type": "txt"},
        {"name": "Goodbaye_no_cf.txt", "title": "🚫 بدون کلودفلر (مخصوص اینترنت حساس)", "icon": "fa-shield-halved", "type": "txt"},
        {"name": "conf-week.txt", "title": "🗓️ آرشیو پایدار هفتگی (۷ روزه)", "icon": "fa-calendar-week", "type": "txt"},
        {"name": "iran_ping_top10.txt", "title": "🇮🇷 پکیج اختصاصی کمترین پینگ برای ایران", "icon": "fa-gauge-high", "type": "txt"},
        {"name": "open_internet_top10.txt", "title": "🌍 پکیج اختصاصی اینترنت آزاد و بدون فیلتر", "icon": "fa-earth-europe", "type": "txt"},
        {"name": "Goodbaye_Clash.yaml", "title": "کلاینت Clash / Mihomo (قوانین هوشمند)", "icon": "fa-circle-nodes", "type": "yaml"},
        {"name": "Goodbaye_Singbox.json", "title": "کلاینت Sing-box (قوانین باینری)", "icon": "fa-box-open", "type": "json"}
    ]

    # بررسی فایل‌های منطقه‌ای موجود در پوشه regions
    regional_files = []
    if os.path.exists("regions"):
        for f in sorted(os.listdir("regions")):
            if f.endswith(".txt"):
                iso = f.replace("conf-", "").replace(".txt", "").upper()
                regional_files.append({"iso": iso, "file": f"regions/{f}"})

    now_tehran = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3, minutes=30)).strftime('%Y-%m-%d %H:%M')

    html_content = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Goodbaye Collector | پنل جامع سابسکریپشن و پروکسی</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;900&display=swap');
        body {{ font-family: 'Vazirmatn', sans-serif; background: #0b0f1a; color: #e2e8f0; font-size: 16px; }}
        .glass {{ background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.08); }}
        .proxy-box {{ font-family: monospace; background: #000; padding: 18px; border-radius: 14px; height: 260px; overflow-y: auto; direction: ltr; text-align: left; font-size: 13px; border: 1px solid #1e293b; }}
        .tab-active {{ border-bottom: 3px solid #3b82f6; color: #3b82f6; font-weight: 900; }}
        .file-card {{ background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255,255,255,0.05); border-radius: 14px; padding: 14px; transition: all 0.2s; }}
        .file-card:hover {{ border-color: rgba(59, 130, 246, 0.4); transform: translateY(-2px); }}
        .btn-action {{ transition: all 0.2s; font-size: 13px; font-weight: 700; }}
        .social-card {{ transition: all 0.3s; border: 1px solid rgba(255,255,255,0.05); }}
        .social-card:hover {{ background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.4); transform: translateY(-3px); }}
        #toast {{ 
            visibility: hidden; min-width: 220px; background-color: #10b981; color: #fff; 
            text-align: center; border-radius: 12px; padding: 12px; position: fixed; 
            z-index: 100; left: 50%; bottom: 30px; transform: translateX(-50%); 
            font-weight: bold; box-shadow: 0 4px 15px rgba(0,0,0,0.3); opacity: 0;
            transition: opacity 0.3s, bottom 0.3s;
        }}
        #toast.show {{ visibility: visible; opacity: 1; bottom: 50px; }}
        .nav-btn {{ position: fixed; right: 20px; width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; z-index: 50; box-shadow: 0 4px 10px rgba(0,0,0,0.5); transition: 0.3s; color: white; cursor: pointer; }}
        .nav-btn:hover {{ transform: scale(1.1); }}
    </style>
</head>
<body class="p-4 md:p-10 relative">
    <div id="toast"><i class="fa-solid fa-check-circle ml-2"></i>کپی شد!</div>

    <button onclick="window.scrollTo(0,0)" class="nav-btn bottom-20 bg-blue-600" title="برو به بالا">
        <i class="fa-solid fa-arrow-up"></i>
    </button>
    <button onclick="window.scrollTo(0, document.body.scrollHeight)" class="nav-btn bottom-5 bg-slate-700" title="برو به پایین">
        <i class="fa-solid fa-arrow-down"></i>
    </button>

    <div class="max-w-6xl mx-auto">
        <header class="text-center mb-12">
            <h1 class="text-4xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-sky-400 to-indigo-400 mb-3">Goodbaye Collector</h1>
            <p class="text-slate-400 text-sm">ابر کالکتور و موتور هوشمند سابسکریپشن V2Ray و پروکسی اضطراری | بروزرسانی: {now_tehran}</p>
        </header>

        <!-- بخش ویژه جدید: پروکسی‌های اضطراری ۳ گانه (Socks5, Telegram, HTTPS) -->
        <section class="mb-12 glass p-6 rounded-3xl border-t-4 border-emerald-500 shadow-2xl">
            <div class="flex justify-between items-center mb-6">
                <div>
                    <h2 class="text-2xl font-black flex items-center text-emerald-400">
                        <i class="fa-solid fa-shield-virus ml-3 text-3xl"></i> پروکسی‌های اضطراری ضد فیلتر (SOCKS5 | تلگرام | HTTPS)
                    </h2>
                    <p class="text-xs text-slate-400 mt-1">کانفیگ‌های تست‌شده با پینگ زیر ۶۵۰ms و سازگار با دوران اختلال و شبکه ملی</p>
                </div>
                <span class="text-xs bg-emerald-500/20 text-emerald-300 px-3 py-1 rounded-full font-bold">تست زنده VIP</span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    """

    for ep in emergency_proxies:
        ep_url = f"{pages_base_url}/{ep['name']}"
        html_content += f"""
                <div class="file-card flex flex-col justify-between gap-3 border border-emerald-500/20 bg-emerald-950/20">
                    <div>
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-xs font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400">{ep['badge']}</span>
                            <i class="fa-solid {ep['icon']} text-emerald-400"></i>
                        </div>
                        <h3 class="text-sm font-bold text-slate-100">{ep['title']}</h3>
                        <p class="text-[11px] text-slate-400 mt-1">{ep['desc']}</p>
                    </div>
                    <div class="flex gap-2 pt-2 border-t border-white/5">
                        <button onclick="copyText('{ep_url}')" class="flex-1 bg-emerald-600/30 text-emerald-300 py-2 rounded-lg btn-action hover:bg-emerald-600 hover:text-white transition">کپی لینک</button>
                        <button onclick="copyContent('{ep_url}')" class="flex-1 bg-purple-600/20 text-purple-300 py-2 rounded-lg btn-action hover:bg-purple-600 hover:text-white transition">کپی متن</button>
                        <button onclick="downloadFile('{ep_url}', '{ep['name']}')" class="bg-slate-700 text-white px-3 py-2 rounded-lg btn-action hover:bg-emerald-600 transition"><i class="fa-solid fa-download"></i></button>
                    </div>
                </div>"""

    html_content += f"""
            </div>
        </section>

        <!-- بخش پروکسی‌های زنده تلگرام MTProto -->
        <section class="mb-12 glass p-6 rounded-3xl border-t-4 border-sky-500 shadow-2xl">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-black flex items-center text-sky-400">
                    <i class="fa-brands fa-telegram ml-3 text-3xl"></i> پروکسی‌های تلگرام (MTProto)
                </h2>
                <span class="text-xs bg-sky-500/20 text-sky-300 px-3 py-1 rounded-full font-bold">بدون نیاز به وی‌پی‌ان</span>
            </div>
            <div class="flex gap-6 mb-4 border-b border-white/10 text-base font-bold">
                <button onclick="switchTG('mixed')" id="tab-mixed" class="pb-3 px-2 tab-active transition-all">میکس (پیشنهادی)</button>
                <button onclick="switchTG('android')" id="tab-android" class="pb-3 px-2 text-slate-400 transition-all">اندروید</button>
                <button onclick="switchTG('windows')" id="tab-windows" class="pb-3 px-2 text-slate-400 transition-all">ویندوز</button>
            </div>
            <div id="proxy-display" class="proxy-box mb-4 shadow-inner text-slate-300">در حال بارگذاری پروکسی‌ها...</div>
            <button onclick="copyCurrentProxy()" class="w-full bg-gradient-to-r from-sky-600 to-blue-600 hover:from-sky-500 hover:to-blue-500 py-3.5 rounded-xl font-bold transition flex items-center justify-center active:scale-95 text-white">
                <i class="fa-solid fa-copy ml-2 text-lg"></i> کپی تمام پروکسی‌ها
            </button>
        </section>

        <!-- بخش سابسکریپشن‌های اصلی V2Ray (دست‌نخورده) -->
        <h2 class="text-2xl font-black mb-6 flex items-center text-blue-400">
            <i class="fa-solid fa-server ml-3"></i> لینک‌های سابسکریپشن اصلی V2Ray
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
    """

    for item in core_files:
        furl = f"{repo_raw_url}/{item['name']}"
        icon = item['icon']
        title = item['title']
        html_content += f"""
            <div class="file-card flex flex-col justify-between gap-3">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400">
                        <i class="fa-solid {icon} text-lg"></i>
                    </div>
                    <span class="text-sm font-bold text-slate-200 truncate">{title}</span>
                </div>
                <div class="flex gap-2">
                    <button onclick="copyText('{furl}')" class="flex-1 bg-blue-600/20 text-blue-400 py-2 rounded-lg btn-action hover:bg-blue-600 hover:text-white transition">کپی لینک</button>
                    <button onclick="copyContent('{furl}')" class="flex-1 bg-purple-600/20 text-purple-400 py-2 rounded-lg btn-action hover:bg-purple-600 hover:text-white transition">کپی متن</button>
                    <button onclick="downloadFile('{furl}', '{item['name']}')" class="bg-slate-700 text-white px-4 py-2 rounded-lg btn-action hover:bg-emerald-600 transition"><i class="fa-solid fa-download"></i></button>
                </div>
            </div>"""

    html_content += """
        </div>
    """

    # بخش سابسکریپشن به تفکیک کشورها (دست‌نخورده)
    if regional_files:
        html_content += """
        <h2 class="text-2xl font-black mb-6 flex items-center text-indigo-400">
            <i class="fa-solid fa-earth-americas ml-3"></i> سابسکریپشن تفکیک‌شده بر اساس کشور
        </h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 mb-12">
        """
        for reg in regional_files:
            rfurl = f"{repo_raw_url}/{reg['file']}"
            html_content += f"""
            <div class="file-card flex flex-col gap-2">
                <div class="flex items-center justify-between">
                    <span class="font-bold text-sm text-slate-200">کشور {reg['iso']}</span>
                    <i class="fa-solid fa-location-dot text-indigo-400"></i>
                </div>
                <div class="flex gap-1">
                    <button onclick="copyText('{rfurl}')" class="flex-1 bg-indigo-600/20 text-indigo-300 py-1.5 rounded-lg btn-action hover:bg-indigo-600 hover:text-white transition text-xs">لینک</button>
                    <button onclick="copyContent('{rfurl}')" class="flex-1 bg-purple-600/20 text-purple-300 py-1.5 rounded-lg btn-action hover:bg-purple-600 hover:text-white transition text-xs">متن</button>
                </div>
            </div>"""
        html_content += """</div>"""

    # فوتر با هر دو کانال رسمی
    html_content += f"""
        <footer class="mt-16 mb-8">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <a href="https://t.me/Goodbaye_filtering" target="_blank" class="social-card glass rounded-2xl p-6 flex items-center justify-between group">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 bg-sky-500/20 rounded-full flex items-center justify-center text-sky-400 text-2xl group-hover:bg-sky-500 group-hover:text-white transition-all">
                            <i class="fa-brands fa-telegram"></i>
                        </div>
                        <div>
                            <h3 class="font-bold text-lg">کانال اصلی گودبای فیلترینگ</h3>
                            <p class="text-slate-400 text-sm">@Goodbaye_filtering</p>
                        </div>
                    </div>
                    <i class="fa-solid fa-arrow-up-right-from-square text-slate-500 group-hover:text-sky-400 transition-all"></i>
                </a>

                <a href="https://t.me/CONFIG_V2RAY_VIP" target="_blank" class="social-card glass rounded-2xl p-6 flex items-center justify-between group">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 bg-amber-500/20 rounded-full flex items-center justify-center text-amber-400 text-2xl group-hover:bg-amber-500 group-hover:text-white transition-all">
                            <i class="fa-solid fa-crown"></i>
                        </div>
                        <div>
                            <h3 class="font-bold text-lg">کانال وی‌آی‌پی کانفیگ</h3>
                            <p class="text-slate-400 text-sm">@CONFIG_V2RAY_VIP</p>
                        </div>
                    </div>
                    <i class="fa-solid fa-arrow-up-right-from-square text-slate-500 group-hover:text-amber-400 transition-all"></i>
                </a>
            </div>
            <p class="text-center mt-12 text-slate-500 text-xs font-bold uppercase tracking-widest">Goodbaye Collector Core | Powered by Open Source</p>
        </footer>
    </div>

    <script>
        let tgData = {{ android: '', windows: '', mixed: '' }};
        const REPO_URL = "{repo_raw_url}";
        
        function showToast(msg = 'کپی شد!') {{
            const t = document.getElementById("toast");
            t.innerHTML = '<i class="fa-solid fa-check-circle ml-2"></i>' + msg;
            t.className = "show";
            setTimeout(() => {{ t.className = t.className.replace("show", ""); }}, 2200);
        }}

        async function loadTGData() {{
            try {{
                const [a, w, m] = await Promise.all([
                    fetch(REPO_URL + '/tg_android.txt').then(r => r.ok ? r.text() : '').catch(() => ''),
                    fetch(REPO_URL + '/tg_windows.txt').then(r => r.ok ? r.text() : '').catch(() => ''),
                    fetch(REPO_URL + '/tg.txt').then(r => r.ok ? r.text() : '').catch(() => '')
                ]);
                tgData.android = a.trim(); 
                tgData.windows = w.trim(); 
                tgData.mixed = m.trim() || a.trim() || w.trim() || 'در حال حاضر پروکسی جدیدی موجود نیست.';
                switchTG('mixed');
            }} catch(e) {{ 
                const disp = document.getElementById('proxy-display');
                if(disp) disp.innerText = 'خطا در بارگذاری پروکسی‌ها.';
            }}
        }}

        function switchTG(mode) {{
            const display = document.getElementById('proxy-display');
            if(display && tgData[mode]) {{
                display.innerText = tgData[mode].split('\\n').join('\\n\\n');
            }}
            ['android', 'windows', 'mixed'].forEach(m => {{
                const btn = document.getElementById('tab-' + m);
                if(btn) btn.className = 'pb-3 px-2 ' + (m === mode ? 'tab-active' : 'text-slate-400');
            }});
            window.currentMode = mode;
        }}

        function copyCurrentProxy() {{ 
            if(!tgData[window.currentMode]) return;
            navigator.clipboard.writeText(tgData[window.currentMode]); 
            showToast('پروکسی‌ها کپی شدند');
        }}

        function copyText(t) {{ 
            navigator.clipboard.writeText(t); 
            showToast('لینک کپی شد');
        }}

        async function copyContent(url) {{
            try {{
                const r = await fetch(url); 
                const t = await r.text();
                navigator.clipboard.writeText(t); 
                showToast('متن کانفیگ‌ها کپی شد');
            }} catch(e) {{ 
                showToast('خطا در دریافت متن');
            }}
        }}

        async function downloadFile(url, name) {{
            try {{
                const r = await fetch(url); 
                const b = await r.blob();
                const a = document.createElement('a'); 
                a.href = URL.createObjectURL(b);
                a.download = name; 
                a.click();
            }} catch(e) {{ 
                showToast('خطا در دانلود');
            }}
        }}

        window.onload = loadTGData;
    </script>
</body>
</html>
"""
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    generate_web_page()
