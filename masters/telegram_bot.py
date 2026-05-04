import requests
from django.conf import settings

# --- Відправка повідомлення адміністратору ---
def send_telegram_notification_to_admin(text):
    chat_id = getattr(settings, 'ADMIN_TELEGRAM_CHAT_ID', None)
    if not chat_id:
        print("⚠️ ADMIN_TELEGRAM_CHAT_ID не налаштовано!")
        return
        
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not token or token == 'ТВОЙ_НОВИЙ_TOKEN':
        # Якщо токен - плейсхолдер, просто виведемо в консоль
        print(f"📡 [DEBUG TELEGRAM ADMIN]: {text}")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Помилка відправки Telegram адміну: {e}")

# --- Відправка повідомлення барберу ---
def send_telegram_message_to_barber(master, text):
    chat_id = getattr(master, 'telegram_chat_id', None)
    if not chat_id:
        print(f"⚠️ Chat ID для майстра {master} не знайдено!")
        return
    
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not token or token == 'ТВОЙ_НОВИЙ_TOKEN':
        print(f"📡 [DEBUG TELEGRAM BARBER {master}]: {text}")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Помилка відправки Telegram майстру: {e}")

# --- Відправка повідомлення клієнту ---
def send_telegram_message_to_client(client_chat_id, text):
    if not client_chat_id:
        return
        
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not token or token == 'ТВОЙ_НОВИЙ_TOKEN':
        print(f"📡 [DEBUG TELEGRAM CLIENT {client_chat_id}]: {text}")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": client_chat_id, "text": text}
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Помилка відправки Telegram клієнту: {e}")
