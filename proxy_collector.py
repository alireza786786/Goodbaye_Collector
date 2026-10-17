import os
import json
import socket
import ssl
import time
import shutil
import urllib.parse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import pytz
import jdatetime

FIXED_TAG_LINE1 = "👉🆔@Goodbaye_filtering"
BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")

# تنظیمات سخت‌گیرانه VIP: تایم‌اوت ۱.۴ ثانیه و حداکثر پینگ ۶۵۰ میلی‌ثانیه
MAX_WORKERS = 200
STRICT_TIMEOUT = 1.4
MAX_PING_CUTOFF = 650

SECRET_SOURCES = {
    "socks5": os.getenv("SOCKS5_SOURCES", ""),
    "https": os.getenv("HTTPS_SOURCES", ""),
    "telegram": os.getenv("TELEGRAM_SOURCES", ""),
    "mixed": os.getenv("MIXED_SOURCES", "")
}

socket.setdefaulttimeout(STRICT_TIMEOUT)

def get_flag(country_code):
    if not country_code or len(country_code) != 2 or country_code.upper() == "XX":
        return "🌐"
    return "".join(chr(127397 + ord(c)) for c in country_code.upper())

def download_urls_from_secret(secret_text):
    if not secret_text:
        return []
    urls = [l.strip() for l in secret_text.replace(",", "\n").splitlines() if l.strip() and not l.strip().startswith("#")]
    proxies = []
    for url in urls:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                for line in r.text.splitlines():
                    l = line.strip()
                    if l and not l.startswith("#"):
                        proxies.append(l)
        except Exception:
            pass
    return proxies

def parse_proxy_line(line, default_proto="socks5"):
    line = line.strip()
    if not line:
        return None

    if any(k in line for k in ["t.me/socks", "tg://socks", "t.me/proxy", "tg://proxy", "?server="]):
        try:
            parsed_url = urllib.parse.urlparse(line)
            qs = urllib.parse.parse_qs(parsed_url.query)
            srv = qs.get("server", [None])[0]
            prt = qs.get("port", [None])[0]
            sec = qs.get("secret", [None])[0]
            usr = qs.get("user", [None])[0]
            pwd = qs.get("pass", [None])[0]
            if srv and prt:
                return {
                    "proto": "telegram",
                    "ip": srv.strip().replace("[", "").replace("]", ""),
                    "port": int(prt.strip()),
                    "user": usr,
                    "pwd": pwd,
                    "secret": sec
                }
        except Exception:
            pass

    proto = default_proto
    user, pwd = None, None

    if "://" in line:
        parts = line.split("://", 1)
        p = parts[0].lower()
        if p in ["socks5", "socks"]:
            proto = "socks5"
        elif p in ["https", "http"]:
            proto = "https"
        rest = parts[1].split("#")[0]
    else:
        rest = line

    if "@" in rest:
        auth, host_port = rest.split("@", 1)
        user, pwd = auth.split(":", 1) if ":" in auth else (auth, None)
        parts = host_port.split(":")
    else:
        parts = rest.split(":")

    if len(parts) >= 2:
        ip = parts[0].strip().replace("[", "").replace("]", "")
        try:
            port = int(parts[1].strip())
            if len(parts) == 4 and not user:
                user, pwd = parts[2].strip(), parts[3].strip()
            return {"proto": proto, "ip": ip, "port": port, "user": user, "pwd": pwd, "secret": None}
        except ValueError:
            return None
    return None

def test_socks5_alive(ip, port):
    start = time.time()
    family = socket.AF_INET6 if ":" in ip else socket.AF_INET
    s = socket.socket(family, socket.SOCK_STREAM)
    s.settimeout(STRICT_TIMEOUT)
    try:
        s.connect((ip, int(port)))
        s.sendall(b"\x05\x01\x00")
        resp = s.recv(2)
        if len(resp) == 2 and resp[0] == 5 and resp[1] == 0:
            lat = int((time.time() - start) * 1000)
            if lat <= MAX_PING_CUTOFF:
                return lat
    except Exception:
        pass
    finally:
        s.close()
    return None

def test_https_tls_alive(ip, port):
    start = time.time()
    family = socket.AF_INET6 if ":" in ip else socket.AF_INET
    s = socket.socket(family, socket.SOCK_STREAM)
    s.settimeout(STRICT_TIMEOUT)
    try:
        s.connect((ip, int(port)))
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with ctx.wrap_socket(s, server_hostname=ip):
            lat = int((time.time() - start) * 1000)
            if lat <= MAX_PING_CUTOFF:
                return lat
    except Exception:
        pass
    finally:
        s.close()
    return None

def fetch_single_geo(ip):
    try:
        r = requests.get(f"https://freeipapi.com/api/json/{ip}", timeout=3)
        if r.status_code == 200:
            d = r.json()
            if d.get("countryName") and d.get("countryCode"):
                return ip, {"country": d["countryName"], "countryCode": d["countryCode"], "city": d.get("cityName") or "Cloud"}
    except Exception:
        pass
    try:
        r = requests.get(f"https://ipwho.is/{ip}", timeout=3)
        if r.status_code == 200:
            d = r.json()
            if d.get("success"):
                return ip, {"country": d["country"], "countryCode": d["country_code"], "city": d.get("city") or "Cloud"}
    except Exception:
        pass
    return ip, {"country": "Germany", "countryCode": "DE", "city": "Frankfurt"}

def resolve_all_geo(unique_ips):
    geo_data = {}
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(fetch_single_geo, ip) for ip in unique_ips]
        for f in as_completed(futures):
            try:
                ip, data = f.result()
                geo_data[ip] = data
            except Exception:
                pass
    return geo_data

def get_proto_tag(proto, ip):
    ver = "IPv6" if ":" in ip else "IPv4"
    if proto == "https":
        return f"HTTPS via TLS ({ver})"
    elif proto == "telegram":
        return f"Telegram Proxy ({ver})"
    return f"SOCKS5 ({ver})"

def get_capability(ping):
    if ping < 180:
        return "⚡Full Speed & Low Ping"
    elif ping < 350:
        return "⚡Bypass Filtering"
    return "⚡Anti-Sanction & Fast"

def generate_link(item):
    proto = item["proto"]
    ip, port, ping = item["ip"], item["port"], item["ping"]
    user, pwd = item.get("user"), item.get("pwd")
    secret = item.get("secret")
    country = item.get("country", "Germany")
    city = item.get("city", "Frankfurt")
    flag = item.get("flag", "🇩🇪")
    cap = get_capability(ping)
    ptag = get_proto_tag(proto, ip)

    remark = f"{FIXED_TAG_LINE1}\n📡{flag} {country}\n®️{city}\n🅿️ping:{ping}ms\n{cap} | {ptag}"
    enc = urllib.parse.quote(remark)
    f_ip = f"[{ip}]" if ":" in ip else ip

    if proto == "telegram":
        if secret:
            link = f"https://t.me/proxy?server={f_ip}&port={port}&secret={secret}"
        else:
            link = f"https://t.me/socks?server={f_ip}&port={port}"
    elif proto == "https":
        link = f"https://{f_ip}:{port}#{enc}"
    else:
        if user and pwd:
            link = f"socks5://{user}:{pwd}@{f_ip}:{port}#{enc}"
        else:
            link = f"socks5://{f_ip}:{port}#{enc}"
    item["link"] = link
    return link

def save_shards(alive_items):
    os.makedirs("proxies/all", exist_ok=True)
    os.makedirs("sub", exist_ok=True)

    all_links = [generate_link(x) for x in alive_items]
    with open("proxies/all/data.txt", "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\r\n".join(all_links) + "\r\n")
    with open("proxies/all/data.json", "w", encoding="utf-8") as f:
        json.dump(alive_items, f, ensure_ascii=False, indent=2)

    by_proto = {}
    by_country = {}

    for item in alive_items:
        p = item["proto"]
        c = item.get("countryCode", "de").lower()
        by_proto.setdefault(p, []).append(item)
        by_country.setdefault(c, []).append(item)

    for p, items in by_proto.items():
        os.makedirs(f"proxies/protocols/{p}", exist_ok=True)
        links = [x["link"] for x in items]
        with open(f"proxies/protocols/{p}/data.txt", "w", encoding="utf-8", newline="\r\n") as f:
            f.write("\r\n".join(links) + "\r\n")
        with open(f"sub/{p}.txt", "w", encoding="utf-8", newline="\r\n") as f:
            f.write("\r\n".join(links) + "\r\n")

    tg_all = []
    for x in alive_items:
        if x["proto"] in ["telegram", "socks5"]:
            f_ip = f"[{x['ip']}]" if ":" in x['ip'] else x['ip']
            if x.get("secret"):
                tg_all.append(f"https://t.me/proxy?server={f_ip}&port={x['port']}&secret={x['secret']}")
            else:
                tg_all.append(f"https://t.me/socks?server={f_ip}&port={x['port']}")

    with open("sub/telegramProxys.txt", "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\r\n".join(tg_all) + "\r\n")

    for c, items in by_country.items():
        os.makedirs(f"proxies/countries/{c}", exist_ok=True)
        links = [x["link"] for x in items]
        with open(f"proxies/countries/{c}/data.txt", "w", encoding="utf-8", newline="\r\n") as f:
            f.write("\r\n".join(links) + "\r\n")

    if os.path.exists("sub/socks5.txt"):
        shutil.copy("sub/socks5.txt", "socks5.txt")
    if os.path.exists("sub/telegramProxys.txt"):
        shutil.copy("sub/telegramProxys.txt", "telegramProxys.txt")

    tehran_tz = pytz.timezone("Asia/Tehran")
    now_tehran = datetime.now(tehran_tz)
    stats = {
        "total_active": len(alive_items),
        "protocols": {p: len(items) for p, items in by_proto.items()},
        "countries": list(by_country.keys()),
        "updated_at_tehran": now_tehran.strftime("%Y/%m/%d - %H:%M:%S"),
        "quality_index": "VIP Strict (Ping < 650ms)"
    }
    with open("proxies/stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def send_telegram_documents():
    if not BOT_TOKEN or not TARGET_CHAT_ID:
        return

    tehran_tz = pytz.timezone("Asia/Tehran")
    now_tehran = datetime.now(tehran_tz)
    shamsi_date = jdatetime.datetime.fromgregorian(datetime=now_tehran).strftime("%Y/%m/%d")
    tehran_time = now_tehran.strftime("%H:%M:%S")

    reply_markup = {
        "inline_keyboard": [
            [{"text": "📢 کانال اصلی Goodbaye Filtering", "url": "https://t.me/Goodbaye_filtering"}],
            [{"text": "⚡ کانال اختصاصی VIP", "url": "https://t.me/CONFIG_V2RAY_VIP"}],
            [{"text": "🔄 اشتراک‌گذاری با دوستان", "url": "https://t.me/share/url?url=https://t.me/Goodbaye_filtering"}]
        ]
    }

    files_to_send = [
        ("sub/socks5.txt", "Goodbaye_Socks5.txt", "SOCKS5 V2Ray/NekoRay"),
        ("sub/telegramProxys.txt", "telegramProxys.txt", "Telegram Direct Proxies")
    ]

    for f_path, doc_name, title in files_to_send:
        if not os.path.exists(f_path) or os.path.getsize(f_path) == 0:
            continue

        with open(f_path, "r", encoding="utf-8") as f:
            lines_count = len([l for l in f if l.strip()])

        caption = (
            f"🚀 **مجموعه کانفیگ‌های تست‌شده و زنده ({title})**\n"
            f"📡 مناسب دوران اختلال، فیلترینگ و شبکه ملی\n\n"
            f"📅 تاریخ شمسی: `{shamsi_date}`\n"
            f"⏰ ساعت تهران: `{tehran_time}`\n"
            f"📊 شاخص کیفیت: `VIP Strict (Ping < 650ms)`\n"
            f"🔢 تعداد کانفیگ سالم این فایل: `{lines_count}`\n\n"
            f"🌐 لینک مستقیم گیت‌هاب پیجز:\n"
            f"`https://alireza786786.github.io/Goodbaye_Collector/{os.path.basename(f_path)}`"
        )

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        try:
            with open(f_path, "rb") as doc:
                req_files = {"document": (doc_name, doc, "text/plain")}
                data = {
                    "chat_id": TARGET_CHAT_ID,
                    "caption": caption,
                    "parse_mode": "Markdown",
                    "reply_markup": json.dumps(reply_markup)
                }
                requests.post(url, data=data, files=req_files, timeout=25)
            time.sleep(1.5)
        except Exception:
            pass

def main():
    all_raw = []
    for proto, sec_val in SECRET_SOURCES.items():
        lines = download_urls_from_secret(sec_val)
        for line in lines:
            p = parse_proxy_line(line, default_proto=proto)
            if p:
                all_raw.append(p)

    dedup = {}
    for item in all_raw:
        dedup[(item["ip"], item["port"])] = item
    unique_proxies = list(dedup.values())

    alive = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_proxy = {}
        for item in unique_proxies:
            ip, port, proto = item["ip"], item["port"], item["proto"]
            if proto == "https":
                future = executor.submit(test_https_tls_alive, ip, port)
            else:
                future = executor.submit(test_socks5_alive, ip, port)
            future_to_proxy[future] = item

        for future in as_completed(future_to_proxy):
            item = future_to_proxy[future]
            lat = future.result()
            if lat is not None:
                item["ping"] = lat
                alive.append(item)

    if not alive:
        return

    alive.sort(key=lambda x: x["ping"])
    unique_ips = list(set([x["ip"] for x in alive]))
    geo_data = resolve_all_geo(unique_ips)

    for item in alive:
        g = geo_data.get(item["ip"], {})
        item["country"] = g.get("country", "Germany")
        item["countryCode"] = g.get("countryCode", "DE")
        item["city"] = g.get("city", "Frankfurt")
        item["flag"] = get_flag(item["countryCode"])

    save_shards(alive)
    send_telegram_documents()

if __name__ == "__main__":
    main()
