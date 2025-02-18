import requests
import json
import time
import random
import datetime
import asyncio
import aiohttp
import aiofiles
from aiohttp_socks import ProxyConnector

# بنر
BANNER = """
█████╗ ██╗     ██╗███████╗███████╗███╗   ██╗███████╗██╗    ██╗██████╗ ██████╗ ██████╗ 
██╔══██╗██║     ██║██╔════╝██╔════╝████╗  ██║██╔════╝██║    ██║██╔══██╗██╔══██╗██╔══██╗
███████║██║     ██║███████╗█████╗  ██╔██╗ ██║███████╗██║ █╗ ██║██████╔╝██████╔╝██████╔╝
██╔══██║██║     ██║╚════██║██╔══╝  ██║╚██╗██║╚════██║██║███╗██║██╔═══╝ ██╔═══╝ ██╔═══╝ 
██║  ██║███████╗██║███████║███████╗██║ ╚████║███████║╚███╔███╔╝██║     ██║     ██║     
╚═╝  ╚═╝╚══════╝╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝ ╚═╝     ╚═╝     ╚═╝     
                         🚀 Aliens_web3 🚀
"""


MAX_DAILY_POINTS = 200
POINTS_PER_INTERACTION = 10
MAX_DAILY_INTERACTIONS = MAX_DAILY_POINTS // POINTS_PER_INTERACTION

AI_ENDPOINTS = {
    "https://deployment-uu9y1z4z85rapgwkss1muuiz.stag-vxzy.zettablock.com/main": {
        "agent_id": "deployment_UU9y1Z4Z85RAPGwkss1mUUiZ",
        "name": "Kite AI Assistant",
        "questions": [
            "Tell me about the latest updates in Kite AI",
            "How can Kite AI improve my development workflow?",
        ]
    }
}

async def load_file(filename):
    try:
        async with aiofiles.open(filename, mode='r', encoding='utf-8') as file:
            data = await file.read()
            return [line.strip() for line in data.split("\n") if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        print(f"[INFO] No {filename} found.")
        return []

class WalletSession:
    def __init__(self, wallet_address, session_id):
        self.wallet_address = wallet_address
        self.session_id = session_id
        self.daily_points = 0
        self.start_time = datetime.datetime.now()
        self.next_reset_time = self.start_time + datetime.timedelta(days=1)

    def update_points(self, success=True):
        if success:
            self.daily_points += POINTS_PER_INTERACTION

    def reset_points_if_needed(self):
        if datetime.datetime.now() >= self.next_reset_time:
            self.daily_points = 0
            self.next_reset_time = datetime.datetime.now() + datetime.timedelta(days=1)

    def print_statistics(self):
        print(f"\n📊 Session {self.session_id} - Wallet: {self.wallet_address}")
        print(f"💰 Total Points: {self.daily_points}")
        print(f"⏳ Next Reset: {self.next_reset_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

def get_random_proxy(proxy_list):
    if not proxy_list:
        return None
    return random.choice(proxy_list)

class KiteAIAutomation:
    def __init__(self, wallet_address, proxy_list, session_id):
        self.session = WalletSession(wallet_address, session_id)
        self.proxy_list = proxy_list
        self.is_running = True

    async def send_ai_query(self, session, endpoint, message):
        agent_id = AI_ENDPOINTS[endpoint]["agent_id"]
        url = f"{endpoint}"
        data = {"message": message, "stream": True}
        
        try:
            async with session.post(url, json=data) as response:
                result = await response.text()
                print(f"🤖 AI Response: {result}")
                return result.strip()
        except Exception as e:
            print(f"❌ AI Query Error: {e}")
            return ""

    async def report_usage(self, session, endpoint, message, response):
        url = "https://quests-usage-dev.prod.zettablock.com/api/report_usage"
        data = {
            "wallet_address": self.session.wallet_address,
            "agent_id": AI_ENDPOINTS[endpoint]["agent_id"],
            "request_text": message,
            "response_text": response
        }
        try:
            async with session.post(url, json=data) as res:
                return res.status == 200
        except Exception as e:
            print(f"❌ Reporting Error: {e}")
            return False

    async def run(self):
        print(f"🚀 Running session for wallet: {self.session.wallet_address}")

        while self.is_running:
            self.session.reset_points_if_needed()
            if self.session.daily_points >= MAX_DAILY_POINTS:
                print("🎯 Max daily points reached. Waiting for reset...")
                await asyncio.sleep(60)
                continue

            proxy = get_random_proxy(self.proxy_list)
            connector = ProxyConnector.from_url(proxy) if proxy else None

            async with aiohttp.ClientSession(connector=connector) as session:
                endpoint = random.choice(list(AI_ENDPOINTS.keys()))
                question = random.choice(AI_ENDPOINTS[endpoint]["questions"])
                print(f"🔑 Sending AI query: {question}")

                response = await self.send_ai_query(session, endpoint, question)
                success = await self.report_usage(session, endpoint, question, response)

                self.session.update_points(success)
                self.session.print_statistics()

                await asyncio.sleep(random.uniform(1, 3))

async def main():
    print(BANNER)

    wallets = await load_file("wallets.txt")
    proxies = await load_file("proxies.txt")

    print(f"📊 Loaded {len(wallets)} wallets and {len(proxies)} proxies")

    tasks = [KiteAIAutomation(wallet, proxies, i + 1).run() for i, wallet in enumerate(wallets)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Process terminated by user.")
