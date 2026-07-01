import telebot
import json
import os
from datetime import datetime

BOT_TOKEN = "8789570499:AAHSg2EetCFMb9DRek6VUAoRededZknARCI"
ADMIN_ID = 7867792990
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
            "blocked": False,
            "messages": []
        }
        save_db(db)
    return db["users"][key]

def get_user_by_support_id(support_id):
    db = load_db()
    for key, user in db["users"].items():
        if user["support_id"] == int(support_id):
            return user, key
    return None, None

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

def is_blocked(telegram_id):
    db = load_db()
    key = str(telegram_id)
    if key in db["users"]:
        return db["users"][key].get("blocked", False)
    return False

# ---------- Сообщения от пользователей ----------

def notify_admin(user, message):
    name = user["first_name"] or user["username"] or "Без имени"
    username_str = f"@{user['username']}" if user["username"] else "нет username"
    header = (f"📨 #{user['support_id']} — {name} ({username_str})\n"
              f"🆔 {user['telegram_id']} | /chat {user['support_id']}\n")
    return header

@bot.message_handler(content_types=["text"], func=lambda m: m.chat.id != ADMIN_ID)
def handle_user_text(message):
    if is_blocked(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Вы заблокированы.")
        return
    user = get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    add_message(message.from_user.id, message.text)
    header = notify_admin(user, message)
    bot.send_message(ADMIN_ID, header + f"💬 {message.text}")
    bot.send_message(message.chat.id, "✅ Сообщение получено!")

@bot.message_handler(content_types=["photo"], func=lambda m: m.chat.id != ADMIN_ID)
def handle_user_photo(message):
    if is_blocked(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Вы заблокированы.")
        return
    user = get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    header = notify_admin(user, message)
    bot.send_message(ADMIN_ID, header + "🖼 Фото:")
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "✅ Фото получено!")

@bot.message_handler(content_types=["video"], func=lambda m: m.chat.id != ADMIN_ID)
def handle_user_video(message):
    if is_blocked(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Вы заблокированы.")
        return
    user = get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    header = notify_admin(user, message)
    bot.send_message(ADMIN_ID, header + "🎥 Видео:")
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "✅ Видео получено!")

@bot.message_handler(content_types=["video_note"], func=lambda m: m.chat.id != ADMIN_ID)
def handle_user_video_note(message):
    if is_blocked(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Вы заблокированы.")
        return
    user = get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    header = notify_admin(user, message)
    bot.send_message(ADMIN_ID, header + "⭕ Кружок:")
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "✅ Получено!")

@bot.message_handler(content_types=["voice"], func=lambda m: m.chat.id != ADMIN_ID)
def handle_user_voice(message):
    if is_blocked(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Вы заблокированы.")
        return
    user = get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    header = notify_admin(user, message)
    bot.send_message(ADMIN_ID, header + "🎤 Голосовое:")
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "✅ Получено!")

@bot.message_handler(content_types=["sticker"], func=lambda m: m.chat.id != ADMIN_ID)
def handle_user_sticker(message):
    if is_blocked(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Вы заблокированы.")
        return
    user = get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    header = notify_admin(user, message)
    bot.send_message(ADMIN_ID, header + "🎭 Стикер:")
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

@bot.message_handler(content_types=["document"], func=lambda m: m.chat.id != ADMIN_ID)
def handle_user_document(message):
    if is_blocked(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Вы заблокированы.")
        return
    user = get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    header = notify_admin(user, message)
    bot.send_message(ADMIN_ID, header + "📎 Файл:")
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "✅ Файл получен!")

# ---------- Команды админа ----------

@bot.message_handler(commands=["start"], func=lambda m: m.chat.id == ADMIN_ID)
def admin_start(message):
    bot.send_message(ADMIN_ID,
        "👋 Панель поддержки\n\n"
        "/list — все пользователи\n"
        "/chat [№] — открыть чат\n"
        "/history [№] — история\n"
        "/block [№] — заблокировать\n"
        "/unblock [№] — разблокировать\n"
        "/close — закрыть чат\n\n"
        "После /chat просто пиши или отправляй медиа — всё идёт пользователю."
    )

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
        blocked = " 🚫" if user.get("blocked") else ""
        lines.append(f"#{user['support_id']}{blocked} — {name} ({username_str})\n   🆔 {user['telegram_id']} | 📅 {user['joined']}")
    bot.send_message(ADMIN_ID, "\n".join(lines))

@bot.message_handler(commands=["chat"], func=lambda m: m.chat.id == ADMIN_ID)
def admin_open_chat(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(ADMIN_ID, "❌ Укажи номер: /chat 1")
        return
    user, _ = get_user_by_support_id(parts[1])
    if not user:
        bot.send_message(ADMIN_ID, f"❌ Пользователь #{parts[1]} не найден.")
        return
    set_active_chat(int(parts[1]))
    name = user["first_name"] or user["username"] or "Без имени"
    blocked = " 🚫 ЗАБЛОКИРОВАН" if user.get("blocked") else ""
    bot.send_message(ADMIN_ID, f"💬 Чат с #{parts[1]} — {name}{blocked}\n🆔 {user['telegram_id']}\n\nПиши или отправляй медиа — всё идёт пользователю.\n/close — закрыть")

@bot.message_handler(commands=["block"], func=lambda m: m.chat.id == ADMIN_ID)
def admin_block(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(ADMIN_ID, "❌ Укажи номер: /block 1")
        return
    user, key = get_user_by_support_id(parts[1])
    if not user:
        bot.send_message(ADMIN_ID, f"❌ Пользователь #{parts[1]} не найден.")
        return
    db = load_db()
    db["users"][key]["blocked"] = True
    save_db(db)
    name = user["first_name"] or user["username"] or "Без имени"
    bot.send_message(ADMIN_ID, f"🚫 #{parts[1]} — {name} заблокирован.")
    try:
        bot.send_message(user["telegram_id"], "🚫 Вы были заблокированы и больше не можете писать в поддержку.")
    except:
        pass

@bot.message_handler(commands=["unblock"], func=lambda m: m.chat.id == ADMIN_ID)
def admin_unblock(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(ADMIN_ID, "❌ Укажи номер: /unblock 1")
        return
    user, key = get_user_by_support_id(parts[1])
    if not user:
        bot.send_message(ADMIN_ID, f"❌ Пользователь #{parts[1]} не найден.")
        return
    db = load_db()
    db["users"][key]["blocked"] = False
    save_db(db)
    name = user["first_name"] or user["username"] or "Без имени"
    bot.send_message(ADMIN_ID, f"✅ #{parts[1]} — {name} разблокирован.")
    try:
        bot.send_message(user["telegram_id"], "✅ Вы были разблокированы и снова можете писать в поддержку.")
    except:
        pass

@bot.message_handler(commands=["history"], func=lambda m: m.chat.id == ADMIN_ID)
def admin_history(message):
    parts = message.text.split()
    support_id = int(parts[1]) if len(parts) > 1 else get_active_chat()
    if not support_id:
        bot.send_message(ADMIN_ID, "❌ Укажи номер: /history 1")
        return
    user, _ = get_user_by_support_id(support_id)
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

# ---------- Ответы админа (текст и медиа) ----------

@bot.message_handler(content_types=["text"], func=lambda m: m.chat.id == ADMIN_ID and not m.text.startswith("/"))
def admin_reply_text(message):
    active = get_active_chat()
    if not active:
        bot.send_message(ADMIN_ID, "⚠️ Нет активного чата. /chat [номер]")
        return
    user, _ = get_user_by_support_id(active)
    try:
        bot.send_message(user["telegram_id"], f"💬 Поддержка: {message.text}")
        add_message(user["telegram_id"], message.text, from_admin=True)
        bot.send_message(ADMIN_ID, f"✅ Отправлено → #{active}")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Ошибка: {e}")

@bot.message_handler(content_types=["photo"], func=lambda m: m.chat.id == ADMIN_ID)
def admin_reply_photo(message):
    active = get_active_chat()
    if not active:
        bot.send_message(ADMIN_ID, "⚠️ Нет активного чата. /chat [номер]")
        return
    user, _ = get_user_by_support_id(active)
    try:
        bot.copy_message(user["telegram_id"], ADMIN_ID, message.message_id)
        bot.send_message(ADMIN_ID, f"✅ Фото отправлено → #{active}")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Ошибка: {e}")

@bot.message_handler(content_types=["video"], func=lambda m: m.chat.id == ADMIN_ID)
def admin_reply_video(message):
    active = get_active_chat()
    if not active:
        bot.send_message(ADMIN_ID, "⚠️ Нет активного чата. /chat [номер]")
        return
    user, _ = get_user_by_support_id(active)
    try:
        bot.copy_message(user["telegram_id"], ADMIN_ID, message.message_id)
        bot.send_message(ADMIN_ID, f"✅ Видео отправлено → #{active}")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Ошибка: {e}")

@bot.message_handler(content_types=["video_note"], func=lambda m: m.chat.id == ADMIN_ID)
def admin_reply_video_note(message):
    active = get_active_chat()
    if not active:
        bot.send_message(ADMIN_ID, "⚠️ Нет активного чата. /chat [номер]")
        return
    user, _ = get_user_by_support_id(active)
    try:
        bot.copy_message(user["telegram_id"], ADMIN_ID, message.message_id)
        bot.send_message(ADMIN_ID, f"✅ Кружок отправлен → #{active}")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Ошибка: {e}")

@bot.message_handler(content_types=["voice"], func=lambda m: m.chat.id == ADMIN_ID)
def admin_reply_voice(message):
    active = get_active_chat()
    if not active:
        bot.send_message(ADMIN_ID, "⚠️ Нет активного чата. /chat [номер]")
        return
    user, _ = get_user_by_support_id(active)
    try:
        bot.copy_message(user["telegram_id"], ADMIN_ID, message.message_id)
        bot.send_message(ADMIN_ID, f"✅ Голосовое отправлено → #{active}")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Ошибка: {e}")

@bot.message_handler(content_types=["sticker"], func=lambda m: m.chat.id == ADMIN_ID)
def admin_reply_sticker(message):
    active = get_active_chat()
    if not active:
        bot.send_message(ADMIN_ID, "⚠️ Нет активного чата. /chat [номер]")
        return
    user, _ = get_user_by_support_id(active)
    try:
        bot.copy_message(user["telegram_id"], ADMIN_ID, message.message_id)
        bot.send_message(ADMIN_ID, f"✅ Стикер отправлен → #{active}")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Ошибка: {e}")

@bot.message_handler(content_types=["document"], func=lambda m: m.chat.id == ADMIN_ID)
def admin_reply_document(message):
    active = get_active_chat()
    if not active:
        bot.send_message(ADMIN_ID, "⚠️ Нет активного чата. /chat [номер]")
        return
    user, _ = get_user_by_support_id(active)
    try:
        bot.copy_message(user["telegram_id"], ADMIN_ID, message.message_id)
        bot.send_message(ADMIN_ID, f"✅ Файл отправлен → #{active}")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🤖 Support Bot запущен...")
    bot.infinity_polling()
