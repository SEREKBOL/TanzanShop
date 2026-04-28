import os
import requests
import json
import time
import sys
import asyncio
import aiohttp
import copy
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from pystyle import Colors, Colorate

# ==========================================
# 1. ТОХИРГОО
# ==========================================
FB_KEY = "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM"
BASE_API_URL = "https://europe-west1-cp-multiplayer.cloudfunctions.net"
FIREBASE_URL = "https://kayzen-1ff37-default-rtdb.firebaseio.com/users"
ADMIN_KEY = "Telmunn69"
LOCAL_DB = "TarganJack.json"

console = Console()

# ҮНЭ ТАРИФ (19 ҮЙЛЧИЛГЭЭ)
PRICES = {
    1: 1500, 2: 4500, 3: 8000, 4: 4500, 5: 100,
    6: 0,    7: 4000, 8: 4000, 9: 3000, 10: 3000,
    11: 4000, 12: 4000, 13: 4000, 14: 2000, 15: 3000,
    16: 1000, 17: 1000, 18: 2000, 19: 2000
}

# --- DATA MANAGEMENT ---
def load_all_local_data():
    if os.path.exists(LOCAL_DB):
        try:
            with open(LOCAL_DB, 'r') as f:
                content = f.read()
                return json.loads(content) if content else {}
        except: return {}
    return {}

def save_to_local(email, data):
    all_data = load_all_local_data()
    all_data[email] = data
    with open(LOCAL_DB, 'w') as f:
        json.dump(all_data, f, indent=4)

# ==========================================
# 2. CPM NUKER КЛАСС
# ==========================================
class CPMNuker:
    def __init__(self, auth_token=None):
        self.auth_token = auth_token

    async def login(self, email, password):
        url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={FB_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, timeout=20) as response:
                    res = await response.json()
                    if "idToken" in res:
                        self.auth_token = res["idToken"]
                        return {"ok": True}
                    return {"ok": False, "message": "LOGIN FAIL"}
            except: return {"ok": False, "message": "CONNECTION ERROR"}

    async def push_data(self, player_data):
        url = f"{BASE_API_URL}/SavePlayerRecordsIOS1"
        payload = {"data": json.dumps([player_data])}
        headers = {"Authorization": f"Bearer {self.auth_token}", "Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, headers=headers) as response:
                    res = await response.json()
                    return res.get("result") == "{\"result\":1}"
            except: return False

# ==========================================
# 3. UI ФУНКЦҮҮД (ТЭГШЛЭЛТТЭЙ)
# ==========================================
def banner():
    os.system('clear')
    print(Colorate.Horizontal(Colors.rainbow, "="*60))
    print(Colorate.Horizontal(Colors.rainbow, "Car Parking Multiplayer Tool".center(60)))
    print(Colorate.Horizontal(Colors.rainbow, "="*60))

async def get_location_details():
    try:
        # Тэгшлэх зай
        W = 20
        async with aiohttp.ClientSession() as session:
            async with session.get("http://ip-api.com/json") as res:
                data = await res.json()
                print(Colorate.Horizontal(Colors.rainbow, '==========[ LOCATION DETAILS ]=========='))
                print(f"  >> {'Ip Address'.ljust(W)} : {data.get('query')}")
                print(f"  >> {'Location'.ljust(W)} : {data.get('city')} {data.get('regionName')}")
                print(f"  >> {'Country'.ljust(W)} : {data.get('country')}")
    except: pass

def show_info(email, key, tg_id, bal, is_vip, data):
    # Тэгшлэх зай
    W = 20

    # PLAYER DETAILS
    print(Colorate.Horizontal(Colors.rainbow, '==========[ PLAYER DETAILS ]=========='))
    print(f"  >> {'Name'.ljust(W)} : {data.get('Name', 'cool')}")
    print(f"  >> {'LocaLID'.ljust(W)} : {data.get('localID', 'DEFAULT_ID')}")
    print(f"  >> {'Moneys'.ljust(W)} : {int(data.get('money', 0)):,}")
    print(f"  >> {'Coins'.ljust(W)} : {int(data.get('coin', 0)):,}")
    print(f"  >> {'Car count'.ljust(W)} : 220")

    # ACCESS KEY DETAILS
    print(Colorate.Horizontal(Colors.rainbow, '==========[ ACCESS KEY DETAILS ]=========='))
    print(f"  >> {'TELEGRAM ID'.ljust(W)} : {tg_id}")
    print(f"  >> {'ACCESS KEY'.ljust(W)} : {key}")
    print(f"  >> {'BALANCE'.ljust(W)} : {'unlimited' if is_vip else f'{bal:,} ₮'}")

# ==========================================
# 4. ҮНДСЭН ПРОГРАМ
# ==========================================
async def main():
    nuker = CPMNuker()
    while True:
        banner()
        e = Prompt.ask("[?] Enter email")
        p = Prompt.ask("[?] Enter password")
        k = Prompt.ask("[?] Enter access key")

        # Firebase Verification
        try:
            db = requests.get(f"{FIREBASE_URL}.json", timeout=10).json() or {}
        except: print("DATABASE ERROR!"); time.sleep(2); continue

        user_ref, found_user = None, None
        is_vip = (k == ADMIN_KEY or k == "0615")
        if not is_vip:
            for uid, d in db.items():
                if str(d.get('key')) == str(k): user_ref, found_user = uid, d; break
            if not found_user or found_user.get('is_blocked'):
                print("INVALID KEY OR BLOCKED"); time.sleep(2); continue

        if found_user and found_user.get('is_unlimited'): is_vip = True

        print("[*] Logging in to CPM...")
        res = await nuker.login(e, p)
        if not res["ok"]: print(f"LOGIN FAILED: {res['message']}"); time.sleep(2); continue

        # Local Data Load
        all_local = load_all_local_data()
        current_data = all_local.get(e, {
            "localID": "DEFAULT_ID", "money": 25000, "Name": "cool", "coin": 0,
            "allData": "E80DFDD793B8A799EB3F10B6B7356B11EFDA02F7", "boughtFsos": [],
            "boughtPoliceSirens": [1], "integers": [0]*120, "floats": [0.0]*54,
            "LevelsDoneTime": [0]*110, "carIDnStatus": {"carStatus": [0]*250}
        })
        save_to_local(e, current_data)

        while True:
            banner()
            try:
                fb_db = requests.get(f"{FIREBASE_URL}.json").json() or {}
                bal = 999999 if is_vip else int(fb_db.get(user_ref, {}).get('balance', 0))
            except: bal = 0

            show_info(e, k, found_user.get('telegram_id', 'ADMIN') if not is_vip else 'ADMIN', bal, is_vip, current_data)
            await get_location_details()

            print(Colorate.Horizontal(Colors.rainbow, '===============[ MENU ]==============='))
            menu_items = [
                ("1. Increase money", "1.5k"), ("2. Increase coins", "4.5k"),
                ("3. Set rank", "8.0k"),       ("4. Id change", "4.5k"),
                ("5. Name change", "100"),     ("6. All levels done", "FREE"),
                ("7. Unlock w16", "4.0k"),     ("8. Unlock smoke", "4.0k"),
                ("9. Unlock damage off", "3.0k"), ("10. Unlimited fuel", "3.0k"),
                ("11. Unlock home3", "4.0k"),  ("12. Unlock wheels", "4.0k"),
                ("13. Unlock animations", "4.0k"), ("14. Unlock M clothes", "2.0k"),
                ("15. Unlock F clothes", "3.0k"), ("16. Change race wins", "1.0k"),
                ("17. Change race loses", "1.0k"), ("18. Change password", "2.0k"),
                ("19. Change email", "2.0k"),    ("0. Exit", "")
            ]

            for item, price in menu_items:
                if item == "0. Exit": print(Colorate.Horizontal(Colors.rainbow, item))
                else: print(Colorate.Horizontal(Colors.rainbow, f"{item.ljust(40)} {price}"))
            print(Colorate.Horizontal(Colors.rainbow, '===============[ Jack ]==============='))

            choice = IntPrompt.ask("\n[?] Select")
            if choice == 0: sys.exit()

            cost = PRICES.get(choice, 0)
            if bal >= cost:
                msg = ""
                # Logic for each choice... (Мөнгө, Койн, Нэр солих гэх мэт)
                if choice == 1:
                    val = IntPrompt.ask("1. Your new money max 50M")
                    current_data["money"] = val; msg = "Money set successfully"
                elif choice == 5:
                    val = Prompt.ask("5. Your new name 1-100")
                    current_data["Name"] = val; msg = "Name changed successfully"
                # ... бусад үйлдлүүдийг энд нэмнэ ...

                print("[*] Syncing with server...")
                if await nuker.push_data(current_data):
                    save_to_local(e, current_data)
                    if not is_vip:
                        requests.patch(f"{FIREBASE_URL}/{user_ref}.json", json={"balance": bal - cost})
                    print(Colorate.Horizontal(Colors.green_to_white, f"√ {msg}"))
                else: print("FAILED TO SYNC")
                time.sleep(2)
            else: print("INSUFFICIENT BALANCE!"); time.sleep(2)

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: sys.exit()

