import os
import json
import socket
import ssl
import time
import urllib.parse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import pytz
import jdatetime

FIXED_TAG_LINE1 = "👉🆔@Goodbaye_filtering"
BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")

# تنظیمات سخت‌گیرانه و فوق‌سریع
MAX_WORKERS = 250
STRICT_TIMEOUT = 1.8  # ثانیه - هر سروری بالای این پینگ باشد درجا حذف می‌شود
MAX_PING_CUTOFF = 1500  # میلی‌ثانیه

SECRET_SOURCES = {
    "socks5": os.getenv("SOCKS5_SOURCES", ""),
    "https": os.getenv("HTTPS_SOURCES", ""),
    "telegram": os.getenv("TELEGRAM_SOURCES", ""),
    "mixed": os.getenv("MIXED_SOURCES", "")
}

socket.setdefaulttimeout(STRICT_TIMEOUT)

def get_flag(country_code):
    if not country_code or len(country_code) != 2:
        return "🌐"
    return "".join(chr(127397 + ord(c)) for c in country_code.upper())

def download_urls_from_secret(secret_text):
    if not secret_text:
        return []
    urls = [line.strip() for line in secret_text.replace(",", "\n").splitlines() if line.strip() and not line.strip().startswith("#")]
    proxies = []
    for url in urls:
        try:
            r = requests.get(url, timeout=6)
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
    proto = default_proto
    user, pwd = None, None

    if "://" in line:
        parts = line.split("://", 1)
        p = parts[0].lower()
        if p in ["socks5", "socks", "https", "http", "tg"]:
            proto = "socks5" if p in ["socks5", "socks"] else p
        rest = parts[1].split("#")[0]
    else:
        rest = line

    if "@" in rest:
        auth, host_port = rest.split("@", 1)
        if ":" in auth:
            user, pwd = auth.split(":", 1)
        else:
            user = auth
        parts = host_port.split(":")
    else:
        parts = rest.split(":")

    if len(parts) >= 2:
        ip = parts[0].strip()
        try:
            port = int(parts[1].strip())
            if len(parts) == 4 and not user:
                user = parts[2].strip()
                pwd = parts[3].strip()
            return {"proto": proto, "ip": ip, "port": port, "user": user, "pwd": pwd}
        except ValueError:
            return None
    return None

def test_socks5_alive(ip, port):
    start = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(STRICT_TIMEOUT)
    try:
        s.connect((ip, int(port)))
        s.sendall(b"\x05\x01\x00")
        resp = s.recv(2)
        if len(resp) == 2 and resp[0] == 5 and resp[1] == 0:
            latency = int((time.time() - start) * 1000)
            if latency <= MAX_PING_CUTOFF:
                return latency
    except Exception:
        pass
    finally:
        s.close()
    return None

def test_https_tls_alive(ip, port):
    start = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(STRICT_TIMEOUT)
    try:
        s.connect((ip, int(port)))
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with context.wrap_socket(s, server_hostname=ip):
            latency = int((time.time() - start) * 1000)
            if latency <= MAX_PING_CUTOFF:
                return latency
    except Exception:
        pass
    finally:
        s.close()
    return None

def batch_geoip(ip_list):
    geo_data = {}
    chunk_size = 100
    for i in range(0, len(ip_list), chunk_size):
        chunk = ip_list[i:i + chunk_size]
        payload = [{"query": ip, "fields": "country,countryCode,city,status"} for ip in chunk]
        try:
            r = requests.post("http://ip-api.com/batch?lang=en", json=payload, timeout=5)
            if r.status_code == 200:
                for item in r.json():
                    if item.get("status") == "success":
                        geo_data[item.get("query")] = item
        except Exception:
            pass
        time.sleep(0.3)
    return geo_data

def get_capability(ping):
    if ping < 200:
        return "⚡Full Speed & Low Ping"
    elif ping < 400:
        return "⚡Bypass Filtering"
    else:
        return "⚡Anti-Sanction & National Net"

def generate_link(item):
    proto = item["proto"]
    ip = item["ip"]
    port = item["port"]
    ping = item["ping"]
    user = item.get("user")
    pwd = item.get("pwd")
    country = item.get("country", "Global")
    city = item.get("city", "Cloud")
    flag = item.get("flag", "🌐")
    cap = get_capability(ping)

    remark = f"{FIXED_TAG_LINE1}\n📡{flag} {country}\n®️{city}\n🅿️ping:{ping}ms\n{cap}"
    enc_remark = urllib.parse.quote(remark)

    if proto == "socks5":
        if user and pwd:
            return f"socks5://{user}:{pwd}@{ip}:{port}#{enc_remark}"
        return f"socks5://{ip}:{port}#{enc_remark}"
    elif proto == "https":
        return f"https://{ip}:{port}#{enc_remark}"
    else:
        return f"tg://proxy?server={ip}&port={port}"

def save_shards(alive_items):
    os.makedirs("proxies/all", exist_ok=True)
    os.makedirs("sub", exist_ok=True)

    all_links = [generate_link(x) for x in alive_items]
    with open("proxies/all/data.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(all_links) + "\n")
    with open("proxies/all/data.json", "w", encoding="utf-8") as f:
        json.dump(alive_items, f, ensure_ascii=False, indent=2)

    by_proto = {}
    by_country = {}

    for item in alive_items:
        p = item["proto"]
        c = item.get("countryCode", "other").lower()
        by_proto.setdefault(p, []).append(item)
        by_country.setdefault(c, []).append(item)

    for p, items in by_proto.items():
        p_dir = f"proxies/protocols/{p}"
        os.makedirs(p_dir, exist_ok=True)
        links = [generate_link(x) for x in items]
        with open(f"{p_dir}/data.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(links) + "\n")
        with open(f"{p_dir}/data.json", "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        with open(f"sub/{p}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(links) + "\n")

    for c, items in by_country.items():
        c_dir = f"proxies/countries/{c}"
        os.makedirs(c_dir, exist_ok=True)
        links = [generate_link(x) for x in items]
        with open(f"{c_dir}/data.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(links) + "\n")

    stats = {
        "total_active": len(alive_items),
        "protocols": {p: len(items) for p, items in by_proto.items()},
        "countries": list(by_country.keys()),
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }
    with open("proxies/stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

def send_telegram_notification(total_count):
    if not BOT_TOKEN or not TARGET_CHAT_ID:
        return

    tehran_tz = pytz.timezone("Asia/Tehran")
    now_tehran = datetime.now(tehran_tz)
    shamsi_date = jdatetime.datetime.fromgregorian(datetime=now_tehran).strftime("%Y/%m/%d")
    tehran_time = now_tehran.strftime("%H:%M:%S")

    caption = (
        f"🚀 **مجموعه کانفیگ‌های تست‌شده و زنده**\n"
        f"📡 مناسب دوران اختلال، فیلترینگ و شبکه ملی\n\n"
        f"📅 تاریخ شمسی: `{shamsi_date}`\n"
        f"⏰ ساعت تهران: `{tehran_time}`\n"
        f"📊 شاخص کیفیت: `Ultra Clean & Auto-Tested`\n"
        f"🔢 تعداد کانفیگ سالم: `{total_count}`\n\n"
        f"🌐 سابسکریپشن گیت‌هاب پیجز:\n"
        f"`https://alireza786786.github.io/Goodbaye_Collector/sub/socks5.txt`"
    )

    reply_markup = {
        "inline_keyboard": [
            [{"text": "📢 کانال اصلی Goodbaye Filtering", "url": "https://t.me/Goodbaye_filtering"}],
            [{"text": "⚡ کانال اختصاصی VIP", "url": "https://t.me/CONFIG_V2RAY_VIP"}],
            [{"text": "🔄 اشتراک‌گذاری با دوستان", "url": "https://t.me/share/url?url=https://t.me/Goodbaye_filtering"}]
        ]
    }

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TARGET_CHAT_ID,
        "text": caption,
        "parse_mode": "Markdown",
        "reply_markup": reply_markup
    }
    try:
        requests.post(url, json=payload, timeout=8)
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
            latency = future.result()
            if latency is not None:
                item["ping"] = latency
                alive.append(item)

    if not alive:
        return

    alive.sort(key=lambda x: x["ping"])
    unique_ips = list(set([x["ip"] for x in alive]))
    geo_data = batch_geoip(unique_ips)

    for item in alive:
        g = geo_data.get(item["ip"], {})
        item["country"] = g.get("country", "Unknown")
        item["countryCode"] = g.get("countryCode", "XX")
        item["city"] = g.get("city", "Cloud")
        item["flag"] = get_flag(item["countryCode"])

    save_shards(alive)
    send_telegram_notification(len(alive))

if __name__ == "__main__":
    main()
