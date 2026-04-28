import telebot
import requests
import random
import string
from telebot import types

# --- ТОХИРГОО ---
BOT_TOKEN = "8600496134:AAHTeOXj_BBuUb40Cd_Tz-zRwGU1LayKCoM"
FIREBASE_URL = "https://kayzen-1ff37-default-rtdb.firebaseio.com/users"
CHANNEL_ID = "@BALDANSHOP_CHANNEL"
CHANNEL_LINK = "https://t.me/BALDANSHOP_CHANNEL"
GITHUB_LINK = "https://github.com/SEREKBOL/Baldan.git"

bot = telebot.TeleBot(BOT_TOKEN)

# 1. Түлхүүр үүсгэх
def generate_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# 2. Суваг шалгах
def is_joined(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# 3. Firebase бүртгэл
def get_or_register(chat_id):
    user_url = f"{FIREBASE_URL}/{chat_id}.json"
    try:
        res = requests.get(user_url).json()
        if res: return res
        new_user = {
            "key": generate_key(),
            "balance": 300,
            "telegram_id": str(chat_id),
            "is_blocked": False,
            "is_unlimited": False
        }
        requests.put(user_url, json=new_user)
        return new_user
    except: return None

# --- БАЛАНС ФОРМАТЛАХ ФУНКЦ (АЛДАА ЗАСАХ ГОЛ ХЭСЭГ) ---
def get_balance_display(u):
    # Хэрэв is_unlimited: True бол шууд Unlimited гэж харуулна
    if u.get('is_unlimited', False):
        return "Unlimited ♾️"

    bal = u.get('balance', 0)

    # Хэрэв баазад 'Unlimited' гэж текстээр хадгалагдсан бол алдаа заахгүй харуулна
    try:
        return f"{int(bal):,}"
    except (ValueError, TypeError):
        return str(bal)

# 4. Төхөөрөмжийн товчлуурууд
def device_buttons():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_termux = types.InlineKeyboardButton("📲 TERMUX", callback_data="get_termux")
    btn_ios = types.InlineKeyboardButton("ISH SHELL 📳", callback_data="get_ios")
    markup.add(btn_termux, btn_ios)
    return markup

# --- КОМАНДУУД ---

@bot.message_handler(commands=['start'])
def start_cmd(message):
    if not is_joined(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK))
        bot.send_message(message.chat.id, "❗ Please join our channel first!", reply_markup=markup)
        return

    u = get_or_register(message.chat.id)
    if u:
        bal_display = get_balance_display(u)
        msg = (f"┌ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <b>Baldanshop</b>!\n"
               f"└We're excited to have you on board\n\n"
               f"┌🆔 ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ: <code>{message.chat.id}</code>\n"
               f"├🔑 ᴀᴄᴄᴇꜱꜱ ᴋᴇʏ: <tg-spoiler><code>{u['key']}</code></tg-spoiler>\n"
               f"└💰 ʙᴀʟᴀɴᴄᴇ: <code>{bal_display}</code>\n\n"
               f"🚀 Enjoy your experience!!")
        bot.send_message(message.chat.id, msg, parse_mode="HTML")

@bot.message_handler(commands=['balance'])
def balance_cmd(message):
    if not is_joined(message.from_user.id): return
    u = get_or_register(message.chat.id)
    if u:
        blocked_status = "Yes ☠️" if u.get('is_blocked') else "No 🚫"
        bal_display = get_balance_display(u)

        msg = (
            "💼 <b>𝗔𝗰𝗰𝗼𝘂𝗻𝘁 𝗕𝗮𝗹𝗮𝗻𝗰е 𝗜𝗻𝗳𝗼𝗿𝗺𝗮𝘁𝗶𝗼н</b>\n\n"
            f"🆔 ┌ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ: <code>{message.chat.id}</code>\n"
            f"💰 ├ʙᴀʟᴀɴᴄᴇ: <code>{bal_display}</code>\n"
            f"🚫 └ʙʟᴏᴄᴋᴇᴅ: {blocked_status}"
        )
        bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_markup=device_buttons())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "get_termux":
        code = f"apt update && apt upgrade -y && pkg install python git -y && pip install requests rich pystyle aiohttp && git clone {GITHUB_LINK} && cd Baldan && python main.py"
        bot.send_message(call.message.chat.id, f"🚀 **TERMUX CODE:**\n\n<code>{code}</code>", parse_mode="HTML")
    elif call.data == "get_ios":
        code = f"apk update && apk add python3 py3-pip git && pip install requests rich pystyle aiohttp && git clone {GITHUB_LINK} && cd Baldan && python3 main.py"
        bot.send_message(call.message.chat.id, f"🍎 **iOS iSH CODE:**\n\n<code>{code}</code>", parse_mode="HTML")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text and m.text.lower() == 'balance')
def text_balance(message):
    balance_cmd(message)

print("Бот амжилттай засагдаж ажиллаж байна...")
bot.infinity_polling()


