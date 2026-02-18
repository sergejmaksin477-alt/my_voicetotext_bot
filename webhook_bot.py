from flask import Flask, request
import os
import httpx

app = Flask(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
SECRET = os.environ.get("SECRET", "my_secret_path_12345")

def transcribe_audio(file_url: str) -> str:
    # Скачай аудио
    audio_response = httpx.get(file_url, timeout=30)
    audio_response.raise_for_status()
    
    # Отправь в Groq
    with httpx.Client(timeout=60) as client:
        response = client.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            data={"model": "whisper-large-v3-turbo", "response_format": "text"},
            files={"file": ("audio.ogg", audio_response.content, "audio/ogg")},
        )
    return response.text.strip()

def send_message(chat_id: int, text: str):
    httpx.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

@app.route(f"/{SECRET}", methods=["POST"])
def webhook():
    update = request.json
    
    if "message" not in update:
        return "ok"
    
    message = update["message"]
    chat_id = message["chat"]["id"]
    
    if "voice" not in message and "audio" not in message:
        return "ok"
    
    voice = message.get("voice") or message.get("audio")
    file_id = voice["file_id"]
    
    send_message(chat_id, "⏳ Транскрибирую...")
    
    try:
        # Получи ссылку на файл
        file_info = httpx.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
        ).json()
        file_path = file_info["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        
        # Транскрибируй
        text = transcribe_audio(file_url)
        send_message(chat_id, f"📝 {text}")
    except Exception as e:
        send_message(chat_id, f"❌ Ошибка: {e}")
    
    return "ok"
```

**Также обнови `requirements.txt`:**
```
Flask==3.0.0
httpx==0.27.0