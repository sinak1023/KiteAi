import aiohttp
import aiofiles
import asyncio
import json
import random
import datetime
from aiohttp_socks import ProxyConnector

RESET = "\033[0m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"

# 🔥 Aliens_web3 Banner
BANNER = f"""
{YELLOW}█████╗ ██╗     ██╗███████╗███████╗███╗   ██╗███████╗██╗    ██╗██████╗ ██████╗ ██████╗ 
██╔══██╗██║     ██║██╔════╝██╔════╝████╗  ██║██╔════╝██║    ██║██╔══██╗██╔══██╗██╔══██╗
███████║██║     ██║███████╗█████╗  ██╔██╗ ██║███████╗██║ █╗ ██║██████╔╝██████╔╝██████╔╝
██╔══██║██║     ██║╚════██║██╔══╝  ██║╚██╗██║╚════██║██║███╗██║██╔═══╝ ██╔═══╝ ██╔═══╝ 
██║  ██║███████╗██║███████║███████╗██║ ╚████║███████║╚███╔███╔╝██║     ██║     ██║     
╚═╝  ╚═╝╚══════╝╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝ ╚═╝     ╚═╝     ╚═╝     
                         🚀 {MAGENTA}Aliens_web3{RESET} 🚀
"""


MAX_DAILY_POINTS = 200
POINTS_PER_INTERACTION = 10
MAX_DAILY_INTERACTIONS = MAX_DAILY_POINTS // POINTS_PER_INTERACTION

# API‌های AI
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
        print(f"{YELLOW}[INFO] No {filename} found.{RESET}")
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
        self.log("📊", f"{CYAN}Current Statistics{RESET}")
        self.log("💰", f"Total Points: {GREEN}{self.daily_points}{RESET}")
        self.log("⏳", f"Next Reset: {YELLOW}{self.next_reset_time.strftime('%Y-%m-%d %H:%M:%S')}{RESET}")

    def log(self, emoji, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session_prefix = f"{BLUE}[Session {self.session_id}]{RESET}"
        wallet_prefix = f"{GREEN}[{self.wallet_address[:6]}...]{RESET}"
        print(f"{YELLOW}[{timestamp}]{RESET} {session_prefix} {wallet_prefix} {emoji} {message}")

class KiteAIAutomation:
    def __init__(self, wallet_address, proxy_list, session_id):
        self.session = WalletSession(wallet_address, session_id)
        self.proxy_list = proxy_list
        self.is_running = True

    async def send_ai_query(self, session, endpoint, message):
        url = f"{endpoint}"
        headers = {
            "Accept": "text/event-stream",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        data = {"message": message, "stream": True}

        try:
            async with session.post(url, json=data, headers=headers, timeout=30) as response:
                if response.status != 200:
                    self.session.log("❌", f"API Error: {response.status}")
                    return ""

                result = ""
                async for line in response.content:
                    decoded_line = line.decode("utf-8").strip()
                    if decoded_line.startswith("data: "):
                        json_data = decoded_line[6:]
                        if json_data == "[DONE]":
                            break
                        try:
                            parsed_data = json.loads(json_data)
                            content = parsed_data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if content:
                                result += content
                                print(content, end="", flush=True)
                        except json.JSONDecodeError:
                            continue

                print("\n")
                return result.strip()

        except asyncio.TimeoutError:
            self.session.log("⏳", "Timeout Error: AI server took too long to respond.")
            return ""
        except Exception as e:
            self.session.log("❌", f"AI Query Error: {e}")
            return ""

    async def run(self):
        self.session.log("🚀", "Initializing Kite AI Auto-Interaction System")
        self.session.log("💼", f"Wallet: {self.session.wallet_address}")
        self.session.log("🎯", f"Daily Target: {MAX_DAILY_POINTS} points ({MAX_DAILY_INTERACTIONS} interactions)")
        self.session.log("⏰", f"Next Reset: {self.session.next_reset_time.strftime('%Y-%m-%d %H:%M:%S')}")

        while self.is_running:
            self.session.reset_points_if_needed()
            if self.session.daily_points >= MAX_DAILY_POINTS:
                self.session.log("🎯", "Max daily points reached. Waiting for reset...")
                await asyncio.sleep(60)
                continue

            async with aiohttp.ClientSession() as session:
                await self.send_ai_query(session, random.choice(list(AI_ENDPOINTS.keys())), random.choice(AI_ENDPOINTS["https://deployment-uu9y1z4z85rapgwkss1muuiz.stag-vxzy.zettablock.com/main"]["questions"]))

async def main():
    print(BANNER)
    wallets = await load_file("wallets.txt")
    proxies = await load_file("proxies.txt")

    print(f"{CYAN}📊 Loaded {len(wallets)} wallets and {len(proxies)} proxies{RESET}")

    tasks = [KiteAIAutomation(wallet, proxies, i + 1).run() for i, wallet in enumerate(wallets)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
