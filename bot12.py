import telebot
from telebot import types
import json

# ===== CONFIG =====
TOKEN = "8614886939:AAHU2WpAKbYNjfEl-pZmk2BDXpKWHebEX4M"  # BotFather token
ADMIN_ID = 123456789  # নিজের Telegram ID

CHANNEL1 = "@allcourse_ssc26_27_28"
CHANNEL2 = "@Free_Paid_Course01"

CHANNEL1_LINK = "https://t.me/+GuBHMBcQk7Y4YmVl"
CHANNEL2_LINK = "https://t.me/+7rJ8oU1vl-k1OGJl"

PRIVATE_LINK = "https://t.me/+r-jkkrvzUUc1ZTFl"
DB = "users.json"

bot = telebot.TeleBot(TOKEN)

# ===== DATABASE =====
def load():
    try:
        with open(DB,"r",encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save(data):
    with open(DB,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False)

users = load()

# ===== MENU =====
def menu():
    m = types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton("👤 প্রোফাইল",callback_data="profile"),
        types.InlineKeyboardButton("🏆 Leaderboard",callback_data="leader")
    )
    m.add(types.InlineKeyboardButton("🔗 রেফার করুন",callback_data="refer"))
    m.add(
        types.InlineKeyboardButton("📢 Channel 1 Join",url=CHANNEL1_LINK),
        types.InlineKeyboardButton("📢 Channel 2 Join",url=CHANNEL2_LINK)
    )
    m.add(types.InlineKeyboardButton("✅ Join Verify",callback_data="verify"))
    return m

# ===== START =====
@bot.message_handler(commands=['start'])
def auto_start(message):
    uid = str(message.from_user.id)
    name = message.from_user.first_name
    args = message.text.split()

    if uid not in users:
        users[uid] = {
            "name": name,
            "points": 0,
            "refs": [],
            "ref_by": None,
            "verified": False
        }
        save(users)

    # Referral detect
    if len(args) > 1:
        ref = args[1]
        if ref != uid and ref in users:
            users[uid]["ref_by"] = ref
            save(users)

    pts = users[uid]["points"]
    text = f"""
👋 Welcome to LEARNING TELEGRAM!

📊 Dashboard
Status: ✅ Active
Points: {pts}/3

🎁 3 রেফার = ফ্রি প্রিমিয়াম কোর্স
"""
    bot.send_message(message.chat.id,text,reply_markup=menu())

# ===== VERIFY JOIN =====
@bot.callback_query_handler(func=lambda call: call.data=="verify")
def verify(call):
    uid = str(call.from_user.id)
    try:
        s1 = bot.get_chat_member(CHANNEL1,uid).status
        s2 = bot.get_chat_member(CHANNEL2,uid).status

        if s1!="left" and s2!="left":
            if users[uid]["verified"]:
                bot.answer_callback_query(call.id,"⚠️ Already verified")
                return

            users[uid]["verified"]=True
            ref = users[uid]["ref_by"]

            if ref and ref in users:
                if uid not in users[ref]["refs"]:
                    users[ref]["refs"].append(uid)
                    users[ref]["points"] += 1

            save(users)
            bot.answer_callback_query(call.id,"✅ Join verified")

        else:
            bot.answer_callback_query(call.id,"❌ দুইটা চ্যানেল join করুন")
    except:
        bot.answer_callback_query(call.id,"❌ Error verifying")

# ===== PROFILE =====
@bot.callback_query_handler(func=lambda call: call.data=="profile")
def profile(call):
    uid = str(call.from_user.id)
    u = users[uid]
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 Back",callback_data="menu"))

    text = f"""
👤 প্রোফাইল

নাম: {u['name']}
🆔 ID: {uid}
✅ Status: Verified
💎 Your Balance: {u['points']} Points

🧾 My Courses:
আপনি এখনো কোনো কোর্স claim করেননি।
✅ কী করবেন:
• 3 রেফার পূর্ণ করে claim করুন
• 🔗 Invite Link শেয়ার করুন

💁‍♂️ Total Referrals: {len(u['refs'])}
"""
    if u["points"]>=3:
        text+=f"\n🎁 Private Channel Link:\n{PRIVATE_LINK}"

    try:
        bot.edit_message_text(text,call.message.chat.id,call.message.message_id,reply_markup=kb)
    except:
        pass

# ===== REFER =====
@bot.callback_query_handler(func=lambda call: call.data=="refer")
def refer(call):
    uid = str(call.from_user.id)
    link = f"https://t.me/{bot.get_me().username}?start={uid}"
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 Back",callback_data="menu"))
    text=f"""
🔗 Your Referral Link

{link}

বন্ধুদের invite করে পয়েন্ট অর্জন করুন!
"""
    try:
        bot.edit_message_text(text,call.message.chat.id,call.message.message_id,reply_markup=kb)
    except:
        pass

# ===== LEADERBOARD =====
@bot.callback_query_handler(func=lambda call: call.data=="leader")
def leader(call):
    sorted_users = sorted(users.items(),key=lambda x:x[1]["points"],reverse=True)
    text="🏆 Leaderboard (Top 10)\n\n"
    rank=1
    for uid,data in sorted_users[:10]:
        if data["points"]>0:
            text+=f"{rank}. {data['name']} - {data['points']} pts\n"
            rank+=1

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 Back",callback_data="menu"))
    try:
        bot.edit_message_text(text,call.message.chat.id,call.message.message_id,reply_markup=kb)
    except:
        pass

# ===== BACK MENU =====
@bot.callback_query_handler(func=lambda call: call.data=="menu")
def back(call):
    uid=str(call.from_user.id)
    pts=users[uid]["points"]
    text=f"""
👋 Welcome Back
Points: {pts}/3
"""
    try:
        bot.edit_message_text(text,call.message.chat.id,call.message.message_id,reply_markup=menu())
    except:
        pass

# ===== BROADCAST =====
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id!=ADMIN_ID:
        return
    msg = message.text.replace("/broadcast ","")
    for uid in users:
        try:
            bot.send_message(uid,msg)
        except:
            pass

bot.infinity_polling()