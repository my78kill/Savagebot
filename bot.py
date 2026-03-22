import telebot
import random
import time
import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, DELETE_TIME, WARN_DELETE, BOT_USERNAME

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")


# 📂 reply loader
def get_reply(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return random.choice(f.readlines()).strip()
    except:
        return None


# 🔍 ADMIN CHECK
def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False


# 🚀 START COMMAND (DM)
@bot.message_handler(commands=['start'])
def start_msg(m):
    user = m.from_user
    name = user.first_name

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            "➕ Add Me To Group",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
        )
    )

    msg = f"""
👋 Hello {name},

Welcome to *Savage Chat Bot* 😈

I’m designed to keep your group active and entertaining with a touch of chaos.

━━━━━━━━━━━━━━━
🔥 Features:
• Smart savage replies  
• Reply-on-reply targeting  
• No mercy (admins included)  
• Edited message detection  
━━━━━━━━━━━━━━━

⚠️ Important:
• Edit your message → it may be deleted ⏳  
• Try to act smart → expect a smarter reply  
• Keep chatting → I’ll keep roasting  

🚀 Add me to your group and enjoy the madness.

Stay sharp.
"""

    bot.send_message(m.chat.id, msg, reply_markup=markup)


# 🔥 SAVAGE SYSTEM
@bot.message_handler(func=lambda m: True)
def savage(m):
    if not m.text:
        return

    text = m.text.lower()
    user = m.from_user
    mention = f"[{user.first_name}](tg://user?id={user.id})"

    # 🎯 reply target
    if m.reply_to_message:
        target = m.reply_to_message.from_user
        target_mention = f"[{target.first_name}](tg://user?id={target.id})"
        target_id = target.id
    else:
        target_mention = mention
        target_id = user.id

    # 🔍 admin check first (highest priority 💀)
    if is_admin(m.chat.id, target_id):
        r = get_reply("replies/admin.txt")

    # 👋 hello trigger
    elif "hello" in text:
        r = get_reply("replies/hello.txt")

    # 💀 abuse trigger
    elif any(x in text for x in ["bc", "mc", "noob", "idiot", "stupid", "gawar"]):
        r = get_reply("replies/abuse.txt")

    # 🎲 default
    else:
        r = get_reply("replies/random.txt")

    if r:
        bot.reply_to(m, f"{target_mention} {r}")


# ⚠️ EDIT MESSAGE HANDLER (SAFE)
@bot.edited_message_handler(func=lambda m: True)
def handle_edit(m):
    if not m.text:
        return

    # ❌ ignore inline / whisper messages
    if m.via_bot:
        return

    user = m.from_user
    mention = f"[{user.first_name}](tg://user?id={user.id})"

    warn = bot.reply_to(
        m,
        f"{mention}, your message will be deleted in 30 minutes 🙂‍↔️"
    )

    # ⏱ background task
    def delete_flow():
        time.sleep(WARN_DELETE)
        try:
            bot.delete_message(m.chat.id, warn.message_id)
        except:
            pass

        time.sleep(DELETE_TIME)
        try:
            bot.delete_message(m.chat.id, m.message_id)
        except:
            pass

    threading.Thread(target=delete_flow).start()


print("Bot Running 😈🔥")
bot.infinity_polling()
