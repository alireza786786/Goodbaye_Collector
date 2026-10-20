import os
import re
import time
import json
import yaml
import html
import socket
import base64
import asyncio
import logging
import datetime
import ipaddress
import urllib.request
import geoip2.database
from typing import Optional, Dict, Any, Set, List, Tuple
from urllib.parse import urlparse, parse_qs, unquote, quote
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("GoodbayeSuperEngine")

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
TARGET_CHAT_ID = os.environ.get("TARGET_CHAT_ID", "")
CHANNELS_STR = os.environ.get('CHANNELS_LIST', "")

OUTPUT_YAML_PRO = "Goodbaye_Clash.yaml"
OUTPUT_TXT = "Goodbaye_Sub.txt"
OUTPUT_JSON = "Goodbaye_Singbox.json"
OUTPUT_ORIGINAL_CONFIGS = "Original-Configs.txt"
OUTPUT_NO_CF = "Goodbaye_no_cf.txt"
OUTPUT_LIGHT = "Goodbaye_Light.txt"

IRAN_PING_FILE = "iran_ping_top10.txt"
OPEN_INTERNET_FILE = "open_internet_top10.txt"

TG_PROXIES_FILE = "tg.txt"
TG_WINDOWS_FILE = "tg_windows.txt"
TG_ANDROID_FILE = "tg_android.txt"

LIGHT_MAX_AGE_HOURS = 1
WEEKLY_FILE = "conf-week.txt"
HISTORY_FILE = "conf-week-history.json"
GEOIP_DATABASE_PATH = 'GeoLite2-City.mmdb'
NO_CF_HISTORY_FILE = "no_cf_history.json"
BLOCKED_IPS_FILE = "blocked_ips.txt"

PING_TIMEOUT_SECONDS = 1.5

# اولویت‌های هوشمند مسیریابی برای ایران
IRAN_PING_PRIORITY = ("TR", "AE", "QA", "BH", "KW", "OM", "SA", "AM", "GE", "DE", "NL", "FR", "RO", "BG")
OPEN_INTERNET_PRIORITY = ("NL", "DE", "IS", "EE", "CA", "CH", "CZ", "AT", "ES", "PT", "TW", "JP", "FR", "AU")

BLOCKED_SERVERS = ("127.0.0.1", "0.0.0.0", "localhost", "t.me", "github.com", "google.com")
CLOUDFLARE_DOMAINS = ('.workers.dev', '.pages.dev', '.trycloudflare.com', 'chatgpt.com')

V2RAY_PATTERNS = [
    re.compile(r'(vless:\/\/[^\s\'\"<>`|()\[\]{}]+)'),
    re.compile(r'(vmess:\/\/[^\s\'\"<>`|()\[\]{}]+)'),
    re.compile(r'(trojan:\/\/[^\s\'\"<>`|()\[\]{}]+)'),
    re.compile(r'(ss:\/\/[^\s\'\"<>`|()\[\]{}]+)'),
    re.compile(r"(hy2://[^\s'\"<>`|()\[\]{}]+)"),
    re.compile(r"(hysteria2://[^\s'\"<>`|()\[\]{}]+)"),
    re.compile(r"(tuic://[^\s'\"<>`|()\[\]{}]+)")
]
TG_PROXY_PATTERN = re.compile(r'(?:tg:\/\/proxy\?|https:\/\/t\.me\/proxy\?)[^\s\'\"<>`|()\[\]{}]+')
BASE64_PATTERN = re.compile(r"([A-Za-z0-9+/=]{50,})", re.MULTILINE)

SS_VALID_CIPHERS = {
    'aes-128-gcm', 'aes-192-gcm', 'aes-256-gcm',
    'aes-128-cfb', 'aes-192-cfb', 'aes-256-cfb',
    'aes-128-ctr', 'aes-192-ctr', 'aes-256-ctr',
    'rc4-md5', 'chacha20-ietf', 'xchacha20',
    'chacha20-ietf-poly1305', 'xchacha20-ietf-poly1305',
    '2022-blake3-aes-128-gcm', '2022-blake3-aes-256-gcm',
    '2022-blake3-chacha20-poly1305', 'none'
}

# لیست کامل ۲۵۰ کشور و پرچم‌های جهان
COUNTRY_FLAGS = {
    'AD': '🇦🇩', 'AE': '🇦🇪', 'AF': '🇦🇫', 'AG': '🇦🇬', 'AI': '🇦🇮', 'AL': '🇦🇱', 'AM': '🇦🇲', 'AO': '🇦🇴',
    'AQ': '🇦🇶', 'AR': '🇦🇷', 'AS': '🇦🇸', 'AT': '🇦🇹', 'AU': '🇦🇺', 'AW': '🇦🇼', 'AX': '🇦🇽', 'AZ': '🇦🇿',
    'BA': '🇧🇦', 'BB': '🇧🇧', 'BD': '🇧🇩', 'BE': '🇧🇪', 'BF': '🇧🇫', 'BG': '🇧🇬', 'BH': '🇧🇭', 'BI': '🇧🇮',
    'BJ': '🇧🇯', 'BL': '🇧🇱', 'BM': '🇧🇲', 'BN': '🇧🇳', 'BO': '🇧🇴', 'BR': '🇧🇷', 'BS': '🇧🇸', 'BT': '🇧🇹',
    'BW': '🇧🇼', 'BY': '🇧🇾', 'BZ': '🇧🇿', 'CA': '🇨🇦', 'CC': '🇨🇨', 'CD': '🇨🇩', 'CF': '🇨🇫', 'CG': '🇨🇬',
    'CH': '🇨🇭', 'CI': '🇨🇮', 'CK': '🇨🇰', 'CL': '🇨🇱', 'CM': '🇨🇲', 'CN': '🇨🇳', 'CO': '🇨🇴', 'CR': '🇨🇷',
    'CU': '🇨🇺', 'CV': '🇨🇻', 'CW': '🇨🇼', 'CX': '🇨🇽', 'CY': '🇨🇾', 'CZ': '🇨🇿', 'DE': '🇩🇪', 'DJ': '🇩🇯',
    'DK': '🇩🇰', 'DM': '🇩🇲', 'DO': '🇩🇴', 'DZ': '🇩🇿', 'EC': '🇪🇨', 'EE': '🇪🇪', 'EG': '🇪🇬', 'EH': '🇪🇭',
    'ER': '🇪🇷', 'ES': '🇪🇸', 'ET': '🇪🇹', 'FI': '🇫🇮', 'FJ': '🇫🇯', 'FK': '🇫🇰', 'FM': '🇫🇲', 'FO': '🇫🇴',
    'FR': '🇫🇷', 'GA': '🇬🇦', 'GB': '🇬🇧', 'GD': '🇬🇩', 'GE': '🇬🇪', 'GF': '🇬🇫', 'GG': '🇬🇬', 'GH': '🇬🇭',
    'GI': '🇬🇮', 'GL': '🇬🇱', 'GM': '🇬🇲', 'GN': '🇬🇳', 'GP': '🇬🇵', 'GQ': '🇬🇶', 'GR': '🇬🇷', 'GT': '🇬🇹',
    'GU': '🇬🇺', 'GW': '🇬🇼', 'GY': '🇬🇾', 'HK': '🇭🇰', 'HN': '🇭🇳', 'HR': '🇭🇷', 'HT': '🇭🇹', 'HU': '🇭🇺',
    'ID': '🇮🇩', 'IE': '🇮🇪', 'IL': '🇮🇱', 'IM': '🇮🇲', 'IN': '🇮🇳', 'IO': '🇮🇴', 'IQ': '🇮🇶', 'IR': '🇮🇷',
    'IS': '🇮🇸', 'IT': '🇮🇹', 'JE': '🇯🇪', 'JM': '🇯🇲', 'JO': '🇯🇴', 'JP': '🇯🇵', 'KE': '🇰🇪', 'KG': '🇰🇬',
    'KH': '🇰🇭', 'KI': '🇰🇮', 'KM': '🇰🇲', 'KN': '🇰🇳', 'KP': '🇰🇵', 'KR': '🇰🇷', 'KW': '🇰🇼', 'KY': '🇰🇾',
    'KZ': '🇰🇿', 'LA': '🇱🇦', 'LB': '🇱🇧', 'LC': '🇱🇨', 'LI': '🇱🇮', 'LK': '🇱🇰', 'LR': '🇱🇷', 'LS': '🇱🇸',
    'LT': '🇱🇹', 'LU': '🇱🇺', 'LV': '🇱🇻', 'LY': '🇱🇾', 'MA': '🇲🇦', 'MC': '🇲🇨', 'MD': '🇲🇩', 'ME': '🇲🇪',
    'MF': '🇲🇫', 'MG': '🇲🇬', 'MH': '🇲🇭', 'MK': '🇲🇰', 'ML': '🇲🇱', 'MM': '🇲🇲', 'MN': '🇲🇳', 'MO': '🇲🇴',
    'MP': '🇲🇵', 'MQ': '🇲🇶', 'MR': '🇲🇷', 'MS': '🇲🇸', 'MT': '🇲🇹', 'MU': '🇲🇺', 'MV': '🇲🇻', 'MW': '🇲🇼',
    'MX': '🇲🇽', 'MY': '🇲🇾', 'MZ': '🇲🇿', 'NA': '🇳🇦', 'NC': '🇳🇨', 'NE': '🇳🇪', 'NF': '🇳🇫', 'NG': '🇳🇬',
    'NI': '🇳🇮', 'NL': '🇳🇱', 'NO': '🇳🇴', 'NP': '🇳🇵', 'NR': '🇳🇷', 'NU': '🇳🇺', 'NZ': '🇳🇿', 'OM': '🇴🇲',
    'PA': '🇵🇦', 'PE': '🇵🇪', 'PF': '🇵🇫', 'PG': '🇵🇬', 'PH': '🇵🇭', 'PK': '🇵🇰', 'PL': '🇵🇱', 'PM': '🇵🇲',
    'PN': '🇵🇳', 'PR': '🇵🇷', 'PS': '🇵🇸', 'PT': '🇵🇹', 'PW': '🇵🇼', 'PY': '🇵🇾', 'QA': '🇶🇦', 'RE': '🇷🇪',
    'RO': '🇷🇴', 'RS': '🇷🇸', 'RU': '🇷🇺', 'RW': '🇷🇼', 'SA': '🇸🇦', 'SB': '🇸🇧', 'SC': '🇸🇨', 'SD': '🇸🇩',
    'SE': '🇸🇪', 'SG': '🇸🇬', 'SH': '🇸🇭', 'SI': '🇸🇮', 'SK': '🇸🇰', 'SL': '🇸🇱', 'SM': '🇸🇲', 'SN': '🇸🇳',
    'SO': '🇸🇴', 'SR': '🇸🇷', 'SS': '🇸🇸', 'ST': '🇸🇹', 'SV': '🇸🇻', 'SX': '🇸🇽', 'SY': '🇸🇾', 'SZ': '🇸🇿',
    'TC': '🇹🇨', 'TD': '🇹🇩', 'TG': '🇹🇬', 'TH': '🇹🇭', 'TJ': '🇹🇯', 'TK': '🇹🇰', 'TL': '🇹🇱', 'TM': '🇹🇲',
    'TN': '🇹🇳', 'TO': '🇹🇴', 'TR': '🇹🇷', 'TT': '🇹🇹', 'TV': '🇹🇻', 'TW': '🇹🇼', 'TZ': '🇹🇿', 'UA': '🇺🇦',
    'UG': '🇺🇬', 'US': '🇺🇸', 'UY': '🇺🇾', 'UZ': 'UZ', 'VA': '🇻🇦', 'VC': '🇻🇨', 'VE': '🇻🇪', 'VG': '🇻🇬',
    'VI': '🇻🇮', 'VN': '🇻🇳', 'VU': '🇻🇺', 'WF': '🇼🇫', 'WS': '🇼🇸', 'YE': '🇾🇪', 'YT': '🇾🇹', 'ZA': '🇿🇦',
    'ZM': '🇿🇲', 'ZW': '🇿🇼'
}

GEOIP_READER = None
BLOCKED_NETWORKS = []

def load_ip_data():
    global GEOIP_READER
    if not os.path.exists(GEOIP_DATABASE_PATH) or os.path.getsize(GEOIP_DATABASE_PATH) < 5000000:
        logger.info("Downloading GeoLite2-City database...")
        city_url = "https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb"
        try:
            urllib.request.urlretrieve(city_url, GEOIP_DATABASE_PATH)
            logger.info("GeoLite2-City mounted successfully.")
        except Exception as e:
            logger.warning(f"GeoIP download error: {e}")

    if os.path.exists(GEOIP_DATABASE_PATH):
        try:
            GEOIP_READER = geoip2.database.Reader(GEOIP_DATABASE_PATH)
            logger.info("Successfully mounted GeoLite2-City database.")
        except Exception as e:
            logger.warning(f"GeoIP reader init warning: {e}")

def load_blocked_ips():
    global BLOCKED_NETWORKS
    if os.path.exists(BLOCKED_IPS_FILE):
        try:
            with open(BLOCKED_IPS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            BLOCKED_NETWORKS.append(ipaddress.ip_network(line, strict=False))
                        except ValueError:
                            pass
        except Exception:
            pass

def is_clean_ip(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_unspecified or ip.is_private:
            return False
        for network in BLOCKED_NETWORKS:
            if ip in network:
                return False 
        return True 
    except ValueError:
        return False 

def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    jy = 979 if gy > 1600 else 0
    gy -= 1600 if gy > 1600 else 621
    gy2 = gy if gm > 2 else gy - 1
    days = 365 * gy + ((gy2 + 4) // 4) - ((gy2 + 100) // 100) + ((gy2 + 400) // 400) - 80 + gd + g_d_m[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    jm = (days // 31) + 1 if days < 186 else ((days - 186) // 30) + 7
    jd = (days % 31) + 1 if days < 186 else ((days - 186) % 30) + 1
    return f"{jy}/{jm:02d}/{jd:02d}"

async def measure_ping(host: str, port: int) -> Tuple[bool, int]:
    try:
        t0 = time.perf_counter()
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=PING_TIMEOUT_SECONDS
        )
        latency = int((time.perf_counter() - t0) * 1000)
        writer.close()
        await writer.wait_closed()
        return True, max(latency, 1)
    except Exception:
        return False, 0

def detect_capability(proxy_type: str, query: dict, net_type: str) -> str:
    sec = query.get("security", "")
    if sec == "reality" or query.get("pbk") or query.get("pk"):
        return "Reality"
    if net_type == "ws":
        return "WebSocket-TLS" if sec in ["tls", "ssl"] else "WebSocket"
    if net_type == "grpc":
        return "gRPC-Multi"
    if proxy_type in ["hysteria2", "hy2"]:
        return "Hysteria2-UDP"
    if proxy_type == "tuic":
        return "Tuic-v5"
    if proxy_type == "vmess":
        return "VMess-TCP"
    return "TCP-Direct"

class GoodbayeExtractor:
    def __init__(self):
        self.raw_configs: Set[str] = set()
        self.raw_config_times: Dict[str, datetime.datetime] = {}
        self.fingerprints: Set[str] = set()
        self._geo_cache: Dict[str, Tuple[str, str, str, str]] = {}
        self.tg_proxies: Set[str] = set()

    async def get_geo_info(self, host: str, fallback_sni: str = "") -> Tuple[str, str, str, str]:
        cache_key = f"{host}_{fallback_sni}"
        if cache_key in self._geo_cache:
            return self._geo_cache[cache_key]

        def _lookup(h, sni):
            if not GEOIP_READER:
                return "US", "🇺🇸", "United States", "Central"
            
            target_ip = None
            for candidate in [h, sni]:
                if not candidate: continue
                try:
                    socket.inet_aton(candidate)
                    target_ip = candidate
                    break
                except:
                    try:
                        target_ip = socket.gethostbyname(candidate)
                        break
                    except:
                        continue

            if not target_ip:
                return "US", "🇺🇸", "United States", "Central"

            try:
                res = GEOIP_READER.city(target_ip)
                iso = res.country.iso_code or res.registered_country.iso_code or res.represented_country.iso_code
                if not iso or iso in ['XX', 'T1', 'N/A']:
                    iso = "US"
                flag = COUNTRY_FLAGS.get(iso, '🌐')
                country = res.country.names.get('en') or res.registered_country.names.get('en') or iso
                city = res.city.names.get('en') or res.subdivisions.most_specific.names.get('en') or "Central"
                return iso, flag, country, city
            except Exception:
                return "US", "🇺🇸", "United States", "Central"

        res = await asyncio.to_thread(_lookup, host, fallback_sni)
        self._geo_cache[cache_key] = res
        return res

    def is_problematic_proxy(self, p: Dict[str, Any]) -> bool:
        if not p: return True
        srv = str(p.get('server', '')).strip().lower()
        port = p.get('port')
        if not srv or not isinstance(port, int) or port < 1 or port > 65535:
            return True
        if any(b in srv for b in BLOCKED_SERVERS):
            return True

        ptype = p.get('type')
        if ptype in {'vmess', 'vless', 'tuic'} and not p.get('uuid'): return True
        if ptype in {'trojan', 'hysteria2'} and not p.get('password'): return True
        if ptype == 'ss':
            cipher = str(p.get('cipher', '')).lower()
            if not cipher or not p.get('password') or cipher not in SS_VALID_CIPHERS:
                return True

        # اعتبارسنجی سخت‌گیرانه برای Reality
        if ptype == 'vless' and p.get('reality-opts'):
            pbk = str(p['reality-opts'].get('public-key', '')).replace('=', '').strip()
            sid = str(p['reality-opts'].get('short-id', '')).strip()
            if len(pbk) != 43 or not re.fullmatch(r'[A-Za-z0-9\-_]+', pbk):
                return True
            if sid and (len(sid) > 16 or len(sid) % 2 != 0 or not re.fullmatch(r'[0-9a-fA-F]+', sid)):
                return True

        return False

    def parse_config_for_clash(self, url: str) -> Optional[Dict[str, Any]]:
        parsers = {
            'vmess://': self.parse_vmess,
            'vless://': self.parse_vless,
            'trojan://': self.parse_trojan,
            'ss://': self.parse_shadowsocks,
            'hysteria2://': self.parse_hysteria2,
            'hy2://': self.parse_hysteria2,
            'tuic://': self.parse_tuic
        }
        for prefix, parser in parsers.items():
            if url.startswith(prefix):
                try:
                    p = parser(url)
                    if p and not self.is_problematic_proxy(p):
                        return p
                except:
                    return None
        return None

    def parse_vmess(self, url: str) -> Optional[Dict[str, Any]]:
        c = json.loads(base64.b64decode(url[8:] + '=' * 4).decode('utf-8', errors='ignore'))
        ws_opts = {'path': c.get('path', '/'), 'headers': {'Host': c.get('host', c.get('add'))}} if c.get('net') == 'ws' else None
        return {'name': c.get('ps', ''), 'type': 'vmess', 'server': c.get('add'), 'port': int(c.get('port', 443)), 'uuid': c.get('id'), 'alterId': int(c.get('aid', 0)), 'cipher': c.get('scy', 'auto'), 'tls': c.get('tls') == 'tls', 'network': c.get('net', 'tcp'), 'udp': True, 'ws-opts': ws_opts, 'servername': c.get('sni', c.get('host'))}

    def parse_vless(self, url: str) -> Optional[Dict[str, Any]]:
        p = urlparse(url)
        q = {k: v[0] for k, v in parse_qs(p.query).items()}
        pbk = (q.get('pbk') or q.get('pk') or '').replace(' ', '+')
        reality = {'public-key': pbk} if q.get('security') == 'reality' and pbk else None
        if reality and q.get('sid'): reality['short-id'] = q.get('sid')
        raw_h = q.get('host') or q.get('sni') or p.hostname
        ws_h = raw_h.split(',')[0].strip() if raw_h else p.hostname
        ws_opts = {'path': q.get('path', '/'), 'headers': {'Host': ws_h}} if q.get('type') == 'ws' else None
        return {'name': unquote(p.fragment or ''), 'type': 'vless', 'server': p.hostname, 'port': p.port or 443, 'uuid': p.username, 'udp': True, 'tls': q.get('security') in ['tls', 'reality'], 'flow': q.get('flow'), 'client-fingerprint': q.get('fp'), 'network': q.get('type', 'tcp'), 'servername': q.get('sni'), 'ws-opts': ws_opts, 'reality-opts': reality}

    def parse_trojan(self, url: str) -> Optional[Dict[str, Any]]:
        p = urlparse(url)
        q = {k: v[0] for k, v in parse_qs(p.query).items()}
        raw_h = q.get('host') or q.get('sni') or p.hostname
        ws_h = raw_h.split(',')[0].strip() if raw_h else p.hostname
        ws_opts = {'path': q.get('path', '/'), 'headers': {'Host': ws_h}} if q.get('type') == 'ws' else None
        return {'name': unquote(p.fragment or ''), 'type': 'trojan', 'server': p.hostname, 'port': p.port or 443, 'password': p.username, 'udp': True, 'sni': q.get('sni'), 'network': q.get('type', 'tcp'), 'ws-opts': ws_opts, 'client-fingerprint': q.get('fp')}

    def parse_shadowsocks(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            content = url[5:]
            name = unquote(content.split('#', 1)[1]) if '#' in content else ''
            content = content.split('#', 1)[0]
            u_b64, s_part = content.rsplit('@', 1)
            host, port = s_part.rsplit(':', 1)
            info = base64.b64decode(u_b64 + '=' * (-len(u_b64) % 4)).decode('utf-8')
            for _ in range(2):
                if info.startswith('ss://'):
                    inner = info[5:]
                    info = base64.b64decode(inner + '=' * (-len(inner) % 4)).decode('utf-8')
                else: break
            cipher, pw = info.split(':', 1)
            if cipher == 'chacha20-poly1305': cipher = 'chacha20-ietf-poly1305'
            if cipher not in SS_VALID_CIPHERS: return None
            return {'name': name, 'type': 'ss', 'server': host, 'port': int(port), 'cipher': cipher, 'password': pw, 'udp': True}
        except: return None

    def parse_hysteria2(self, url: str) -> Optional[Dict[str, Any]]:
        p = urlparse(url)
        q = {k: v[0] for k, v in parse_qs(p.query).items()}
        return {'name': unquote(p.fragment or ''), 'type': 'hysteria2', 'server': p.hostname, 'port': p.port or 443, 'password': p.username or p.password, 'sni': q.get('sni', [p.hostname])[0], 'skip-cert-verify': q.get('insecure') in ['1', 'true']}

    def parse_tuic(self, url: str) -> Optional[Dict[str, Any]]:
        p = urlparse(url)
        q = {k: v[0] for k, v in parse_qs(p.query).items()}
        return {'name': unquote(p.fragment or ''), 'type': 'tuic', 'server': p.hostname, 'port': p.port or 443, 'uuid': p.username, 'password': q.get('password'), 'sni': q.get('sni', [p.hostname])[0]}

    def generate_sip002_link(self, proxy: Dict[str, Any], encoded_name: str) -> str:
        try:
            uinfo = base64.urlsafe_b64encode(f"{proxy['cipher']}:{proxy['password']}".encode()).decode().rstrip('=')
            return f"ss://{uinfo}@{proxy['server']}:{proxy['port']}#{encoded_name}"
        except: return None

    # اسکن هوشمند: دقیقاً فقط ۲ پست آخر ویتوری + تفکیک پروکسی‌های تلگرام
    async def fetch_web_channel(self, channel: str):
        channel_name = channel.replace('@', '').strip()
        if not channel_name: return
        url = f"https://t.me/s/{channel_name}"
        logger.info(f"Target scan: {channel_name}...")

        def _fetch():
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req, timeout=12) as resp:
                    raw_content = resp.read().decode('utf-8', errors='ignore')
                    return html.unescape(raw_content)
            except Exception as e:
                logger.warning(f"Failed to fetch {channel_name}: {e}")
                return ""

        content = await asyncio.to_thread(_fetch)
        if not content: return

        posts = re.split(r'<div class="tgme_widget_message_wrap', content)
        posts.reverse() # اسکن از جدیدترین پست به قدیم

        now = datetime.datetime.now()
        v2ray_posts_collected = 0

        for post in posts:
            if v2ray_posts_collected >= 2: break

            post_lower = post.lower()
            if any(ad in post_lower for ad in ['#تبلیغ', '#ads', 'رزرو تبلیغ', 'تعرفه تبلیغات', 'ادمین تبلیغات']):
                continue

            # جمع‌آوری پروکسی‌های تلگرام
            for tg_match in TG_PROXY_PATTERN.findall(post):
                self.tg_proxies.add(tg_match.strip().rstrip('.,;!؟()[]{}<>"\''))

            # استخراج کانفیگ‌های ویتوری
            post_configs = set()
            texts = [post]
            for b64 in BASE64_PATTERN.findall(post):
                try:
                    texts.append(base64.b64decode(b64 + '=' * 4).decode('utf-8', errors='ignore'))
                except: pass

            for t in texts:
                for pattern in V2RAY_PATTERNS:
                    for match in pattern.findall(t):
                        clean_u = match.strip().rstrip('.,;!؟()[]{}<>"\'')
                        if not clean_u.startswith('vmess://') and '#' in clean_u:
                            clean_u = clean_u.split('#')[0]
                        post_configs.add(clean_u)

            if post_configs:
                self.raw_configs.update(post_configs)
                for u in post_configs:
                    if u not in self.raw_config_times:
                        self.raw_config_times[u] = now
                v2ray_posts_collected += 1
                logger.info(f"[{channel_name}] Post #{v2ray_posts_collected}: Extracted {len(post_configs)} valid configs.")

    # قانون ثابت: اصل اول
    def format_config_name(self, flag: str, country: str, city: str, ping_ms: int, capability: str) -> str:
        return (
            f"👉🆔@Goodbaye_filtering\n"
            f"📡{flag} {country}\n"
            f"®️{city}\n"
            f"🅿️ping:{ping_ms}ms\n"
            f"⚡{capability}"
        )

    def handle_weekly_file(self, new_configs: List[str]):
        now = datetime.datetime.now(); hist = {}
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f: hist = json.load(f)
            except: pass
        new_h = {k: v for k, v in hist.items() if datetime.datetime.fromisoformat(v['date']) > (now - datetime.timedelta(days=7))}
        for c in new_configs:
            base = c.split('#')[0]
            if base not in new_h:
                new_h[base] = {"link": c, "date": now.isoformat()}
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_h, f, indent=2, ensure_ascii=False)
        lns = [v['link'] for v in new_h.values()]
        with open(WEEKLY_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(sorted(lns)))

    def handle_no_cf_retention(self, new_configs: List[str]):
        now = datetime.datetime.now(); hist = {}
        if os.path.exists(NO_CF_HISTORY_FILE):
            try:
                with open(NO_CF_HISTORY_FILE, 'r', encoding='utf-8') as f: hist = json.load(f)
            except: pass
        new_h = {k: v for k, v in hist.items() if datetime.datetime.fromisoformat(v['date']) > (now - datetime.timedelta(hours=72))}
        for c in new_configs:
            p = self.parse_config_for_clash(c)
            if p:
                uid = str(p.get('uuid') or p.get('password') or c.split('#')[0])
                if uid not in new_h:
                    new_h[uid] = {"link": c, "date": now.isoformat()}
        with open(NO_CF_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_h, f, indent=2, ensure_ascii=False)
        lns = [v['link'] for v in new_h.values()]
        with open(OUTPUT_NO_CF, 'w', encoding='utf-8') as f:
            f.write("\n".join(sorted(lns)))

    def handle_country_retention(self, country_dict: Dict[str, List[str]]):
        os.makedirs('regions', exist_ok=True)
        TARGET_COUNTRIES = ['US', 'UK', 'NL', 'FR', 'DE', 'FI', 'TR', 'SG', 'JP', 'CA', 'PL'] 
        HISTORY_FILE_REGION = "regions/country_history.json"
        now = datetime.datetime.now(); hist = {}
        if os.path.exists(HISTORY_FILE_REGION):
            try:
                with open(HISTORY_FILE_REGION, 'r', encoding='utf-8') as f: hist = json.load(f)
            except: pass
            
        new_hist = {}
        for iso, configs in hist.items():
            new_hist[iso] = {}
            for base, data in configs.items():
                if datetime.datetime.fromisoformat(data['date']) > (now - datetime.timedelta(days=2)):
                    new_hist[iso][base] = data

        for iso, links in country_dict.items():
            if iso not in TARGET_COUNTRIES: continue
            if iso not in new_hist: new_hist[iso] = {}
            for link in links:
                base = link.split('#')[0]
                if base not in new_hist[iso]:
                    new_hist[iso][base] = {"link": link, "date": now.isoformat()}
                    
        with open(HISTORY_FILE_REGION, 'w', encoding='utf-8') as f:
            json.dump(new_hist, f, indent=2, ensure_ascii=False)
            
        for iso, configs in new_hist.items():
            final_links = [v['link'] for v in configs.values()]
            if final_links:
                with open(f"regions/conf-{iso}.txt", 'w', encoding='utf-8') as f:
                    f.write("\n".join(sorted(final_links)))

    def build_pro_config(self, proxies):
        clean_p, clean_n, seen = [], [], set()
        for p in proxies:
            srv = p.get('server', '').lower()
            if not srv or len(srv) > 60: continue
            net = p.get('network', 'tcp')
            if net not in ['tcp', 'ws', 'grpc', 'h2']: p['network'] = 'tcp'
            
            name = p['name']; count = 1; orig = name
            while name in seen:
                name = f"{orig}_{count}"; count += 1
            p['name'] = name; seen.add(name)
            clean_p.append({k: v for k, v in p.items() if v is not None and v != ''})
            clean_n.append(name)

        if not clean_p: return {}

        return {
            'mixed-port': 7890, 'ipv6': True, 'allow-lan': False, 'tcp-concurrent': True,
            'log-level': 'warning', 'mode': 'rule', 'external-controller': '127.0.0.1:9090',
            'dns': {
                'enable': True, 'ipv6': True, 'listen': '127.0.0.1:1053', 'enhanced-mode': 'fake-ip',
                'fake-ip-range': '198.18.0.1/16', 'nameserver': ['https://8.8.8.8/dns-query#✅ Selector'],
                'proxy-server-nameserver': ['8.8.8.8#DIRECT'], 'direct-nameserver': ['8.8.8.8#DIRECT'],
                'nameserver-policy': {
                    'rule-set:openai': '178.22.122.100#DIRECT', 'rule-set:googleai': '178.22.122.100#DIRECT',
                    'rule-set:microsoft': '178.22.122.100#DIRECT', 'rule-set:ir': '8.8.8.8#DIRECT'
                }
            },
            'tun': {
                'enable': True, 'stack': 'mixed', 'auto-route': True, 'strict-route': True,
                'auto-detect-interface': True, 'dns-hijack': ['any:53', 'tcp://any:53'], 'mtu': 9000
            },
            'sniffer': {
                'enable': True, 'force-dns-mapping': True, 'parse-pure-ip': True, 'override-destination': True,
                'sniff': {
                    'HTTP': {'ports': [80, 8080, 8880, 2052, 2082, 2086, 2095]},
                    'TLS': {'ports': [443, 8443, 2053, 2083, 2087, 2096]}
                }
            },
            'proxies': clean_p,
            'proxy-groups': [
                {'name': '✅ Selector', 'type': 'select', 'proxies': ['💥 Best Ping 🚀', 'DIRECT', *clean_n]},
                {'name': '💥 Best Ping 🚀', 'type': 'url-test', 'proxies': clean_n, 'url': 'https://www.gstatic.com/generate_204', 'interval': 30, 'tolerance': 50}
            ],
            'rule-providers': {
                'ir': {'type': 'http', 'behavior': 'domain', 'format': 'text', 'url': "https://raw.githubusercontent.com/Chocolate4U/Iran-clash-rules/release/ir.txt", 'path': './ruleset/ir.txt', 'interval': 86400},
                'ir-cidr': {'type': 'http', 'behavior': 'ipcidr', 'format': 'text', 'url': "https://raw.githubusercontent.com/Chocolate4U/Iran-clash-rules/release/ircidr.txt", 'path': './ruleset/ir-cidr.txt', 'interval': 86400},
                'openai': {'type': 'http', 'behavior': 'domain', 'format': 'yaml', 'url': "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/openai.yaml", 'path': './ruleset/openai.yaml', 'interval': 86400},
                'googleai': {'type': 'http', 'behavior': 'domain', 'format': 'yaml', 'url': "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/google-deepmind.yaml", 'path': './ruleset/googleai.yaml', 'interval': 86400},
                'microsoft': {'type': 'http', 'behavior': 'domain', 'format': 'yaml', 'url': "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/microsoft.yaml", 'path': './ruleset/microsoft.yaml', 'interval': 86400}
            },
            'rules': [
                'GEOIP,lan,DIRECT,no-resolve', 'NETWORK,udp,REJECT',
                'RULE-SET,ir,DIRECT', 'RULE-SET,openai,DIRECT', 'RULE-SET,googleai,DIRECT',
                'RULE-SET,microsoft,DIRECT', 'RULE-SET,ir-cidr,DIRECT', 'MATCH,✅ Selector'
            ]
        }

    def build_sing_box_config(self, proxies: List[Dict[str, Any]]) -> Dict[str, Any]:
        outbounds = []
        for p in proxies:
            sb_out = {'type': p['type'] if p['type'] != 'ss' else 'shadowsocks', 'tag': p['name'], 'server': p['server'], 'server_port': p['port']}
            if p['type'] == 'vmess':
                sb_out.update({'uuid': p['uuid'], 'alter_id': p['alterId'], 'security': p['cipher'], 'tls': {'enabled': True, 'server_name': p['servername']} if p.get('tls') else None})
            if p['type'] == 'vless':
                sb_out.update({'uuid': p['uuid'], 'flow': p.get('flow', ''), 'tls': {'enabled': True, 'server_name': p['servername'], 'reality': {'enabled': True, 'public_key': p.get('reality-opts', {}).get('public-key'), 'short_id': p.get('reality-opts', {}).get('short-id')} if p.get('reality-opts') else None} if p.get('tls') else None})
            if p['type'] == 'trojan':
                sb_out.update({'password': p['password'], 'tls': {'enabled': True, 'server_name': p.get('sni')}})
            if p['type'] == 'ss':
                sb_out.update({'method': p['cipher'], 'password': p['password']})
            if p['type'] in ['hysteria2', 'tuic']:
                sb_out.update({'password': p.get('password'), 'tls': {'enabled': True, 'server_name': p.get('sni'), 'insecure': p.get('skip-cert-verify')}})
            if p.get('ws-opts'):
                sb_out['transport'] = {'type': 'ws', 'path': p['ws-opts']['path'], 'headers': p['ws-opts']['headers']}
            outbounds.append(sb_out)
        tags = [o['tag'] for o in outbounds]
        return {
            "log": {"level": "warn"},
            "dns": {"servers": [{"tag": "dns_proxy", "address": "https://dns.google/dns-query", "detour": "PROXY"}, {"tag": "dns_direct", "address": "1.1.1.1"}], "rules": [{"outbound": "PROXY", "server": "dns_proxy"}, {"rule_set": ["geosite-ir", "geoip-ir"], "server": "dns_direct"}], "final": "dns_direct"},
            "inbounds": [{"type": "mixed", "listen": "0.0.0.0", "listen_port": 2080}],
            "outbounds": [{"type": "direct", "tag": "direct"}, {"type": "block", "tag": "block"}, {"type": "dns", "tag": "dns-out"}, *outbounds, {"type": "selector", "tag": "PROXY", "outbounds": ["auto", *tags]}, {"type": "urltest", "tag": "auto", "outbounds": tags, "url": "http://www.gstatic.com/generate_204", "interval": "5m"}],
            "route": {"rule_set": [{"tag": "geosite-ir", "type": "remote", "format": "binary", "url": "https://cdn.jsdelivr.net/gh/Chocolate4U/Iran-sing-box-rules@rule-set/geosite-ir.srs", "download_detour": "direct"}, {"tag": "geoip-ir", "type": "remote", "format": "binary", "url": "https://cdn.jsdelivr.net/gh/Chocolate4U/Iran-sing-box-rules@rule-set/geoip-ir.srs", "download_detour": "direct"}], "rules": [{"protocol": "dns", "outbound": "dns-out"}, {"rule_set": ["geosite-ir", "geoip-ir"], "outbound": "direct"}], "final": "PROXY"}
        }

    # قانون ثابت: اصل دوم و سوم (۴ دکمه شیشه‌ای رسمی)
    async def send_to_telegram(self, configs: List[str], pings: List[int]):
        if not BOT_TOKEN or not TARGET_CHAT_ID or not API_ID or not API_HASH:
            return

        tehran_tz = datetime.timezone(datetime.timedelta(hours=3, minutes=30))
        now_tehran = datetime.datetime.now(tehran_tz)
        tehran_time = now_tehran.strftime("%H:%M")
        jalali_date = gregorian_to_jalali(now_tehran.year, now_tehran.month, now_tehran.day)

        avg_ping = int(sum(pings) / len(pings)) if pings else 100
        quality_status = f"🟢 فوق‌العاده بالا (میانگین {avg_ping}ms)" if avg_ping < 200 else f"🟡 مطلوب ({avg_ping}ms)"

        caption_main = (
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📂 نام پکیج: پکیج اختصاصی تست‌شده و زنده\n"
            f"📄 شماره فایل: #1\n\n"
            f"📡 نوع اتصال: VLESS Reality | Hysteria2 | Trojan | VMess\n"
            f"📊 تعداد پروکسی‌های فعال: {len(configs)} عدد (سالم و متصل)\n\n"
            f"🕒 ساعت بروزرسانی: {tehran_time} (به وقت تهران)\n"
            f"📅 تاریخ: {jalali_date}\n\n"
            f"⚡️ کیفیت و پایداری: {quality_status}\n"
            f"🛡 آنتی‌فیلتر | سازگار با همراه اول، ایرانسل و مخابرات\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"👉🆔 @Goodbaye_filtering"
        )

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 کانال اصلی گودبای فیلترینگ", url="https://t.me/Goodbaye_filtering")],
            [InlineKeyboardButton("👑 کانال وی‌آی‌پی", url="https://t.me/CONFIG_V2RAY_VIP")],
            [InlineKeyboardButton("🌐 وب‌پنل آنلاین سابسکریپشن", url="https://alireza786786.github.io/Goodbaye_Collector/")],
            [InlineKeyboardButton("🚀 اشتراک‌گذاری با دوستان", url="https://t.me/share/url?url=https://t.me/Goodbaye_filtering")]
        ])

        try:
            bot = Client("goodbaye_bot_pub", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
            async with bot:
                chat_dest = int(TARGET_CHAT_ID) if TARGET_CHAT_ID.lstrip("-").isdigit() else TARGET_CHAT_ID
                if os.path.exists(OUTPUT_TXT):
                    await bot.send_document(
                        chat_id=chat_dest,
                        document=OUTPUT_TXT,
                        caption=caption_main,
                        reply_markup=buttons
                    )
                logger.info("Clean file successfully sent to Telegram channel!")
        except Exception as e:
            logger.error(f"Error publishing to Telegram: {e}")

    def save_split_chunks(self, configs: List[str], chunk_size: int = 500):
        os.makedirs("sub/split/normal", exist_ok=True)
        os.makedirs("sub/split/base64", exist_ok=True)
        chunks = [configs[i:i + chunk_size] for i in range(0, len(configs), chunk_size)]
        for idx, chunk in enumerate(chunks, 1):
            content = "\n".join(chunk)
            with open(f"sub/split/normal/{idx}.txt", "w", encoding="utf-8") as f:
                f.write(content)
            with open(f"sub/split/base64/{idx}.txt", "w", encoding="utf-8") as f:
                f.write(base64.b64encode(content.encode("utf-8")).decode("utf-8"))

    async def save_files(self):
        if not self.raw_configs:
            logger.warning("No configs found to save.")
            return

        valid_u = set()
        for u in self.raw_configs:
            try:
                p = urlparse(u)
                if p.hostname in ['127.0.0.1', 'localhost', '0.0.0.0']: continue
                valid_u.add(u)
            except: continue

        p_list, ren_txt, clean_ip, light_txt = [], [], [], []
        pings = []
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        light_cutoff = now_utc - datetime.timedelta(hours=LIGHT_MAX_AGE_HOURS)
        country_links = {}

        logger.info(f"Pinging and validating {len(valid_u)} configurations...")

        for u in sorted(list(valid_u)):
            proxy = self.parse_config_for_clash(u)
            if not proxy: continue
            srv = proxy.get('server')
            port = proxy.get('port')
            if not srv or not port or srv in ['127.0.0.1', 'localhost', '0.0.0.0']: continue

            fp = f"{proxy.get('type')}_{srv}:{port}_{proxy.get('uuid') or proxy.get('password')}"
            if fp in self.fingerprints: continue
            self.fingerprints.add(fp)

            alive, ping_ms = await measure_ping(srv, port)
            if not alive: continue

            pings.append(ping_ms)
            fallback_sni = proxy.get('servername') or proxy.get('sni') or ""
            iso, flag, country_name, city = await self.get_geo_info(srv, fallback_sni)
            cap = detect_capability(proxy.get('type'), proxy.get('ws-opts') or {}, proxy.get('network', 'tcp'))

            # قانون ثابت: اصل اول
            custom_name = self.format_config_name(flag, country_name, city, ping_ms, cap)
            proxy['name'] = f"{iso} 💥Goodbaye-{len(p_list)+1:02d}"
            p_list.append(proxy)

            # انکود کامل و تک‌خطی ماندن در فایل متنی
            encoded_name = quote(custom_name, safe='')

            if proxy['type'] == 'vmess':
                try:
                    b64_raw = u[8:].strip()
                    b64_raw += "=" * (-len(b64_raw) % 4)
                    c_json = json.loads(base64.urlsafe_b64decode(b64_raw).decode('utf-8', errors='ignore'))
                    c_json['ps'] = custom_name
                    new_b64 = base64.b64encode(json.dumps(c_json, ensure_ascii=False).encode('utf-8')).decode('utf-8')
                    final = f"vmess://{new_b64}"
                except:
                    final = f"{u.split('#')[0]}#{encoded_name}"
            elif proxy['type'] == 'ss':
                cp = proxy.copy()
                final = self.generate_sip002_link(cp, encoded_name) or f"{u.split('#')[0]}#{encoded_name}"
            else:
                base_u = u.split('#')[0]
                final = f"{base_u}#{encoded_name}"

            clean_final = final.replace('\r', '').replace('\n', '')
            ren_txt.append(clean_final)

            msg_date = self.raw_config_times.get(u)
            if msg_date:
                msg_utc = msg_date if msg_date.tzinfo else msg_date.replace(tzinfo=datetime.timezone.utc)
                if msg_utc > light_cutoff:
                    light_txt.append(clean_final)

            if is_clean_ip(srv):
                clean_ip.append(clean_final)
                if iso and iso != "N/A":
                    if iso == 'GB': iso = 'UK'
                    if iso not in country_links: country_links[iso] = []
                    country_links[iso].append(clean_final)

        # تولید لیست‌های هوشمند پینگ ایران و اینترنت آزاد
        iran_ping_configs = []
        open_internet_configs = []
        for iso_code in IRAN_PING_PRIORITY:
            if iso_code in country_links:
                iran_ping_configs.extend(country_links[iso_code][:50])

        for iso_code in OPEN_INTERNET_PRIORITY:
            if iso_code in country_links:
                open_internet_configs.extend(country_links[iso_code][:50])

        with open(IRAN_PING_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(iran_ping_configs))

        with open(OPEN_INTERNET_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(open_internet_configs))

        # تفکیک پروکسی‌های تلگرام برای وب‌پنل
        win_tg, and_tg = [], []
        for proxy_link in self.tg_proxies:
            sec_match = re.search(r"secret=([a-zA-Z0-9%_\-]+)", proxy_link)
            if sec_match:
                s = sec_match.group(1).lower()
                if not any(c in s for c in ['%', '_', '-']) and not s.startswith('ee'):
                    win_tg.append(proxy_link)
                else:
                    and_tg.append(proxy_link)
            else:
                and_tg.append(proxy_link)

        with open(TG_PROXIES_FILE, "w", encoding="utf-8") as f: f.write("\n".join(self.tg_proxies))
        with open(TG_WINDOWS_FILE, "w", encoding="utf-8") as f: f.write("\n".join(win_tg))
        with open(TG_ANDROID_FILE, "w", encoding="utf-8") as f: f.write("\n".join(and_tg))

        # ذخیره فایل‌ها به صورت تک‌خطی و استاندارد
        with open(OUTPUT_ORIGINAL_CONFIGS, 'w', encoding='utf-8') as f:
            f.write("\n".join(sorted(list(self.raw_configs))))
        with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
            f.write("\n".join(ren_txt))
        with open(OUTPUT_LIGHT, 'w', encoding='utf-8') as f:
            f.write("\n".join(light_txt))

        # تقسیم به پارت‌های ۵۰۰ تایی
        self.save_split_chunks(ren_txt, 500)

        self.handle_no_cf_retention(clean_ip)
        self.handle_weekly_file(ren_txt)
        self.handle_country_retention(country_links)

        os.makedirs('ruleset', exist_ok=True)
        if p_list:
            c_cfg = self.build_pro_config(p_list)
            if c_cfg:
                with open(OUTPUT_YAML_PRO, 'w', encoding='utf-8') as f:
                    yaml.dump(c_cfg, f, allow_unicode=True, sort_keys=False, indent=2)
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                json.dump(self.build_sing_box_config(p_list), f, ensure_ascii=False, indent=4)

        logger.info(f"Total Fresh & Clean Configs Saved: {len(ren_txt)}")
        await self.send_to_telegram(ren_txt, pings)

async def main():
    logger.info("Starting Goodbaye Extractor...")
    load_ip_data()
    load_blocked_ips()
    ext = GoodbayeExtractor()

    ch_list = [ch.strip() for ch in CHANNELS_STR.split(',')] if CHANNELS_STR else []
    tasks = [ext.fetch_web_channel(ch) for ch in ch_list if ch]
    if tasks:
        await asyncio.gather(*tasks)

    await ext.save_files()

if __name__ == "__main__":
    asyncio.run(main())
