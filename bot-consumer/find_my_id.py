import os, requests
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or "Pega_aqui_tu_token"
u = requests.get(f"https://api.telegram.org/bot8378692580:AAHrk868MbaKQUnID0fMcVZWZttpF5yYxUQ/getUpdates").json()
print(u)
# Busca en el JSON: result[...].message.chat.id -> ese es tu CHAT_ID
