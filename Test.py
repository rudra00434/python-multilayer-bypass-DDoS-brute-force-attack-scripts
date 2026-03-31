import argparse
import socket
import ssl
import threading
import random
import sys
import time
import statistics
from collections import Counter

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
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 (Internal-Testing-ID-993)"
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36 (Internal-Testing-ID-994)"
    
]
# --- RANDOM REFERERS ---
REFERERS = [
    "https://www.google.com/",
    "https://www.facebook.com/",
    "https://t.co/", 
    "https://www.bing.com/",
    "https://duckduckgo.com/",
    "https://www.zeromove.in/shop",
    "https://www.linkedin.com/",
    "https://www.reddit.com/",
     "https://www.youtube.com/",
    "https://www.twitter.com/"
]


lock = threading.Lock()
stats = {
    'success': 0,
    'errors': 0,
    'latency_sum': 0.0,
    'latencies': [],
    'requests': 0,
    'connections': 0,
    'status': Counter(),
    'last_error': None,
}
stop_event = threading.Event()


def parse_args():
    parser = argparse.ArgumentParser(description='Simple HTTP/HTTPS load tester for your website')
    parser.add_argument('host', nargs='?', default='www.zeromove.in', help='Target host')
    parser.add_argument('--port', type=int, default=443, help='Target port (80 for HTTP, 443 for HTTPS)')
    parser.add_argument('--path', default='/', help='Request path')
    parser.add_argument('--threads', type=int, default=1000, help='Number of worker threads')
    parser.add_argument('--duration', type=int, default=70, help='Test duration in seconds')
    parser.add_argument('--timeout', type=float, default=10.0, help='Socket timeout in seconds')
    parser.add_argument('--keepalive', action='store_true', help='Use Connection: keep-alive instead of close')
    parser.add_argument('--requests-per-connection', type=int, default=1, help='Number of requests to send per connection')
    parser.add_argument('--strong', action='store_true', help='Use a stronger test mode with keep-alive and more requests per connection')
    return parser.parse_args()


def resolve_host(host):
    try:
        ip = socket.gethostbyname(host)
        print(f"[*] Resolved {host} to {ip}")
        return ip
    except socket.gaierror:
        print(f"[!] Error: Could not resolve hostname {host}")
        sys.exit(1)


def build_request(host, path, use_keepalive):
    connection_header = 'keep-alive' if use_keepalive else 'close'
    ua = random.choice(USER_AGENTS)
    return (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: {ua}\r\n"
        f"Connection: {connection_header}\r\n\r\n"
    ).encode('ascii')


def extract_status(response_bytes):
    if not response_bytes:
        return 'NO_RESPONSE'
    first_line = response_bytes.split(b'\r\n', 1)[0]
    try:
        return first_line.decode('utf-8', errors='replace')
    except Exception:
        return 'INVALID_STATUS'


def worker(target_ip, target_port, host, path, timeout, use_tls, request_bytes, duration, requests_per_connection):
    ssl_context = ssl.create_default_context() if use_tls else None
    deadline = time.perf_counter() + duration

    while not stop_event.is_set() and time.perf_counter() < deadline:
        sock = None
        try:
            sock = socket.create_connection((target_ip, target_port), timeout=timeout)
            sock.settimeout(timeout)
            if ssl_context is not None:
                sock = ssl_context.wrap_socket(sock, server_hostname=host)

            with lock:
                stats['connections'] += 1

            for _ in range(requests_per_connection):
                if stop_event.is_set() or time.perf_counter() >= deadline:
                    break

                req_start = time.perf_counter()
                sock.sendall(request_bytes)
                response = sock.recv(4096)
                latency = time.perf_counter() - req_start
                status = extract_status(response)

                with lock:
                    stats['success'] += 1
                    stats['requests'] += 1
                    stats['latency_sum'] += latency
                    stats['latencies'].append(latency)
                    stats['status'][status] += 1
        except Exception as exc:
            with lock:
                stats['errors'] += 1
                stats['requests'] += 1
                stats['last_error'] = str(exc)
        finally:
            if sock is not None:
                try:
                    sock.close()
                except Exception:
                    pass


def print_summary(elapsed=None):
    with lock:
        total = stats['requests']
        errors = stats['errors']
        success = stats['success']
        avg_latency = (stats['latency_sum'] / success) if success else 0.0
        latency_ms = [l * 1000 for l in stats['latencies']]
        p50 = statistics.median(latency_ms) if latency_ms else 0.0
        p90 = statistics.quantiles(latency_ms, n=100)[89] if len(latency_ms) >= 100 else p50
        p99 = statistics.quantiles(latency_ms, n=100)[98] if len(latency_ms) >= 100 else p90

        print('\n=== Load Test Summary ===')
        if elapsed is not None:
            print(f'Elapsed time: {elapsed:.1f}s')
        print(f'Total requests: {total}')
        print(f'Successful responses: {success}')
        print(f'Error responses: {errors}')
        print(f'Average latency (successful): {avg_latency * 1000:.1f} ms')
        print(f'Latency p50: {p50:.1f} ms')
        print(f'Latency p90: {p90:.1f} ms')
        print(f'Latency p99: {p99:.1f} ms')
        print(f'Total connections opened: {stats["connections"]}')
        print(f'Requests/sec: {total / elapsed:.1f}' if elapsed and elapsed > 0 else 'Requests/sec: N/A')
        if stats['status']:
            print('Status codes:')
            for status, count in stats['status'].most_common():
                print(f'  {status}: {count}')
        if stats['last_error']:
            print(f'Last error: {stats['last_error']}')


def main():
    args = parse_args()
    use_tls = args.port == 443
    target_ip = resolve_host(args.host)

    if args.strong:
        args.keepalive = True
        args.requests_per_connection = max(args.requests_per_connection, 5)
        args.threads = max(args.threads, 250)
        args.timeout = min(args.timeout, 5.0)
        print(f"[*] Strong mode enabled: threads={args.threads}, requests_per_connection={args.requests_per_connection}, timeout={args.timeout}s")

    request_bytes = build_request(args.host, args.path, args.keepalive)

    print(f"[*] Starting load test: {args.host}:{args.port}{args.path} with {args.threads} threads for {args.duration}s")
    print(f"[*] TLS: {'enabled' if use_tls else 'disabled'} | timeout: {args.timeout}s | keep-alive: {args.keepalive} | requests/connection: {args.requests_per_connection}")

    threads = []
    start_time = time.perf_counter()
    for _ in range(args.threads):
        thread = threading.Thread(
            target=worker,
            args=(target_ip, args.port, args.host, args.path, args.timeout, use_tls, request_bytes, args.duration, args.requests_per_connection),
            daemon=True,
        )
        thread.start()
        threads.append(thread)

    try:
        while time.perf_counter() - start_time < args.duration and not stop_event.is_set():
            time.sleep(1)
            with lock:
                total = stats['requests']
                print(f"[*] {total} requests sent so far", end='\r')
    except KeyboardInterrupt:
        stop_event.set()

    elapsed = time.perf_counter() - start_time
    try:
        for thread in threads:
            while thread.is_alive():
                thread.join(timeout=1)
                if stop_event.is_set():
                    break
    except KeyboardInterrupt:
        stop_event.set()
        print('\n[!] Interrupted during shutdown. Waiting for worker threads to stop...')
        for thread in threads:
            if thread.is_alive():
                thread.join(timeout=1)

    print_summary(elapsed)


if __name__ == '__main__':
    main()