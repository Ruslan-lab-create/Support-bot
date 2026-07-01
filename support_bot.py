import telebot
import json
import os
from datetime import datetime

BOT_TOKEN = "ВСТАВЬ_ТОКЕН_СЮДА"
ADMIN_ID = 123456789
DB_FILE = "users_db.json"

bot = telebot.TeleBot(BOT_TOKEN)

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": {}, "counter": 0, "active_chat": None}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_or_create_user(telegram_id, username, first_name):
    db = load_db()
    key = str(telegram_id)
    if key not in db["users"]:
        db["counter"] += 1
        db["users"][key] = {
            "support_id": db["counter"],
            "telegram_id": telegram_id,
            "username": username or "",
            "first_name": first_name or "",
            "joined": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "messages": []
        }
        save_db(db)
    return db["users"][key]

def get_user_by_support_id(support_id):
    db = load_db()
    for key, user in db["users"].items():
        if user["support_id"] == int(support_id):
            return user
    return None

def get_active_chat():
    db = load_db()
    return db.get("active_chat")

def set_active_chat(support_id):
    db = load_db()
    db["active_chat"] = support_id
    save_db(db)

def add_message(telegram_id, text, from_admin=False):
    db = load_db()
    key = str(telegram_id)
    if key in db["users"]:
        db["users"][key]["messages"].append({
            "from": "admin" if from_admin else "user",
            "text": text,
            "time": datetime.now().strftime("%H:%M")
        })
        save_db(db)

@bot.message_handler(func=lambda m: m.chat.id != ADMIN_ID)
def handle_user_message(message):
    user = get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    add_message(message.from_user.id, message.text)
    name = user["first_name"] or user["username"] or "Без имени"
    username_str = f"@{user['username']}" if user["username"] else "нет username"
    notify = (f"📨 Новое сообщение\n👤 #{user['support_id']} — {name} ({username_str})\n"
              f"🆔 TG ID: {user['telegram_id']}\n💬 {message.text}\n\nЧтобы ответить: /chat {user['support_id']}")
    bot.send_message(ADMIN_ID, notify)
    bot.send_message(message.chat.id, "✅ Ваше сообщение получено! Мы ответим вам в ближайшее время.")

@bot.message_handler(commands=["start"], func=lambda m: m.chat.id == ADMIN_ID)
def admin_start(message):
    bot.send_message(ADMIN_ID, "👋 Панель поддержки\n\n/list — все пользователи\n/chat [номер] — открыть чат\n/history [номер] — история\n/close — закрыть чат\n\nПосле /chat просто пиши — сообщения идут пользователю.")

@bot.message_handler(commands=["list"], func=lambda m: m.chat.id == ADMIN_ID)
def admin_list(message):
    db = load_db()
    if not db["users"]:
        bot.send_message(ADMIN_ID, "📭 Пока нет пользователей.")
        return
    lines = ["👥 Список пользователей:\n"]
    for key, user in sorted(db["users"].items(), key=lambda x: x[1]["support_id"]):
        name = user["first_name"] or user["username"] or "Без имени"
        username_str = f"@{user['username']}" if user["username"] else "—"
        lines.append(f"#{user['support_id']} — {name} ({username_str})\n   🆔 {user['telegram_id']} | 📅 {user['joined']}")
    bot.send_message(ADMIN_ID, "\n".join(lines))

@bot.message_handler(commands=["chat"], func=lambda m: m.chat.id == ADMIN_ID)
def admin_open_chat(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(ADMIN_ID, "❌ Укажи номер: /chat 1")
        return
    user = get_user_by_support_id(parts[1])
    if not user:
        bot.send_message(ADMIN_ID, f"❌ Пользователь #{parts[1]} не найден.")
        return
    set_active_chat(int(parts[1]))
    name = user["first_name"] or user["username"] or "Без имени"
    bot.send_message(ADMIN_ID, f"💬 Открыт чат с #{parts[1]} — {name}\n🆔 {user['telegram_id']}\n\nПросто пиши — сообщения идут ему.\n/close — закрыть чат")

@bot.message_handler(commands=["history"], func=lambda m: m.chat.id == ADMIN_ID)
def admin_history(message):
    parts = message.text.split()
    support_id = int(parts[1]) if len(parts) > 1 else get_active_chat()
    if not support_id:
        bot.send_message(ADMIN_ID, "❌ Укажи номер: /history 1")
        return
    user = get_user_by_support_id(support_id)
    if not user or not user["messages"]:
        bot.send_message(ADMIN_ID, "📭 Сообщений нет.")
        return
    name = user["first_name"] or "Без имени"
    lines = [f"📜 История #{support_id} — {name}:\n"]
    for msg in user["messages"][-20:]:
        icon = "🔵" if msg["from"] == "user" else "🟢"
        sender = name if msg["from"] == "user" else "Ты"
        lines.append(f"{icon} [{msg['time']}] {sender}: {msg['text']}")
    bot.send_message(ADMIN_ID, "\n".join(lines))

@bot.message_handler(commands=["close"], func=lambda m: m.chat.id == ADMIN_ID)
def admin_close_chat(message):
    set_active_chat(None)
    bot.send_message(ADMIN_ID, "✅ Чат закрыт.")

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and not m.text.startswith("/"))
def admin_reply(message):
    active = get_active_chat()
    if not active:
        bot.send_message(ADMIN_ID, "⚠️ Нет активного чата. Выбери: /chat [номер]")
        return
    user = get_user_by_support_id(active)
    try:
        bot.send_message(user["telegram_id"], f"💬 Поддержка: {message.text}")
        add_message(user["telegram_id"], message.text, from_admin=True)
        bot.send_message(ADMIN_ID, f"✅ Отправлено → #{active}")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🤖 Support Bot запущен...")
    bot.infinity_polling()
